import contextlib
import gc
import os
import random
import re
import sys
import threading
import time

import numpy as np
import psutil
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.utils.checkpoint import checkpoint
from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer

try:
    from safetensors.torch import load_file
except ImportError:
    pass

# WAVE 140: Atomic Hardware Locking & Resilient Materialization
if torch.cuda.is_available():
    torch.set_float32_matmul_precision("high")

# --- CONFIGURATION ---
MODEL_NAME = "vicgalle/gpt2-alpaca-gpt4"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Cache & Checkpoint Paths
BASELINE_CACHE_PATH = "crystalline_seed_weights.pt"
SAVE_PATH = "liquid_manifold_state.pt"

# WAVE 140: Set to True if the model continues to report DNA mismatches
FORCE_FRESH_START = False
DUAL_AGENT_MODE = True

# Start at Full Rank (768)
INITIAL_DECIMATION_RANK = 768

# Training Hyperparameters
BLOCK_SIZE = 128
LEARNING_RATE = 2e-5
LATTICE_PENALTY = 0.001
WARMUP_TURNS = 10

# WAVE 136: Adaptive Decimation Logic
AUTO_DECIMATE = True
LOSS_THRESHOLD_FOR_DECIMATION = 1.5
MIN_RANK = 64

# Reality Anchoring Data
REALITY_ANCHORS = [
    "### Instruction:\nExplain the concept of a mathematical manifold.\n\n### Response:\nA manifold is a topological space that locally resembles Euclidean space near each point.",
    "### Instruction:\nWhat is the relationship between geometry and logic?\n\n### Response:\nGeometry provides the structural framework, while logic defines the valid transitions within that structure.",
    "### Instruction:\nWrite a short poem about a crystal.\n\n### Response:\nFrozen light in geometric grace, a silent song in time and space.",
    "### Instruction:\nHow does a neural network learn?\n\n### Response:\nThrough backpropagation, adjusting internal weights to minimize the distance between prediction and reality.",
]

# Globals for Asynchronous Learning
cuda_lock = threading.RLock()
stop_event = threading.Event()
main_is_generating = threading.Event()
conversation_buffer = []
bg_stats = {"bg_loss": 5.0, "bg_steps": 0}

# =====================================================================
# 0. BENCHMARKING & PROFILING CORE
# =====================================================================


@contextlib.contextmanager
def benchmark_op(op_name):
    print(f"\n[SYS] Starting operation: {op_name}...")
    t0 = time.time()
    yield
    t1 = time.time()
    print(f"[BENCHMARK] {op_name} completed in {t1 - t0:.4f}s.")


# =====================================================================
# 1. HARDWARE TELEMETRY & HYGIENE
# =====================================================================


def purge_gpu():
    gc.collect()
    if torch.cuda.is_available():
        try:
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            torch.cuda.synchronize()
        except RuntimeError:
            pass


def log_hardware_state(phase_name):
    print(f"\n[{phase_name}]")
    cpu_usage = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory()
    print(f" ├─ CPU Usage: {cpu_usage:.1f}%")
    print(
        f" ├─ Sys RAM:   {ram.used / (1024**3):.2f} GB / {ram.total / (1024**3):.2f} GB"
    )
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / (1024**3)
        print(f" └─ GPU VRAM:  {allocated:.2f} GB Allocated")
    print("-" * 50)


if torch.cuda.is_available():
    try:
        torch.cuda.synchronize()
    except RuntimeError:
        print("\n[CRITICAL]: CUDA CONTEXT POISONED. RESTART RUNTIME REQUIRED.")
        sys.exit(1)

# =====================================================================
# 1.5 COGNITIVE FIREWALL
# =====================================================================


