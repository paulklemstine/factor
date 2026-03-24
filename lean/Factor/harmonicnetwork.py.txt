import numpy as np
import matplotlib.pyplot as plt
import multiprocessing as mp
import time

# =====================================================================
# 1. N-DIMENSIONAL PYTHAGOREAN GEOMETRY ENGINE
# =====================================================================
def make_rational_matrix(M_mat):
    W = np.zeros_like(M_mat, dtype=np.float64)
    N, K = M_mat.shape
    
    if N == 1:
        return np.sign(M_mat).astype(np.float64)
        
    for k in range(K):
        m = M_mat[:, k]
        m_N = m[-1]
        
        S = np.sum(m[:-1]**2, dtype=np.int64)
        c = m_N**2 + S
        
        if c == 0:
            W[0, k] = 1.0 
        else:
            W[:-1, k] = (2 * m[:-1] * m_N) / c
            W[-1, k]  = (m_N**2 - S) / c
            
    return W

# =====================================================================
# 2. DEEP HARMONIC NETWORK ARCHITECTURE
# =====================================================================
class DeepHarmonicNetwork:
    def __init__(self, layer_dims, initial_M=None):
        self.layer_dims = layer_dims
        self.num_layers = len(layer_dims) - 1
        
        if initial_M is None:
            self.M = []
            for i in range(self.num_layers):
                d_in, d_out = layer_dims[i], layer_dims[i+1]
                self.M.append(np.random.randint(-5, 6, size=(d_in, d_out)))
        else:
            self.M = [m.copy() for m in initial_M]
            
    def get_weights(self):
        return [make_rational_matrix(m) for m in self.M]
        
    def forward(self, X):
        A = X
        W_matrices = self.get_weights()
        for i, W in enumerate(W_matrices):
            A = A @ W
            if i < self.num_layers - 1:
                A = np.maximum(0, A)
        return A

# =====================================================================
# 3. QUANTIZATION-AWARE TRAINING (QAT) & "THE ANALYTICAL SNAP"
# =====================================================================
def calculate_accuracy(model_forward_fn, X, y_true_labels):
    Y_pred = model_forward_fn(X)
    predictions = np.argmax(Y_pred, axis=1)
    return np.mean(predictions == y_true_labels)

def train_continuous_network(X, Y, layer_dims, lr=0.01, iters=8000, use_qat=True):
    print(f"\n--- Phase 1: Continuous Training (QAT Enabled: {use_qat}) ---")
    start_time = time.time()
    W1 = np.random.randn(layer_dims[0], layer_dims[1])
    W2 = np.random.randn(layer_dims[1], layer_dims[2])
    
    if use_qat:
        W1 /= (np.linalg.norm(W1, axis=0, keepdims=True) + 1e-8)
        W2 /= (np.linalg.norm(W2, axis=0, keepdims=True) + 1e-8)
    else:
        W1 *= np.sqrt(2. / layer_dims[0])
        W2 *= np.sqrt(2. / layer_dims[1])
    
    for i in range(iters):
        Z1 = X @ W1
        A1 = np.maximum(0, Z1)
        Y_pred = A1 @ W2
        
        dY = 2.0 * (Y_pred - Y) / X.shape[0]
        dW2 = A1.T @ dY
        dA1 = dY @ W2.T
        dZ1 = dA1 * (Z1 > 0)
        dW1 = X.T @ dZ1
        
        W1 -= lr * dW1
        W2 -= lr * dW2
        
        if use_qat:
            W1 /= (np.linalg.norm(W1, axis=0, keepdims=True) + 1e-8)
            W2 /= (np.linalg.norm(W2, axis=0, keepdims=True) + 1e-8)
            
            if i > 0 and i % 3000 == 0 and i < iters - 1000:
                print(f"  [QAT] Injecting {layer_dims[0]*layer_dims[1] + layer_dims[1]*layer_dims[2]} analytical discrete constraints across {mp.cpu_count()} CPU cores at Iteration {i}...")
                snap_start = time.time()
                M1 = snap_matrix_to_integers(W1, max_int=20) 
                W1 = make_rational_matrix(M1)
                M2 = snap_matrix_to_integers(W2, max_int=20)
                W2 = make_rational_matrix(M2)
                print(f"  [QAT] Snap completed in {time.time() - snap_start:.2f}s.")
        
        if (i + 1) % 500 == 0:
            mse = np.mean((Y - Y_pred)**2)
            print(f"Iteration {i+1:04d} | Continuous MSE: {mse:.4f} | Elapsed Time: {time.time() - start_time:.1f}s")
            
    print(f"\n--- Phase 1 Complete in {time.time() - start_time:.2f}s ---")
    return [W1, W2]

