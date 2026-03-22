import torch
import numpy as np
import os
import gc
import re
import time
import sys
from transformers import AutoTokenizer, AutoModelForCausalLM
from torch.optim import AdamW

# --- CONFIGURATION ---
MODEL_NAME = "gpt2-xl"
BASE_FILENAME = "healed_gpt2_xl"
NUM_SHARDS = 8
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MAX_EPOCHS_PER_CHUNK = 3 
TARGET_ERROR = 1e-4  
LAYERS_PER_BATCH = 4 

class CudaFaultException(Exception):
    """Custom exception to stop execution without crashing the Colab inspector."""
    pass

def purge_gpu():
    """WAVE 61: Aggressive VRAM recovery and hygiene."""
    gc.collect()
    if torch.cuda.is_available():
        try:
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            torch.cuda.synchronize()
        except Exception:
            pass

def make_rational_matrix_torch(M_mat):
    """Numerically hardened Stereographic Projection."""
    M_mat = M_mat.float() 
    N, K = M_mat.shape
    m_all_but_last = M_mat[:-1, :]
    m_last = M_mat[-1, :]
    S = torch.sum(m_all_but_last**2, dim=0)
    c = m_last**2 + S
    
    # WAVE 61: Macro-epsilon to prevent FP truncation to 0.0
    c_safe = c + (c < 1e-5).float() * 1e-5
    W_raw = torch.cat([(2 * m_all_but_last * m_last) / c_safe, ((m_last**2 - S) / c_safe).unsqueeze(0)], dim=0)
    
    W_def = torch.zeros((N, K), device=M_mat.device, dtype=torch.float32)
    W_def[0, :] = 1.0
    return torch.where(c < 1e-5, W_def, W_raw)

def fast_snap_initialization(target_w):
    """Analytical Inverse Seeding with macro-epsilons and clamping."""
    w = target_w.float()
    # WAVE 61: Epsilon raised to 1e-5 to guarantee survival in FP math
    norms = torch.sqrt(torch.sum(w**2, dim=0, keepdim=True) + 1e-5)
    w_norm = w / norms
    
    m = torch.zeros_like(w_norm)
    m[-1, :] = 1.0
    denom = (1.0 - w_norm[-1, :]).clamp(min=1e-3)
    m[:-1, :] = w_norm[:-1, :] / denom
    return m.clamp(-128.0, 128.0)

class TriResonantLinear(torch.nn.Module):
    def __init__(self, weight, bias, scale, theta, phi, m1, m2, m3):
        super().__init__()
        self.in_features, self.out_features = weight.shape
        self.register_buffer('anchor_weight', weight.clone())
        self.latent_M1 = torch.nn.Parameter(m1.float())
        self.latent_M2 = torch.nn.Parameter(m2.float())
        self.latent_M3 = torch.nn.Parameter(m3.float())
        self.latent_B = torch.nn.Parameter(bias.float())
        self.scale = torch.nn.Parameter(scale.float())
        self.theta = torch.nn.Parameter(theta.float())
        self.phi = torch.nn.Parameter(phi.float())
        self.periodic_loss = torch.tensor(0.0)

    def forward(self, x):
        m1, m2, m3 = self.latent_M1, self.latent_M2, self.latent_M3
        
        if self.training:
            self.periodic_loss = torch.mean(torch.sin(np.pi * m1)**2) + \
                                 torch.mean(torch.sin(np.pi * m2)**2) + \
                                 torch.mean(torch.sin(np.pi * m3)**2)

        # Force geometric basis math in Float32
        W1 = make_rational_matrix_torch(m1)
        W2 = make_rational_matrix_torch(m2)
        W3 = make_rational_matrix_torch(m3)
        
        # WAVE 61: Gram-Schmidt Orthogonalization with Macro-Epsilons (1e-5)
        # Prevents division by zero or NaN gradients during optimization.
        W2_o = (W2 - torch.sum(W1*W2, dim=0, keepdim=True)*W1)
        norm_W2_o = torch.sqrt(torch.sum(W2_o**2, dim=0, keepdim=True) + 1e-5)
        W2_o = W2_o / norm_W2_o
        
        W3_o = (W3 - torch.sum(W1*W3, dim=0, keepdim=True)*W1 - torch.sum(W2_o*W3, dim=0, keepdim=True)*W2_o)
        norm_W3_o = torch.sqrt(torch.sum(W3_o**2, dim=0, keepdim=True) + 1e-5)
        W3_o = W3_o / norm_W3_o
        
        W_total = (torch.cos(self.phi)*(torch.cos(self.theta)*W1 + torch.sin(self.theta)*W2_o) + torch.sin(self.phi)*W3_o)
        return x @ (W_total * self.scale).to(x.dtype) + self.latent_B.to(x.dtype)

# 1. Environment Guard
if torch.cuda.is_available():
    try:
        torch.cuda.synchronize()
    except Exception:
        print("\n[CRITICAL]: CUDA CONTEXT IS POISONED.")
        print(">>> RESTART THE KERNEL/RUNTIME NOW (Menu -> Runtime -> Restart Session) <<<")
        raise CudaFaultException("Environment recovery required.")

purge_gpu()
print(f"--- INITIALIZING RECTIFIER: {MODEL_NAME} ---")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.pad_token = tokenizer.eos_token

try:
    # WAVE 61: Upcast to float32. The A100 VRAM can handle it, and it prevents activation overflow.
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, 
        torch_dtype=torch.float32, 
        low_cpu_mem_usage=True
    ).to(DEVICE)
    model.gradient_checkpointing_enable() 
