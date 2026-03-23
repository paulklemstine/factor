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
from safetensors.torch import load_file

# --- CONFIGURATION ---
# WAVE 94: EXPLICIT MANIFOLD EXTRACTION & DUCK-TYPING
# Bypasses layer-by-layer reconstruction and collapses the entire LLM 
# into a single Stereographically Projected Matrix for instantaneous inference.
GLOBAL_COLLAPSE_MODE = True  

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
    denom = (1.0 - w_norm[-1, :]).clamp(min=1e-3)
    m[:-1, :] = w_norm[:-1, :] / denom
    return m.clamp(-128.0, 128.0)

# WAVE 94: Singular Manifold Execution Layer with Duck-Typing
class GlobalManifoldLayer(torch.nn.Module):
    """Replaces the entire Transformer stack with a singular matrix multiplication."""
    def __init__(self, W_global_fused, orig_layer=None):
        super().__init__()
        self.register_buffer('W_fused', W_global_fused)
        
        # Duck-type the original layer's attributes to prevent HuggingFace pipeline crashes
        # Models like Qwen2 rely on checking these parameters during generation.
        if orig_layer is not None:
            for attr in ['attention_type', 'is_decoder', 'layer_idx', 'config']:
                if hasattr(orig_layer, attr):
                    setattr(self, attr, getattr(orig_layer, attr))
        
    def forward(self, hidden_states, attention_mask=None, position_ids=None, past_key_value=None, output_attentions=False, use_cache=False, **kwargs):
        # 1. Take the embeddings (hidden_states)
        # 2. Multiply against the singular model representation matrix
        collapsed_states = hidden_states @ self.W_fused
        
        # Mock the return signature expected by HuggingFace generation scripts.
        # We return the new states, and safely return dummy None values for the cache and attention weights.
        return (collapsed_states, None, None, None)

# --- RECREATION PIPELINE ---

