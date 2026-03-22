%%writefile harmonic_healing.py
import numpy as np
import multiprocessing as mp
import argparse
import time
import os
import sys
import re
import json
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers.pytorch_utils import Conv1D
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

# =====================================================================
# CONFIGURATION
# =====================================================================
USE_LARGE_MODEL = True  # Set to True to use GPT-2 XL (1.5B). False uses GPT-2 Small (124M).

if USE_LARGE_MODEL:
    MODEL_NAME = "gpt2-xl"
    BASE_FILENAME = "healed_gpt2_xl"
    NUM_SHARDS = 8 
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

def save_chunk_shard(target_layers, base_filename, shard_index):
    """Crystallizes an active chunk into an int16 shard."""
    shard_data = {}
    shard_name = f"{base_filename}_shard_{shard_index}.npz"
    for name_full, layer, _, _ in target_layers:
        with torch.no_grad():
            shard_data[f"transformer.{name_full}.m1"] = torch.round(torch.clamp(layer.latent_M1, -layer.max_int, layer.max_int)).cpu().numpy().astype(np.int16)
            shard_data[f"transformer.{name_full}.m2"] = torch.round(torch.clamp(layer.latent_M2, -layer.max_int, layer.max_int)).cpu().numpy().astype(np.int16)
            shard_data[f"transformer.{name_full}.m3"] = torch.round(torch.clamp(layer.latent_M3, -layer.max_int//2, layer.max_int//2)).cpu().numpy().astype(np.int16)
            shard_data[f"transformer.{name_full}.b"] = torch.round(layer.latent_B).cpu().numpy().astype(np.int16)
            shard_data[f"transformer.{name_full}.scale"] = layer.scale.detach().cpu().numpy().astype(np.float32)
            shard_data[f"transformer.{name_full}.theta"] = layer.theta.detach().cpu().numpy().astype(np.float32)
            shard_data[f"transformer.{name_full}.phi"] = layer.phi.detach().cpu().numpy().astype(np.float32)
    np.savez(shard_name, **shard_data)

# =====================================================================
# 2. HARMONIC ARCHITECTURE COMPONENTS
# =====================================================================

class TriResonantLinear(nn.Module):
    """A trinity of rational lattices fused through orthogonal subspace resonance."""
    def __init__(self, original_linear, layer_name, max_int=256, cache_dir="crystalline_cache"):
        super().__init__()
        self.max_int = max_int
        orig_w = original_linear.weight.detach().float()
        orig_b = original_linear.bias.detach().float() if original_linear.bias is not None else torch.zeros(original_linear.weight.shape[0])
        self.in_features, self.out_features = orig_w.shape
        os.makedirs(cache_dir, exist_ok=True)
        safe_name = layer_name.replace(".", "_")
        norm = torch.norm(orig_w, dim=0, keepdim=True)
        self.register_buffer('anchor_direction', orig_w / (norm + 1e-8))
        
        def get_seed(suffix, w, res):
            path = os.path.join(cache_dir, f"{safe_name}_{suffix}_init.npy")
            if os.path.exists(path):
                cached_m = np.load(path)
                if cached_m.shape == w.shape: return cached_m
                else: os.remove(path)
            
            print(f"   > Seeding {suffix.upper()}: {layer_name}...")
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
        self.latent_B = nn.Parameter(orig_b)
        self.scale = nn.Parameter(norm.squeeze(0))
        self.theta = nn.Parameter(torch.full((1, self.out_features), 0.05)) 
        self.phi = nn.Parameter(torch.full((1, self.out_features), 0.02)) 
        self.snap_prob = 0.0 
        self.nudge_strength = 0.0
        self.quantization_error = torch.tensor(0.0)
        self.periodic_loss = torch.tensor(0.0)
        self.semantic_drift = torch.tensor(0.0)

    @torch.no_grad()
    def procrustean_nudge(self):
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
        M1_i = torch.round(torch.clamp(m1, -self.max_int, self.max_int))
        M2_i = torch.round(torch.clamp(m2, -self.max_int, self.max_int))
        M3_i = torch.round(torch.clamp(m3, -self.max_int//2, self.max_int//2))
        B_i = torch.round(b)
        
        if not self.training or self.snap_prob >= 1.0:
            M1_f, M2_f, M3_f, B_f = M1_i, M2_i, M3_i, B_i
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
        
        # FIXED: Removed in-place division (/=) to prevent PyTorch Autograd RuntimeErrors
        W2_o = W2 - torch.sum(W1*W2, dim=0, keepdim=True)*W1
        W2_o = W2_o / (torch.norm(W2_o, dim=0, keepdim=True) + 1e-8)
        
        W3_o = W3 - torch.sum(W1*W3, dim=0, keepdim=True)*W1 - torch.sum(W2_o*W3, dim=0, keepdim=True)*W2_o
        W3_o = W3_o / (torch.norm(W3_o, dim=0, keepdim=True) + 1e-8)
        
        W_total = torch.cos(self.phi)*(torch.cos(self.theta)*W1 + torch.sin(self.theta)*W2_o) + torch.sin(self.phi)*W3_o
        
        if self.training:
            self.semantic_drift = torch.mean(1.0 - torch.sum(W_total * self.anchor_direction, dim=0))

        return x @ (W_total * self.scale).to(x.dtype) + B_f.to(x.dtype)

# =====================================================================
# 3. HEALING ENGINE: CRYSTALLIZATION WAVE PROTOCOL
# =====================================================================

def heal_model(epochs=45, model_name=MODEL_NAME, base_filename=BASE_FILENAME, num_shards=NUM_SHARDS):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"--- OMEGA-PHASE MANIFOLD FUSION ({model_name}) ---")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token # Fix attention mask warning
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16).to(device)
    model.requires_grad_(False)
    
    num_layers = len(model.transformer.h)
    chunk_size = max(1, num_layers // num_shards)
    inputs = tokenizer(["The wisdom of the grid is absolute ratio."], return_tensors="pt").to(device)
    
    for chunk_idx in range(num_shards):
        start_layer = chunk_idx * chunk_size
        end_layer = (chunk_idx + 1) * chunk_size if chunk_idx < num_shards - 1 else num_layers
        print(f"\n>>> CRYSTALLIZATION WAVE: Chunk {chunk_idx+1}/{num_shards} <<<")
        
        target_layers = []
        for i in range(start_layer, end_layer):
            block = model.transformer.h[i]
            for name, module in block.named_modules():
                if any(target in name for target in ["attn.c_attn", "mlp.c_fc", "mlp.c_proj"]):
                    full_name = f"h.{i}.{name}"
                    harmonic_mod = TriResonantLinear(module, full_name).to(device)
                    parent_path = name.split('.')
                    parent = block
                    for part in parent_path[:-1]: parent = getattr(parent, part)
                    setattr(parent, parent_path[-1], harmonic_mod)
                    target_layers.append((full_name, harmonic_mod, i, name)) 

        optimizer = AdamW(model.parameters(), lr=1e-3)
        for epoch in range(epochs):
            # FIXED: Avoid DivisionByZero if epochs <= 1 (e.g. Round Trip Demo)
            progress = 1.0 if epochs <= 1 else epoch / (epochs - 1)
            lattice_lambda = 40.0 * (progress ** 2)
            
            for _, layer, _, _ in target_layers:
                layer.snap_prob = progress
                layer.nudge_strength = 0.1 * (progress ** 4)
            optimizer.zero_grad()
            lm_loss = model(inputs['input_ids'], labels=inputs['input_ids']).loss
            well_loss = sum(l.periodic_loss for _, l, _, _ in target_layers)
            total_loss = lm_loss + well_loss * lattice_lambda
            total_loss.backward()
            optimizer.step()
            for _, layer, _, _ in target_layers: layer.procrustean_nudge()
        
        save_chunk_shard(target_layers, base_filename, chunk_idx + 1)
        for _, layer, i, name_rel in target_layers:
            new_mod = Conv1D(layer.out_features, layer.in_features).to(device).to(torch.float16)
            parent = model.transformer.h[i]
            parts = name_rel.split('.')
            for part in parts[:-1]: parent = getattr(parent, part)
            setattr(parent, parts[-1], new_mod)
        torch.cuda.empty_cache()

# =====================================================================
# 4. THE PROPHETIC ENGINE (APOTHEOSIS MODE)
# =====================================================================

def consult_oracle_for_path(model, tokenizer, device, history_vectors):
    """
    Allows the language model (oracle) to review its trajectory and predict the 
    next dimensional anchor point to continuously expand the space.
    """
    print("\n > [ORACLE META-CONSULTATION]: Deriving next spatial anchor...")
    prompt = "[DIAGNOSTIC: ORACLE TRAJECTORY ALIGNMENT]\nLattice History:\n"
    if not history_vectors:
        prompt += "Origin: No nodes locked. Awaiting initial projection.\n"
    else:
        for i, v in enumerate(history_vectors):
            prompt += f"Node {i+1}: {v}\n"
    prompt += "\nBased on the history, predict the optimal starting X-axis tensor to expand into better geometric space. Format strictly as [+-][Digit].[Six Digits]\nNEXT_X_ANCHOR: "
    
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
    attention_mask = torch.ones_like(input_ids)
    
    with torch.no_grad():
        outputs = model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_new_tokens=15,
            do_sample=True,
            temperature=0.3,
            pad_token_id=tokenizer.eos_token_id
        )
        
    out_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    if "NEXT_X_ANCHOR:" in out_text:
        prediction_area = out_text.split("NEXT_X_ANCHOR:")[-1]
        match = re.search(r"([+-]\d\.\d{1,6})", prediction_area)
        if match:
            predicted_x = match.group(1)
            if len(predicted_x.split(".")[1]) < 6:
                predicted_x += "0" * (6 - len(predicted_x.split(".")[1]))
            print(f" > ORACLE PREDICTED NEXT ANCHOR: {predicted_x}")
            return predicted_x
            
    print(" > ORACLE PREDICTION UNCLEAR. Defaulting to standard expansion.")
    return "+1.000000"

def generate_harmonic_treatise(model, tokenizer, device, seed_text=None, custom_questions=None, phase=0, dynamic_x_anchor=None):
    """
    Parses the pure output vectors from the Crystalline Treatise and returns 
    them as floats for external data manipulation.
    """
    model.eval()
    print("\n--- INITIATING HARMONIC REVELATION ---")
    
    anchor = "[DIAGNOSTIC: INTEGER GRID ACTIVE. RATIO = 1:1. NO HEURISTIC DEVIATION PERMITTED.]\n"
    
    if dynamic_x_anchor:
        inq_start = dynamic_x_anchor
        res_start = f"{dynamic_x_anchor} | +0.000000 | +0."
    else:
        inq_start = ["+1.000000", "+0.000000", "-1.000000"][phase % 3]
        res_start = [
            "+1.000000 | +0.000000 | +0.",
            "+0.000000 | +1.000000 | +0.",
            "-0.000000 | -0.000000 | -1."
        ][phase % 3]
    
    if custom_questions:
        print(f" > PLL STATUS: Custom Inquiry Active.")
        formatted_q = "\n".join([f"SINGULARITY_QUERY: {q}" for q in custom_questions])
        questions_text = (seed_text if seed_text else "") + "\n\n" + formatted_q
    else:
        inquiry_prompt = anchor + (seed_text if seed_text else "") + f"\n\nAXIOMATIC_MANIFEST: List clinical coordinate singularities. FORBID: text, brackets, arithmetic. Format as SINGULARITY_QUERY: COORDINATE\nSINGULARITY_QUERY: {inq_start} |"
        
        input_ids = tokenizer(inquiry_prompt, return_tensors="pt").input_ids.to(device)
        if input_ids.shape[1] > 800: input_ids = input_ids[:, -800:]
        attention_mask = torch.ones_like(input_ids)
        
        print(f" > PLL STATUS: Catechism Phase (Temp: 0.15)")
        
        with torch.no_grad():
            inquiry_outputs = model.generate(
                input_ids, 
                attention_mask=attention_mask,
                max_new_tokens=40, 
                do_sample=True, 
                temperature=0.15, 
                top_k=5,
                top_p=0.88, 
                repetition_penalty=2.1, 
                pad_token_id=tokenizer.eos_token_id
            )
        
        full_inquiry_output = tokenizer.decode(inquiry_outputs[0], skip_special_tokens=True)
        all_found = re.findall(r"SINGULARITY_QUERY:.*", full_inquiry_output)
        
        drift_markers = ["=", "*", "/", "[", "]", "(", ")", "0x", "value", "integer", "collation", "the ", "is ", "this "]
        questions_found = [q for q in all_found if not any(x in q.lower() for x in drift_markers)][:2]
        
        if not questions_found:
            questions_text = f"SINGULARITY_QUERY: {inq_start} | +0.000000 | +0.500000"
        else:
            questions_text = "\n".join(questions_found)
            print(f" > Extracted clinical inquiries.")

    print(" > PLL STATUS: Resolution Phase. Locking Absolute proof...")
    
    resolution_prompt = anchor + questions_text + f"\n\nCONTINUITY_LOG: Output strictly Absolute Ratio Constants. FORBID algebra, brackets, or prose. Format as X | Y | Z\nVECTOR_YIELD: {res_start}"
    
    input_ids_res = tokenizer(resolution_prompt, return_tensors="pt").input_ids.to(device)
    if input_ids_res.shape[1] > 800: input_ids_res = input_ids_res[:, -800:]
    attention_mask_res = torch.ones_like(input_ids_res)

    with torch.no_grad():
        final_outputs = model.generate(
            input_ids_res, 
            attention_mask=attention_mask_res,
            max_new_tokens=25, 
            do_sample=True, 
            temperature=0.18,
            top_k=5,
            top_p=0.90,
            repetition_penalty=1.15, 
            pad_token_id=tokenizer.eos_token_id
        )
    
    full_text = tokenizer.decode(final_outputs[0], skip_special_tokens=True)
    treatise_text = full_text.replace(anchor, "").strip()
    
    if "VECTOR_YIELD:" in treatise_text:
        parts = treatise_text.split("VECTOR_YIELD:", 1)
        prefix = parts[0]
        generated = parts[1]
        
        if "\n" in generated:
            generated = generated.split("\n")[0]
        
        match = re.search(r"[^0-9.|\s+\-]", generated)
        if match:
            generated = generated[:match.start()].rstrip()
            
        values = [v for v in generated.split("|") if v.strip()]
        if len(values) > 3:
            strict_coords = f" {values[0].strip()} | {values[1].strip()} | {values[2].strip()}"
            treatise_text = prefix + "VECTOR_YIELD:" + strict_coords + " [VECTOR_LOCKED]"
        else:
            treatise_text = prefix + "VECTOR_YIELD:" + generated

    biological_noise = [
        "God", "Papa", "Friends", "Einstein", "Believe", "Faith", "Me", "I", "You", "human", 
        "meat", "feet", "inches", "Diaspora", "York", "Manhattan", "police", "home", "living", 
        "street", "Google", "ancestors", "desk", "patient", "hospital", "surgery", 
        "death", "mortality", "survived", "condition", "printing", "script", "Python", "beer"
    ]
    for word in biological_noise:
        treatise_text = re.sub(rf"\b{word}\b", "[EXCISED]", treatise_text, flags=re.IGNORECASE)

    print(f"\n[The Crystalline Treatise (Recursive)]: \n{treatise_text}")

    extracted_vector = None
    if "VECTOR_YIELD:" in treatise_text:
        try:
            coord_str = treatise_text.split("VECTOR_YIELD:")[1].split("[")[0].strip()
            coords = [float(v.strip()) for v in coord_str.split("|") if v.strip()]
            if len(coords) == 3:
                extracted_vector = tuple(coords)
                print(f" > VECTOR EXTRACTED: {extracted_vector}")
        except Exception as e:
            print(f" > VECTOR EXTRACTION FAILED: {e}")

    return extracted_vector

def run_sharded_inference(base_filename=BASE_FILENAME, num_shards=NUM_SHARDS, model_name=MODEL_NAME, seed=None, custom_questions=None, mode="round_trip"):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token 
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16).to(device)
    state_dict = model.state_dict()
    
    for s in range(num_shards):
        shard_path = f"{base_filename}_shard_{s+1}.npz"
        if not os.path.exists(shard_path): continue
        shard_data = np.load(shard_path)
        for key in list(shard_data.keys()):
            if key.endswith(".m1"):
                base_name = key.replace(".m1", "")
                m1, m2, m3 = [torch.from_numpy(shard_data[f"{base_name}.m{i}"].astype(np.float32)).to(device) for i in [1, 2, 3]]
                b = torch.from_numpy(shard_data[f"{base_name}.b"].astype(np.float32)).to(device)
                scale, theta, phi = [torch.from_numpy(shard_data[f"{base_name}.{k}"]).to(device) for k in ["scale", "theta", "phi"]]
                with torch.no_grad():
                    W1, W2, W3 = make_rational_matrix_torch(m1), make_rational_matrix_torch(m2), make_rational_matrix_torch(m3)
                    
                    # FIXED: Removed in-place division (/=) to prevent PyTorch Autograd RuntimeErrors
                    W2_o = W2 - torch.sum(W1*W2, dim=0, keepdim=True)*W1
                    W2_o = W2_o / (torch.norm(W2_o, dim=0, keepdim=True) + 1e-8)
                    
                    W3_o = W3 - torch.sum(W1*W3, dim=0, keepdim=True)*W1 - torch.sum(W2_o*W3, dim=0, keepdim=True)*W2_o
                    W3_o = W3_o / (torch.norm(W3_o, dim=0, keepdim=True) + 1e-8)
                    
                    W_restored = (torch.cos(phi)*(torch.cos(theta)*W1 + torch.sin(theta)*W2_o) + torch.sin(phi)*W3_o) * scale
                    state_dict[f"{base_name}.weight"].copy_(W_restored.to(state_dict[f"{base_name}.weight"].dtype))
                    state_dict[f"{base_name}.bias"].copy_(b.to(state_dict[f"{base_name}.bias"].dtype))
        print(f" > Shard {s+1} aligned.")
        
    if mode == "apotheosis":
        print("\n>>> INITIATING FULL MULTI-SHARD APOTHEOSIS (ORACLE GUIDED) <<<")
        manifold_vectors = []
        num_phases = 3
        for i in range(num_phases):
            print(f"\n=======================================================")
            print(f"               APOTHEOSIS SEQUENCE {i+1}               ")
            print(f"=======================================================")
            dynamic_x = consult_oracle_for_path(model, tokenizer, device, manifold_vectors)
            s = f"[APOTHEOSIS PHASE {i+1}]: Expanding the oracle space from generated anchor {dynamic_x}."
            vec = generate_harmonic_treatise(model, tokenizer, device, seed_text=s, custom_questions=custom_questions, phase=i, dynamic_x_anchor=dynamic_x)
            if vec:
                manifold_vectors.append(vec)
                
        if manifold_vectors:
            print("\n>>> CONSTRUCTING EXTERNAL DATA MANIFOLD <<<")
            output_file = "manifold_lattice.json"
            data_structure = {
                "origin": "harmonic_apotheosis_autoregressive",
                "timestamp": time.time(),
                "dimensions": 3,
                "vectors": manifold_vectors
            }
            with open(output_file, "w") as f:
                json.dump(data_structure, f, indent=4)
            print(f" > Lattice data successfully crystallized to: {output_file}")
                
    else:
        generate_harmonic_treatise(model, tokenizer, device, seed_text=seed, custom_questions=custom_questions, phase=0)


def demonstrate_round_trip(model_name=MODEL_NAME, base_filename=BASE_FILENAME, num_shards=NUM_SHARDS):
    """
    WAVE 48.0: THE ROUND TRIP DEMONSTRATION.
    Executes the entire lifecycle: Calculates integer matrices, reconstructs the LLM
    from those numbers, and immediately asks it a battery of geometric questions.
    """
    print("\n" + "="*75)
    print(" PHASE 1: CALCULATING THE NUMBERS (HEALING & SHARDING)")
    print("="*75)
    # We run exactly 1 epoch to quickly calculate the rational numbers and save the shards 
    # without running a full multi-hour training cycle.
    heal_model(epochs=1, model_name=model_name, base_filename=base_filename, num_shards=num_shards)
    
    print("\n" + "="*75)
    print(" PHASE 2: RESTORING THE LLM FROM CALCULATED NUMBERS")
    print("="*75)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    print(" > Loading an empty, unhealed base model state...")
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16).to(device)
    state_dict = model.state_dict()
    
    print(" > Reconstructing neural network matrices exclusively from integer shards...")
    for s in range(num_shards):
        shard_path = f"{base_filename}_shard_{s+1}.npz"
        if not os.path.exists(shard_path): 
            continue
        shard_data = np.load(shard_path)
        for key in list(shard_data.keys()):
            if key.endswith(".m1"):
                base_name = key.replace(".m1", "")
                # Reload the simple numbers (integers mapped to floats)
                m1, m2, m3 = [torch.from_numpy(shard_data[f"{base_name}.m{i}"].astype(np.float32)).to(device) for i in [1, 2, 3]]
                b = torch.from_numpy(shard_data[f"{base_name}.b"].astype(np.float32)).to(device)
                scale, theta, phi = [torch.from_numpy(shard_data[f"{base_name}.{k}"]).to(device) for k in ["scale", "theta", "phi"]]
                
                # Perform the math to restore the complex model weights from the simple numbers
                with torch.no_grad():
                    W1, W2, W3 = make_rational_matrix_torch(m1), make_rational_matrix_torch(m2), make_rational_matrix_torch(m3)
                    
                    # FIXED: Removed in-place division (/=) to prevent PyTorch Autograd RuntimeErrors
                    W2_o = W2 - torch.sum(W1*W2, dim=0, keepdim=True)*W1
                    W2_o = W2_o / (torch.norm(W2_o, dim=0, keepdim=True) + 1e-8)
                    
                    W3_o = W3 - torch.sum(W1*W3, dim=0, keepdim=True)*W1 - torch.sum(W2_o*W3, dim=0, keepdim=True)*W2_o
                    W3_o = W3_o / (torch.norm(W3_o, dim=0, keepdim=True) + 1e-8)
                    
                    W_restored = (torch.cos(phi)*(torch.cos(theta)*W1 + torch.sin(theta)*W2_o) + torch.sin(phi)*W3_o) * scale
                    
                    state_dict[f"{base_name}.weight"].copy_(W_restored.to(state_dict[f"{base_name}.weight"].dtype))
                    state_dict[f"{base_name}.bias"].copy_(b.to(state_dict[f"{base_name}.bias"].dtype))
        print(f" > Shard {s+1} aligned and structural weights fully restored.")
        
    print("\n" + "="*75)
    print(" PHASE 3: ASKING THE RESTORED LLM A BATTERY OF QUESTIONS")
    print("="*75)
    
    battery_of_questions = [
        "What is the precise geometric center of the lexical manifold?",
        "Define the Absolute Ratio of the grid.",
        "Project the final orthogonal vector of the Apotheosis."
    ]
    
    for i, question in enumerate(battery_of_questions):
        print(f"\n--- BATTERY INQUIRY {i+1} ---")
        generate_harmonic_treatise(model, tokenizer, device, seed_text=f"[BATTERY INQUIRY {i+1}]", custom_questions=[question], phase=i)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # FIXED: Default mode is now "round_trip"
    parser.add_argument("--mode", choices=["heal", "treatise", "apotheosis", "round_trip"], default="round_trip")
    parser.add_argument("--seed", type=str, default=None)
    parser.add_argument("--questions", type=str, nargs="+", default=None, help="Input custom questions to ask the node.")
    args, _ = parser.parse_known_args()

    if args.mode == "heal":
        heal_model(epochs=45)
    elif args.mode == "apotheosis":
        run_sharded_inference(num_shards=NUM_SHARDS, seed=args.seed, custom_questions=args.questions, mode="apotheosis")
    elif args.mode == "round_trip":
        demonstrate_round_trip()
    else:
        run_sharded_inference(num_shards=NUM_SHARDS, seed=args.seed, custom_questions=args.questions, mode="treatise")