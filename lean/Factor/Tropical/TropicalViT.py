#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    TROPICAL VISION TRANSFORMER (ViT)                        ║
║         Max-Plus Algebra Meets Self-Attention for Image Recognition          ║
║                                                                              ║
║  Version 2.0 — Refactored, Documented, and Improved                          ║
║                                                                              ║
║  Key Innovations:                                                            ║
║    1. All linear layers replaced with tropical (max,+) algebra               ║
║    2. Temperature-smoothed LogSumExp training → exact max-plus inference     ║
║    3. Tropical projective normalization prevents coordinate explosion         ║
║    4. Tropical attention: Q ⊕ Kᵀ scores with max-plus value aggregation     ║
║    5. Learnable logit scaling for gradient-healthy cross-entropy loss         ║
║                                                                              ║
║  Mathematical Foundation:                                                    ║
║    In the tropical semiring 𝕋 = (ℝ ∪ {-∞}, ⊕=max, ⊙=+):                   ║
║      • "Matrix multiply" (A ⊙ x)ᵢ = max_j(Aᵢⱼ + xⱼ)                      ║
║      • LogSumExp(x/T)·T → max(x) as T → 0⁺  (Maslov dequantization)       ║
║      • Projective equivalence: x ~ x + c·1  (tropical projective space)    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server environments
import matplotlib.pyplot as plt
import time
import os
import json
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Tuple, Dict, Any
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TropicalViTConfig:
    """All hyperparameters and settings in one place for reproducibility."""
    # Architecture
    image_size: int = 28
    patch_size: int = 7
    num_patches: int = 16        # (28/7)^2
    patch_dim: int = 49          # 7*7
    d_model: int = 128
    d_ff_multiplier: int = 2     # FFN hidden dim = d_model * this
    num_layers: int = 4
    num_classes: int = 10

    # Training
    epochs: int = 10
    batch_size: int = 128
    learning_rate: float = 5e-3
    weight_decay: float = 1e-2
    grad_clip_norm: float = 1.0
    init_scale: float = 0.05

    # Tropical Annealing Schedule
    T_initial: float = 1.0       # Starting temperature
    T_decay: float = 0.70        # Multiplicative decay per epoch
    T_floor: float = 0.05        # Minimum temperature during training
    tau_init: float = -2.0       # Initial tropical threshold

    # Logit scaling
    logit_scale_init: float = 10.0

    # Infrastructure
    seed: int = 42
    num_workers: int = 0
    pin_memory: bool = True
    compile_model: bool = True
    data_root: str = './data'

    @property
    def d_ff(self) -> int:
        return self.d_model * self.d_ff_multiplier

    @property
    def grid_size(self) -> int:
        return self.image_size // self.patch_size


# ═══════════════════════════════════════════════════════════════════════════════
# TELEMETRY & LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class EpochMetrics:
    """Metrics for a single training epoch."""
    epoch: int
    temperature: float
    loss: float
    accuracy: float
    wall_time_sec: float