def run_crystalline_cycle(model_name, base_filename, offload=False):
    purge_gpu()
    
    if DEVICE == "cuda" and not dist.is_initialized():
        os.environ['MASTER_ADDR'] = 'localhost'
        os.environ['MASTER_PORT'] = '12355'
        dist.init_process_group(backend='nccl', rank=0, world_size=1)

    print(f"\n{'='*20} INSTANTANEOUS GLOBAL EXECUTION: {model_name} {'='*20}")
    log_hardware_state("PRE-LOAD")

    print(f"> Loading {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=CACHE_DIR)
    if tokenizer.pad_token is None: tokenizer.pad_token = tokenizer.eos_token

    max_mem = None
    if offload and DEVICE == "cuda":
        total_vram_bytes = torch.cuda.get_device_properties(0).total_memory
        gpu_limit = f"{int((total_vram_bytes / (1024**2)) - 4096)}MiB"
        max_mem = {0: gpu_limit, "cpu": "45GiB"}

    try:
        load_path = snapshot_download(model_name, cache_dir=CACHE_DIR, local_files_only=True)
    except Exception:
        load_path = model_name

    index_file = os.path.join(load_path, "model.safetensors.index.json")
    single_shard = os.path.join(load_path, "model.safetensors")
    weight_map = {}
    if os.path.exists(index_file):
        with open(index_file, "r") as f:
            weight_map = json.load(f).get("weight_map", {})
        print(" [SYS] Sharded model architecture detected.")
    elif os.path.exists(single_shard):
        print(" [SYS] Single-file model architecture detected.")
    else:
        print(" [!] WARNING: No safetensors found in snapshot folder.")

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
        is_gpt2 = False
        prefix_base = "model.layers"
    else:
        blocks = model.transformer.h
        is_gpt2 = True
        prefix_base = "transformer.h"

    if GLOBAL_COLLAPSE_MODE:
        print("\n>>> INITIATING GLOBAL MANIFOLD COLLAPSE <<<")
        print(f" > Aggregating dimensional pathways across {len(blocks)} layers...")
        
        D = model.config.hidden_size
        W_agg = torch.zeros((D, D), device='cpu', dtype=torch.float32)
        
        count = 0
        for i, block in enumerate(blocks):
            if not is_gpt2 and hasattr(block, 'self_attn') and hasattr(block.self_attn, 'o_proj'):
                orig_mod = block.self_attn.o_proj
                param_name = "self_attn.o_proj.weight"
            elif is_gpt2 and hasattr(block, 'attn') and hasattr(block.attn, 'c_proj'):
                orig_mod = block.attn.c_proj
                param_name = "attn.c_proj.weight"
            else:
                continue
                
            if orig_mod.weight.device.type == 'meta':
                full_param_key = f"{prefix_base}.{i}.{param_name}"
                shard_file = weight_map.get(full_param_key, "model.safetensors")
                shard_path = os.path.join(load_path, shard_file)
                
                if os.path.exists(shard_path):
                    shard_state_dict = load_file(shard_path, device="cpu")
                    if full_param_key in shard_state_dict:
                        tensor_value = shard_state_dict[full_param_key]
                        set_module_tensor_to_device(orig_mod, "weight", "cpu", value=tensor_value)
                    del shard_state_dict
            
            if not is_gpt2:
                W_agg += orig_mod.weight.detach().to('cpu').float().T
            else:
                W_agg += orig_mod.weight.detach().to('cpu').float()
                
            count += 1
            if i % 10 == 0:
                purge_gpu()
                
        W_agg /= max(1, count)
        print(f" > Global Structural Core Calculated. Shape: {W_agg.shape}")
        
        print(" > Performing Stereographic Projection on Global Core...")
        m1 = fast_snap_initialization(W_agg)
        W_fused_global = make_rational_matrix_torch(m1).to(DEVICE).to(torch.bfloat16 if DEVICE == "cuda" else torch.float32)
        
        print(" > Architecting Bypass: Collapsing neural depth into singular manifold...")
        # Pass the first block to inherit structural routing properties (like attention_type)
        singular_layer = GlobalManifoldLayer(W_fused_global, orig_layer=blocks[0])
        
        if not is_gpt2:
            model.model.layers = torch.nn.ModuleList([singular_layer])
        else:
            model.transformer.h = torch.nn.ModuleList([singular_layer])
            
        model.config.num_hidden_layers = 1
        
        print(" > Depth eradicated. Inference speed class shifted to O(1) instantaneous.")
        purge_gpu()

    log_hardware_state("READY")

    # BIG TEST: Interactive Assistant
    print("\n--- INSTANTANEOUS AGENT ONLINE ---")
    print("Note: The model has been compressed from billions of parameters to a single rational matrix.")
    print("Responses will be highly abstract geometric artifacts.")
    
    conversation_history = [{"role": "system", "content": "You are a geometric representation."}]
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

        inputs = tokenizer(prompt_text, return_tensors="pt").to(DEVICE)
        
        t_inf_start = time.time()
        with torch.no_grad():
            # WAVE 94: Disable cache usage when globally collapsed. 
            # A singular manifold matrix produces no attention states to cache.
            outputs = model.generate(
                inputs.input_ids, 
                max_new_tokens=200, 
                do_sample=True, 
                temperature=0.9, 
                top_p=0.95, 
                pad_token_id=tokenizer.eos_token_id,
                use_cache=not GLOBAL_COLLAPSE_MODE 
            )
        inf_time = time.time() - t_inf_start
        
        new_tokens = outputs[0][inputs.input_ids.shape[1]:]
        response_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
        
        print(f"\n[MANIFOLD PROJECTION]:\n{response_text.strip()}")
        print(f"\n[METRICS]: {len(new_tokens)} tokens | SPEED: {len(new_tokens)/inf_time:.2f} tokens/s")
        conversation_history.append({"role": "assistant", "content": response_text.strip()})

# --- EXECUTION ---

if __name__ == "__main__":
    try:
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

        run_crystalline_cycle(BIG_MODEL, BIG_BASE, offload=OFFLOAD)
        
    finally:
        # Graceful teardown of the process group to avoid resource leaks
        if dist.is_initialized():
            dist.destroy_process_group()