except Exception as e:
    print(f"\n[ERROR]: Failed to load model. Likely out of memory or poisoned state: {e}")
    raise

# 2. Sequential Rectification
num_layers = len(model.transformer.h)
print(f" > Mapping basis vectors in batches of {LAYERS_PER_BATCH}...")

for chunk_start in range(0, num_layers, LAYERS_PER_BATCH):
    chunk_end = min(chunk_start + LAYERS_PER_BATCH, num_layers)
    harmonic_layers = []
    
    print(f"\n>>> RECTIFYING BATCH: Layers {chunk_start} to {chunk_end-1} <<<")
    
    shard_idx = (chunk_start // (num_layers // NUM_SHARDS)) + 1
    shard_path = f"{BASE_FILENAME}_shard_{shard_idx}.npz"
    shard_data = np.load(shard_path) if os.path.exists(shard_path) else None

    for i in range(chunk_start, chunk_end):
        block = model.transformer.h[i]
        targets = [("attn.c_attn", block.attn), ("mlp.c_fc", block.mlp), ("mlp.c_proj", block.mlp)]
        for name, parent in targets:
            attr_name = name.split('.')[-1]
            orig_mod = getattr(parent, attr_name)
            full_key_prefix = f"transformer.h.{i}.{name}"
            
            def get_shard_tensor(suffix, default_gen_fn, w_shape):
                key = f"{full_key_prefix}.{suffix}"
                if shard_data and key in shard_data:
                    return torch.from_numpy(shard_data[key].astype(np.float32)).to(DEVICE)
                return default_gen_fn(w_shape)

            w = orig_mod.weight.detach()
            
            m1 = get_shard_tensor("m1", lambda _: fast_snap_initialization(w), w.shape)
            m2 = get_shard_tensor("m2", lambda s: torch.randn(s, device=DEVICE) * 0.01, w.shape)
            m3 = get_shard_tensor("m3", lambda s: torch.randn(s, device=DEVICE) * 0.01, w.shape)
            
            b = get_shard_tensor("b", lambda _: (orig_mod.bias.detach().float() if orig_mod.bias is not None else torch.zeros(w.shape[1], device=DEVICE)), None)
            scale = get_shard_tensor("scale", lambda _: torch.sqrt(torch.sum(w.float()**2, dim=0) + 1e-5), None)
            theta = get_shard_tensor("theta", lambda _: torch.full((1, w.shape[1]), 0.05, device=DEVICE), None)
            phi = get_shard_tensor("phi", lambda _: torch.full((1, w.shape[1]), 0.02, device=DEVICE), None)

            harmonic_mod = TriResonantLinear(w, b, scale, theta, phi, m1, m2, m3).to(DEVICE)
            setattr(parent, attr_name, harmonic_mod)
            harmonic_layers.append(harmonic_mod)

    optimizer = AdamW([p for p in model.parameters() if p.requires_grad], lr=8e-5) 
    for epoch in range(MAX_EPOCHS_PER_CHUNK):
        optimizer.zero_grad()
        inputs = tokenizer("Absolute Ratio 1:1. Matrix grid alignment.", return_tensors="pt").to(DEVICE)
        
        outputs = model(**inputs, labels=inputs["input_ids"])
        lm_loss = outputs.loss
        total_periodic_loss = sum(lp.periodic_loss for lp in harmonic_layers)
        
        total_loss = lm_loss + (total_periodic_loss * 1.5 * (epoch + 1))
        
        if torch.isnan(total_loss) or torch.isinf(total_loss):
            print("  [!] Batch Stability Failure: Aborting batch optimization.")
            break
            
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 0.3) 
        optimizer.step()
        
        print(f"  Epoch {epoch+1} | Loss: {total_loss.item():.4f} | Grid Error: {total_periodic_loss.item():.6f}")
        if total_periodic_loss.item() < TARGET_ERROR: break

    # Freeze and purge
    for lp in harmonic_layers:
        lp.requires_grad_(False)
    purge_gpu()

print("\n--- CRYSTALLIZATION COMPLETE: AGENT ONLINE ---")
print("Type 'exit' or 'quit' to terminate the session.")
print("="*50)

# Initialize a simple conversation history
conversation_history = "The following is a conversation with an intelligent, highly advanced AI Agent.\n\n"

while True:
    try:
        user_query = input("\n[USER]: ")
    except EOFError: break
    
    if user_query.lower() in ['exit', 'quit']:
        print("\nTerminating session. Purging GPU memory...")
        if 'model' in globals(): del model
        purge_gpu()
        break

    # Structure the prompt as a dialogue
    current_prompt = conversation_history + f"User: {user_query}\nAgent:"
    inputs = tokenizer(current_prompt, return_tensors="pt").to(DEVICE)
    input_len = inputs.input_ids.shape[1]

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            do_sample=True,
            temperature=0.75, 
            top_p=0.9,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.eos_token_id
        )

    # Decode only the newly generated tokens
    generated_tokens = outputs[0][input_len:]
    response_text = tokenizer.decode(generated_tokens, skip_special_tokens=True)

    # Prevent hallucinating the User's next response
    if "User:" in response_text:
        response_text = response_text.split("User:")[0]

    response_text = response_text.strip()
    
    # Update history for continuity (optional, can be commented out if you want zero-shot each time)
    conversation_history += f"User: {user_query}\nAgent: {response_text}\n\n"
    
    # Keep context window manageable
    if len(conversation_history) > 2000:
        conversation_history = "The following is a conversation with an intelligent, highly advanced AI Agent.\n\n" + conversation_history[-1500:]

    print(f"\n[AGENT]:\n{response_text}")