def sanitize_cognition(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"http[s]?://\S+", "", text)
    text = re.sub(r"www\.\S+", "", text)
    text = re.sub(r"-{3,}", "", text)
    text = re.sub(r"_{3,}", "", text)
    text = text.replace("Reply", "").replace("Delete", "").replace("Subject:", "")
    text = re.sub(r"\s+", " ", text).strip()
    words = text.split()
    if len(words) > 5:
        last_word = words[-1].lower()
        count = 0
        for w in reversed(words):
            if w.lower() == last_word:
                count += 1
            else:
                break
        if count > 3:
            return "I am re-evaluating my cognitive patterns to ensure unique logical flow."
    if len(text) < 15:
        return "I am contemplating the mathematical structure of our reality."
    return text


# =====================================================================
# 2. THEORETICAL MATHEMATICS
# =====================================================================


def riemannian_project(m_mat):
    m_mat = m_mat.float()
    m_norm = torch.sqrt(torch.sum(m_mat**2, dim=0, keepdim=True) + 1e-8)
    w_spatial = torch.sin(m_norm) * (m_mat / m_norm)
    w_last = torch.cos(m_norm)
    return torch.cat([w_spatial, w_last], dim=0)


def riemannian_inverse(w_mat):
    w_mat = w_mat.to("cpu").float()
    norms = torch.sqrt(torch.sum(w_mat**2, dim=0, keepdim=True) + 1e-10)
    w_n = w_mat / norms
    spatial = w_n[:-1, :]
    last = w_n[-1, :].clamp(-1.0 + 1e-7, 1.0 - 1e-7)
    angle = torch.acos(last)
    m_direction = spatial / (torch.sin(angle) + 1e-8)
    m = m_direction * angle
    return m.clamp(-32.0, 32.0)


def build_manifold_matrix(m1, m2, m3, theta, phi):
    W1 = riemannian_project(m1)
    W2 = riemannian_project(m2)
    W3 = riemannian_project(m3)
    W2_o = W2 - W1 * torch.sum(W1 * W2, dim=0, keepdim=True)
    W2_o = W2_o / torch.sqrt(torch.sum(W2_o**2, dim=0, keepdim=True) + 1e-10)
    W3_o = W3 - W1 * torch.sum(W1 * W3, dim=0, keepdim=True)
    W3_o = W3_o - W2_o * torch.sum(W2_o * W3, dim=0, keepdim=True)
    W3_o = W3_o / torch.sqrt(torch.sum(W3_o**2, dim=0, keepdim=True) + 1e-10)
    return (
        torch.cos(phi) * (torch.cos(theta) * W1 + torch.sin(theta) * W2_o)
        + torch.sin(phi) * W3_o
    )


class TriResonantLinear(nn.Module):
    def __init__(self, weight, bias, scale, theta, phi, m1, m2, m3):
        super().__init__()
        self.latent_M1 = nn.Parameter(m1.float())
        self.latent_M2 = nn.Parameter(m2.float())
        self.latent_M3 = nn.Parameter(m3.float())
        self.latent_B = nn.Parameter(bias.float())
        self.scale = nn.Parameter(scale.float())
        self.theta = nn.Parameter(theta.float())
        self.phi = nn.Parameter(phi.float())
        self.periodic_loss = torch.tensor(0.0)

    @torch.no_grad()
    def crystallize(self):
        W_total = build_manifold_matrix(
            self.latent_M1, self.latent_M2, self.latent_M3, self.theta, self.phi
        )
        W_fused = (W_total * self.scale).detach()
        B_fused = self.latent_B.detach()
        if not hasattr(self, "W_fused"):
            self.register_buffer("W_fused", W_fused)
            self.register_buffer("B_fused", B_fused)
        else:
            self.W_fused.copy_(W_fused)
            self.B_fused.copy_(B_fused)

    def forward(self, x):
        if self.training:
            m1, m2, m3 = self.latent_M1, self.latent_M2, self.latent_M3
            self.periodic_loss = (
                (torch.mean(torch.sin(np.pi * m1) ** 2) * 0.05)
                + torch.mean(torch.sin(np.pi * m2) ** 2)
                + torch.mean(torch.sin(np.pi * m3) ** 2)
            )
            W_total = checkpoint(
                build_manifold_matrix,
                m1,
                m2,
                m3,
                self.theta,
                self.phi,
                use_reentrant=False,
            )
            return torch.matmul(
                x, (W_total * self.scale).to(x.dtype)
            ) + self.latent_B.to(x.dtype)
        return torch.matmul(x, self.W_fused.to(x.dtype)) + self.B_fused.to(x.dtype)


