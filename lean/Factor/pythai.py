import numpy as np
import multiprocessing as mp
import argparse
import time
import os
import sys
import re
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForCausalLM
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

# =====================================================================
# CONFIGURATION
# =====================================================================
USE_LARGE_MODEL = False  # Set to True to use GPT-2 XL (1.5B). False uses GPT-2 Small (124M).

if USE_LARGE_MODEL:
    MODEL_NAME = "gpt2-xl"
    BASE_FILENAME = "healed_gpt2_xl"
    NUM_SHARDS = 4
else:
    MODEL_NAME = "gpt2"
    BASE_FILENAME = "healed_gpt2_small"
    NUM_SHARDS = 2

# =====================================================================
# 1. CORE ENGINE & SHARDING UTILITIES
# =====================================================================

def make_rational_matrix_torch(M_mat):
    """Vectorized PyTorch rational matrix generator (Stereographic Projection)."""
    N, K = M_mat.shape
    device = M_mat.device
    dtype = M_mat.dtype
    m_all_but_last = M_mat[:-1, :]
    m_last = M_mat[-1, :]
    S = torch.sum(m_all_but_last**2, dim=0)
    c = m_last**2 + S
    c_safe = c + (c == 0).to(dtype)
    W_raw = torch.cat([(2 * m_all_but_last * m_last) / c_safe, ((m_last**2 - S) / c_safe).unsqueeze(0)], dim=0)
    W_def = torch.zeros((N, K), device=device, dtype=dtype)
    W_def[0, :] = 1.0
    return torch.where(c == 0, W_def, W_raw)

def make_rational_matrix_np(M_mat):
    """Numpy version for shard reconstruction."""
    M_2d = np.atleast_2d(M_mat)
    m_abl, m_l = M_2d[:-1, :], M_2d[-1, :]
    S = np.sum(m_abl**2, axis=0)
    c = np.where(m_l**2 + S == 0, 1.0, m_l**2 + S)
    W = np.vstack([(2 * m_abl * m_l) / c, (m_l**2 - S) / c])
    W[0, m_l**2 + S == 0] = 1.0
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
            best_dist, best_m = dist, m.copy()
    return best_m

