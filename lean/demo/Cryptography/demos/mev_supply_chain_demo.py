"""
MEV Supply Chain Demo
=====================
Demonstrates the formally verified properties of proposer-builder separation:
1. Builder competition dynamics
2. Specialization benefits
3. MEV-Share welfare tradeoff
4. Timing game analysis
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ═══════════════════════════════════════════════════════
# Demo 1: Builder Competition
# ═══════════════════════════════════════════════════════
print("=" * 60)
print("Demo 1: Builder Competition (Theorem 4.1)")
print("=" * 60)

total_mev = 10.0  # ETH

class Builder:
    def __init__(self, name, efficiency, cost):
        self.name = name
        self.efficiency = efficiency
        self.cost = cost
        self.max_bid = efficiency * total_mev - cost
        self.profit_at_bid = lambda bid: efficiency * total_mev - cost - bid

builders = [
    Builder("General A", 0.7, 0.5),
    Builder("General B", 0.75, 0.6),
    Builder("Specialist C", 0.9, 1.0),
    Builder("Efficient D", 0.85, 0.3),
]

print(f"\nTotal MEV: {total_mev} ETH")
print(f"{'Builder':<15} {'Efficiency':>10} {'Cost':>6} {'Max Bid':>9} {'Net Profit':>11}")
print("-" * 55)
for b in builders:
    print(f"{b.name:<15} {b.efficiency:>10.0%} {b.cost:>6.2f} {b.max_bid:>9.2f} {b.max_bid:>11.2f}")

winner = max(builders, key=lambda b: b.max_bid)
print(f"\nWinner: {winner.name} (max bid = {winner.max_bid:.2f} ETH)")
print(f"Formally verified: builder with highest net margin wins")

# ═══════════════════════════════════════════════════════
# Demo 2: Specialization Benefits
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Demo 2: Specialization Benefits (Theorem 4.2)")
print("=" * 60)

base_efficiency = 0.7
specialty_efficiency = 0.95
specialty_fractions = np.linspace(0, 1, 11)

print(f"\nBase efficiency: {base_efficiency:.0%}")
print(f"Specialty efficiency: {specialty_efficiency:.0%}")
print(f"\n{'Specialty Frac':>14} {'General':>9} {'Specialized':>12} {'Improvement':>12}")
print("-" * 50)

for frac in specialty_fractions:
    general = base_efficiency * total_mev
    specialized = (specialty_efficiency * frac * total_mev +
                   base_efficiency * (1 - frac) * total_mev)
    improvement = specialized - general
    print(f"{frac:>14.0%} {general:>9.2f} {specialized:>12.2f} {improvement:>12.2f}")

print(f"\nFormally verified: specialized ≥ general for all fractions")

# ═══════════════════════════════════════════════════════
# Demo 3: MEV-Share Welfare Tradeoff
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Demo 3: MEV-Share Welfare Tradeoff (Theorems 4.4-4.5)")
print("=" * 60)

user_shares = np.linspace(0, 1, 11)
print(f"\n{'User Share':>11} {'User Return':>12} {'Builder Rev':>12}")
print("-" * 38)
for s in user_shares:
    user_return = s * total_mev
    builder_rev = (1 - s) * total_mev
    print(f"{s:>11.0%} {user_return:>12.2f} {builder_rev:>12.2f}")

print(f"\nFormally verified: higher user share → lower builder revenue")

# ═══════════════════════════════════════════════════════
# Demo 4: Timing Game
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Demo 4: Timing Game (Theorem 4.6)")
print("=" * 60)

base_mev = 5.0
growth_rate = 0.01  # ETH per ms
delays = np.linspace(0, 500, 11)  # ms

print(f"\nBase MEV: {base_mev} ETH, Growth rate: {growth_rate} ETH/ms")
print(f"\n{'Delay (ms)':>11} {'Total MEV':>10} {'Reorg Risk':>11} {'Expected Value':>15}")
print("-" * 50)
for d in delays:
    total = base_mev + d * growth_rate
    reorg_risk = min(0.5, d / 2000)  # Simplified risk model
    ev = (1 - reorg_risk) * total
    print(f"{d:>11.0f} {total:>10.2f} {reorg_risk:>11.1%} {ev:>15.2f}")

print(f"\nFormally verified: delay always increases available MEV")

# ═══════════════════════════════════════════════════════
# Generate Plot
# ═══════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Builder bids
ax1 = axes[0, 0]
names = [b.name for b in builders]
max_bids = [b.max_bid for b in builders]
colors = ['#4CAF50' if b == winner else '#2196F3' for b in builders]
ax1.bar(names, max_bids, color=colors)
ax1.set_ylabel('Maximum Bid (ETH)')
ax1.set_title('Builder Competition: Max Bids')
ax1.tick_params(axis='x', rotation=15)

# Plot 2: Specialization
ax2 = axes[0, 1]
general_vals = [base_efficiency * total_mev] * len(specialty_fractions)
specialized_vals = [specialty_efficiency * f * total_mev +
                    base_efficiency * (1-f) * total_mev for f in specialty_fractions]
ax2.plot(specialty_fractions*100, general_vals, 'b--', linewidth=2, label='General')
ax2.plot(specialty_fractions*100, specialized_vals, 'r-', linewidth=2, label='Specialized')
ax2.fill_between(specialty_fractions*100, general_vals, specialized_vals,
                 alpha=0.2, color='green', label='Improvement')
ax2.set_xlabel('Specialty Fraction (%)')
ax2.set_ylabel('Total Capture (ETH)')
ax2.set_title('Specialization is Beneficial (Verified)')
ax2.legend()

# Plot 3: MEV-Share tradeoff
ax3 = axes[1, 0]
shares = np.linspace(0, 1, 100)
ax3.plot(shares*100, shares * total_mev, 'g-', linewidth=2, label='User Return')
ax3.plot(shares*100, (1-shares) * total_mev, 'r-', linewidth=2, label='Builder Revenue')
ax3.axvline(x=50, color='gray', linestyle=':', alpha=0.5)
ax3.set_xlabel('User Share (%)')
ax3.set_ylabel('ETH')
ax3.set_title('MEV-Share Tradeoff (Verified)')
ax3.legend()

# Plot 4: Timing game
ax4 = axes[1, 1]
fine_delays = np.linspace(0, 500, 100)
mev_values = base_mev + fine_delays * growth_rate
reorg_risks = np.minimum(0.5, fine_delays / 2000)
expected_values = (1 - reorg_risks) * mev_values
ax4.plot(fine_delays, mev_values, 'b-', linewidth=2, label='Available MEV')
ax4.plot(fine_delays, expected_values, 'r--', linewidth=2, label='Expected Value')
ax4.set_xlabel('Delay (ms)')
ax4.set_ylabel('ETH')
ax4.set_title('Timing Game: MEV vs Risk')
ax4.legend()

plt.tight_layout()
plt.savefig('/workspace/request-project/Cryptography/demos/mev_supply_chain_plot.png', dpi=150)
print("\n✓ Plot saved to demos/mev_supply_chain_plot.png")