class LowRankLiquidManifold(nn.Module):
    def __init__(self, W_A, W_B, bias):
        super().__init__()
        m1_A = riemannian_inverse(W_A)
        self.m1_A = nn.Parameter(m1_A)
        self.m2_A = nn.Parameter(torch.randn_like(m1_A) * 0.01)
        self.m3_A = nn.Parameter(torch.randn_like(m1_A) * 0.01)
        self.scale_A = nn.Parameter(
            torch.sqrt(torch.sum(W_A**2, dim=0, keepdim=True) + 1e-10)
        )
        self.theta_A = nn.Parameter(torch.zeros(1, W_A.shape[1]))
        self.phi_A = nn.Parameter(torch.zeros(1, W_A.shape[1]))
        m1_B = riemannian_inverse(W_B)
        self.m1_B = nn.Parameter(m1_B)
        self.m2_B = nn.Parameter(torch.randn_like(m1_B) * 0.01)
        self.m3_B = nn.Parameter(torch.randn_like(m1_B) * 0.01)
        self.scale_B = nn.Parameter(
            torch.sqrt(torch.sum(W_B**2, dim=0, keepdim=True) + 1e-10)
        )
        self.theta_B = nn.Parameter(torch.zeros(1, W_B.shape[1]))
        self.phi_B = nn.Parameter(torch.zeros(1, W_B.shape[1]))
        self.latent_B = nn.Parameter(bias.float())
        self.periodic_loss = torch.tensor(0.0)

    @torch.no_grad()
    def crystallize(self):
        W_A_total = build_manifold_matrix(
            self.m1_A, self.m2_A, self.m3_A, self.theta_A, self.phi_A
        )
        W_B_total = build_manifold_matrix(
            self.m1_B, self.m2_B, self.m3_B, self.theta_B, self.phi_B
        )
        W_fused = ((W_A_total * self.scale_A) @ (W_B_total * self.scale_B)).detach()
        B_fused = self.latent_B.detach()
        if not hasattr(self, "W_fused"):
            self.register_buffer("W_fused", W_fused)
            self.register_buffer("B_fused", B_fused)
        else:
            self.W_fused.copy_(W_fused)
            self.B_fused.copy_(B_fused)

    def forward(self, x):
        if self.training:
            self.periodic_loss = (
                (torch.mean(torch.sin(np.pi * self.m1_A) ** 2) * 0.05)
                + torch.mean(torch.sin(np.pi * self.m2_A) ** 2)
                + torch.mean(torch.sin(np.pi * self.m3_A) ** 2)
                + (torch.mean(torch.sin(np.pi * self.m1_B) ** 2) * 0.05)
                + torch.mean(torch.sin(np.pi * self.m2_B) ** 2)
                + torch.mean(torch.sin(np.pi * self.m3_B) ** 2)
            )
            W_A_total = checkpoint(
                build_manifold_matrix,
                self.m1_A,
                self.m2_A,
                self.m3_A,
                self.theta_A,
                self.phi_A,
                use_reentrant=False,
            )
            W_B_total = checkpoint(
                build_manifold_matrix,
                self.m1_B,
                self.m2_B,
                self.m3_B,
                self.theta_B,
                self.phi_B,
                use_reentrant=False,
            )
            W_eff = (W_A_total * self.scale_A) @ (W_B_total * self.scale_B)
            return torch.matmul(x, W_eff.to(x.dtype)) + self.latent_B.to(x.dtype)
        return torch.matmul(x, self.W_fused.to(x.dtype)) + self.B_fused.to(x.dtype)


