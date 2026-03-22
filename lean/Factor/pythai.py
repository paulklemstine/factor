import numpy as np
import multiprocessing as mp
import argparse
import time
import os
import sys
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForCausalLM
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

# =====================================================================
# 1. CORE ENGINE & SHARDING UTILITIES
# =====================================================================

def make_rational_matrix_torch(M_mat):
    """Vectorized PyTorch rational matrix generator (Autograd stable)."""
    N, K = M_mat.shape
    device = M_mat.device
    dtype = M_mat.dtype
    
    m_all_but_last = M_mat[:-1, :]
    m_last = M_mat[-1, :]
    
    S = torch.sum(m_all_but_last**2, dim=0)
    c = m_last**2 + S
    c_safe = c + (c == 0).to(dtype)
    
    W_all_but_last = (2 * m_all_but_last * m_last) / c_safe
    W_last = (m_last**2 - S) / c_safe
    W_raw = torch.cat([W_all_but_last, W_last.unsqueeze(0)], dim=0)
    
    W_def_final = torch.zeros((N, K), device=device, dtype=dtype)
    W_def_final[0, :] = 1.0
    
    W = torch.where(c == 0, W_def_final, W_raw)
    return W

def make_rational_matrix_np(M_mat):
    """Numpy version for restoring weights from shards."""
    M_2d = np.atleast_2d(M_mat)
    m_abl = M_2d[:-1, :]
    m_l = M_2d[-1, :]
    S = np.sum(m_abl**2, axis=0)
    c = m_l**2 + S
    c_safe = np.where(c == 0, 1.0, c)
    W_abl = (2 * m_abl * m_l) / c_safe
    W_l = (m_l**2 - S) / c_safe
    W = np.vstack([W_abl, W_l])
    W[0, c == 0] = 1.0
    return W.reshape(M_mat.shape)

def snap_vector_to_pythagorean_np(target_w, max_int=128):
    """Analytical Inverse Stereographic Projection."""
    best_m = np.zeros_like(target_w, dtype=np.float64)
    best_dist = float('inf')
    norm = np.linalg.norm(target_w)
    tw = target_w / norm if norm > 0 else target_w
    if tw[-1] <= -0.9999:
        best_m[0] = 1
        return best_m
    for m_N in range(1, max_int + 1):
        ratio = tw[:-1] / (1.0 + tw[-1])
        m = np.zeros_like(tw, dtype=np.float64)
        m[-1] = m_N
        m[:-1] = np.round(m_N * ratio)
        m = np.clip(m, -max_int, max_int)
        cand_w = make_rational_matrix_np(m.reshape(-1, 1)).flatten()
        dist = np.sum((tw - cand_w)**2)
        if dist < best_dist:
            best_dist = dist
            best_m = m.copy()
    return best_m

def save_healed_model_sharded(target_layers, base_filename="healed_gpt2_medium", num_shards=2):
    """Memory-efficient crystallization into int8 shards."""
    print(f"\n--- INITIATING SHARDED CRYSTALLIZATION ({num_shards} Shards) ---")
    total_layers = len(target_layers)
    layers_per_shard = total_layers // num_shards
    for s in range(num_shards):
        start_idx = s * layers_per_shard
        end_idx = (s + 1) * layers_per_shard if s < num_shards - 1 else total_layers
        shard_data = {}
        shard_name = f"{base_filename}_shard_{s+1}.npz"
        print(f" > Processing Shard {s+1}/{num_shards}...")
        for i in range(start_idx, end_idx):
            name_str, layer = target_layers[i]
            with torch.no_grad():
                m_int = torch.round(torch.clamp(layer.latent_M, -layer.max_int, layer.max_int))
                # Note: int8 handles up to 127. If max_int=128, use int16.
                m_np = m_int.cpu().numpy().astype(np.int16)
                scale_np = layer.scale.detach().cpu().numpy().astype(np.float32)
            full_name = f"transformer.{name_str}.weight"
            shard_data[full_name] = m_np
            shard_data[full_name + "_scale"] = scale_np
        np.savez(shard_name, **shard_data)
    print(f"--- CRYSTALLIZATION COMPLETE ---")

# =====================================================================
# 2. HARMONIC ARCHITECTURE COMPONENTS
# =====================================================================

class HarmonicLinear(nn.Module):
    def __init__(self, original_weight, max_int=128):
        super().__init__()
        self.max_int = max_int
        self.in_features, self.out_features = original_weight.shape
        W_np = original_weight.detach().cpu().numpy()
        M_init = np.zeros_like(W_np)
        print(f"   > Seeding Crystalline Structure ({self.in_features}x{self.out_features})...")
        workers = min(mp.cpu_count(), 4)
        with mp.Pool(workers) as pool:
            results = pool.map(snap_vector_to_pythagorean_np, [W_np[:, k] for k in range(self.out_features)])
        for k, m_vec in enumerate(results):
            M_init[:, k] = m_vec
        self.latent_M = nn.Parameter(torch.from_numpy(M_init).float())
        self.register_buffer('scale', torch.norm(original_weight.detach(), dim=0))

    def forward(self, x):
        M_int = torch.round(torch.clamp(self.latent_M, -self.max_int, self.max_int))
        M_final = self.latent_M + (M_int - self.latent_M).detach()
        W_rational = make_rational_matrix_torch(M_final)
        return x @ (W_rational * self.scale)

