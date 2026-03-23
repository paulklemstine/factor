import torch
import torch.nn as nn
import numpy as np
import os
import gc
import time
import sys
import psutil
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
from torch.optim import AdamW
from torch.utils.checkpoint import checkpoint

# --- DYNAMIC DEPENDENCY INJECTION ---
try:
    from datasets import load_dataset
except ImportError:
    print("[SYS] 'datasets' library not found. Installing...")
    os.system(f"{sys.executable} -m pip install datasets")
    from datasets import load_dataset

# --- CONFIGURATION ---
MODEL_NAME = "gpt2" # Base architecture to hollow out and train
DATASET_NAME = "wikitext"
DATASET_CONFIG = "wikitext-2-raw-v1"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Training Hyperparameters
BATCH_SIZE = 1             
GRAD_ACCUM_STEPS = 4       # Accumulate 4 micro-batches to simulate batch size 4
BLOCK_SIZE = 128           # Context window for training
MAX_STEPS = 100            # Set higher (e.g., 5000) for actual deep training
LEARNING_RATE = 5e-4
LATTICE_PENALTY = 0.1      # Strength of the geometric grid alignment

# =====================================================================
# 1. HARDWARE TELEMETRY & HYGIENE
# =====================================================================

def purge_gpu():
    gc.collect()
    if torch.cuda.is_available():
        try:
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            torch.cuda.synchronize()
        except Exception:
            pass

def log_hardware_state(phase_name):
    print(f"\n[{phase_name}]")
    cpu_usage = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory()
    print(f" ├─ CPU Usage: {cpu_usage:.1f}%")
    print(f" ├─ Sys RAM:   {ram.used / (1024**3):.2f} GB / {ram.total / (1024**3):.2f} GB")
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / (1024**3)
        print(f" └─ GPU VRAM:  {allocated:.2f} GB Allocated")
    print("-" * 50)

# =====================================================================
# 2. THEORETICAL MATHEMATICS (TRI-RESONANT LATTICE)
# =====================================================================

def make_rational_matrix_torch(M_mat):
    """Numerically hardened stereographic projection."""
    M_mat = M_mat.float() 
    N, K = M_mat.shape
    m_all_but_last = M_mat[:-1, :]
    m_last = M_mat[-1, :]
    S = torch.sum(m_all_but_last**2, dim=0)
    c = m_last**2 + S
    c_safe = c + (c < 1e-5).float() * 1e-5
    W_raw = torch.cat([(2 * m_all_but_last * m_last) / c_safe, ((m_last**2 - S) / c_safe).unsqueeze(0)], dim=0)
    W_def = torch.zeros((N, K), device=M_mat.device, dtype=torch.float32)
    W_def[0, :] = 1.0
    return torch.where(c < 1e-5, W_def, W_raw)

def fast_snap_initialization(target_w):
    """CPU-bound analytical inverse seeding."""
    w = target_w.to('cpu').float()
    norms = torch.sqrt(torch.sum(w**2, dim=0, keepdim=True) + 1e-5)
    w_norm = w / norms
    m = torch.zeros_like(w_norm)
    m[-1, :] = 1.0
    denom = (1.0 + w_norm[-1, :]).clamp(min=1e-5)
    m[:-1, :] = w_norm[:-1, :] / denom
    return m.clamp(-128.0, 128.0)

def build_manifold_matrix(m1, m2, m3, theta, phi):
    """Isolated construction geometry for gradient checkpointing."""
    W1 = make_rational_matrix_torch(m1)
    W2 = make_rational_matrix_torch(m2)
    W3 = make_rational_matrix_torch(m3)
    
    W2_o = W2 - W1 * torch.sum(W1 * W2, dim=0, keepdim=True)
    W2_o = W2_o / torch.sqrt(torch.sum(W2_o**2, dim=0, keepdim=True) + 1e-5)
    
    W3_o = W3 - W1 * torch.sum(W1 * W3, dim=0, keepdim=True)
    W3_o = W3_o - W2_o * torch.sum(W2_o * W3, dim=0, keepdim=True)
    W3_o = W3_o / torch.sqrt(torch.sum(W3_o**2, dim=0, keepdim=True) + 1e-5)
    
    return (torch.cos(phi)*(torch.cos(theta)*W1 + torch.sin(theta)*W2_o) + torch.sin(phi)*W3_o)