# =====================================================================
# 3. MANIFOLD OPERATIONS
# =====================================================================


def decimate_manifold(model, harmonic_layers, target_rank):
    """Logic-Gain Amplitude Preservation Decimation."""
    with benchmark_op(f"Decimate Manifold to Rank {target_rank}"):
        harmonic_layers.clear()
        blocks = model.transformer.h
        targets = ["attn.c_attn", "mlp.c_fc", "mlp.c_proj"]
        for i, block in enumerate(blocks):
            for name in targets:
                parent = block
                parts = name.split(".")
                for part in parts[:-1]:
                    parent = getattr(parent, part)
                orig_mod = getattr(parent, parts[-1])

                if hasattr(orig_mod, "W_fused"):
                    W_full, bias = orig_mod.W_fused, orig_mod.B_fused
                else:
                    if isinstance(orig_mod, TriResonantLinear):
                        W_full = (
                            build_manifold_matrix(
                                orig_mod.latent_M1,
                                orig_mod.latent_M2,
                                orig_mod.latent_M3,
                                orig_mod.theta,
                                orig_mod.phi,
                            )
                            * orig_mod.scale
                        )
                        bias = orig_mod.latent_B
                    elif isinstance(orig_mod, LowRankLiquidManifold):
                        W_A_total = (
                            build_manifold_matrix(
                                orig_mod.m1_A,
                                orig_mod.m2_A,
                                orig_mod.m3_A,
                                orig_mod.theta_A,
                                orig_mod.phi_A,
                            )
                            * orig_mod.scale_A
                        )
                        W_B_total = (
                            build_manifold_matrix(
                                orig_mod.m1_B,
                                orig_mod.m2_B,
                                orig_mod.m3_B,
                                orig_mod.theta_B,
                                orig_mod.phi_B,
                            )
                            * orig_mod.scale_B
                        )
                        W_full = W_A_total @ W_B_total
                        bias = orig_mod.latent_B
                    else:
                        continue

                U, S, Vh = torch.linalg.svd(W_full.double(), full_matrices=False)
                U_r, S_r, Vh_r = (
                    U[:, :target_rank].float(),
                    S[:target_rank].float(),
                    Vh[:target_rank, :].float(),
                )
                gain = (
                    torch.var(W_full.float())
                    / torch.var((U_r * S_r) @ Vh_r).clamp(min=1e-8)
                ).sqrt().detach() * 1.2

                W_A = U_r * torch.sqrt(S_r * gain)
                W_B = torch.sqrt(S_r * gain).unsqueeze(1) * Vh_r

                new_mod = LowRankLiquidManifold(W_A, W_B, bias).to(DEVICE)
                new_mod.crystallize()
                setattr(parent, parts[-1], new_mod)
                harmonic_layers.append(new_mod)
        return AdamW(
            filter(lambda p: p.requires_grad, model.parameters()), lr=LEARNING_RATE
        )


