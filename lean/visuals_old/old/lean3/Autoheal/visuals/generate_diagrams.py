#!/usr/bin/env python3
"""
Visual Diagrams for AutoHeal
==============================

Generates ASCII and Matplotlib-based diagrams illustrating the
AutoHeal architecture, data flow, and performance characteristics.

Outputs PNG files to the ``visuals/`` directory.

Dependencies: matplotlib (optional — falls back to ASCII art).

Run::

    python -m autoheal.visuals.generate_diagrams
"""

import os
import sys
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent


def ascii_architecture():
    """Generate ASCII architecture diagram."""
    diagram = r"""
╔══════════════════════════════════════════════════════════════════════╗
║                      AutoHeal Architecture                         ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  ┌────────────────────────────────────────────────────────────┐    ║
║  │                    PARENT APPLICATION                      │    ║
║  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │    ║
║  │  │ Module A │  │ Module B │  │ Module C │  │ Module D │     │    ║
║  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘     │    ║
║  │       │            │            │            │            │    ║
║  │       └────────────┴────────────┴────────────┘            │    ║
║  │                         │                                  │    ║
║  │                    stdout/stderr                           │    ║
║  │                         │                                  │    ║
║  │                    ┌────▼────┐                             │    ║
║  │                    │ LOG FILE │                             │    ║
║  │                    └────┬────┘                             │    ║
║  └─────────────────────────┼──────────────────────────────────┘    ║
║                            │                                       ║
║  ┌─────────────────────────▼──────────────────────────────────┐    ║
║  │                    AUTOHEAL ENGINE                          │    ║
║  │                                                            │    ║
║  │  ┌──────────────┐    ┌───────────────┐    ┌────────────┐  │    ║
║  │  │ TailWatcher  │───▶│ Diagnostician │───▶│ CodeSurgeon│  │    ║
║  │  │ (poll loop)  │    │ (regex + AI)  │    │ (patching) │  │    ║
║  │  └──────────────┘    └───────────────┘    └─────┬──────┘  │    ║
║  │                                                 │          │    ║
║  │                    ┌────────────────┐     ┌─────▼──────┐  │    ║
║  │                    │   HotSwapper   │◀────│  Compiler  │  │    ║
║  │                    │ (in-place swap)│     │(py_compile)│  │    ║
║  │                    └───────┬────────┘     └────────────┘  │    ║
║  │                            │                               │    ║
║  │  ┌─────────────────────────▼───────────────────────────┐  │    ║
║  │  │              ORACLE TEAM (AI Council)                │  │    ║
║  │  │  ┌──────────┐ ┌────────────┐ ┌──────────────┐      │  │    ║
║  │  │  │Researcher│ │Hypothesizer│ │ Experimenter │      │  │    ║
║  │  │  └────┬─────┘ └─────┬──────┘ └──────┬───────┘      │  │    ║
║  │  │       │              │               │               │  │    ║
║  │  │  ┌────▼─────┐ ┌─────▼──────┐ ┌──────▼───────┐      │  │    ║
║  │  │  │Validator │ │  Updater   │ │   Iterator   │      │  │    ║
║  │  │  └──────────┘ └────────────┘ └──────────────┘      │  │    ║
║  │  └─────────────────────────────────────────────────────┘  │    ║
║  └────────────────────────────────────────────────────────────┘    ║
║                            │                                       ║
║                     ┌──────▼──────┐                                ║
║                     │  PATCHED    │  ← hot-swapped back into       ║
║                     │  MODULE     │    the running process         ║
║                     └─────────────┘                                ║
╚══════════════════════════════════════════════════════════════════════╝
"""
    out = OUTPUT_DIR / "architecture.txt"
    out.write_text(diagram)
    print(f"✅ ASCII architecture → {out}")
    return diagram


