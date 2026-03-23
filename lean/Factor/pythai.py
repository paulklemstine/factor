import torch
import torch.distributed as dist
import numpy as np
import os
import gc
import re
import time
import sys
import psutil
import json
from transformers import AutoTokenizer, AutoModelForCausalLM
from accelerate.utils import set_module_tensor_to_device
from huggingface_hub import snapshot_download

# --- CONFIGURATION ---
RUN_QUICK_TEST = False  # Disabled to prevent VRAM overlap
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
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

# --- CORE MATHEMATICAL UTILITIES ---

def log_hardware_state(phase_name):
    print(f"\n[{phase_name}]")
    cpu_usage = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory()
    print(f" ├─ CPU Usage: {cpu_usage:.1f}%")
    print(f" ├─ Sys RAM:   {ram.used / (1024**3):.2f} GB / {ram.total / (1024**3):.2f} GB")
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / (1024**3)
        reserved = torch.cuda.memory_reserved() / (1024**3)
        print(f" └─ GPU VRAM:  {allocated:.2f} GB Allocated")
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

def fast_snap_initialization(target_w):
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
        # Math strictly on CPU to avoid GPU spikes
        self.to('cpu')
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
            self.register_buffer('W_fused', (W_total * self.scale).to(dtype=target_dtype))
            self.register_buffer('B_fused', self.latent_B.to(dtype=target_dtype))
            del W1, W2_o, W3_o, W_total

    def purge_scaffolding(self):
        for attr in ['latent_M1', 'latent_M2', 'latent_M3', 'theta', 'phi', 'scale', 'latent_B']:
            if hasattr(self, attr): delattr(self, attr)

    def forward(self, x):
        if hasattr(self, 'W_fused'):
            return x @ self.W_fused + self.B_fused
        return x @ (make_rational_matrix_torch(self.latent_M1) * self.scale).to(x.dtype) + self.latent_B.to(x.dtype)

# --- RECREATION PIPELINE ---