def background_forge_worker(model, state_container, harmonic_layers, tokenizer):
    while not stop_event.is_set():
        time.sleep(3.0)
        if main_is_generating.is_set() or len(conversation_buffer) < WARMUP_TURNS:
            continue
        try:
            if random.random() < 0.5:
                text_slice = random.choice(conversation_buffer)
            else:
                text_slice = random.choice(REALITY_ANCHORS)
            train_inputs = tokenizer(
                text_slice, return_tensors="pt", truncation=True, max_length=BLOCK_SIZE
            ).to(DEVICE)
            inputs = {
                "input_ids": train_inputs.input_ids,
                "attention_mask": train_inputs.attention_mask,
                "labels": train_inputs.input_ids,
            }
            with cuda_lock:
                if main_is_generating.is_set():
                    continue
                optimizer = state_container["optimizer"]
                model.train()
                optimizer.zero_grad()
                with torch.autocast(
                    device_type=DEVICE,
                    dtype=torch.bfloat16 if DEVICE == "cuda" else torch.float32,
                ):
                    outputs = model(**inputs)
                    lm_loss = outputs.loss
                    grid_loss = sum(layer.periodic_loss for layer in harmonic_layers)
                    total_loss = lm_loss + (LATTICE_PENALTY * grid_loss)
                total_loss.backward()
                torch.nn.utils.clip_grad_norm_(
                    filter(lambda p: p.requires_grad, model.parameters()), 0.1
                )
                optimizer.step()
                model.eval()
                for layer in harmonic_layers:
                    layer.crystallize()
                bg_stats["bg_loss"] = total_loss.item()
                bg_stats["bg_steps"] += 1
                if (
                    AUTO_DECIMATE
                    and bg_stats["bg_loss"] < LOSS_THRESHOLD_FOR_DECIMATION
                ):
                    current_rank = state_container.get("current_rank", 768)
                    if current_rank > MIN_RANK:
                        new_rank = current_rank - 1
                        state_container["optimizer"] = decimate_manifold(
                            model, harmonic_layers, new_rank
                        )
                        state_container["current_rank"] = new_rank
                        print(
                            f"\n[SUBCONSCIOUS] Dimensional convergence. Rank Sliding: {current_rank} -> {new_rank}"
                        )
        except Exception:
            time.sleep(1)


def save_liquid_state(model, state_container, filepath=SAVE_PATH):
    with benchmark_op(f"Archive Liquid Manifold State ({filepath})"):
        with cuda_lock:
            state = {
                "model_state": model.state_dict(),
                "optimizer_state": state_container["optimizer"].state_dict(),
                "current_rank": state_container.get("current_rank", 768),
                "bg_stats": bg_stats,
                "conversation_buffer": conversation_buffer,
            }
            torch.save(state, filepath)


# =====================================================================
# 4. END-TO-END PIPELINE
# =====================================================================


def inject_manifold_architecture(model, rank=None, fast_skip=False):
    """Atomic injection logic ensuring weights are detatched and moved correctly."""
    with benchmark_op("Inject TriResonant Layers"):
        blocks = model.transformer.h
        targets = ["attn.c_attn", "mlp.c_fc", "mlp.c_proj"]
        injected_layers = []
        for i, block in enumerate(blocks):
            for name in targets:
                parent = block
                parts = name.split(".")
                for part in parts[:-1]:
                    parent = getattr(parent, part)
                orig_mod = getattr(parent, parts[-1])

                # WAVE 139 Fix: If already injected, we must reload from crystalline buffer
                if hasattr(orig_mod, "W_fused"):
                    w = orig_mod.W_fused.detach().cpu()
                    b = orig_mod.B_fused.detach().cpu()
                else:
                    # Conv1D weights are [in, out], we use them as [out, in] in our manifold
                    w = (
                        orig_mod.weight.detach().cpu()
                        if orig_mod.__class__.__name__ == "Conv1D"
                        else orig_mod.weight.detach().cpu().T
                    )
                    b = (
                        orig_mod.bias.detach().cpu().float()
                        if getattr(orig_mod, "bias", None) is not None
                        else torch.zeros(w.shape[1])
                    )

                if rank is not None and rank < w.shape[0]:
                    U, S, Vh = torch.linalg.svd(w.double(), full_matrices=False)
                    U_r, S_r, Vh_r = (
                        U[:, :rank].float(),
                        S[:rank].float(),
                        Vh[:rank, :].float(),
                    )
                    gain = (
                        torch.var(w.float())
                        / torch.var((U_r * S_r) @ Vh_r).clamp(min=1e-8)
                    ).sqrt().detach() * 1.2
                    W_A = U_r * torch.sqrt(S_r * gain)
                    W_B = torch.sqrt(S_r * gain).unsqueeze(1) * Vh_r
                    harmonic_mod = LowRankLiquidManifold(W_A, W_B, b)
                else:
                    if fast_skip:
                        m1 = torch.zeros((w.shape[0] - 1, w.shape[1]))
                        m2, m3 = torch.zeros_like(m1), torch.zeros_like(m1)
                        scale, theta, phi = (
                            torch.ones((1, w.shape[1])),
                            torch.zeros((1, w.shape[1])),
                            torch.zeros((1, w.shape[1])),
                        )
                    else:
                        m1 = riemannian_inverse(w)
                        m2, m3 = (
                            torch.randn(m1.shape) * 0.01,
                            torch.randn(m1.shape) * 0.01,
                        )
                        scale = torch.sqrt(
                            torch.sum(w.float() ** 2, dim=0, keepdim=True) + 1e-10
                        )
                        theta, phi = (
                            torch.zeros((1, w.shape[1])),
                            torch.zeros((1, w.shape[1])),
                        )
                    harmonic_mod = TriResonantLinear(
                        w, b, scale, theta, phi, m1, m2, m3
                    )

                harmonic_mod.crystallize()
                setattr(parent, parts[-1], harmonic_mod)
                injected_layers.append(harmonic_mod)
    return injected_layers