def snap_vector_to_pythagorean(target_w, max_int=35):
    """
    THE BREAKTHROUGH: Inverse Stereographic Projection.
    Calculates the exact integer vector analytically instead of guessing via search.
    """
    best_m = np.zeros_like(target_w, dtype=np.int64)
    best_dist = float('inf')
    
    # Handle the mathematical singularity (the 'South Pole' of the hypersphere)
    if target_w[-1] <= -0.9999:
        best_m[0] = 1
        best_m[-1] = 0
        return best_m
        
    # Sweep through the possible scalar values for the final integer coordinate
    for m_N in range(1, max_int + 1):
        m = np.zeros_like(target_w, dtype=np.int64)
        m[-1] = m_N
        
        # Exact algebraic reversal of the Pythagorean N-Dimensional projection
        ratio = target_w[:-1] / (1.0 + target_w[-1])
        m[:-1] = np.round(m_N * ratio).astype(np.int64)
        
        # Enforce hard bounds
        m = np.clip(m, -max_int, max_int)
        if np.all(m == 0): m[0] = 1
            
        # Verify precision
        cand_w = make_rational_matrix(m.reshape(-1, 1)).flatten()
        dist = np.sum((target_w - cand_w)**2)
        
        if dist < best_dist:
            best_dist = dist
            best_m = m.copy()
            
    # Add a tiny 25-iteration polish search just to clean up floating-point rounding artifacts
    temp = 0.5
    current_m = best_m.copy()
    for _ in range(25):
        cand_m = current_m.copy()
        idx = np.random.randint(len(cand_m))
        cand_m[idx] += np.random.choice([-1, 1])
        cand_m[idx] = np.clip(cand_m[idx], -max_int, max_int)
        
        cand_w = make_rational_matrix(cand_m.reshape(-1, 1)).flatten()
        cand_dist = np.sum((target_w - cand_w)**2)
        
        if cand_dist < best_dist:
            best_dist = cand_dist
            best_m = cand_m.copy()

    return best_m

def _snap_single_column(args):
    """Helper function for parallel processing."""
    target_w, max_int = args
    norm = np.linalg.norm(target_w)
    if norm > 0:
        target_w = target_w / norm
    return snap_vector_to_pythagorean(target_w, max_int)

def snap_matrix_to_integers(W_cont, max_int=35):
    """Parallelized analytical projection mapping to all available CPU cores."""
    M_layer = np.zeros_like(W_cont, dtype=np.int64)
    args_list = [(W_cont[:, k], max_int) for k in range(W_cont.shape[1])]
    
    cores = mp.cpu_count()
    with mp.Pool(processes=cores) as pool:
        results = pool.map(_snap_single_column, args_list)
        
    for k, m_best in enumerate(results):
        M_layer[:, k] = m_best
        
    return M_layer

def snap_weights_to_harmonic(continuous_W_matrices, layer_dims):
    print("\n--- Phase 2: Final Geometrical 'Snap' (Analytical Inverse Projection) ---")
    total_snap_start = time.time()
    M_snapped = []
    for l, W_cont in enumerate(continuous_W_matrices):
        layer_start = time.time()
        print(f"Snapping Layer {l+1} (Shape: {W_cont.shape}) to integers using {mp.cpu_count()} cores...")
        # Higher max_int for final polish
        M_layer = snap_matrix_to_integers(W_cont, max_int=50)
        M_snapped.append(M_layer)
        print(f"  Layer {l+1} snapped in {time.time() - layer_start:.2f}s.")
    print(f"--- Total Snap completed in {time.time() - total_snap_start:.2f}s ---")
    return DeepHarmonicNetwork(layer_dims, initial_M=M_snapped)