class TriResonantLinear(nn.Module):
    """WAVE 103: Liquid Layer. Retains dynamic parameters for online learning."""
    def __init__(self, weight, bias, scale, theta, phi, m1, m2, m3):
        super().__init__()
        self.in_features, self.out_features = weight.shape
        
        # Trainable Manifold Parameters
        self.latent_M1 = nn.Parameter(m1.float())
        self.latent_M2 = nn.Parameter(m2.float())
        self.latent_M3 = nn.Parameter(m3.float())
        self.latent_B = nn.Parameter(bias.float())
        self.scale = nn.Parameter(scale.float())
        self.theta = nn.Parameter(theta.float())
        self.phi = nn.Parameter(phi.float())
        
        self.periodic_loss = torch.tensor(0.0)

    def forward(self, x):
        m1, m2, m3 = self.latent_M1, self.latent_M2, self.latent_M3
        
        if self.training:
            self.periodic_loss = torch.mean(torch.sin(np.pi * m1)**2) + \
                                 torch.mean(torch.sin(np.pi * m2)**2) + \
                                 torch.mean(torch.sin(np.pi * m3)**2)
            # Use gradient checkpointing to slash graph memory footprint
            W_total = checkpoint(build_manifold_matrix, m1, m2, m3, self.theta, self.phi, use_reentrant=False)
        else:
            # Instantaneous projection for inference
            W_total = build_manifold_matrix(m1, m2, m3, self.theta, self.phi)
        
        return torch.matmul(x, (W_total * self.scale).to(x.dtype)) + self.latent_B.to(x.dtype)

# =====================================================================
# 3. END-TO-END PIPELINE: DATA -> TRAIN -> LIQUIDATE -> AGENT
# =====================================================================

def prepare_training_data(tokenizer):
    print(f"\n[SYS] Downloading & Preparing {DATASET_NAME} dataset...")
    raw_datasets = load_dataset(DATASET_NAME, DATASET_CONFIG)
    
    def tokenize_function(examples):
        return tokenizer(examples["text"])

    tokenized_datasets = raw_datasets.map(tokenize_function, batched=True, num_proc=4, remove_columns=["text"])

    def group_texts(examples):
        concatenated_examples = {k: sum(examples[k], []) for k in examples.keys()}
        total_length = len(concatenated_examples[list(examples.keys())[0]])
        total_length = (total_length // BLOCK_SIZE) * BLOCK_SIZE
        result = {
            k: [t[i : i + BLOCK_SIZE] for i in range(0, total_length, BLOCK_SIZE)]
            for k, t in concatenated_examples.items()
        }
        result["labels"] = result["input_ids"].copy()
        return result

    lm_datasets = tokenized_datasets.map(group_texts, batched=True, num_proc=4)
    train_dataset = lm_datasets["train"]
    
    def collate_fn(batch):
        return {
            'input_ids': torch.tensor([item['input_ids'] for item in batch]),
            'attention_mask': torch.tensor([item['attention_mask'] for item in batch]),
            'labels': torch.tensor([item['labels'] for item in batch])
        }
        
    return DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate_fn)

def inject_manifold_architecture(model):
    print("\n[SYS] Hollowing out base architecture and injecting TriResonant layers...")
    blocks = model.transformer.h
    targets = ["attn.c_attn", "mlp.c_fc", "mlp.c_proj"]
    
    injected_layers = []
    for i, block in enumerate(blocks):
        for name in targets:
            parent = block
            parts = name.split('.')
            for part in parts[:-1]: parent = getattr(parent, part)
            orig_mod = getattr(parent, parts[-1])
            
            w = orig_mod.weight.detach() if orig_mod.__class__.__name__ == "Conv1D" else orig_mod.weight.detach().T
            m1 = fast_snap_initialization(w)
            m2 = torch.randn(w.shape, device='cpu') * 0.01
            m3 = torch.randn(w.shape, device='cpu') * 0.01
            b = (orig_mod.bias.detach().to('cpu').float() if getattr(orig_mod, 'bias', None) is not None else torch.zeros(w.shape[1], device='cpu'))
            scale = torch.sqrt(torch.sum(w.to('cpu').float()**2, dim=0, keepdim=True) + 1e-5)
            theta, phi = torch.zeros((1, w.shape[1]), device='cpu'), torch.zeros((1, w.shape[1]), device='cpu')

            harmonic_mod = TriResonantLinear(w, b, scale, theta, phi, m1, m2, m3)
            setattr(parent, parts[-1], harmonic_mod)
            injected_layers.append(harmonic_mod)
            
    model.to(DEVICE)
    return injected_layers

