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

# --- HARDWARE AUTO-SENSING (WAVE 83: ATOMIC PROJECTION ISOLATION) ---
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

if DEVICE == "cuda":
    total_vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    print(f"[SYS] Hardware Sensed: {total_vram:.2f} GB VRAM detected.")
    
    if total_vram > 20.0:
        # WAVE 83: Pushing 32B onto 22GB card with CPU-side math offloading
        print("[+] MID-HIGH VRAM: Proceeding with 32B Reasoning Architecture (Atomic Isolation).")
        MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
        BASE_FILENAME = "healed_r1_32b"
        LAYERS_PER_BATCH = 1 
        OFFLOAD_REASONING = True
    elif total_vram >= 8.0:
        print(f"[+] MID-RANGE VRAM ({total_vram:.2f}GB): Scaling to 7B Reasoning Architecture.")
        MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
        BASE_FILENAME = "healed_r1_7b"
        LAYERS_PER_BATCH = 1 
        OFFLOAD_REASONING = False
    else:
        print("[!] LOW VRAM (<8GB): Restricting to 1.5B Reasoning Architecture.")
        MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
        BASE_FILENAME = "healed_r1_1.5b"
        LAYERS_PER_BATCH = 4
        OFFLOAD_REASONING = False
else:
    print("[!] NO CUDA: Defaulting to 1.5B on CPU.")
    MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
    BASE_FILENAME = "healed_r1_1.5b"
    LAYERS_PER_BATCH = 1
    OFFLOAD_REASONING = False

LATTICE_FILE = "manifold_lattice.json"
NUM_SHARDS = 8

# DRIVE CACHE PROTOCOL
try:
    from google.colab import drive
    print("\n[SYS] Mounting Google Drive...")
    drive.mount('/content/drive')
    CACHE_DIR = "/content/drive/MyDrive/Model_Cache"
    OFFLOAD_DIR = "/content/drive/MyDrive/Model_Offload"
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(OFFLOAD_DIR, exist_ok=True)
    os.environ['HF_HOME'] = CACHE_DIR
except ImportError:
    CACHE_DIR = "."
    OFFLOAD_DIR = "offload_tmp"

class CudaFaultException(Exception):
    pass

def log_hardware_state(phase_name):
    print(f"\n[{phase_name}]")
    cpu_usage = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage(CACHE_DIR)
    print(f" ├─ CPU Usage: {cpu_usage:.1f}%")
    print(f" ├─ Sys RAM:   {ram.used / (1024**3):.2f} GB / {ram.total / (1024**3):.2f} GB")
    print(f" ├─ Storage:   {disk.used / (1024**3):.2f} GB / {disk.total / (1024**3):.2f} GB")
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / (1024**3)
        print(f" └─ GPU VRAM:  {allocated:.2f} GB Allocated")
    print("-" * 50)

def purge_gpu():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()

def make_rational_matrix_torch(M_mat):
    # Mathematics remain strictly in FP32 for spatial integrity
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
    # WAVE 83: CPU-Side analytical math
    w = target_w.to('cpu').float()
    norms = torch.sqrt(torch.sum(w**2, dim=0, keepdim=True) + 1e-5)
    w_norm = w / norms
    m = torch.zeros_like(w_norm)
    m[-1, :] = 1.0
    denom = (1.0 + w_norm[-1, :]).clamp(min=1e-5)
    m[:-1, :] = w_norm[:-1, :] / denom
    return m.clamp(-128.0, 128.0)

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
        purge_gpu()
        with torch.no_grad():
            m1, m2, m3 = self.latent_M1, self.latent_M2, self.latent_M3
            W1 = make_rational_matrix_torch(m1)
            
            W2 = make_rational_matrix_torch(m2)
            W2_o = W2.sub_(W1.mul(torch.sum(W1 * W2, dim=0, keepdim=True)))
            del W2
            W2_o.div_(torch.sqrt(torch.sum(W2_o**2, dim=0, keepdim=True).add_(1e-5)))
            
            W3 = make_rational_matrix_torch(m3)
            W3.sub_(W1.mul(torch.sum(W1 * W3, dim=0, keepdim=True)))
            W3.sub_(W2_o.mul(torch.sum(W2_o * W3, dim=0, keepdim=True)))
            W3_o = W3
            W3_o.div_(torch.sqrt(torch.sum(W3_o**2, dim=0, keepdim=True).add_(1e-5)))
            
            W_total = (torch.cos(self.phi)*(torch.cos(self.theta)*W1 + torch.sin(self.theta)*W2_o) + torch.sin(self.phi)*W3_o)
            
            self.register_buffer('W_fused', (W_total * self.scale).to(target_dtype))
            self.register_buffer('B_fused', self.latent_B.to(target_dtype))
            del W1, W2_o, W3_o, W_total
            purge_gpu()

    def purge_scaffolding(self):
        for attr in ['latent_M1', 'latent_M2', 'latent_M3', 'theta', 'phi', 'scale', 'latent_B']:
            if hasattr(self, attr): delattr(self, attr)

    def forward(self, x):
        if hasattr(self, 'W_fused'):
            return x @ self.W_fused + self.B_fused
        return x @ (make_rational_matrix_torch(self.latent_M1) * self.scale).to(x.dtype) + self.latent_B.to(x.dtype)