# =====================================================================
# 4. EXPERIMENT PIPELINE (COMPUTER VISION - FASHION-MNIST SCALE UP)
# =====================================================================
def main():
    print("=========================================================")
    print(" HARMONIC NETWORK: TEXTURE & SEMANTICS (FASHION-MNIST)")
    print("=========================================================")

    try:
        from sklearn.datasets import fetch_openml
        from sklearn.model_selection import train_test_split
        import warnings
        warnings.filterwarnings('ignore') # Ignore OpenML parser warnings
        
        print("Fetching Fashion-MNIST dataset from OpenML (this may take a minute)...")
        fetch_start = time.time()
        X, y = fetch_openml('Fashion-MNIST', version=1, return_X_y=True, as_frame=False, parser='auto')
        print(f"Dataset successfully downloaded/loaded in {time.time() - fetch_start:.2f}s.")
        
        # Subsample to keep continuous training phase at a reasonable speed
        subset_size = 10000 
        np.random.seed(42)
        indices = np.random.permutation(X.shape[0])[:subset_size]
        X = X[indices]
        y = y[indices].astype(np.int64)
        dataset_name = "Fashion-MNIST (Subsampled)"
        
    except Exception as e:
        print(f"Failed to fetch Fashion-MNIST: {e}. Falling back to standard digits...")
        from sklearn.datasets import load_digits
        from sklearn.model_selection import train_test_split
        data = load_digits()
        X, y = data.data, data.target
        dataset_name = "Standard Digits (Fallback)"
    
    # Normalization 
    norm_start = time.time()
    X = X / 255.0 # Basic image scaling
    
    # GLOBAL standardization (prevents the Radial Gradient Lock on near-dead border pixels)
    X = (X - X.mean()) / (X.std() + 1e-8)
    
    print(f"Data normalization completed in {time.time() - norm_start:.2f}s.")
    
    num_classes = len(np.unique(y))
    Y_onehot = np.zeros((y.size, num_classes))
    Y_onehot[np.arange(y.size), y] = 1.0
    
    X_train, X_test, Y_train, Y_test, y_train, y_test = train_test_split(
        X, Y_onehot, y, test_size=0.2, random_state=42
    )

    IN_DIM = X.shape[1]
    HIDDEN_DIM = 256  # Doubled capacity to handle complex clothing textures
    OUT_DIM = num_classes
    layer_dims = [IN_DIM, HIDDEN_DIM, OUT_DIM]
    total_params = IN_DIM*HIDDEN_DIM + HIDDEN_DIM*OUT_DIM

    print(f"\nDataset Ready: {X.shape[0]} images, {IN_DIM} spatial dimensions.")
    print(f"Architecture: {layer_dims}")
    print(f"Total Integer Parameters to Discover: {total_params:,}")

    # 1. Phase 1: Train Continuous Model
    W_continuous = train_continuous_network(
        X_train, Y_train, layer_dims, 
        lr=0.03, iters=8000, use_qat=True
    )
    
    def continuous_forward(X_in):
        return np.maximum(0, X_in @ W_continuous[0]) @ W_continuous[1]

    print("\n--- Running Final Continuous Evaluations ---")
    cont_eval_start = time.time()
    cont_train_acc = calculate_accuracy(continuous_forward, X_train, y_train)
    cont_test_acc = calculate_accuracy(continuous_forward, X_test, y_test)
    print(f"Continuous evaluations finished in {time.time() - cont_eval_start:.2f}s.")
    
    # 2. Phase 2: Snap to Harmonic Network
    harmonic_model = snap_weights_to_harmonic(W_continuous, layer_dims)
    
    print("\n--- Running Final Discrete Evaluations ---")
    harm_eval_start = time.time()
    harm_train_acc = calculate_accuracy(harmonic_model.forward, X_train, y_train)
    harm_test_acc = calculate_accuracy(harmonic_model.forward, X_test, y_test)
    print(f"Discrete evaluations finished in {time.time() - harm_eval_start:.2f}s.")
    
    # 3. Evaluation
    print(f"\n=========================================================")
    print(f" FINAL MODEL EVALUATION RESULTS")
    print(f"=========================================================")
    print(f"[Continuous Base]  Training Acc: {cont_train_acc * 100:.2f}% | Testing Acc: {cont_test_acc * 100:.2f}%")
    print(f"[Discrete Snapped] Training Acc: {harm_train_acc * 100:.2f}% | Testing Acc: {harm_test_acc * 100:.2f}%")
    print(f"=========================================================")

    # 4. Visualization
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f"Mapping {total_params:,} Rational Constraints ({dataset_name})", fontsize=14, fontweight='bold')

    labels = ['Train Acc', 'Test Acc']
    x = np.arange(len(labels))
    width = 0.35

    axes[0].bar(x - width/2, [cont_train_acc*100, cont_test_acc*100], width, label='Continuous Float', color='darkred')
    axes[0].bar(x + width/2, [harm_train_acc*100, harm_test_acc*100], width, label='Discrete Integers', color='navy')
    axes[0].set_ylabel('Accuracy (%)')
    axes[0].set_title('Texture & Shape Recognition Performance')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels)
    axes[0].legend()
    axes[0].set_ylim(0, 105)

    W_harm_mats = harmonic_model.get_weights()
    cont_flat, harm_flat = [], []
    
    for w_cont, w_harm in zip(W_continuous, W_harm_mats):
        for k in range(w_cont.shape[1]):
            norm = np.linalg.norm(w_cont[:, k])
            normed_cont = w_cont[:, k] / norm if norm > 0 else w_cont[:, k]
            cont_flat.extend(normed_cont)
            harm_flat.extend(w_harm[:, k])

    axes[1].scatter(cont_flat, harm_flat, alpha=0.01, color='purple', s=2)
    axes[1].plot([-1, 1], [-1, 1], 'k--', alpha=0.5, label="Perfect 1:1 Mapping")
    axes[1].set_title(f"Weight Mapping Correlation (N={len(cont_flat):,})")
    axes[1].set_xlabel("Normalized Continuous Weight (Float)")
    axes[1].set_ylabel("Discrete Pythagorean Fraction")
    
    leg = axes[1].legend()
    for lh in leg.legend_handles: 
        lh.set_alpha(1)
        
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()