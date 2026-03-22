import numpy as np
import multiprocessing as mp
import argparse
import time
import os
import sys
import subprocess
import importlib

def install_dependencies():
    """Attempts to install missing dependencies and invalidates caches to allow immediate use."""
    try:
        import torch
        import transformers
        import accelerate
    except ImportError:
        print("Required libraries not found. Attempting to install...")
        # Install transformers and accelerate (required for newer GPT-2 loading)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "torch", "transformers", "accelerate"])
        print("Installation complete. Invalidating module caches...")
        importlib.invalidate_caches()

# Run installation check immediately if in Colab/Jupyter
if any('jupyter' in arg or 'ipykernel' in arg or arg.endswith('.json') for arg in sys.argv):
    install_dependencies()

# Attempt to load the deep learning stack
try:
    import torch
    import torch.nn as nn
    from transformers import GPT2LMHeadModel, GPT2Tokenizer
    from torch.optim import AdamW
    HAS_TRANSFORMERS = True
except ImportError:
    try:
        importlib.invalidate_caches()
        import torch
        import torch.nn as nn
        from transformers import GPT2LMHeadModel, GPT2Tokenizer
        from torch.optim import AdamW
        HAS_TRANSFORMERS = True
    except ImportError:
        HAS_TRANSFORMERS = False

# =====================================================================
# 1. N-DIMENSIONAL PYTHAGOREAN GEOMETRY ENGINE
# =====================================================================
def make_rational_matrix_torch(M_mat):
    """
    FULLY FUNCTIONAL Vectorized PyTorch version of the rational matrix generator.
    Strictly avoids in-place modifications to ensure Autograd stability.
    """
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
    
    W_def_first = torch.ones((1, K), device=device, dtype=dtype)
    W_def_others = torch.zeros((N-1, K), device=device, dtype=dtype)
    W_def_final = torch.cat([W_def_first, W_def_others], dim=0)
    
    W = torch.where(c == 0, W_def_final, W_raw)
    return W

def make_rational_matrix_np(M_mat):
    """Vectorized Numpy version for serialization and inference."""
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

def snap_vector_to_pythagorean_np(target_w, max_int=64):
    """
    Analytical Inverse Stereographic Projection (Numpy).
    Higher max_int provides more 'tonal range' for the crystalline mind.
    """
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

# =====================================================================
# 2. THE HARMONIC STE LAYER (Straight-Through Estimator)
# =====================================================================
class HarmonicLinear(nn.Module):
    def __init__(self, original_weight, max_int=64):
        super().__init__()
        self.max_int = max_int
        self.in_features = original_weight.shape[0]
        self.out_features = original_weight.shape[1]
        
        # --- PHASE 0: PRE-SEEDING THE CRYSTAL ---
        print(f"  > Seeding High-Resolution Crystal ({self.in_features}x{self.out_features})...")
        W_np = original_weight.detach().cpu().numpy()
        M_init = np.zeros_like(W_np)
        
        # Parallel initialization for speed
        with mp.Pool(mp.cpu_count()) as pool:
            results = pool.map(snap_vector_to_pythagorean_np, [W_np[:, k] for k in range(self.out_features)])
        
        for k, m_vec in enumerate(results):
            M_init[:, k] = m_vec
            
        self.latent_M = nn.Parameter(torch.from_numpy(M_init).float())
        self.register_buffer('scale', torch.norm(original_weight.detach(), dim=0))

    def forward(self, x):
        # Discretize
        M_int = torch.round(torch.clamp(self.latent_M, -self.max_int, self.max_int))
        # STE Trick
        M_final = self.latent_M + (M_int - self.latent_M).detach()
        W_rational = make_rational_matrix_torch(M_final)
        W_final = W_rational * self.scale
        return x @ W_final