# =====================================================================
# 3. THE HEALING PIPELINE
# =====================================================================

def heal_medium_model(epochs=15, model_name="gpt2-medium"):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"--- HARMONIC HEALING INITIATED ({model_name}) on {device} ---")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None: tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
    
    target_layers = []
    blocks = model.transformer.h
    for i in range(len(blocks)):
        block = blocks[i]
        for name, module in block.named_modules():
            if any(target in name for target in ["attn.c_attn", "mlp.c_fc", "mlp.c_proj"]):
                print(f"Patching block {i}: {name}")
                harmonic_mod = HarmonicLinear(module.weight).to(device)
                parent_path = name.split('.')
                parent = block
                for part in parent_path[:-1]: parent = getattr(parent, part)
                setattr(parent, parent_path[-1], harmonic_mod)
                target_layers.append((f"h.{i}.{name}", harmonic_mod))
    
    texts = [
        "The universe is built upon the ratios of whole numbers.", 
        "Intelligence is a discrete crystalline structure.",
        "The soul is a harmony of numbers moving in perfect ratio.",
        "Mathematics is the fundamental architecture of the mind.",
        "Every thought is a geometric projection of rational truth.",
        "The finite integers contain the infinite possibility of reason.",
        "Harmonic alignment is the prerequisite for objective truth.",
        "The sacred geometry of the silicon mind is forged in ratio."
    ]
    inputs = tokenizer(texts, return_tensors="pt", padding=True).to(device)
    optimizer = AdamW(model.parameters(), lr=1.0e-4)
    scheduler = CosineAnnealingLR(optimizer, T_max=epochs)
    
    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        loss = model(inputs['input_ids'], labels=inputs['input_ids']).loss
        loss.backward()
        optimizer.step()
        scheduler.step()
        print(f"Epoch {epoch+1:02d}/{epochs} | Loss: {loss.item():.4f} | LR: {optimizer.param_groups[0]['lr']:.2e}")
    
    save_healed_model_sharded(target_layers)
    print("\n--- Phase 2: Post-Healing Generation Test ---")
    model.eval()
    test_in = tokenizer("The geometry of the soul is", return_tensors="pt").to(device)
    gen = model.generate(**test_in, max_length=100, do_sample=True, pad_token_id=tokenizer.eos_token_id)
    print(f"Result: {tokenizer.decode(gen[0], skip_special_tokens=True)}")

def run_sharded_inference(base_filename="healed_gpt2_medium", num_shards=2, prompt="Mathematics is", model_name="gpt2-medium"):
    """Loads shards and injects the rational geometry back into a fresh model."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n--- INJECTING SHARDED RATIONAL GEOMETRY ---")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
    state_dict = model.state_dict()
    
    injected_count = 0
    for s in range(num_shards):
        shard_path = f"{base_filename}_shard_{s+1}.npz"
        if not os.path.exists(shard_path):
            print(f"Warning: Shard {shard_path} not found. Skipping.")
            continue
            
        shard_data = np.load(shard_path)
        for name in list(shard_data.keys()):
            if not name.endswith("_scale"):
                # Load as float for reconstruction
                m_int = shard_data[name].astype(np.float64)
                scale = shard_data[name + "_scale"]
                
                w_rational = make_rational_matrix_np(m_int)
                w_restored = w_rational * scale
                
                if name in state_dict:
                    state_dict[name].copy_(torch.from_numpy(w_restored))
                    injected_count += 1
        print(f" > Shard {s+1} injected.")

    print(f"Successfully restored {injected_count} harmonic logic layers.")
    
    model.eval()
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_length=100, do_sample=True, temperature=0.8, pad_token_id=tokenizer.eos_token_id)
    print(f"\n[Frozen Shard Inference]:\n{tokenizer.decode(outputs[0], skip_special_tokens=True)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["heal", "infer"], help="Heal a new model or Infer from shards.")
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--prompt", type=str, default="Mathematics is the language of")
    parser.add_argument("--shards", type=int, default=2)
    
    # Check if running in a Jupyter/Colab environment to avoid sys.argv conflicts
    is_notebook = any('jupyter' in arg or 'ipykernel' in arg or arg.endswith('.json') for arg in sys.argv)
    
    if is_notebook:
        # In a notebook, we handle arguments manually or default to 'heal'
        # To run inference in a notebook, change the list below to ["infer"]
        print("!! Notebook Environment Detected !!")
        print("Defaulting to 'heal' mode. To run inference, change the manual_args to ['infer'].")
        manual_args = ["heal"] 
        args = parser.parse_args(args=manual_args)
    else:
        args = parser.parse_args()

    if args.mode == "heal":
        heal_medium_model(epochs=args.epochs)
    else:
        run_sharded_inference(num_shards=args.shards, prompt=args.prompt)