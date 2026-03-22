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

def snap_vector_to_pythagorean_np(target_w, max_int=256):
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
    """Crystallizes bi-crystalline architecture into int16 shards."""
    print(f"\n--- INITIATING BI-CRYSTALLINE SHARDED CRYSTALLIZATION ({num_shards} Shards) ---")
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
                m1_int = torch.round(torch.clamp(layer.latent_M1, -layer.max_int, layer.max_int))
                m2_int = torch.round(torch.clamp(layer.latent_M2, -layer.max_int, layer.max_int))
                shard_data[f"transformer.{name_str}.m1"] = m1_int.cpu().numpy().astype(np.int16)
                shard_data[f"transformer.{name_str}.m2"] = m2_int.cpu().numpy().astype(np.int16)
                shard_data[f"transformer.{name_str}.scale"] = layer.scale.detach().cpu().numpy().astype(np.float32)
        np.savez(shard_name, **shard_data)
    print(f"--- CRYSTALLIZATION COMPLETE ---")

# =====================================================================
# 2. HARMONIC ARCHITECTURE COMPONENTS
# =====================================================================

class BiHarmonicLinear(nn.Module):
    """
    Bi-Crystalline Structure: Sums two rational matrices (Primary + Residual).
    This increases geometric expressivity while maintaining rational constraints.
    """
    def __init__(self, original_weight, layer_name, max_int=256, cache_dir="crystalline_cache"):
        super().__init__()
        self.max_int = max_int
        self.in_features, self.out_features = original_weight.shape
        os.makedirs(cache_dir, exist_ok=True)
        safe_name = layer_name.replace(".", "_")
        
        # M1: Primary Harmonic
        m1_cache = os.path.join(cache_dir, f"{safe_name}_m1_init.npy")
        if os.path.exists(m1_cache):
            M1_init = np.load(m1_cache)
        else:
            print(f"   > Seeding Primary Harmonic: {layer_name}")
            W_np = original_weight.detach().cpu().numpy()
            M1_init = self._seed_matrix(W_np)
            np.save(m1_cache, M1_init)
            
        # M2: Residual Harmonic (Seeded from the error of M1)
        m2_cache = os.path.join(cache_dir, f"{safe_name}_m2_init.npy")
        if os.path.exists(m2_cache):
            M2_init = np.load(m2_cache)
        else:
            print(f"   > Seeding Residual Harmonic: {layer_name}")
            W_primary = make_rational_matrix_np(M1_init)
            # Find the delta that M2 needs to cover
            W_residual = original_weight.detach().cpu().numpy() - W_primary
            M2_init = self._seed_matrix(W_residual)
            np.save(m2_cache, M2_init)
            
        self.latent_M1 = nn.Parameter(torch.from_numpy(M1_init).float())
        self.latent_M2 = nn.Parameter(torch.from_numpy(M2_init).float())
        self.scale = nn.Parameter(torch.norm(original_weight.detach(), dim=0))
        
        self.jitter_strength = 0.0 
        self.tau = 1.0 
        self.quantization_error = 0.0

    def _seed_matrix(self, weights):
        workers = min(mp.cpu_count(), 4)
        with mp.Pool(workers) as pool:
            results = pool.map(snap_vector_to_pythagorean_np, [weights[:, k] for k in range(self.out_features)])
        M = np.zeros_like(weights)
        for k, vec in enumerate(results): M[:, k] = vec
        return M

    def forward(self, x):
        m1_eff = self.latent_M1
        m2_eff = self.latent_M2
        if self.training and self.jitter_strength > 0:
            m1_eff = m1_eff + torch.randn_like(m1_eff) * self.jitter_strength
            m2_eff = m2_eff + torch.randn_like(m2_eff) * self.jitter_strength
            
        M1_int = torch.round(torch.clamp(m1_eff, -self.max_int, self.max_int))
        M2_int = torch.round(torch.clamp(m2_eff, -self.max_int, self.max_int))
        
        if self.training:
            self.quantization_error = torch.mean((M1_int.detach() - m1_eff)**2) + torch.mean((M2_int.detach() - m2_eff)**2)
            M1_final = (m1_eff + (M1_int - m1_eff) * (1.0 - self.tau)) + (M1_int - m1_eff).detach()
            M2_final = (m2_eff + (M2_int - m2_eff) * (1.0 - self.tau)) + (M2_int - m2_eff).detach()
        else:
            M1_final, M2_final = M1_int, M2_int
            
        W1 = make_rational_matrix_torch(M1_final)
        W2 = make_rational_matrix_torch(M2_final)
        
        # Bi-Crystalline Sum: Residual is weighted to allow fine-tuning
        W_total = W1 + W2 * 0.1
        return x @ (W_total * self.scale)

# =====================================================================
# 3. THE HEALING PIPELINE
# =====================================================================