def train_and_liquefy():
    purge_gpu()
    log_hardware_state("INITIALIZING FORGE")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None: tokenizer.pad_token = tokenizer.eos_token
    
    train_dataloader = prepare_training_data(tokenizer)

    print(f"\n> Loading Base {MODEL_NAME}...")
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    model.gradient_checkpointing_enable()
    
    harmonic_layers = inject_manifold_architecture(model)
    
    print("\n=======================================================")
    print(f" IGNITING MANIFOLD FORGE (Initial Pre-training: {MAX_STEPS} steps)")
    print("=======================================================")
    
    model.train()
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)
    
    step = 0
    t_start = time.time()
    optimizer.zero_grad()
    
    for i, batch in enumerate(train_dataloader):
        if step >= MAX_STEPS: break
        inputs = {k: v.to(DEVICE) for k, v in batch.items()}
        
        with torch.autocast(device_type=DEVICE, dtype=torch.bfloat16 if DEVICE == "cuda" else torch.float32):
            outputs = model(**inputs)
            lm_loss = outputs.loss
            grid_loss = sum(layer.periodic_loss for layer in harmonic_layers)
            total_loss = (lm_loss + (LATTICE_PENALTY * grid_loss)) / GRAD_ACCUM_STEPS
            
        total_loss.backward()
        
        if (i + 1) % GRAD_ACCUM_STEPS == 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            optimizer.zero_grad()
            if step % 10 == 0:
                print(f" [Step {step:4d}/{MAX_STEPS}] Total Loss: {total_loss.item() * GRAD_ACCUM_STEPS:.4f} | LM Loss: {lm_loss.item():.4f}")
            step += 1
            del outputs, lm_loss, grid_loss, total_loss

    print(f"\n[SYS] Pre-training concluded in {time.time() - t_start:.2f}s.")
    
    # WAVE 103: We do NOT crystallize or freeze the model. We keep it liquid.
    model.eval()
    print(" [SYS] Dynamic dimensions retained. Model entering Liquid Manifold State.")
    purge_gpu()
    log_hardware_state("READY FOR CONTINUOUS INFERENCE")
    
    return model, tokenizer, optimizer, harmonic_layers

def run_liquid_agent(model, tokenizer, optimizer, harmonic_layers):
    streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

    print("\n--- LIQUID CRYSTAL AGENT ONLINE ---")
    print("This model learns continuously. Every interaction alters its geometric weights.")
    print("Type 'exit' to terminate.")
    
    conversation_history = "The following is a conversation with a rapidly learning geometric entity.\n\n"
    
    while True:
        try:
            user_query = input("\n[USER]: ")
        except EOFError: break
        if user_query.lower() in ['exit', 'quit']: break
        
        conversation_history += f"User: {user_query}\nAgent:"
        inputs = tokenizer(conversation_history, return_tensors="pt").to(DEVICE)
        
        print("\n[AGENT]: ", end="")
        t_inf_start = time.time()
        
        # Phase 1: Generation (Inference)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100, 
                do_sample=True, 
                temperature=0.8, 
                top_p=0.9, 
                repetition_penalty=1.15, 
                pad_token_id=tokenizer.eos_token_id,
                use_cache=True,
                streamer=streamer
            )
            
        inf_time = time.time() - t_inf_start
        new_tokens = outputs[0][inputs.input_ids.shape[1]:]
        response_text = tokenizer.decode(new_tokens, skip_special_tokens=True).split("User:")[0].strip()
        
        print(f"\n\n[METRICS]: {len(new_tokens)} tokens | SPEED: {len(new_tokens)/inf_time:.2f} tokens/s")
        conversation_history += f" {response_text}\n\n"

        # Phase 2: Online Assimilation (Training)
        print("[SYS] Assimilating interaction into manifold weights...")
        model.train()
        optimizer.zero_grad()
        
        train_inputs = tokenizer(conversation_history, return_tensors="pt").to(DEVICE)
        
        # Prevent OOM during live training by bounding the context window
        if train_inputs.input_ids.shape[1] > BLOCK_SIZE:
            train_inputs.input_ids = train_inputs.input_ids[:, -BLOCK_SIZE:]
            train_inputs.attention_mask = train_inputs.attention_mask[:, -BLOCK_SIZE:]
            
        with torch.autocast(device_type=DEVICE, dtype=torch.bfloat16 if DEVICE == "cuda" else torch.float32):
            loss_outputs = model(input_ids=train_inputs.input_ids, attention_mask=train_inputs.attention_mask, labels=train_inputs.input_ids)
            lm_loss = loss_outputs.loss
            grid_loss = sum(layer.periodic_loss for layer in harmonic_layers)
            total_loss = lm_loss + (LATTICE_PENALTY * grid_loss)
            
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        model.eval() # Return to frozen inference state
        
        print(f"[SYS] Knowledge integrated. Synaptic Flux: {lm_loss.item():.4f}")

# --- EXECUTION ---

if __name__ == "__main__":
    # 1. Forge the model & keep it liquid
    trained_liquid_model, tokenizer, active_optimizer, harmonic_layers = train_and_liquefy()
    
    # 2. Serve it with online learning enabled
    run_liquid_agent(trained_liquid_model, tokenizer, active_optimizer, harmonic_layers)