def run_crystalline_cycle(model_name, base_filename, offload=False, is_test=False):
    purge_gpu()
    
    # WAVE 88: Initialize Process Group for materialization utilities
    if DEVICE == "cuda" and not dist.is_initialized():
        os.environ['MASTER_ADDR'] = 'localhost'
        os.environ['MASTER_PORT'] = '12355'
        dist.init_process_group(backend='nccl', rank=0, world_size=1)

    print(f"\n{'='*20} {'QUICK TEST' if is_test else 'BIG TEST'}: {model_name} {'='*20}")
    log_hardware_state("PRE-LOAD")

    print(f"> Loading {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=CACHE_DIR)
    if tokenizer.pad_token is None: tokenizer.pad_token = tokenizer.eos_token

    # VRAM Ceiling logic
    max_mem = None
    if offload and DEVICE == "cuda":
        total_vram_bytes = torch.cuda.get_device_properties(0).total_memory
        gpu_limit = f"{int((total_vram_bytes / (1024**2)) - 4096)}MiB"
        max_mem = {0: gpu_limit, "cpu": "45GiB"}
        print(f" [!] Capping GPU allocation at {gpu_limit} to prevent OOM spikes.")

    try:
        load_path = snapshot_download(model_name, cache_dir=CACHE_DIR, local_files_only=True)
    except Exception:
        load_path = model_name

    model = AutoModelForCausalLM.from_pretrained(
        model_name, 
        torch_dtype=torch.bfloat16 if DEVICE == "cuda" else torch.float32, 
        low_cpu_mem_usage=True,
        cache_dir=CACHE_DIR,
        device_map="auto" if offload else None,
        max_memory=max_mem,
        offload_folder=OFFLOAD_DIR if offload else None,
        attn_implementation="sdpa" if DEVICE == "cuda" else "eager"
    )

    if not offload: model = model.to(DEVICE)
    model.eval() 
    for param in model.parameters(): param.requires_grad_(False)

    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        blocks = model.model.layers
        targets = ["self_attn.q_proj", "self_attn.k_proj", "self_attn.v_proj", "self_attn.o_proj", "mlp.gate_proj", "mlp.up_proj", "mlp.down_proj"]
    else:
        blocks = model.transformer.h
        targets = ["attn.c_attn", "mlp.c_fc", "mlp.c_proj"]

    print(f"> Crystallizing {len(blocks)} layers...")
    for i in range(len(blocks)):
        block = blocks[i]
        
        # WAVE 88: Block-Level Materialization
        # Materialize the whole layer once from disk to satisfy hierarchical keys
        if any(p.device.type == 'meta' for p in block.parameters()):
            from accelerate import load_checkpoint_in_model
            # Reconstitute the full block into CPU memory
            load_checkpoint_in_model(block, load_path)
            
        for name in targets:
            try:
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

                harmonic_mod = TriResonantLinear(w.to('cpu'), b, scale, theta, phi, m1, m2, m3)
                harmonic_mod.crystallize(orig_mod.weight.dtype)
                harmonic_mod.purge_scaffolding()
                
                # Keep crystallized weights on CPU during loop if offloading
                target_dev = 'cpu' if offload else orig_mod.weight.device
                harmonic_mod.to(target_dev)
                
                delattr(parent, parts[-1])
                setattr(parent, parts[-1], harmonic_mod)
                del m1, m2, m3, b, scale, w
            except AttributeError: continue 
            
        # WAVE 88: Block Cleanup
        # If we materialized this block to CPU, move it back to its original device map preference
        if offload:
            block.to('cpu')

        if i % 8 == 0: 
            print(f"  > Progressive Lock: Layer {i}/{len(blocks)}...")
            purge_gpu()

    log_hardware_state("READY")

    if is_test:
        print("\n--- TEST INFERENCE ---")
        prompt = "The quick brown fox"
        inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=10)
        res = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"[TEST OUTPUT]: {res}")
        del model, tokenizer
        purge_gpu()
        return

    # BIG TEST: Interactive Assistant
    print("\n--- ASSISTANT ONLINE ---")
    conversation_history = [{"role": "system", "content": "You are a highly skilled AI assistant."}]
    while True:
        try:
            user_query = input("\n[USER]: ")
        except EOFError: break
        if user_query.lower() in ['exit', 'quit']: break
        
        conversation_history.append({"role": "user", "content": user_query})
        try:
            prompt_text = tokenizer.apply_chat_template(conversation_history, add_generation_prompt=True, tokenize=False)
        except Exception:
            prompt_text = "\n".join([f"{m['role']}: {m['content']}" for m in conversation_history]) + "\nassistant:"

        forced_thought = "<think>\n[SYSTEM: Optimizing for performance. Reasoning deeply.]\n"
        prompt_text += forced_thought
        inputs = tokenizer(prompt_text, return_tensors="pt").to(DEVICE)
        t_inf_start = time.time()
        with torch.no_grad():
            outputs = model.generate(inputs.input_ids, max_new_tokens=1000, do_sample=True, temperature=0.6, top_p=0.95, pad_token_id=tokenizer.eos_token_id)
        inf_time = time.time() - t_inf_start
        
        new_tokens = outputs[0][inputs.input_ids.shape[1]:]
        response_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
        full_trace = forced_thought.replace("<think>\n", "") + response_text
        
        think_trace, agent_response = (full_trace.split("</think>", 1) if "</think>" in full_trace else (full_trace, "[Inference Truncated]"))
        print(f"\n[THOUGHT]: {think_trace.strip()}\n[ASSISTANT]: {agent_response.strip()}\n[METRICS]: {len(new_tokens)} tokens | {len(new_tokens)/inf_time:.2f} tokens/s")
        conversation_history.append({"role": "assistant", "content": agent_response.strip()})

# --- EXECUTION ---

if __name__ == "__main__":
    if RUN_QUICK_TEST:
        run_crystalline_cycle("gpt2", "test_gpt2", offload=False, is_test=True)

    if DEVICE == "cuda":
        total_vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        if total_vram > 20.0:
            BIG_MODEL, BIG_BASE, OFFLOAD = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B", "healed_r1_32b", True
        elif total_vram >= 8.0:
            BIG_MODEL, BIG_BASE, OFFLOAD = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B", "healed_r1_7b", False
        else:
            BIG_MODEL, BIG_BASE, OFFLOAD = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B", "healed_r1_1.5b", False
    else:
        BIG_MODEL, BIG_BASE, OFFLOAD = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B", "healed_r1_1.5b", False

    run_crystalline_cycle(BIG_MODEL, BIG_BASE, offload=OFFLOAD, is_test=False)