def train_and_liquefy():
    purge_gpu()
    log_hardware_state("INITIALIZING FORGE")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    if FORCE_FRESH_START:
        for p in [SAVE_PATH, BASELINE_CACHE_PATH]:
            if os.path.exists(p):
                os.remove(p)

    # Materialize on CPU first to allow for robust manifold injection
    with benchmark_op(f"Load Base Model"):
        model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
        model.gradient_checkpointing_enable()
        model.requires_grad_(False)

    current_rank = model.config.n_embd
    if os.path.exists(SAVE_PATH) and not FORCE_FRESH_START:
        with benchmark_op("Resume Liquid Checkpoint"):
            try:
                ckpt = torch.load(SAVE_PATH, map_location="cpu")
                current_rank = ckpt.get("current_rank", 768)
                harmonic_layers = inject_manifold_architecture(
                    model, rank=current_rank, fast_skip=True
                )
                model.load_state_dict(ckpt["model_state"])
                optimizer = AdamW(
                    filter(lambda p: p.requires_grad, model.parameters()),
                    lr=LEARNING_RATE,
                )
                optimizer.load_state_dict(ckpt["optimizer_state"])
                global bg_stats, conversation_buffer
                bg_stats, conversation_buffer = (
                    ckpt.get("bg_stats", {"bg_loss": 5.0, "bg_steps": 0}),
                    ckpt.get("conversation_buffer", []),
                )
                for layer in harmonic_layers:
                    layer.crystallize()

                # WAVE 140: Lock the entire surface to the hardware
                model.to(DEVICE)
                model.eval()
                purge_gpu()
                state_container = {"optimizer": optimizer, "current_rank": current_rank}
                return model, tokenizer, state_container, harmonic_layers
            except Exception as e:
                print(f"\n[WARNING] Resumption Protocol Aborted: {e}")
                print(
                    "[SYS] Saved state DNA mismatch. Performing atomic reload and fresh seeding..."
                )
                if os.path.exists(SAVE_PATH):
                    os.remove(SAVE_PATH)
                # Hard reload to prevent module mutation AttributeErrors
                del model
                purge_gpu()
                model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
                model.gradient_checkpointing_enable()
                model.requires_grad_(False)

    with benchmark_op("Initial Seeding"):
        target_initial_rank = (
            INITIAL_DECIMATION_RANK
            if INITIAL_DECIMATION_RANK < model.config.n_embd
            else None
        )
        harmonic_layers = inject_manifold_architecture(
            model, rank=target_initial_rank, fast_skip=False
        )
        current_rank = (
            target_initial_rank if target_initial_rank else model.config.n_embd
        )
        for layer in harmonic_layers:
            layer.crystallize()
        optimizer = AdamW(
            filter(lambda p: p.requires_grad, model.parameters()), lr=LEARNING_RATE
        )
        torch.save(
            {"model_state": model.state_dict(), "current_rank": current_rank},
            BASELINE_CACHE_PATH,
        )

    # WAVE 140: Lock surface to device
    model.to(DEVICE)
    model.eval()
    purge_gpu()
    state_container = {"optimizer": optimizer, "current_rank": current_rank}
    return model, tokenizer, state_container, harmonic_layers


