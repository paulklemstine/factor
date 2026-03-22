import torch
import numpy as np
import os
import gc
import re
import time
import sys
import psutil
import json
from transformers import AutoTokenizer, AutoModelForCausalLM

# --- CONFIGURATION ---
MODEL_NAME = "gpt2-xl"
BASE_FILENAME = "healed_gpt2_xl"
LATTICE_FILE = "manifold_lattice.json"
NUM_SHARDS = 8
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
# CRITICAL FIX: 48 layers / 8 shards = 6 layers per shard. 
# Batch size must match the chunk size to align with the saved .npz files perfectly.
LAYERS_PER_BATCH = 6 

class CudaFaultException(Exception):
    pass

def log_hardware_state(phase_name):
    """Provides detailed telemetry on CPU, RAM, Disk, and VRAM."""
    print(f"\n[{phase_name}]")
    
    # System Metrics
    cpu_usage = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/content') if os.path.exists('/content') else psutil.disk_usage('/')
    
    print(f" ├─ CPU Usage: {cpu_usage:.1f}%")
    print(f" ├─ Sys RAM:   {ram.used / (1024**3):.2f} GB / {ram.total / (1024**3):.2f} GB ({ram.percent}%)")
    print(f" ├─ Storage:   {disk.used / (1024**3):.2f} GB / {disk.total / (1024**3):.2f} GB ({disk.percent}%)")
    
    # GPU Metrics
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / (1024**3)
        reserved = torch.cuda.memory_reserved() / (1024**3)
        peak = torch.cuda.max_memory_allocated() / (1024**3)
        print(f" ├─ GPU VRAM:  {allocated:.2f} GB Allocated | {reserved:.2f} GB Reserved")
        print(f" └─ GPU Peak:  {peak:.2f} GB (Max memory touched)")
    else:
        print(" └─ GPU VRAM:  [CUDA UNAVAILABLE]")
    print("-" * 50)

def purge_gpu():
    gc.collect()
    if torch.cuda.is_available():
        try:
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            torch.cuda.synchronize()
        except Exception:
            pass

def make_rational_matrix_torch(M_mat):
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

