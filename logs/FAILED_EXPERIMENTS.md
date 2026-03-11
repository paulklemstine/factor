# Graveyard Log: Failed Experiments

## Format
Each entry: hypothesis, benchmark results, technical reason for failure.

---

### Pure Python trial_divide_smart (replaced numpy with Python loop)
- **Hypothesis**: Per-element Python loop avoids numpy dispatch overhead
- **Result**: 10x slower (48d: 89s vs 8.4s)
- **Reason**: Python loop overhead per element far exceeds numpy's vectorized batch dispatch. The numpy approach does one C-level pass over the array.

### DLP (Double Large Prime) with trial division splitting
- **Hypothesis**: DLP cofactor splitting via trial division up to 50000 yields extra relations
- **Result**: 56% of runtime spent in _quick_split, marginal relation gain
- **Reason**: DLP cofactors at 10-15 digits have factors > 50000, so trial division fails. SLP alone provides sufficient relations with the sieve-informed approach.

### DLP re-enabled with Pollard rho (limit=5000)
- **Hypothesis**: Double large prime variation yields 2-3x more relations, speeding up 60d
- **Result**: 57d: 23.7s → 52.3s (2.2x SLOWER). 60d: 80s → 122s FAIL
- **Reason**: Pollard rho cofactor splitting + is_prime checks on every non-smooth candidate overwhelm the benefit. For 60d, 157K DLP candidates processed with 5000-iteration Pollard rho each. BFS cycle-finding rarely yields full relations early in collection. Net: massive overhead, minimal relation gain.

### M value tuning (larger sieve widths)
- **Hypothesis**: Larger M increases smooth yield per polynomial
- **Result**: No measurable improvement, slight regression at some sizes
- **Reason**: Larger M increases sieve time and candidate count proportionally. The extra smooth values don't compensate for the increased per-polynomial cost.