def ascii_data_flow():
    """Generate data-flow diagram."""
    diagram = r"""
╔══════════════════════════════════════════════════════════════╗
║                 AutoHeal Data Flow                          ║
╠══════════════════════════════════════════════════════════════╣
║                                                             ║
║   ① App writes to log                                      ║
║      │                                                      ║
║      ▼                                                      ║
║   ② TailWatcher detects new lines  (poll every 250ms)      ║
║      │                                                      ║
║      ▼                                                      ║
║   ③ Diagnostician classifies severity                      ║
║      │  DEBUG/INFO → discard                                ║
║      │  WARNING+   → continue                               ║
║      ▼                                                      ║
║   ④ Cooldown check (same file within N seconds?)           ║
║      │  yes → skip                                          ║
║      │  no  → continue                                      ║
║      ▼                                                      ║
║   ⑤ CodeSurgeon generates patch                            ║
║      │  heuristic rules → fast path                         ║
║      │  Oracle / Team   → deep path                         ║
║      ▼                                                      ║
║   ⑥ AST validation gate                                    ║
║      │  invalid → reject, log                               ║
║      │  valid   → continue                                  ║
║      ▼                                                      ║
║   ⑦ Backup original → .autoheal.bak                       ║
║      │                                                      ║
║      ▼                                                      ║
║   ⑧ Write patched source to disk                           ║
║      │                                                      ║
║      ▼                                                      ║
║   ⑨ Compiler: py_compile + importlib.reload()              ║
║      │  fail → rollback from backup                         ║
║      │  ok   → continue                                     ║
║      ▼                                                      ║
║   ⑩ HotSwapper: in-place __code__ replacement              ║
║      │                                                      ║
║      ▼                                                      ║
║   ⑪ Emit HealEvent to registered callbacks                 ║
║      │                                                      ║
║      ▼                                                      ║
║   ⑫ App continues with patched code — no restart needed    ║
║                                                             ║
╚══════════════════════════════════════════════════════════════╝
"""
    out = OUTPUT_DIR / "data_flow.txt"
    out.write_text(diagram)
    print(f"✅ Data flow diagram → {out}")
    return diagram


def ascii_oracle_cycle():
    """Generate oracle team cycle diagram."""
    diagram = r"""
╔══════════════════════════════════════════════════════════════╗
║              Oracle Team — Iterative Repair Cycle           ║
╠══════════════════════════════════════════════════════════════╣
║                                                             ║
║            ┌─────────────────────────────┐                  ║
║            │         RESEARCHER          │                  ║
║            │  • Read source code         │                  ║
║            │  • Analyze error context    │                  ║
║            │  • Produce research brief   │                  ║
║            └────────────┬────────────────┘                  ║
║                         │                                   ║
║                         ▼                                   ║
║            ┌─────────────────────────────┐                  ║
║            │       HYPOTHESIZER          │                  ║
║            │  • Rank root-cause hypoths  │                  ║
║            │  • State evidence needed    │                  ║
║            │  • Define falsification     │                  ║
║            └────────────┬────────────────┘                  ║
║                         │                                   ║
║                         ▼                                   ║
║            ┌─────────────────────────────┐                  ║
║            │       EXPERIMENTER          │                  ║
║            │  • Design minimal diffs     │                  ║
║            │  • Test hypotheses          │                  ║
║            │  • Produce candidate fix    │                  ║
║            └────────────┬────────────────┘                  ║
║                         │                                   ║
║                         ▼                                   ║
║            ┌─────────────────────────────┐                  ║
║            │        VALIDATOR            │                  ║
║            │  • Correctness check        │                  ║
║            │  • Regression analysis      │                  ║
║            │  • Minimality review        │                  ║
║            └────────────┬────────────────┘                  ║
║                         │                                   ║
║                         ▼                                   ║
║            ┌─────────────────────────────┐                  ║
║            │         UPDATER             │                  ║
║            │  • Merge fix into source    │                  ║
║            │  • Update call sites        │                  ║
║            │  • Format consistently      │                  ║
║            └────────────┬────────────────┘                  ║
║                         │                                   ║
║                         ▼                                   ║
║            ┌─────────────────────────────┐                  ║
║            │        ITERATOR             │                  ║
║            │  • Review full cycle        │                  ║
║            │  • CONVERGED → done         │                  ║
║            │  • RETRY → loop back ───────┼──┐              ║
║            └─────────────────────────────┘  │              ║
║                         ▲                    │              ║
║                         └────────────────────┘              ║
║                                                             ║
╚══════════════════════════════════════════════════════════════╝
"""
    out = OUTPUT_DIR / "oracle_cycle.txt"
    out.write_text(diagram)
    print(f"✅ Oracle cycle diagram → {out}")
    return diagram