# =====================================================================
# RECREATION SEQUENCE
# =====================================================================

purge_gpu()
print("=" * 60)
print(f" RECREATION & BENCHMARKED OPTIMIZATION: {MODEL_NAME} ")
print("=" * 60)

log_hardware_state("BASELINE (PRE-LOAD)")

print(f"\n> Loading Reasoning Architecture ({MODEL_NAME})...")
t0 = time.time()
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
if tokenizer.pad_token is None: tokenizer.pad_token = tokenizer.eos_token

# Load Model with explicit offloading
from accelerate.utils import set_module_tensor_to_device

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME, 
    torch_dtype=torch.bfloat16, 
    low_cpu_mem_usage=True,
    cache_dir=CACHE_DIR,
    device_map="auto" if OFFLOAD_REASONING else None,
    offload_folder=OFFLOAD_DIR,
    attn_implementation="sdpa" 
)

if not OFFLOAD_REASONING:
    model = model.to(DEVICE)

model.eval() 
for param in model.parameters(): param.requires_grad_(False)

if hasattr(model, 'model') and hasattr(model.model, 'layers'):
    blocks = model.model.layers
    target_names = ["self_attn.q_proj", "self_attn.k_proj", "self_attn.v_proj", "self_attn.o_proj", "mlp.gate_proj", "mlp.up_proj", "mlp.down_proj"]
else:
    blocks = model.transformer.h
    target_names = ["attn.c_attn", "mlp.c_fc", "mlp.c_proj"]

num_layers = len(blocks)
print(f"\n> Reconstructing Rational Matrices across {num_layers} layers...")