class TriResonantLinear(torch.nn.Module):
    def __init__(self, weight, bias, scale, theta, phi, m1, m2, m3):
        super().__init__()
        self.in_features, self.out_features = weight.shape
        self.latent_M1 = torch.nn.Parameter(m1.float())
        self.latent_M2 = torch.nn.Parameter(m2.float())
        self.latent_M3 = torch.nn.Parameter(m3.float())
        self.latent_B = torch.nn.Parameter(bias.float())
        self.scale = torch.nn.Parameter(scale.float())
        self.theta = torch.nn.Parameter(theta.float())
        self.phi = torch.nn.Parameter(phi.float())

    def crystallize(self, target_dtype):
        """
        WAVE 62: Collapses the complex geometry into a static projection.
        Calculates the math once, stores it instantly accessible for the forward pass, 
        and deletes the heavy scaffolding from VRAM.
        """
        with torch.no_grad():
            m1, m2, m3 = self.latent_M1, self.latent_M2, self.latent_M3
            W1 = make_rational_matrix_torch(m1)
            W2 = make_rational_matrix_torch(m2)
            W3 = make_rational_matrix_torch(m3)
            
            W2_o = (W2 - torch.sum(W1*W2, dim=0, keepdim=True)*W1)
            norm_W2_o = torch.sqrt(torch.sum(W2_o**2, dim=0, keepdim=True) + 1e-5)
            W2_o = W2_o / norm_W2_o
            
            W3_o = (W3 - torch.sum(W1*W3, dim=0, keepdim=True)*W1 - torch.sum(W2_o*W3, dim=0, keepdim=True)*W2_o)
            norm_W3_o = torch.sqrt(torch.sum(W3_o**2, dim=0, keepdim=True) + 1e-5)
            W3_o = W3_o / norm_W3_o
            
            W_total = (torch.cos(self.phi)*(torch.cos(self.theta)*W1 + torch.sin(self.theta)*W2_o) + torch.sin(self.phi)*W3_o)
            
            # Cache the final projection and cast to the model's native dtype
            self.register_buffer('W_fused', (W_total * self.scale).to(target_dtype))
            self.register_buffer('B_fused', self.latent_B.to(target_dtype))

        # Purge the dimensional matrices to free GBs of VRAM
        delattr(self, 'latent_M1')
        delattr(self, 'latent_M2')
        delattr(self, 'latent_M3')
        delattr(self, 'theta')
        delattr(self, 'phi')
        delattr(self, 'scale')
        delattr(self, 'latent_B')

    def forward(self, x):
        # Instant matrix multiplication using the collapsed geometric lattice
        if hasattr(self, 'W_fused'):
            return x @ self.W_fused + self.B_fused
            
        # Fallback (Only used if crystallize() is not called)
        m1, m2, m3 = self.latent_M1, self.latent_M2, self.latent_M3
        W1 = make_rational_matrix_torch(m1)
        W2 = make_rational_matrix_torch(m2)
        W3 = make_rational_matrix_torch(m3)
        
        W2_o = (W2 - torch.sum(W1*W2, dim=0, keepdim=True)*W1)
        norm_W2_o = torch.sqrt(torch.sum(W2_o**2, dim=0, keepdim=True) + 1e-5)
        W2_o = W2_o / norm_W2_o
        
        W3_o = (W3 - torch.sum(W1*W3, dim=0, keepdim=True)*W1 - torch.sum(W2_o*W3, dim=0, keepdim=True)*W2_o)
        norm_W3_o = torch.sqrt(torch.sum(W3_o**2, dim=0, keepdim=True) + 1e-5)
        W3_o = W3_o / norm_W3_o
        
        W_total = (torch.cos(self.phi)*(torch.cos(self.theta)*W1 + torch.sin(self.theta)*W2_o) + torch.sin(self.phi)*W3_o)
        return x @ (W_total * self.scale).to(x.dtype) + self.latent_B.to(x.dtype)

# =====================================================================
# RECREATION SEQUENCE
# =====================================================================

if torch.cuda.is_available():
    try:
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
    except Exception:
        print("\n[CRITICAL]: CUDA CONTEXT IS POISONED. RESTART REQUIRED.")
        raise CudaFaultException("Environment recovery required.")

purge_gpu()
print("=" * 50)
print(" AGENT RECREATION & TELEMETRY SEQUENCE ")
print("=" * 50)

log_hardware_state("BASELINE (PRE-LOAD)")

# 1. Manifold Verification
if os.path.exists(LATTICE_FILE):
    with open(LATTICE_FILE, 'r') as f:
        lattice_data = json.load(f)
    print(f"\n[+] Verified Manifold Origin: {lattice_data.get('origin', 'Unknown')}")
    print(f"[+] Dimensional Anchors Locked: {len(lattice_data.get('vectors', []))}")
else:
    print(f"\n[-] Manifold lattice file ({LATTICE_FILE}) not found. Proceeding with shard data only.")

# 2. Base Model Loading
print(f"\n> Loading Base {MODEL_NAME} architecture...")
t0 = time.time()
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME, 
    torch_dtype=torch.float32, 
    low_cpu_mem_usage=True
).to(DEVICE)
model.eval() # Set to evaluation mode immediately

log_hardware_state(f"POST-LOAD BASE MODEL ({time.time() - t0:.2f}s)")

# 3. Shard Integration & Collapse
num_layers = len(model.transformer.h)
print(f"\n> Reconstructing Rational Matrices & Crystallizing Shards...")