def try_matplotlib_diagrams():
    """Generate PNG diagrams if matplotlib is available."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        print("ℹ️  matplotlib not installed — skipping PNG generation.")
        return

    # ── Heal pipeline timeline ─────────────────────────────────────
    fig, ax = plt.subplots(figsize=(14, 5))
    stages = [
        ("Log\nDetected", 0.5, "#4CAF50"),
        ("Classified\n(ERROR)", 1.5, "#FF9800"),
        ("Patch\nGenerated", 2.5, "#2196F3"),
        ("AST\nValidated", 3.5, "#9C27B0"),
        ("Compiled", 4.5, "#F44336"),
        ("Hot-\nSwapped", 5.5, "#00BCD4"),
        ("App\nHealed ✓", 6.5, "#4CAF50"),
    ]
    for label, x, color in stages:
        circle = plt.Circle((x, 0.5), 0.35, color=color, alpha=0.85)
        ax.add_patch(circle)
        ax.text(x, 0.5, label, ha="center", va="center", fontsize=8,
                fontweight="bold", color="white")
    for i in range(len(stages) - 1):
        ax.annotate("", xy=(stages[i+1][1] - 0.35, 0.5),
                     xytext=(stages[i][1] + 0.35, 0.5),
                     arrowprops=dict(arrowstyle="->", color="#333", lw=2))

    ax.set_xlim(-0.2, 7.2)
    ax.set_ylim(-0.1, 1.1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("AutoHeal Pipeline — From Error to Live Fix", fontsize=14, pad=20)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "pipeline_timeline.png", dpi=150, bbox_inches="tight")
    print(f"✅ Pipeline timeline → {OUTPUT_DIR / 'pipeline_timeline.png'}")
    plt.close(fig)

    # ── Performance characteristics (simulated) ────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left: Heal latency breakdown
    categories = ["Detect", "Diagnose", "Patch Gen", "AST Check", "Compile", "Swap"]
    times_ms = [250, 15, 800, 5, 120, 2]
    colors = ["#4CAF50", "#FF9800", "#2196F3", "#9C27B0", "#F44336", "#00BCD4"]
    axes[0].barh(categories, times_ms, color=colors)
    axes[0].set_xlabel("Time (ms)")
    axes[0].set_title("Heal Latency Breakdown")
    for i, v in enumerate(times_ms):
        axes[0].text(v + 10, i, f"{v}ms", va="center", fontsize=9)

    # Right: Success rate by error type
    error_types = ["Syntax\nError", "Import\nError", "Type\nError", "Runtime\nError", "Logic\nError"]
    success_rates = [95, 80, 65, 55, 30]
    bar_colors = ["#4CAF50" if r >= 70 else "#FF9800" if r >= 50 else "#F44336" for r in success_rates]
    axes[1].bar(error_types, success_rates, color=bar_colors)
    axes[1].set_ylabel("Success Rate (%)")
    axes[1].set_title("Auto-Heal Success by Error Type")
    axes[1].set_ylim(0, 100)
    for i, v in enumerate(success_rates):
        axes[1].text(i, v + 2, f"{v}%", ha="center", fontsize=10, fontweight="bold")

    fig.suptitle("AutoHeal Performance Characteristics", fontsize=14, y=1.02)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "performance.png", dpi=150, bbox_inches="tight")
    print(f"✅ Performance chart → {OUTPUT_DIR / 'performance.png'}")
    plt.close(fig)


def main():
    print("Generating AutoHeal diagrams...\n")
    ascii_architecture()
    ascii_data_flow()
    ascii_oracle_cycle()
    try_matplotlib_diagrams()
    print("\n✅ All diagrams generated.")


if __name__ == "__main__":
    main()