# =====================================================================
# 3. THE HEALING PIPELINE
# =====================================================================
def heal_model(model_name="gpt2", output_file="healed_gpt2.npz", epochs=15, limit_blocks=12):
    if not HAS_TRANSFORMERS:
        print("Error: Required libraries not found.")
        return

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"--- FULL SYSTEM HEALING (HI-RES) INITIATED on {device} ---")
    
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        
    model = GPT2LMHeadModel.from_pretrained(model_name).to(device)
    
    target_layers = []
    print("Patching system architecture...")
    for i in range(min(limit_blocks, len(model.transformer.h))):
        block = model.transformer.h[i]
        # Patch Attention and MLP
        block.attn.c_attn = HarmonicLinear(block.attn.c_attn.weight).to(device)
        target_layers.append((f"h.{i}.attn.c_attn", block.attn.c_attn))
        
        block.mlp.c_fc = HarmonicLinear(block.mlp.c_fc.weight).to(device)
        block.mlp.c_proj = HarmonicLinear(block.mlp.c_proj.weight).to(device)
        target_layers.append((f"h.{i}.mlp.c_fc", block.mlp.c_fc))
        target_layers.append((f"h.{i}.mlp.c_proj", block.mlp.c_proj))
        
    print(f"System patched: {len(target_layers)} logic blocks converted to Hi-Res Harmonic Layers.")

    # High-density philosophical dataset to guide the healing
    texts = [
        "The universe is built upon the ratios of whole numbers.",
        "Mathematics is the language in which God has written the universe.",
        "In the rhythm of numbers, we find the heartbeat of reality.",
        "Intelligence is not continuous; it is a discrete crystalline structure.",
        "To know the truth, one must look past the illusion of the smooth curve.",
        "Everything that is known has a number; without this, nothing could be understood.",
        "The harmony of the world is manifested in the relations of the integers.",
        "The soul is a harmony of numbers moving in perfect ratio.",
        "Existence is a vast geometric architecture of indivisible points.",
        "Reason is the discovery of the absolute proportions of nature.",
        "The sacred geometry of the mind is forged in the fires of integer logic.",
        "A singular point of truth is worth an infinite array of approximations."
    ]
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True).to(device)
    
    optimizer = AdamW(model.parameters(), lr=1.2e-4)
    
    print(f"\n--- Phase 1: Total Re-Learning ({epochs} Epochs) ---")
    torch.set_grad_enabled(True)
    model.train()
    
    start_train = time.time()
    for epoch in range(epochs):
        optimizer.zero_grad(set_to_none=True)
        outputs = model(inputs['input_ids'], labels=inputs['input_ids'], use_cache=False)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        print(f"Epoch {epoch+1:02d}/{epochs} | System Loss: {loss.item():.4f}")
        del outputs
        del loss

    print(f"\n--- Phase 1 Complete in {time.time() - start_train:.2f}s ---")

    print("\n--- Phase 2: Freezing the mind ---")
    integer_matrices = {}
    for name_str, layer in target_layers:
        with torch.no_grad():
            M_final = torch.round(torch.clamp(layer.latent_M, -layer.max_int, layer.max_int)).cpu().numpy().astype(np.int64)
        full_name = f"transformer.{name_str}.weight"
        integer_matrices[full_name] = M_final
        integer_matrices[full_name + "_scale"] = layer.scale.detach().cpu().numpy()

    np.savez_compressed(output_file, **integer_matrices)
    print(f"Hi-Res Healed model saved to {output_file}")
    
    # Analyze the Crystalline Structure
    print("\n--- Phase 3: Inspecting the Hi-Res Crystalline Logic ---")
    for name, matrix in list(integer_matrices.items())[:5]:
        if not name.endswith("_scale"):
            unique, counts = np.unique(matrix, return_counts=True)
            print(f"Diversity [{name}]: {len(unique)} unique integers (Resolution: {np.max(np.abs(matrix))}).")

    model.eval()
    prompt = "The universe is built upon"
    test_input = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        gen_output = model.generate(
            **test_input, 
            max_length=100, 
            do_sample=True, 
            top_k=40, 
            top_p=0.92, 
            repetition_penalty=1.3, 
            temperature=0.88,
            pad_token_id=tokenizer.eos_token_id
        )
    print(f"\n[Post-Healing Generation]:\n{tokenizer.decode(gen_output[0], skip_special_tokens=True)}")

# =====================================================================
# 4. INFRASTRUCTURE: INFER
# =====================================================================
def run_inference(frozen_file="healed_gpt2.npz", prompt="The universe is built upon", model_name="gpt2"):
    if not os.path.exists(frozen_file):
        print(f"Error: Could not find frozen model at {frozen_file}")
        return
        
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name)
    frozen_data = np.load(frozen_file)
    state_dict = model.state_dict()
    
    print(f"\n--- INJECTING HI-RES HEALED RATIONAL GEOMETRY FROM {frozen_file} ---")
    with torch.no_grad():
        injected = 0
        for name in list(frozen_data.keys()):
            if not name.endswith("_scale"):
                M_int = frozen_data[name]
                scale = frozen_data[name + "_scale"]
                W_rational = make_rational_matrix_np(M_int)
                W_restored = W_rational * scale
                if name in state_dict:
                    state_dict[name].copy_(torch.from_numpy(W_restored))
                    injected += 1
        print(f"Successfully injected {injected} discrete logic layers.")
                
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(
        **inputs, 
        max_length=100, 
        do_sample=True, 
        top_k=40, 
        top_p=0.92,
        repetition_penalty=1.3,
        temperature=0.88,
        pad_token_id=tokenizer.eos_token_id
    )
    print(f"\n[Frozen Inference]:\n{tokenizer.decode(outputs[0], skip_special_tokens=True)}")

if __name__ == "__main__":
    if any('jupyter' in arg or 'ipykernel' in arg or arg.endswith('.json') for arg in sys.argv):
        print("COLAB DETECTED: Running Hi-Res Full System Healing (Pre-Seeded, 15 Epochs)...")
        if HAS_TRANSFORMERS:
            heal_model(epochs=15, limit_blocks=12)
        else:
            importlib.invalidate_caches()
            try:
                from transformers import GPT2LMHeadModel, GPT2Tokenizer
                from torch.optim import AdamW
                HAS_TRANSFORMERS = True
                heal_model(epochs=15, limit_blocks=12)
            except ImportError:
                print("Environment setup still initializing. Run again.")
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("mode", choices=["heal", "infer"])
        parser.add_argument("--file", default="healed_gpt2.npz")
        parser.add_argument("--epochs", type=int, default=15)
        parser.add_argument("--prompt", default="The universe is built upon")
        args = parser.parse_args()
        
        if args.mode == "heal":
            heal_model(epochs=args.epochs)
        else:
            run_inference(frozen_file=args.file, prompt=args.prompt)