for i in range(num_layers):
    block = blocks[i]
    
    shard_idx = (i // (max(1, num_layers // NUM_SHARDS))) + 1
    shard_path = os.path.join(CACHE_DIR, f"{BASE_FILENAME}_shard_{shard_idx}.npz")
    shard_data = np.load(shard_path) if os.path.exists(shard_path) else None 

    for name in target_names:
        try:
            parent = block
            parts = name.split('.')
            for part in parts[:-1]: parent = getattr(parent, part)
            attr_name = parts[-1]
            orig_mod = getattr(parent, attr_name)
            
            # WAVE 83: Atomic Materialization - move ONLY the linear layer weight to GPU
            # and immediately perform math to minimize the resident footprint.
            orig_mod.to(DEVICE)
            
            full_key_prefix = f"layer.{i}.{name}"
            is_linear = isinstance(orig_mod, torch.nn.Linear)
            w = orig_mod.weight.detach().T if is_linear else orig_mod.weight.detach()
            
            if w.device.type == 'meta':
                # Emergency materialization if device_map left it on meta
                set_module_tensor_to_device(orig_mod, "weight", DEVICE, dtype=torch.bfloat16)
                w = orig_mod.weight.detach().T if is_linear else orig_mod.weight.detach()

            def get_val(suffix):
                key = f"{full_key_prefix}.{suffix}"
                if shard_data and key in shard_data: return torch.from_numpy(shard_data[key].astype(np.float32)).to(DEVICE)
                return None

            # WAVE 83: Critical Math Offload. Perform F32 heavy operations on CPU.
            m1 = get_val("m1")
            if m1 is None:
                m1 = fast_snap_initialization(w).to(DEVICE)
            
            m2 = get_val("m2") if get_val("m2") is not None else torch.randn(w.shape, device=DEVICE) * 0.01
            m3 = get_val("m3") if get_val("m3") is not None else torch.randn(w.shape, device=DEVICE) * 0.01
            b = get_val("b") if get_val("b") is not None else (orig_mod.bias.detach().float() if getattr(orig_mod, 'bias', None) is not None else torch.zeros(w.shape[1], device=DEVICE))
            
            scale = get_val("scale")
            if scale is None:
                # Perform norm calculation on CPU to avoid the OOM spike
                w_cpu = w.to('cpu').float()
                scale = torch.sqrt(torch.sum(w_cpu**2, dim=0, keepdim=True) + 1e-5).to(DEVICE)
                del w_cpu

            theta = get_val("theta") if get_val("theta") is not None else torch.zeros((1, w.shape[1]), device=DEVICE)
            phi = get_val("phi") if get_val("phi") is not None else torch.zeros((1, w.shape[1]), device=DEVICE)

            harmonic_mod = TriResonantLinear(w, b, scale, theta, phi, m1, m2, m3).to(DEVICE)
            harmonic_mod.crystallize(w.dtype)
            harmonic_mod.purge_scaffolding()
            
            setattr(parent, attr_name, harmonic_mod)
            
            # Atomic Reclamation: Move crystallized module back to its offload location
            harmonic_mod.to('cpu') 
            del m1, m2, m3, b, scale, theta, phi, w, orig_mod
            purge_gpu()
        except AttributeError: continue 

    if i % 8 == 0: print(f"  > Crystallized Layer {i}/{num_layers}...")

log_hardware_state("FINAL AGENT STATE (READY)")

print("\n--- OPTIMIZATION COMPLETE: ASSISTANT ONLINE ---")
print("="*60)

conversation_history = [
    {"role": "system", "content": "You are an elite AI assistant. Provide extremely detailed and step-by-step reasoning. Prioritize depth, accuracy, and efficiency."}
]

while True:
    try:
        user_query = input("\n[USER]: ")
    except EOFError: break
    if not user_query.strip(): continue
    if user_query.lower() in ['exit', 'quit']: break

    conversation_history.append({"role": "user", "content": user_query})
    prompt_text = tokenizer.apply_chat_template(conversation_history, add_generation_prompt=True, tokenize=False)
    
    forced_thought = "<think>\n[SYSTEM: Pushing architectural limits. Offload reasoning enabled. Deep thought active.]\n"
    prompt_text += forced_thought
    inputs = tokenizer(prompt_text, return_tensors="pt").to(DEVICE)
    input_ids = inputs.input_ids
    input_len = input_ids.shape[1]

    t_inf_start = time.time()
    with torch.no_grad():
        outputs = model.generate(
            input_ids, 
            max_new_tokens=1000, 
            do_sample=True, 
            temperature=0.6, 
            top_p=0.95, 
            pad_token_id=tokenizer.eos_token_id,
            use_cache=True 
        )
    inf_time = time.time() - t_inf_start

    new_tokens = outputs[0][input_len:]
    num_generated = len(new_tokens)
    tps = num_generated / inf_time if inf_time > 0 else 0

    response_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
    full_trace = forced_thought.replace("<think>\n", "") + response_text
    
    if "</think>" in full_trace:
        think_trace, agent_response = full_trace.split("</think>", 1)
    else:
        think_trace, agent_response = full_trace, "[Inference Truncated]"

    print(f"\n[THOUGHT TRACE]:\n{think_trace.strip()}")
    print(f"\n[ASSISTANT]:\n{agent_response.strip()}")
    print(f"\n[METRICS]: {num_generated} tokens in {inf_time:.2f}s | Speed: {tps:.2f} tokens/s")
    
    conversation_history.append({"role": "assistant", "content": agent_response.strip()})
    if len(conversation_history) > 7: conversation_history = [conversation_history[0]] + conversation_history[-4:]