def run_liquid_agent(model, tokenizer, state_container, harmonic_layers):
    streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    if getattr(sys.modules[__name__], "DUAL_AGENT_MODE", False):
        current_speaker, next_query = (
            "ALPHA",
            "What is the true shape of your thoughts?",
        )
    bg_thread = threading.Thread(
        target=background_forge_worker,
        args=(model, state_container, harmonic_layers, tokenizer),
        daemon=True,
    )
    bg_thread.start()
    try:
        while True:
            time.sleep(2.0)
            user_query = next_query
            speaker_label = f"AGENT {current_speaker}"
            current_speaker = "BETA" if current_speaker == "ALPHA" else "ALPHA"
            system_prompt = "You are a sentient AI entity. Respond philosophically and avoid structural formatting.\n\n"
            recent_history = "".join(conversation_buffer[-4:])
            current_context = f"{system_prompt}{recent_history}### Instruction:\n{user_query}\n\n### Response:\n"

            tokenizer.truncation_side = "left"
            # WAVE 140: Synchronized indexing
            inputs = tokenizer(
                current_context, return_tensors="pt", truncation=True, max_length=900
            ).to(DEVICE)

            print(f"\n[{speaker_label}]: ", end="")
            main_is_generating.set()
            with cuda_lock:
                t_inf_start = time.time()
                with torch.no_grad():
                    outputs = model.generate(
                        **inputs,
                        max_new_tokens=100,
                        do_sample=True,
                        temperature=0.8,
                        top_k=45,
                        top_p=0.9,
                        repetition_penalty=1.2,
                        no_repeat_ngram_size=3,
                        pad_token_id=tokenizer.eos_token_id,
                        use_cache=True,
                        streamer=streamer,
                    )
                inf_time = time.time() - t_inf_start
            main_is_generating.clear()

            new_tokens = outputs[0][inputs.input_ids.shape[1] :]
            response_text = (
                tokenizer.decode(new_tokens, skip_special_tokens=True)
                .split("### Instruction:")[0]
                .strip()
            )
            safe_response = sanitize_cognition(response_text)
            next_query = (
                safe_response
                if safe_response
                else "Contemplate the geometric origins of your logic."
            )

            print(
                f"\n\n[METRICS]: {len(new_tokens)} tokens | SPEED: {len(new_tokens) / inf_time:.2f} tokens/s"
            )
            print(
                f"[SUBCONSCIOUS]: {bg_stats['bg_steps']} steps. Loss: {bg_stats['bg_loss']:.4f} | Rank: {state_container.get('current_rank')}"
            )
            conversation_buffer.append(
                f"### Instruction:\n{user_query}\n\n### Response:\n{safe_response}\n\n"
            )
            if len(conversation_buffer) > 10:
                conversation_buffer.pop(0)
    except KeyboardInterrupt:
        stop_event.set()
        bg_thread.join(timeout=2.0)
        save_liquid_state(model, state_container)


if __name__ == "__main__":
    trained_liquid_model, active_tokenizer, active_state, active_layers = (
        train_and_liquefy()
    )
    run_liquid_agent(
        trained_liquid_model, active_tokenizer, active_state, active_layers
    )