for chunk_start in range(0, num_layers, LAYERS_PER_BATCH):
    chunk_end = min(chunk_start + LAYERS_PER_BATCH, num_layers)
    shard_idx = (chunk_start // (num_layers // NUM_SHARDS)) + 1
    shard_path = f"{BASE_FILENAME}_shard_{shard_idx}.npz"
    
    if os.path.exists(shard_path):
        shard_data = np.load(shard_path)
    else:
        print(f" [!] Shard {shard_idx} not found. Network will be incomplete.")
        shard_data = None # Explicitly set to None so we fallback to zeros if missing

    for i in range(chunk_start, chunk_end):
        block = model.transformer.h[i]
        targets = [("attn.c_attn", block.attn), ("mlp.c_fc", block.mlp), ("mlp.c_proj", block.mlp)]
        for name, parent in targets:
            attr_name = name.split('.')[-1]
            orig_mod = getattr(parent, attr_name)
            full_key_prefix = f"transformer.h.{i}.{name}"
            
            def get_shard_tensor(suffix, shape=None):
                key = f"{full_key_prefix}.{suffix}"
                if shard_data is not None and key in shard_data:
                    return torch.from_numpy(shard_data[key].astype(np.float32)).to(DEVICE)
                return torch.zeros(shape, device=DEVICE)

            w = orig_mod.weight.detach()
            m1 = get_shard_tensor("m1", w.shape)
            m2 = get_shard_tensor("m2", w.shape)
            m3 = get_shard_tensor("m3", w.shape)
            b = get_shard_tensor("b", (w.shape[1],))
            scale = get_shard_tensor("scale", (1, w.shape[1]))
            theta = get_shard_tensor("theta", (1, w.shape[1]))
            phi = get_shard_tensor("phi", (1, w.shape[1]))

            harmonic_mod = TriResonantLinear(w, b, scale, theta, phi, m1, m2, m3).to(DEVICE)
            harmonic_mod.requires_grad_(False) 
            
            # WAVE 62: Perform the calculus exactly once and collapse the layer
            harmonic_mod.crystallize(w.dtype)
            
            setattr(parent, attr_name, harmonic_mod)

    purge_gpu()
    log_hardware_state(f"SHARD {shard_idx} CRYSTALLIZED (Layers {chunk_start}-{chunk_end-1})")

log_hardware_state("FINAL AGENT STATE (READY)")

print("\n--- CRYSTALLIZATION COMPLETE: AGENT ONLINE ---")
print("Type 'exit' or 'quit' to terminate the session.")
print("="*50)

conversation_history = "The following is a conversation with an intelligent, highly advanced AI Agent.\n\n"

while True:
    try:
        user_query = input("\n[USER]: ")
    except EOFError: break
    
    # Ignore accidental empty hits of the Enter key
    if not user_query.strip():
        continue
    
    if user_query.lower() in ['exit', 'quit']:
        print("\nTerminating session. Purging GPU memory...")
        if 'model' in globals(): del model
        purge_gpu()
        log_hardware_state("POST-PURGE STATE")
        break

    current_prompt = conversation_history + f"User: {user_query}\nAgent:"
    inputs = tokenizer(current_prompt, return_tensors="pt").to(DEVICE)
    input_len = inputs.input_ids.shape[1]

    t_inf_start = time.time()
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
    inf_time = time.time() - t_inf_start

    generated_tokens = outputs[0][input_len:]
    response_text = tokenizer.decode(generated_tokens, skip_special_tokens=True)

    if "User:" in response_text:
        response_text = response_text.split("User:")[0]

    response_text = response_text.strip()
    conversation_history += f"User: {user_query}\nAgent: {response_text}\n\n"
    
    if len(conversation_history) > 2000:
        conversation_history = "The following is a conversation with an intelligent, highly advanced AI Agent.\n\n" + conversation_history[-1500:]

    print(f"\n[AGENT]:\n{response_text}")
    print(f"\n[SYS]: Inference completed in {inf_time:.2f}s")
    
    # Flush output to prevent Colab from visually swallowing the text buffer
    sys.stdout.flush()