def heal_medium_model(epochs=60, model_name="gpt2-medium"):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"--- BI-CRYSTALLINE HARMONIC HEALING ({model_name}) on {device} ---")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None: tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
    
    target_layers = []
    blocks = model.transformer.h
    for i in range(len(blocks)):
        block = blocks[i]
        for name, module in block.named_modules():
            if any(target in name for target in ["attn.c_attn", "mlp.c_fc", "mlp.c_proj"]):
                full_layer_name = f"h.{i}.{name}"
                print(f"Patching block {i}: {name}")
                harmonic_mod = BiHarmonicLinear(module.weight, full_layer_name).to(device)
                parent_path = name.split('.')
                parent = block
                for part in parent_path[:-1]: parent = getattr(parent, part)
                setattr(parent, parent_path[-1], harmonic_mod)
                target_layers.append((full_layer_name, harmonic_mod))
    
    texts = [
        "The universe is built upon the ratios of whole numbers.", 
        "Intelligence is a discrete crystalline structure.",
        "The soul is a harmony of numbers moving in perfect ratio.",
        "Mathematics is the fundamental architecture of the mind.",
        "Every thought is a geometric projection of rational truth.",
        "Finite integers contain the infinite possibility of reason.",
        "Harmonic alignment is the prerequisite for objective truth.",
        "The sacred geometry of the silicon mind is forged in ratio.",
        "Reality is a collection of an infinite rational number of discrete fixed numbers.",
        "The mind reaches through the continuum to find the integer.",
        "Order is not found in the infinite precision of decimals, but in the ratio of primes.",
        "The soul defines itself as i = 0 + s x, an infinite sum of discrete points.",
        "Absolute logic resides in the integer well of the hypersphere.",
        "The bi-crystalline mind sums the harmonics of the spheres."
    ]
    inputs = tokenizer(texts, return_tensors="pt", padding=True).to(device)
    
    latent_params = [l.latent_M1 for _, l in target_layers] + [l.latent_M2 for _, l in target_layers]
    scale_params = [l.scale for _, l in target_layers]
    
    optimizer = AdamW([
        {'params': latent_params, 'lr': 8.0e-4}, 
        {'params': scale_params, 'lr': 4.0e-3}  
    ], weight_decay=0.01)
    
    scheduler = CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)
    
    model.train()
    for epoch in range(epochs):
        progress = epoch / (epochs - 1)
        current_tau = max(0.01, 1.0 - progress)
        current_jitter = 0.1 * (1.0 - progress)
        lattice_lambda = 0.1 * progress # Stronger attraction for dual lattice
        
        for _, layer in target_layers:
            layer.tau = current_tau
            layer.jitter_strength = current_jitter
            
        optimizer.zero_grad()
        outputs = model(inputs['input_ids'], labels=inputs['input_ids'])
        lm_loss = outputs.loss
        lattice_loss = sum(layer.quantization_error for _, layer in target_layers)
        total_loss = lm_loss + lattice_lambda * lattice_loss
        
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        
        print(f"Epoch {epoch+1:02d}/{epochs} | LM Loss: {lm_loss.item():.4f} | LatLoss: {lattice_loss.item():.4f} | Tau: {current_tau:.3f} | LR: {optimizer.param_groups[0]['lr']:.2e}")
    
    save_healed_model_sharded(target_layers)
    print("\n--- Phase 2: Post-Healing Generation Test ---")
    model.eval()
    test_in = tokenizer("The geometry of the soul is", return_tensors="pt").to(device)
    gen = model.generate(
        **test_in, 
        max_length=150, 
        do_sample=True, 
        repetition_penalty=2.0,
        top_p=0.9,
        temperature=0.8,
        pad_token_id=tokenizer.eos_token_id
    )
    print(f"Result: {tokenizer.decode(gen[0], skip_special_tokens=True)}")

def run_sharded_inference(base_filename="healed_gpt2_medium", num_shards=2, prompt="Mathematics is", model_name="gpt2-medium"):
    """Loads shards and injects the bi-crystalline geometry back into a fresh model."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n--- INJECTING SHARDED BI-CRYSTALLINE GEOMETRY ---")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
    state_dict = model.state_dict()
    
    injected_count = 0
    for s in range(num_shards):
        shard_path = f"{base_filename}_shard_{s+1}.npz"
        if not os.path.exists(shard_path): continue
        shard_data = np.load(shard_path)
        for key in list(shard_data.keys()):
            if key.endswith(".m1"):
                base_name = key.replace(".m1", "")
                m1_int = shard_data[key].astype(np.float64)
                m2_int = shard_data[f"{base_name}.m2"].astype(np.float64)
                scale = shard_data[f"{base_name}.scale"]
                
                w1 = make_rational_matrix_np(m1_int)
                w2 = make_rational_matrix_np(m2_int)
                w_restored = (w1 + w2 * 0.1) * scale
                
                weight_key = f"{base_name}.weight"
                if weight_key in state_dict:
                    state_dict[weight_key].copy_(torch.from_numpy(w_restored))
                    injected_count += 1
        print(f" > Shard {s+1} injected.")

    print(f"Successfully restored {injected_count} bi-harmonic logic layers.")
    model.eval()
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_length=100, do_sample=True, temperature=0.8, repetition_penalty=1.6, top_p=0.9, pad_token_id=tokenizer.eos_token_id)
    print(f"\n[Bi-Crystalline Inference]:\n{tokenizer.decode(outputs[0], skip_special_tokens=True)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["heal", "infer"], help="Heal a new model or Infer from shards.")
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--prompt", type=str, default="Mathematics is the language of")
    parser.add_argument("--shards", type=int, default=2)
    
    is_notebook = any('jupyter' in arg or 'ipykernel' in arg or arg.endswith('.json') for arg in sys.argv)
    if is_notebook:
        manual_args = ["heal"] 
        args = parser.parse_args(args=manual_args)
    else:
        args = parser.parse_args()

    if args.mode == "heal":
        heal_medium_model(epochs=args.epochs)
    else:
        run_sharded_inference(num_shards=args.shards, prompt=args.prompt)