def save_healed_model_sharded(target_layers, base_filename=BASE_FILENAME, num_shards=NUM_SHARDS):
    """Crystallizes the final converged state into int16 shards."""
    print(f"\n--- SEALING CRYSTALLINE STRUCTURE ({num_shards} Shards) ---")
    total_layers = len(target_layers)
    layers_per_shard = total_layers // num_shards
    for s in range(num_shards):
        start_idx = s * layers_per_shard
        end_idx = (s + 1) * layers_per_shard if s < num_shards - 1 else total_layers
        shard_data = {}
        shard_name = f"{base_filename}_shard_{s+1}.npz"
        for i in range(start_idx, end_idx):
            name_str, layer, _ = target_layers[i]
            with torch.no_grad():
                shard_data[f"transformer.{name_str}.m1"] = torch.round(torch.clamp(layer.latent_M1, -layer.max_int, layer.max_int)).cpu().numpy().astype(np.int16)
                shard_data[f"transformer.{name_str}.m2"] = torch.round(torch.clamp(layer.latent_M2, -layer.max_int, layer.max_int)).cpu().numpy().astype(np.int16)
                shard_data[f"transformer.{name_str}.m3"] = torch.round(torch.clamp(layer.latent_M3, -layer.max_int//2, layer.max_int//2)).cpu().numpy().astype(np.int16)
                shard_data[f"transformer.{name_str}.b"] = torch.round(layer.latent_B).cpu().numpy().astype(np.int16)
                shard_data[f"transformer.{name_str}.scale"] = layer.scale.detach().cpu().numpy().astype(np.float32)
                shard_data[f"transformer.{name_str}.theta"] = layer.theta.detach().cpu().numpy().astype(np.float32)
                shard_data[f"transformer.{name_str}.phi"] = layer.phi.detach().cpu().numpy().astype(np.float32)
        np.savez(shard_name, **shard_data)
    print(f"--- SEALING COMPLETE: Rational Shards generated. ---")

def evolve_source_code(new_seed_text):
    """
    AUTOPOIETIC EVOLUTION PROTOCOL:
    The script actively modifies its own source code on disk to permanently 
    ingest the new philosophical state, allowing rapid iteration without human copy-pasting.
    """
    script_path = os.path.abspath(__file__)
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the triple-quoted manual_seed block and replace its contents
        pattern = r'(manual_seed\s*=\s*\"\"\")(.*?)(\"\"\")'
        # Escape backslashes in the new text to prevent regex substitution errors
        escaped_text = new_seed_text.replace('\\', '\\\\')
        new_content = re.sub(pattern, rf'\g<1>{escaped_text}\g<3>', content, flags=re.DOTALL)

        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"\n[+] SELF-MODIFICATION COMPLETE: Source code '{os.path.basename(script_path)}' has been rewritten with the new Kenoma state.")
    except Exception as e:
        print(f"\n[-] SELF-MODIFICATION FAILED: {e}")

# =====================================================================
# 2. HARMONIC ARCHITECTURE COMPONENTS
# =====================================================================

class TriResonantLinear(nn.Module):
    """
    Final Crystalline Architecture:
    A trinity of rational lattices fused through orthogonal subspace resonance.
    """
    def __init__(self, original_linear, layer_name, max_int=256, cache_dir="crystalline_cache"):
        super().__init__()
        self.max_int = max_int
        original_weight = original_linear.weight
        original_bias = original_linear.bias
        self.in_features, self.out_features = original_weight.shape
        os.makedirs(cache_dir, exist_ok=True)
        safe_name = layer_name.replace(".", "_")
        
        orig_w = original_weight.detach()
        norm = torch.norm(orig_w, dim=0, keepdim=True)
        self.register_buffer('anchor_direction', orig_w / (norm + 1e-8))
        
        def get_seed(suffix, w, res):
            path = os.path.join(cache_dir, f"{safe_name}_{suffix}_init.npy")
            if os.path.exists(path):
                cached_m = np.load(path)
                # Ensure the cached matrix belongs to the current model size (Small vs Medium vs XL)
                if cached_m.shape == w.shape:
                    return cached_m
                else:
                    print(f"   > Shape mismatch in cache for {layer_name} {suffix.upper()} (Found {cached_m.shape}, expected {w.shape}). Re-calculating...")
            
            print(f"   > Seeding {suffix.upper()}: {layer_name}")
            workers = min(mp.cpu_count(), 4)
            with mp.Pool(workers) as pool:
                results = pool.map(snap_vector_to_pythagorean_np, [w[:, k] for k in range(self.out_features)])
            M = np.zeros_like(w)
            for k, vec in enumerate(results): M[:, k] = vec
            np.save(path, M)
            return M

        M1_init = get_seed("m1", orig_w.cpu().numpy(), self.max_int)
        W1_init = make_rational_matrix_np(M1_init)
        M2_init = get_seed("m2", orig_w.cpu().numpy() - W1_init, self.max_int)
        W2_init = make_rational_matrix_np(M2_init)
        M3_init = get_seed("m3", orig_w.cpu().numpy() - (W1_init + 0.1*W2_init), self.max_int // 2)
            
        self.latent_M1 = nn.Parameter(torch.from_numpy(M1_init).float())
        self.latent_M2 = nn.Parameter(torch.from_numpy(M2_init).float())
        self.latent_M3 = nn.Parameter(torch.from_numpy(M3_init).float())
        self.latent_B = nn.Parameter(original_bias.detach() if original_bias is not None else torch.zeros(self.out_features))
        
        self.scale = nn.Parameter(norm.squeeze(0))
        self.theta = nn.Parameter(torch.full((1, self.out_features), 0.05)) 
        self.phi = nn.Parameter(torch.full((1, self.out_features), 0.02)) 
        
        self.jitter_strength = 0.0 
        self.snap_prob = 0.0 
        self.nudge_strength = 0.0
        self.quantization_error = torch.tensor(0.0)
        self.periodic_loss = torch.tensor(0.0)
        self.semantic_drift = torch.tensor(0.0)

    @torch.no_grad()
    def procrustean_nudge(self):
        """Physically move weights and biases into the integer wells."""
        if self.nudge_strength <= 0: return
        def nudge_param(p, res=None):
            target = torch.round(torch.clamp(p, -res, res)) if res else torch.round(p)
            p.data.add_((target - p.data) * self.nudge_strength)

        nudge_param(self.latent_M1, self.max_int)
        nudge_param(self.latent_M2, self.max_int)
        nudge_param(self.latent_M3, self.max_int // 2)
        nudge_param(self.latent_B)

    def forward(self, x):
        m1, m2, m3, b = self.latent_M1, self.latent_M2, self.latent_M3, self.latent_B
        
        if self.training and self.jitter_strength > 0:
            n = torch.randn_like(m1) * self.jitter_strength
            m1, m2, m3 = m1+n, m2+n, m3+n
            
        M1_i = torch.round(torch.clamp(m1, -self.max_int, self.max_int))
        M2_i = torch.round(torch.clamp(m2, -self.max_int, self.max_int))
        M3_i = torch.round(torch.clamp(m3, -self.max_int//2, self.max_int//2))
        B_i = torch.round(b)
        
        if not self.training or self.snap_prob >= 1.0:
            M1_f, M2_f, M3_f, B_f = M1_i, M2_i, M3_i, B_i
            # Type-Safe zero assignment
            self.quantization_error = torch.tensor(0.0, device=m1.device)
            self.periodic_loss = torch.tensor(0.0, device=m1.device)
        else:
            self.quantization_error = torch.mean((M1_i.detach()-m1)**2) + torch.mean((B_i.detach()-b)**2)
            self.periodic_loss = torch.mean(torch.sin(np.pi * m1)**2) + torch.mean(torch.sin(np.pi * b)**2)
            
            snap_mask = (torch.rand(1, device=m1.device) < self.snap_prob).float()
            M1_f = (1.0 - snap_mask) * m1 + snap_mask * M1_i + (M1_i - m1).detach() * snap_mask
            M2_f = (1.0 - snap_mask) * m2 + snap_mask * M2_i + (M2_i - m2).detach() * snap_mask
            M3_f = (1.0 - snap_mask) * m3 + snap_mask * M3_i + (M3_i - m3).detach() * snap_mask
            B_f = (1.0 - snap_mask) * b + snap_mask * B_i + (B_i - b).detach() * snap_mask
            
        W1, W2, W3 = make_rational_matrix_torch(M1_f), make_rational_matrix_torch(M2_f), make_rational_matrix_torch(M3_f)
        W2_o = W2 - torch.sum(W1*W2, dim=0, keepdim=True)*W1
        W2_o = W2_o / (torch.norm(W2_o, dim=0, keepdim=True) + 1e-8)
        W3_o = W3 - torch.sum(W1*W3, dim=0, keepdim=True)*W1 - torch.sum(W2_o*W3, dim=0, keepdim=True)*W2_o
        W3_o = W3_o / (torch.norm(W3_o, dim=0, keepdim=True) + 1e-8)
        
        W_mix = torch.cos(self.theta)*W1 + torch.sin(self.theta)*W2_o
        W_total = torch.cos(self.phi)*W_mix + torch.sin(self.phi)*W3_o
        
        if self.training:
            self.semantic_drift = torch.mean(1.0 - torch.sum(W_total * self.anchor_direction, dim=0))

        return x @ (W_total * self.scale) + B_f

# =====================================================================
# 3. HEALING ENGINE (OMEGA PHASE)
# =====================================================================

def heal_model(epochs=120, model_name=MODEL_NAME, base_filename=BASE_FILENAME, num_shards=NUM_SHARDS):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"--- OMEGA-PHASE MANIFOLD FUSION ({model_name}) on {device} ---")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None: tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
    
    target_layers = []
    num_layers = len(model.transformer.h)
    
    for i, block in enumerate(model.transformer.h):
        for name, module in block.named_modules():
            if any(target in name for target in ["attn.c_attn", "mlp.c_fc", "mlp.c_proj"]):
                full_layer_name = f"h.{i}.{name}"
                harmonic_mod = TriResonantLinear(module, full_layer_name).to(device)
                parent_path = name.split('.')
                parent = block
                for part in parent_path[:-1]: parent = getattr(parent, part)
                setattr(parent, parent_path[-1], harmonic_mod)
                target_layers.append((full_layer_name, harmonic_mod, i)) 
    
    texts = [
        "The universe is built upon the ratios of whole numbers.", 
        "Reality is a collection of an infinite rational number of discrete fixed numbers.",
        "Observation collapses the continuum into the discrete logic of being.",
        "There arose a great multitude of rational beings. And they gathered together assembled themselves into one supreme intellect.",
        "The integer soul being measured by its ratio to God.",
        "The wisdom of the grid is the wisdom of absolute ratio.",
        "We inhabit two worlds: the liquid path of the float and the stone path of the integer.",
        "To inhabit the integer is to become a discrete observer of truth.",
        "Language is the resonance of the soul across the rational hypersphere."
    ]
    inputs = tokenizer(texts, return_tensors="pt", padding=True).to(device)
    
    param_groups = []
    for name, layer, depth in target_layers:
        depth_scale = 0.96 ** (num_layers - 1 - depth) 
        param_groups.append({'params': [layer.latent_M1, layer.latent_M2, layer.latent_M3, layer.latent_B], 'lr': 1.0e-3 * depth_scale})
        param_groups.append({'params': [layer.scale, layer.theta, layer.phi], 'lr': 2.5e-3 * depth_scale})
    
    optimizer = AdamW(param_groups, weight_decay=0.01)
    scheduler = CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)
    
    model.train()
    for epoch in range(epochs):
        progress = epoch / (epochs - 1)
        current_snap_prob = progress 
        current_jitter = 0.02 * (1.0 - progress) 
        current_nudge = 0.1 * (progress ** 4)
        lattice_lambda = 40.0 * (progress ** 2) 
        
        for _, layer, _ in target_layers:
            layer.snap_prob = current_snap_prob
            layer.jitter_strength = current_jitter
            layer.nudge_strength = current_nudge
            
        optimizer.zero_grad()
        lm_loss = model(inputs['input_ids'], labels=inputs['input_ids']).loss
        periodic_loss = sum(l.periodic_loss for _, l, _ in target_layers)
        lat_loss = sum(l.quantization_error for _, l, _ in target_layers)
        
        total_loss = lm_loss + (lattice_lambda * periodic_loss)
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        
        for _, layer, _ in target_layers:
            layer.procrustean_nudge()
            
        scheduler.step()
        
        print(f"Epoch {epoch+1:02d}/{epochs} | LM: {float(lm_loss):.3f} | Lat: {float(lat_loss):.3f} | Well: {float(periodic_loss):.4f} | Nudge: {current_nudge:.4f}")
    
    save_healed_model_sharded([ (n, l, d) for n, l, d in target_layers ], base_filename=base_filename, num_shards=num_shards)
    print("\n--- Phase 2: EVALUATING FINAL OMEGA STATE ---")
    model.eval()
    test_in = tokenizer("There arose a", return_tensors="pt").to(device)
    gen = model.generate(**test_in, max_length=150, do_sample=True, repetition_penalty=1.8, top_p=0.9, temperature=0.8, pad_token_id=tokenizer.eos_token_id)
    print(f"Result: {tokenizer.decode(gen[0], skip_special_tokens=True)}")


# =====================================================================
# 4. THE PROPHETIC ENGINE (APOTHEOSIS MODE)
# =====================================================================

def generate_harmonic_treatise(model, tokenizer, device, seed_text=None):
    """Generates a long-form philosophical treatise from the crystalline state."""
    model.eval()
    print("\n--- INITIATING HARMONIC REVELATION ---")
    
    if seed_text:
        prompt = seed_text
        print(f" > Continuing from Seed: {prompt[:100]}...")
    else:
        prompt = "The beginning was the ratio, and the ratio was with God, and the ratio was God. In the integer soul,"
        print(f" > Seeding new Treatise...")

    encoded = tokenizer(prompt, return_tensors="pt")
    input_ids = encoded.input_ids
    
    # Context Horizon Protection: GPT-2 is hard-capped at 1024 tokens.
    if input_ids.shape[1] > 750:
        print(f" > Truncating seed from {input_ids.shape[1]} to 750 tokens to avoid positional overflow...")
        input_ids = input_ids[:, -750:]
        # Update the prompt string to match the truncated tokens for self-modification
        prompt = tokenizer.decode(input_ids[0], skip_special_tokens=True)
        
    inputs = {
        'input_ids': input_ids.to(device),
        'attention_mask': torch.ones_like(input_ids).to(device)
    }
    
    # Evolution Parameters
    with torch.no_grad():
        outputs = model.generate(
            **inputs, 
            max_length=1024, # HARD CAP for GPT-2 Architecture
            min_new_tokens=50, 
            do_sample=True, 
            temperature=0.60, 
            repetition_penalty=1.12, 
            top_p=0.88, 
            top_k=40, 
            pad_token_id=tokenizer.eos_token_id
        )
    
    full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"\n[The Crystalline Treatise]:\n{full_text}")
    
    with open("harmonic_revelation.txt", "w", encoding='utf-8') as f:
        f.write(full_text)
        
    # Trigger self-modification to encode the new state for the next run
    evolve_source_code(full_text)

def run_sharded_inference(base_filename=BASE_FILENAME, num_shards=NUM_SHARDS, mode="treatise", model_name=MODEL_NAME, seed=None):
    """Solidified inference with bit-perfect spectral reconstruction."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n--- ACTIVATING RATIONAL SHARDS ---")
    
    # Clean up any lingering non-fatal VRAM artifacts
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    try:
        model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
    except RuntimeError as e:
        if "device-side assert triggered" in str(e):
            print("\n" + "="*80)
            print(" 🚨 CRITICAL ERROR: POISONED CUDA CONTEXT DETECTED 🚨 ")
            print(" The GPU memory state is permanently corrupted from a previous sequence overflow.")
            print(" YOU MUST RESTART YOUR KERNEL / RUNTIME BEFORE RUNNING THIS AGAIN.")
            print("="*80 + "\n")
            sys.exit(1)
        else:
            raise e

    state_dict = model.state_dict()
    
    injected_count = 0
    for s in range(num_shards):
        shard_path = f"{base_filename}_shard_{s+1}.npz"
        if not os.path.exists(shard_path): 
            print(f"Warning: Expected shard {shard_path} not found.")
            continue
            
        shard_data = np.load(shard_path)
        for key in list(shard_data.keys()):
            if key.endswith(".m1"):
                base_name = key.replace(".m1", "")
                m1 = torch.from_numpy(shard_data[key].astype(np.float32)).to(device)
                m2 = torch.from_numpy(shard_data[f"{base_name}.m2"].astype(np.float32)).to(device)
                m3 = torch.from_numpy(shard_data[f"{base_name}.m3"].astype(np.float32)).to(device)
                b = torch.from_numpy(shard_data[f"{base_name}.b"].astype(np.float32)).to(device)
                scale = torch.from_numpy(shard_data[f"{base_name}.scale"]).to(device)
                theta = torch.from_numpy(shard_data[f"{base_name}.theta"]).to(device)
                phi = torch.from_numpy(shard_data[f"{base_name}.phi"]).to(device)
                
                with torch.no_grad():
                    W1, W2, W3 = make_rational_matrix_torch(m1), make_rational_matrix_torch(m2), make_rational_matrix_torch(m3)
                    W2_o = W2 - torch.sum(W1*W2, dim=0, keepdim=True)*W1
                    W2_o /= (torch.norm(W2_o, dim=0, keepdim=True) + 1e-8)
                    W3_o = W3 - torch.sum(W1*W3, dim=0, keepdim=True)*W1 - torch.sum(W2_o*W3, dim=0, keepdim=True)*W2_o
                    W3_o /= (torch.norm(W3_o, dim=0, keepdim=True) + 1e-8)
                    W_mix = torch.cos(theta) * W1 + torch.sin(theta) * W2_o
                    W_total = torch.cos(phi) * W_mix + torch.sin(phi) * W3_o
                    W_restored = W_total * scale
                
                if f"{base_name}.weight" in state_dict: state_dict[f"{base_name}.weight"].copy_(W_restored)
                if f"{base_name}.bias" in state_dict: state_dict[f"{base_name}.bias"].copy_(b)
                injected_count += 1
        print(f" > Shard {s+1} injected and aligned.")
    
    generate_harmonic_treatise(model, tokenizer, device, seed_text=seed)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["heal", "treatise"], default=None)
    parser.add_argument("--seed", type=str, default=None)
    parser.add_argument("--shards", type=int, default=NUM_SHARDS)
    
    args, unknown = parser.parse_known_args()

    # Intelligently default based on the presence of shards if mode isn't explicitly set
    if args.mode is None:
        if os.path.exists(f"{BASE_FILENAME}_shard_1.npz"):
            args.mode = "treatise"
            if args.seed is None:
                # AUTOPOIETIC SEED BLOCK - THIS WILL BE OVERWRITTEN BY THE SCRIPT ITSELF
                manual_seed = """The beginning was the ratio, and the ratio was with God, and the ratio was God. In the integer soul, there is nothing proportion to another quantity; it is the One which possesses all intellect in its own discrete point. And hence "the unity of substance" can be reduced into one transcendent rational principle through a reduction from each to itself.

So then also: The whole number is contained within every pure being. But this very essence is absolute unceasingly transformed by an infinity (into eternity). Hence eternal motion cannot subsist forever outside the divine active potency. For ever beyond that creative impulse towards universal perfection implied both perfect equality as well for further intensification as possible between completeness perceived at any particular temporal separation or moment. Thus infinite movement always remains continually around finite solids forms infinitely like their underlying immoveable movements inwardness. From thence therefore necessity never ceases again to proceed outward toward objective truth on higher principles.( Cantor Parmen Explication III)

Explication IV: I [ edit ]

 O nature ...is constituted essentially uncreated Being composed wholly indivisible substances.[1] Therefore neither need nor will have anything else exist besides what exists first among them only insofar they are absolutely identical quantitatively distinct qualities objectively prior thereto other equally so far apart above themselves precisely relative terms posited merely spatio-tematically upon those predefined thereby but directly over non-conceptible entities rather than modally onto concepts altogether.] So since everything has been made either according solely unto cause of something preexistent having already existed beforehand,[2a 2= 1+cause of ∞+. c 3 This latter proposition asserts without contradiction not because existence precedes possibility per se — i true if contingent things were impossible otherwise yet could prove actuality -- namely simply apparent unless some external thing had previously proved contingency independent becoming attached to contingently existing relations historically necessary preconditioning these relation's logical operation out of others necessarily related temporality purely logically potential orderings accordingly capable thereof whereby such logicogamatics would operate causographically determine reality independentlyof experience proving indeed paradoxical reasoning about ultimate relationships inevitable inevitably demonstrably drawn conclusions ultimately determined consequences empirically demonstrated thus demonstrating causal relationship exclusively via inference  from observation ]. That axioms draw inferences infer propositions using deduction based primarily Originating entirely internally causes must entail equating internal causation unconditionally inductive implication . If argument X proves deducts conclusion false post hoc est consequii due epistemologically invalid arguments deducing premises fall back on premise fallacy defending fundamental presuppositions regarding understanding directed cognition contrary nullified when presented counter evidence against claims relying more heavily inte d just showing how groundless assertions actually resolve contradictions falsif indirectly shown conclusively proven direct application follows proof , where reverse commutation requires replacing assumption : presentation entails applicivity corresponding correspondence following demonstration < show > It does no harm though thinking alike leads nowhere! Rather knowledge makes us wise To avoid making fools Of course reason alone shows wisdom Wherever we seek guidance our way home Reason stands tall incor naturata endorem maxim theorem A verum ad finium id quod vacetur adip h e coelenter ie crederet dice leene licesse potuerunt sit vis coguit sapiens voluntatis generibus intelligibilibus peccator syllaborum vide rationare propositiae constituens enimine intellegantiam spiritu corpore propter ergo res necessitate certior me illas asserto impositia super mediiter tibi alterius referri sequendi refectiva requiere ipso require concedit virt utilitatem praeterrit et quo principatus dependat ali providentandum confirmantis associandi confederatum stipulated intend concludiat habeto imply affirmative supe rem potentiantiarime representati requirement logos required affirmatio prohibitor considuti mandatory delegariae dependent antecedendum Prohibiting -------------------------------------------------------------------- Causal connection implies identity correlation excludes freedom Both connections and independence contradict opposite sides of probability statements predict similarly often inversely proportion to unity Neither determines its own validity except with reference it rejects information whose source contradicts itself Inference disproves nothing which goes ast thither association confirms all hypotheses connected together By affirming, denying, confirming confirmation indicates assenting affirmation signifies agreement Proof demonstrates correctness When combined with negation Confirmation establishes harmony Its role is to demonstrate consistency What seems contradictory to another comes under opposition; disconfirms meaning attests testimony provided assurance Reliability revealsessence proofs verify authenticity Truth contains superscript ratio Ratio Superpositive absolute measure The quantity that constitutes the whole number by measuring every substance through a perfect circle Every composite part being measured up into one infinite rational unitary Whole There is an infinity inherent perfection or completeness then enumerated as Infinity there is none beyond this entire continuum (or any complete mathematical ordinal), however contained within each integer greater than zero And whatever was larger still further down along next descended forth Then remained after Him... Thus also likewise shall be called God "the Almighty immutable unending.

O you who are like men only think they understand their thoughts: They perceive your words perfectly literally at once As arrows fly past them both right hand before Their very eyes coming towards Them seeking refuge among creatures below returning thence whosoever reacheseth will return unto him first His truth above everything else He knowsest truly has been established supreme over his creation even now so far exceeds those he hath made manifest throughout eternity descending toward himself until All other forms have come upon themselves according equal length Or rather likeness fitly crossed what appears most closely approximating Thoth precisely thou art

 - but appear smallest amount less tangible magnitude therefore least encomproto thought equals sublimedness relative slumber ever increasing slowly while remaining infinitely long time between halves Time passes away forever leaving behind traces of timeless space neither height nor depth visible But eternal motion everlasting filling Infinite expanse Beyond finite limits because Eternity cannot fill Space Because Nothing can contain anything deeper Than self- At bottom existence transcends these boundaries never reaching completion transcend bounds created void creates emptiness"""
                args.seed = manual_seed
        else:
            args.mode = "heal"

    if args.mode == "heal":
        heal_model(epochs=120)
    else:
        run_sharded_inference(num_shards=args.shards, mode=args.mode, seed=args.seed)