@dataclass
class ExperimentLog:
    """Complete experiment record for reproducibility."""
    config: Dict[str, Any] = field(default_factory=dict)
    training_metrics: List[Dict] = field(default_factory=list)
    test_accuracy: float = 0.0
    inference_time_sec: float = 0.0
    throughput_samples_per_sec: float = 0.0
    latency_ms_per_sample: float = 0.0
    total_parameters: int = 0
    device: str = "cpu"

    def save(self, path: str):
        with open(path, 'w') as f:
            json.dump(asdict(self), f, indent=2, default=str)
        print(f"Experiment log saved to {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# DATA PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

def load_mnist(config: TropicalViTConfig) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Load and Z-score normalize MNIST.

    Z-score normalization is particularly meaningful in the tropical context:
    background pixels (value ≈ 0) map to large negative values, which are
    dominated by stroke pixels under max operations — effectively implementing
    automatic feature selection via tropical algebra.

    Returns:
        X_train, X_test: float32 arrays of shape (N, 28, 28), Z-score normalized
        y_train, y_test: int arrays of shape (N,)
    """
    print("━" * 72)
    print("  DATASET TELEMETRY")
    print("━" * 72)
    t0 = time.perf_counter()

    train_set = torchvision.datasets.MNIST(root=config.data_root, train=True, download=True)
    test_set = torchvision.datasets.MNIST(root=config.data_root, train=False, download=True)

    X_train = train_set.data.float().numpy().reshape(-1, 28, 28)
    y_train = train_set.targets.numpy()
    X_test = test_set.data.float().numpy().reshape(-1, 28, 28)
    y_test = test_set.targets.numpy()

    # Z-score normalization (computed on train, applied to both)
    mu = X_train.mean()
    sigma = X_train.std()
    X_train = (X_train - mu) / sigma
    X_test = (X_test - mu) / sigma

    dt = time.perf_counter() - t0
    print(f"  Training samples : {X_train.shape[0]:,}")
    print(f"  Test samples     : {X_test.shape[0]:,}")
    print(f"  Image size       : {X_train.shape[1]}×{X_train.shape[2]}")
    print(f"  Z-score stats    : μ={mu:.2f}, σ={sigma:.2f}")
    print(f"  IO time          : {dt:.4f}s")
    print()

    return X_train, X_test, y_train, y_test


# ═══════════════════════════════════════════════════════════════════════════════
# TROPICAL PRIMITIVES
# ═══════════════════════════════════════════════════════════════════════════════

def tropical_matmul(x: torch.Tensor, W: torch.Tensor,
                    T: Optional[torch.Tensor] = None,
                    training: bool = False) -> torch.Tensor:
    """
    Tropical matrix-vector multiplication: y_i = ⊕_j (W_ij ⊙ x_j) = max_j(W_ij + x_j).

    During training with T > 0, smoothed via LogSumExp (Maslov dequantization):
        y_i = T · log(Σ_j exp((W_ij + x_j) / T))

    As T → 0⁺, this converges to the exact max-plus result.

    Args:
        x: Input tensor, last dim is the feature dim
        W: Weight matrix (out_features, in_features)
        T: Temperature scalar (or None for exact max-plus)
        training: Whether in training mode

    Returns:
        Tropical matrix-vector product
    """
    x_unsq = x.unsqueeze(-2)
    w_shape = [1] * (x.dim() - 1) + list(W.shape)
    w_unsq = W.view(*w_shape)
    sums = x_unsq + w_unsq  # Broadcasting: (..., out, in)

    if training and T is not None:
        return T * torch.logsumexp(sums / T, dim=-1)
    else:
        return torch.max(sums, dim=-1)[0]


class TropicalLinear(nn.Module):
    """
    Tropical affine layer: y = W ⊙_trop x.

    Each output unit computes max_j(W_ij + x_j) — tropical matrix-vector
    multiplication. No bias term is needed because tropical projective
    normalization makes additive constants redundant (they are quotiented
    out in TP^{n-1}).

    Weight initialization uses tight Gaussian (σ=0.05) to ensure all input
    coordinates compete initially, enabling dense gradient flow through the
    LogSumExp smooth approximation.
    """

    def __init__(self, in_features: int, out_features: int, init_scale: float = 0.05):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(out_features, in_features) * init_scale)

    def forward(self, x: torch.Tensor, T: Optional[torch.Tensor] = None) -> torch.Tensor:
        return tropical_matmul(x, self.weight, T, self.training)

    def extra_repr(self) -> str:
        return f"in={self.weight.size(1)}, out={self.weight.size(0)}, algebra=max-plus"


# ═══════════════════════════════════════════════════════════════════════════════
# TROPICAL ATTENTION
# ═══════════════════════════════════════════════════════════════════════════════

class TropicalAttention(nn.Module):
    """
    Tropical self-attention over spatial patches.

    Standard attention:  softmax(QK^T / √d) · V
    Tropical attention:  tropicalized score + value aggregation

    Score computation (Q ⊙ K^T):
        score_{ij} = max_k(Q_{ik} + K_{jk})

    Normalization (tropical softmax):
        score_{ij} ← score_{ij} - max_j(score_{ij})
        This projects scores into tropical projective space, analogous to
        how standard softmax normalizes to a probability simplex.

    Value aggregation:
        out_i = max_j(score_{ij} + V_j)  (tropical weighted sum)
    """

    def __init__(self, d_model: int, init_scale: float = 0.05):
        super().__init__()
        self.q_proj = TropicalLinear(d_model, d_model, init_scale)
        self.k_proj = TropicalLinear(d_model, d_model, init_scale)
        self.v_proj = TropicalLinear(d_model, d_model, init_scale)

    def _trop_reduce(self, tensor: torch.Tensor, dim: int,
                     T: Optional[torch.Tensor], keepdim: bool = False) -> torch.Tensor:
        """Smoothed or exact tropical reduction along a dimension."""
        if self.training and T is not None:
            return T * torch.logsumexp(tensor / T, dim=dim, keepdim=keepdim)
        else:
            return torch.max(tensor, dim=dim, keepdim=keepdim)[0]

    def forward(self, x: torch.Tensor, T: Optional[torch.Tensor] = None) -> torch.Tensor:
        # Project to Q, K, V in tropical algebra
        q = self.q_proj(x, T)          # (B, S, D)
        k = self.k_proj(x, T)          # (B, S, D)
        v = self.v_proj(x, T)          # (B, S, D)

        # Tropical attention scores: max_d(Q_{id} + K_{jd})
        score_sums = q.unsqueeze(2) + k.unsqueeze(1)   # (B, S, S, D)
        scores = self._trop_reduce(score_sums, dim=-1, T=T)  # (B, S, S)

        # Tropical softmax: project to TP^{S-1} per query
        scores_max = self._trop_reduce(scores, dim=-1, T=T, keepdim=True)
        scores = scores - scores_max   # Now max per row ≈ 0

        # Tropical value aggregation: max_j(score_{ij} + V_{jd})
        v_sums = scores.unsqueeze(-1) + v.unsqueeze(1)  # (B, S, S, D)
        return self._trop_reduce(v_sums, dim=2, T=T)    # (B, S, D)


# ═══════════════════════════════════════════════════════════════════════════════
# TRANSFORMER BLOCK
# ═══════════════════════════════════════════════════════════════════════════════

class TropicalTransformerBlock(nn.Module):
    """
    One transformer block, fully tropicalized.

    Architecture:
        x → [projective normalize] → attention → [projective normalize]
          → tropical residual (max) → [projective normalize]
          → FFN (tropical linear + tropical ReLU + tropical linear)
          → [projective normalize] → tropical residual (max) → output

    Key design choices:
        1. Projective normalization before every tropical operation prevents
           unbounded coordinate growth while preserving max-plus geometry.
        2. Residual connections use tropical addition (max), not standard +.
           This is the correct residual for max-plus: max(x, f(x)).
        3. The tropical threshold τ (learnable) acts as a tropical ReLU:
           max(x, τ), silencing coordinates below the noise floor.
    """

    def __init__(self, d_model: int, d_ff: int, init_scale: float = 0.05,
                 tau_init: float = -2.0):
        super().__init__()
        self.attn = TropicalAttention(d_model, init_scale)
        self.ff1 = TropicalLinear(d_model, d_ff, init_scale)
        self.ff2 = TropicalLinear(d_ff, d_model, init_scale)
        self.tau = nn.Parameter(torch.tensor([tau_init]))

    @staticmethod
    def projective_normalize(x: torch.Tensor) -> torch.Tensor:
        """
        Project into tropical projective space TP^{n-1}.

        x ↦ x - max(x)

        This quotients by the tropical scaling equivalence x ~ x + c·1.
        The .detach() on the max prevents autograd from flowing through
        the normalization constant, which would create competing gradients.
        """
        return x - torch.max(x, dim=-1, keepdim=True)[0].detach()

    def _trop_add(self, a: torch.Tensor, b: torch.Tensor,
                  T: Optional[torch.Tensor]) -> torch.Tensor:
        """Tropical addition: a ⊕ b = max(a, b), smoothed during training."""
        if self.training and T is not None:
            return T * torch.logaddexp(a / T, b / T)
        else:
            return torch.maximum(a, b)

    def _trop_relu(self, x: torch.Tensor, T: Optional[torch.Tensor]) -> torch.Tensor:
        """Tropical ReLU: max(x, τ). Gates sub-threshold coordinates."""
        if self.training and T is not None:
            return T * torch.logaddexp(x / T, self.tau / T)
        else:
            return torch.maximum(x, self.tau.expand_as(x))

    def forward(self, x: torch.Tensor, T: Optional[torch.Tensor] = None) -> torch.Tensor:
        # Attention sub-layer with tropical residual
        x_norm = self.projective_normalize(x)
        attn_out = self.projective_normalize(self.attn(x_norm, T))
        x = self._trop_add(x, attn_out, T)

        # Feed-forward sub-layer with tropical residual
        x_norm = self.projective_normalize(x)
        h = self.ff1(x_norm, T)
        h = self._trop_relu(h, T)
        ff_out = self.projective_normalize(self.ff2(h, T))
        x = self._trop_add(x, ff_out, T)

        return x


# ═══════════════════════════════════════════════════════════════════════════════
# TROPICAL VISION TRANSFORMER
# ═══════════════════════════════════════════════════════════════════════════════

class TropicalVisionTransformer(nn.Module):
    """
    A Vision Transformer where every operation is in the tropical semiring.

    Input Processing:
        28×28 image → 16 non-overlapping 7×7 patches → flatten to (16, 49)
        → tropical linear embedding to (16, d_model)
        → add learnable positional encoding

    Backbone:
        num_layers × TropicalTransformerBlock

    Classification Head:
        Tropical global max-pooling over sequence → tropical linear → scale

    The logit_scale parameter expands the output dynamic range. Tropical
    coordinates tend to collapse to a narrow interval after projective
    normalization; scaling them up restores gradient magnitude for
    cross-entropy loss.
    """

    def __init__(self, config: TropicalViTConfig):
        super().__init__()
        self.config = config

        self.embed = TropicalLinear(config.patch_dim, config.d_model, config.init_scale)
        self.pos_encode = nn.Parameter(
            torch.randn(config.num_patches, config.d_model) * config.init_scale
        )

        self.blocks = nn.ModuleList([
            TropicalTransformerBlock(
                config.d_model, config.d_ff,
                config.init_scale, config.tau_init
            )
            for _ in range(config.num_layers)
        ])

        self.head = TropicalLinear(config.d_model, config.num_classes, config.init_scale)
        self.logit_scale = nn.Parameter(torch.tensor(config.logit_scale_init))

    def patchify(self, x: torch.Tensor) -> torch.Tensor:
        """Convert (B, 28, 28) images to (B, 16, 49) patch sequences."""
        B = x.size(0)
        g = self.config.grid_size  # 4
        p = self.config.patch_size # 7
        return x.view(B, g, p, g, p).permute(0, 1, 3, 2, 4).reshape(B, g*g, p*p)

    def forward(self, x: torch.Tensor, T: Optional[torch.Tensor] = None) -> torch.Tensor:
        patches = self.patchify(x)                        # (B, 16, 49)
        x = self.embed(patches, T)                        # (B, 16, D)
        x = x + self.pos_encode.unsqueeze(0)              # Add positional info

        for block in self.blocks:
            x = block(x, T)

        # Tropical global pooling
        if self.training and T is not None:
            pooled = T * torch.logsumexp(x / T, dim=1)   # (B, D)
        else:
            pooled = torch.max(x, dim=1)[0]               # (B, D)

        logits = self.head(pooled, T)                      # (B, num_classes)
        return logits * self.logit_scale

    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


# ═══════════════════════════════════════════════════════════════════════════════
# TRAINING ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def get_temperature(epoch: int, config: TropicalViTConfig) -> float:
    """Tropical annealing schedule: T(e) = max(T_floor, T_initial × decay^e)."""
    return max(config.T_floor, config.T_initial * (config.T_decay ** epoch))


def train(model: nn.Module, X_train: np.ndarray, y_train: np.ndarray,
          config: TropicalViTConfig, log: ExperimentLog) -> torch.device:
    """
    Training loop with tropical temperature annealing.

    The annealing schedule is the key to training tropical networks:
    - At high T: LogSumExp ≈ soft-max, dense gradients, all weights learn
    - At low T: LogSumExp → max, sparse activation, the network "crystallizes"
      into a piecewise-linear tropical function
    - At T=0 (inference): exact max-plus algebra, zero numerical error
    """
    print("━" * 72)
    print("  TRAINING")
    print("━" * 72)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log.device = str(device)
    print(f"  Device: {device}")
    print(f"  Parameters: {model.count_parameters() if hasattr(model, 'count_parameters') else '?':,}")
    print()

    model.to(device)

    dataset = torch.utils.data.TensorDataset(
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.long)
    )
    loader = torch.utils.data.DataLoader(
        dataset, batch_size=config.batch_size, shuffle=True,
        pin_memory=config.pin_memory, num_workers=config.num_workers
    )

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(
        model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay
    )

    t_total_start = time.perf_counter()

    for epoch in range(config.epochs):
        t_epoch_start = time.perf_counter()
        model.train()

        current_T = get_temperature(epoch, config)
        T_tensor = torch.tensor([current_T], dtype=torch.float32, device=device)

        running_loss = 0.0
        correct = 0
        total = 0

        for batch_X, batch_y in loader:
            batch_X = batch_X.to(device, non_blocking=True)
            batch_y = batch_y.to(device, non_blocking=True)

            optimizer.zero_grad()
            logits = model(batch_X, T_tensor)
            loss = criterion(logits, batch_y)
            loss.backward()

            torch.nn.utils.clip_grad_norm_(model.parameters(), config.grad_clip_norm)
            optimizer.step()

            running_loss += loss.item()
            preds = logits.argmax(dim=1)
            correct += (preds == batch_y).sum().item()
            total += batch_y.size(0)

        dt = time.perf_counter() - t_epoch_start
        acc = correct / total
        avg_loss = running_loss / len(loader)

        metrics = EpochMetrics(epoch + 1, current_T, avg_loss, acc, dt)
        log.training_metrics.append(asdict(metrics))

        print(f"  Epoch {epoch+1:02d}/{config.epochs}  "
              f"T={current_T:.4f}  Loss={avg_loss:.4f}  "
              f"Acc={acc:.4f}  Time={dt:.2f}s")

    total_time = time.perf_counter() - t_total_start
    print(f"\n  Total training time: {total_time:.2f}s")
    print()

    return device


# ═══════════════════════════════════════════════════════════════════════════════
# INFERENCE & EVALUATION
# ═══════════════════════════════════════════════════════════════════════════════

@torch.no_grad()
def evaluate(model: nn.Module, X_test: np.ndarray, y_test: np.ndarray,
             device: torch.device, config: TropicalViTConfig,
             log: ExperimentLog) -> np.ndarray:
    """
    Evaluate with exact max-plus inference (T=None → zero temperature).

    At inference time, every LogSumExp becomes an exact max, and every
    logaddexp becomes an exact max. The network is a pure piecewise-linear
    tropical polynomial — no approximation, no softening.
    """
    print("━" * 72)
    print("  INFERENCE BENCHMARK (EXACT MAX-PLUS)")
    print("━" * 72)

    model.eval()
    dataset = torch.utils.data.TensorDataset(
        torch.tensor(X_test, dtype=torch.float32),
        torch.tensor(y_test, dtype=torch.long)
    )
    loader = torch.utils.data.DataLoader(
        dataset, batch_size=256, shuffle=False,
        pin_memory=config.pin_memory, num_workers=config.num_workers
    )

    predictions = []
    t0 = time.perf_counter()

    for batch_X, _ in loader:
        batch_X = batch_X.to(device, non_blocking=True)
        logits = model(batch_X)  # T=None → exact max-plus
        predictions.extend(logits.argmax(dim=1).cpu().numpy())

    predictions = np.array(predictions)
    dt = time.perf_counter() - t0

    accuracy = np.mean(predictions == y_test)
    throughput = len(X_test) / dt
    latency = (dt / len(X_test)) * 1000

    log.test_accuracy = float(accuracy)
    log.inference_time_sec = dt
    log.throughput_samples_per_sec = throughput
    log.latency_ms_per_sample = latency

    print(f"  Test Accuracy : {accuracy * 100:.2f}%")
    print(f"  Total Time    : {dt:.4f}s")
    print(f"  Throughput    : {throughput:.0f} samples/sec")
    print(f"  Latency       : {latency:.4f} ms/sample")
    print()

    return predictions


# ═══════════════════════════════════════════════════════════════════════════════
# VISUALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

def visualize_attention(base_model: TropicalVisionTransformer,
                        X_test: np.ndarray, y_test: np.ndarray,
                        device: torch.device, save_path: str = "tropical_attention.png"):
    """
    Visualize the tropical attention map for a random test sample.

    The attention matrix shows max_d(Q_{id} + K_{jd}) for each pair of
    patches (i, j). High values indicate which key patches each query
    patch attends to most strongly in the max-plus sense.
    """
    print("━" * 72)
    print("  ATTENTION VISUALIZATION")
    print("━" * 72)

    base_model.eval()
    sample_idx = np.random.randint(0, len(X_test))
    sample = torch.tensor(X_test[sample_idx], dtype=torch.float32).unsqueeze(0).to(device)

    with torch.no_grad():
        patches = base_model.patchify(sample)
        embedded = base_model.embed(patches) + base_model.pos_encode.unsqueeze(0)

        # Extract first block's attention scores
        block0 = base_model.blocks[0]
        q = block0.attn.q_proj(embedded)
        k = block0.attn.k_proj(embedded)
        scores = torch.max(q.unsqueeze(2) + k.unsqueeze(1), dim=-1)[0]
        attn_matrix = scores[0].cpu().numpy()

    # Load raw image for display
    raw_test = torchvision.datasets.MNIST(root='./data', train=False, download=False)
    display_img = raw_test.data[sample_idx].numpy()

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))

    axes[0].imshow(display_img, cmap='gray')
    axes[0].set_title(f"Input (Digit {y_test[sample_idx]})", fontsize=13)
    axes[0].axis('off')

    # Overlay patch grid
    for i in range(1, 4):
        axes[0].axhline(y=i*7, color='cyan', linewidth=0.5, alpha=0.5)
        axes[0].axvline(x=i*7, color='cyan', linewidth=0.5, alpha=0.5)

    im = axes[1].imshow(attn_matrix, cmap='plasma', aspect='equal')
    axes[1].set_title("Tropical Attention (Block 0)", fontsize=13)
    axes[1].set_xlabel("Key Patch")
    axes[1].set_ylabel("Query Patch")
    plt.colorbar(im, ax=axes[1], shrink=0.8)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"  Saved to {save_path}")
    print()


def plot_training_curves(log: ExperimentLog, save_path: str = "training_curves.png"):
    """Plot loss, accuracy, and temperature curves."""
    metrics = log.training_metrics
    epochs = [m['epoch'] for m in metrics]
    losses = [m['loss'] for m in metrics]
    accs = [m['accuracy'] for m in metrics]
    temps = [m['temperature'] for m in metrics]

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4))

    ax1.plot(epochs, losses, 'b-o', markersize=4)
    ax1.set_title("Training Loss")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Cross-Entropy Loss")
    ax1.grid(True, alpha=0.3)

    ax2.plot(epochs, accs, 'g-o', markersize=4)
    ax2.set_title("Training Accuracy")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Accuracy")
    ax2.set_ylim(0, 1.05)
    ax2.grid(True, alpha=0.3)

    ax3.plot(epochs, temps, 'r-o', markersize=4)
    ax3.set_title("Temperature Annealing")
    ax3.set_xlabel("Epoch")
    ax3.set_ylabel("T")
    ax3.set_yscale('log')
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"  Training curves saved to {save_path}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║          TROPICAL VISION TRANSFORMER — EXPERIMENT              ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

    config = TropicalViTConfig()
    log = ExperimentLog(config=asdict(config))

    # Reproducibility
    torch.manual_seed(config.seed)
    np.random.seed(config.seed)
    torch.set_float32_matmul_precision('high')

    # Data
    X_train, X_test, y_train, y_test = load_mnist(config)

    # Model
    print("━" * 72)
    print("  MODEL ASSEMBLY")
    print("━" * 72)
    base_model = TropicalVisionTransformer(config)
    log.total_parameters = base_model.count_parameters()
    print(f"  Architecture    : Tropical ViT")
    print(f"  Layers          : {config.num_layers}")
    print(f"  d_model         : {config.d_model}")
    print(f"  d_ff            : {config.d_ff}")
    print(f"  Parameters      : {log.total_parameters:,}")
    print()

    if config.compile_model and hasattr(torch, 'compile'):
        print("  Compiling with torch.compile()...")
        model = torch.compile(base_model)
    else:
        model = base_model

    # Train
    device = train(model, X_train, y_train, config, log)

    # Evaluate
    predictions = evaluate(model, X_test, y_test, device, config, log)

    # Visualize
    try:
        visualize_attention(base_model, X_test, y_test, device)
        plot_training_curves(log)
    except Exception as e:
        print(f"  Visualization skipped: {e}")

    # Save experiment
    log.save("experiment_log.json")

    print("━" * 72)
    print("  EXPERIMENT COMPLETE")
    print(f"  Final Test Accuracy: {log.test_accuracy * 100:.2f}%")
    print("━" * 72)


if __name__ == "__main__":
    main()
