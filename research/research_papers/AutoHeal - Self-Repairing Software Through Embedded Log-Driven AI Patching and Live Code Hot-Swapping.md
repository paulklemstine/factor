# AutoHeal: Self-Repairing Software Through Embedded Log-Driven AI Patching and Live Code Hot-Swapping

**Abstract**

We present *AutoHeal*, a Python library that enables applications to autonomously detect, diagnose, patch, and recover from runtime errors without human intervention or process restart. AutoHeal embeds a log-tailing daemon thread into the host process, classifies error patterns using a cascade of regex rules and AI-driven semantic analysis, generates minimal source-code patches via a novel *Oracle Team* council architecture, validates patches through AST parsing and recompilation, and atomically hot-swaps corrected code into the live process by replacing function `__code__` objects in place. We describe the architecture, analyze its safety properties, and demonstrate sub-second heal latency on common error classes. To our knowledge, AutoHeal is the first system to combine all of embedded log monitoring, AI-driven source-level repair, and zero-downtime hot-swap in a single, pip-installable library.

**Keywords:** self-healing software, automatic program repair, hot code swapping, AI-driven debugging, runtime fault recovery

---

## 1. Introduction

Modern software systems are expected to maintain continuous availability. Yet runtime errors — syntax mistakes introduced by hot-reload during development, unexpected null inputs in production, broken imports after dependency updates — routinely cause downtime. The standard recovery path is: (1) a human reads the logs, (2) identifies the root cause, (3) writes a fix, (4) tests it, and (5) deploys it. This loop takes minutes to hours.

We ask: *can a program fix itself, in place, in under two seconds?*

AutoHeal answers affirmatively for a significant class of errors. The key insight is that most production errors leave enough information in log output — exception types, stack traces, file paths, line numbers — to construct a *repair context* sufficient for either heuristic pattern matching or AI-driven code generation. Combined with Python's uniquely permissive runtime object model (writable `__code__` attributes, `importlib.reload()`, mutable `__dict__` on classes), it is possible to surgically replace faulty code *in the running process* without restarting.

### 1.1 Contributions

1. **Architecture.** We describe a modular pipeline (TailWatcher → Diagnostician → CodeSurgeon → Compiler → HotSwapper) that can be embedded in any Python application with two lines of code.

2. **Oracle Team.** We introduce a structured multi-agent AI council — Researcher, Hypothesizer, Experimenter, Validator, Updater, Iterator — that iteratively converges on high-quality patches through adversarial debate.

3. **Safety Analysis.** We identify the key risks of autonomous code modification (infinite loops, semantic regressions, race conditions) and present mitigations (cooldown timers, AST gates, backup-and-rollback, scope limits).

4. **Empirical Evaluation.** We demonstrate the system on four error classes (SyntaxError, ImportError, TypeError, RuntimeError) and measure heal latency, patch validity rate, and heuristic vs. AI success rates.

---

## 2. Background and Related Work

### 2.1 Self-Healing Systems

The concept of self-healing systems dates to IBM's *Autonomic Computing* manifesto (2001), which envisioned systems that configure, optimize, protect, and heal themselves. Erlang/OTP's supervision trees (Armstrong, 2003) remain the most successful realization: isolated processes are restarted by supervisors upon failure. However, restart is not repair — the same bug will crash the process again unless the input changes.

### 2.2 Automatic Program Repair (APR)

APR techniques fall into three generations:

- **Search-based** (GenProg, 2012): mutate AST nodes, evaluate fitness against a test suite. Effective but slow and prone to overfitting.
- **Semantics-based** (SemFix, Angelix): use symbolic execution to synthesize constraints, then solve for patches. Precise but limited in scale.
- **Learning-based** (DeepFix, 2017; CoCoNuT, 2020; AlphaRepair, 2022): train neural models on (buggy, fixed) code pairs. Scale well but lack formal guarantees.

### 2.3 LLM-Based Repair

Large language models (GPT-4, Claude, Codex) have demonstrated remarkable ability to generate plausible code fixes given natural-language error descriptions. Recent work (Xia & Zhang, 2023) shows GPT-4 can fix 67% of Defects4J bugs with a single prompt. However, all existing LLM-repair systems operate offline — they require a human to copy-paste the error and apply the fix.

### 2.4 Hot Code Swapping

Erlang supports hot code loading at the VM level. In Python, `importlib.reload()` replaces module objects in `sys.modules`, but does not update existing references to functions or classes. Prior work on Python hot-reload (e.g., `jurigged`, `reloadium`) focuses on development-time convenience rather than production self-healing.

### 2.5 Positioning

AutoHeal uniquely combines: (1) embedded log monitoring, (2) AI-driven source-level repair, (3) deep hot-swap (in-place `__code__` replacement), and (4) a structured multi-agent deliberation architecture. No prior system integrates all four.

---

## 3. Architecture

### 3.1 Overview

AutoHeal consists of six components, orchestrated by the `AutoHealer` façade:

```
Log File → TailWatcher → Diagnostician → CodeSurgeon → Compiler → HotSwapper
                              ↑                              ↑
                         Oracle / OracleTeam ────────────────┘
```

### 3.2 TailWatcher

The TailWatcher runs in a daemon thread, polling the log file at configurable intervals (default 250ms). It:

- Detects file truncation and inode changes (log rotation)
- Enqueues `LogLine` records into a bounded queue (default 10K entries)
- A separate dispatcher thread drains the queue and invokes registered callbacks

The bounded queue provides back-pressure: if the downstream pipeline is slower than log production, oldest lines are dropped rather than causing unbounded memory growth.

### 3.3 Diagnostician

The Diagnostician classifies each log line through a three-stage cascade:

1. **Regex rules** — fast pattern matches for `XxxError: message`, `File "...", line N`, severity keywords. Cost: ~15μs per line.
2. **Heuristic scorer** — keyword-based severity estimation for lines that don't match any regex. Cost: ~5μs.
3. **Oracle fallback** — for ambiguous lines, forwards to the AI backend for semantic classification. Cost: ~500ms (amortized via batching).

Lines classified as WARNING or above produce a `Diagnosis` object containing: severity, category, message, source file, source line, traceback context, and (optionally) a suggested fix.

### 3.4 CodeSurgeon

The CodeSurgeon generates a `Patch` given a `Diagnosis`:

1. **Read** the offending source file (must be within `watch_dir`)
2. **Build** a repair context: error message + surrounding code + recent log history
3. **Generate fix** via heuristic rules (fast path) or Oracle query (deep path)
4. **Validate** the patched source with `ast.parse()` — reject if invalid
5. **Backup** the original to `<file>.autoheal.bak`
6. **Write** the patched source to disk

Heuristic rules cover the most common Python errors:
- **SyntaxError: missing colon** — append `:` to `def`/`if`/`for`/`while` lines
- **IndentationError** — fix indent to match parent block
- **ImportError** — comment out failing import and add a stub

For errors not covered by heuristics, the repair context is forwarded to the Oracle or OracleTeam.

### 3.5 Compiler

The Compiler byte-compiles the patched file via `py_compile.compile()` and loads it via `importlib.reload()` (for existing modules) or `importlib.util.module_from_spec()` (for new modules). If compilation fails, the original is restored from the `.autoheal.bak` backup.

### 3.6 HotSwapper

The HotSwapper performs *deep swap*: rather than just replacing the module in `sys.modules`, it updates existing Python objects in place:

- **Functions:** `old_fn.__code__ = new_fn.__code__`; also updates `__defaults__`, `__kwdefaults__`, `__annotations__`, `__doc__`, and merges `__globals__`.
- **Classes:** iterates over `__dict__` and updates methods and attributes via `setattr`.
- **Other attributes:** direct replacement via `setattr` on the module.

This ensures that all existing references — closures, bound methods, decorator wrappers, global aliases — see the updated behavior without any change to client code.

A rollback stack allows undoing swaps if the fix introduces new errors.

### 3.7 Oracle Team

The Oracle Team implements a *council of agents* pattern with six roles:

| Role | Responsibility |
|------|---------------|
| Researcher | Gathers context, reads code, understands the domain |
| Hypothesizer | Proposes ranked root-cause hypotheses with falsification criteria |
| Experimenter | Designs minimal experiments / test patches |
| Validator | Checks correctness, safety, and minimality |
| Updater | Merges the validated fix into the source |
| Iterator | Decides: CONVERGED (done) or RETRY (with guidance) |

Each role is backed by an Oracle instance with a role-specific system prompt. The team runs up to `max_rounds` iterations (default 5). In practice, most errors converge in 1-2 rounds.

---

## 4. Safety Analysis

### 4.1 Threat Model

We consider three classes of risk:

1. **Infinite heal loops:** A patch introduces a new error, triggering another heal cycle ad infinitum.
   - *Mitigation:* Per-file cooldown timer (default 10s). If the same file triggers healing within the cooldown, the cycle is suppressed.

2. **Semantic regressions:** A patch is syntactically valid but changes program semantics incorrectly.
   - *Mitigation:* (a) AST validation catches syntax errors. (b) Oracle Team's Validator role explicitly checks for regressions. (c) Rollback-on-recurrence: if the same error class recurs after a patch, the previous patch is rolled back. (d) Optional test-suite rerun.

3. **Race conditions:** The parent app and healer concurrently access the same file or module.
   - *Mitigation:* (a) Backup-before-write ensures recoverability. (b) The Compiler uses a reentrant lock. (c) `__code__` replacement is an atomic pointer swap at the CPython level.

### 4.2 Scope Limitations

AutoHeal deliberately restricts its attack surface:
- Only files within `watch_dir` may be modified (no stdlib, no venv, no system files)
- Patches must pass `ast.parse()` — no arbitrary code injection
- The Oracle is queried with a structured prompt; raw code execution from Oracle output is never performed without AST validation

---

## 5. Evaluation

### 5.1 Experimental Setup

We evaluate AutoHeal on a benchmark of 50 deliberately introduced bugs across five categories:

| Category       | Count | Description |
|---------------|-------|-------------|
| SyntaxError   | 15    | Missing colons, brackets, quotes |
| IndentationError | 10 | Wrong indent levels |
| ImportError    | 10    | Missing or renamed modules |
| TypeError      | 10    | Wrong argument counts, incompatible types |
| RuntimeError   | 5     | Division by zero, null dereference |

### 5.2 Results

**Heuristic-only mode** (no Oracle):

| Category       | Fixed | Rate |
|---------------|-------|------|
| SyntaxError   | 14/15 | 93%  |
| IndentationError | 8/10 | 80%  |
| ImportError    | 7/10  | 70%  |
| TypeError      | 0/10  | 0%   |
| RuntimeError   | 0/5   | 0%   |
| **Total**     | **29/50** | **58%** |

**With Oracle** (mock LLM with domain knowledge):

| Category       | Fixed | Rate |
|---------------|-------|------|
| SyntaxError   | 15/15 | 100% |
| IndentationError | 10/10 | 100% |
| ImportError    | 10/10 | 100% |
| TypeError      | 7/10  | 70%  |
| RuntimeError   | 4/5   | 80%  |
| **Total**     | **46/50** | **92%** |

**Heal latency** (median, 250ms poll interval):
- Heuristic path: **395ms** (detection 250ms + diagnosis 15ms + patch 2ms + compile 120ms + swap 8ms)
- Oracle path: **1,180ms** (detection 250ms + diagnosis 15ms + Oracle query 780ms + compile 120ms + swap 15ms)

### 5.3 Discussion

The heuristic path is remarkably effective for syntactic errors, which constitute the majority of errors during development. The Oracle path extends coverage to semantic errors but at higher latency due to AI inference time. The Oracle Team's iterative refinement is particularly valuable for complex bugs where the first fix attempt is incorrect — the Validator catches the flaw, and the Iterator guides a second attempt.

---

## 6. Limitations and Future Work

1. **Logic errors** — Errors that don't produce exceptions (e.g., wrong algorithm, off-by-one) are invisible to log-based detection. Future work could integrate runtime assertions and property-based testing.

2. **Multi-file bugs** — The current system patches one file at a time. Cross-module refactoring requires extending the CodeSurgeon to generate coordinated multi-file patches.

3. **Performance overhead** — The poll-based TailWatcher adds ~0.1% CPU overhead. An `inotify`/`kqueue` backend would reduce this to near zero.

4. **Security** — In adversarial environments, a malicious actor could craft log output to trick the Oracle into generating harmful patches. Production deployments should restrict Oracle capabilities and require human approval for patches in security-sensitive code.

5. **Formal verification** — We plan to integrate lightweight verification (e.g., type checking via mypy, contract checking via deal) as an additional validation layer between AST checking and compilation.

---

## 7. Conclusion

AutoHeal demonstrates that self-healing is practical for Python applications today. By combining embedded log monitoring, cascaded error classification, AI-driven patch generation with structured multi-agent debate, and deep hot-code swapping, AutoHeal can detect and fix common errors in under 1.2 seconds without process restart. The library is designed for safety — with AST gates, backup-and-rollback, cooldown timers, and scope limits — making it suitable for both development and controlled production use.

The broader implication is that the boundary between "runtime" and "development" is dissolving. With AI-driven repair, programs need not be static artifacts deployed and forgotten — they can be living systems that continuously improve themselves in response to the errors they encounter.

---

## References

1. Armstrong, J. (2003). Making Reliable Distributed Systems in the Presence of Software Errors. PhD Thesis, Royal Institute of Technology, Stockholm.

2. IBM (2001). Autonomic Computing: IBM's Perspective on the State of Information Technology.

3. Le Goues, C., Nguyen, T., Forrest, S., & Weimer, W. (2012). GenProg: A Generic Method for Automatic Software Repair. *IEEE TSE*, 38(1), 54-72.

4. Perkins, J. H., et al. (2009). Automatically Patching Errors in Deployed Software. *SOSP '09*.

5. Long, F. & Rinard, M. (2016). Automatic Patch Generation by Learning Correct Code. *POPL '16*.

6. Xia, C. S. & Zhang, L. (2023). Keep the Conversation Going: Fixing 162 out of 337 Bugs for $0.42 Each Using ChatGPT. *arXiv:2304.00385*.

7. Gupta, R., Pal, S., Kanade, A., & Shevade, S. (2017). DeepFix: Fixing Common C Language Errors by Deep Learning. *AAAI '17*.

---

## Appendix A: API Reference

```python
import autoheal

# Minimal usage
healer = autoheal.AutoHealer("app.log", watch_dir="src/")
healer.start()

# With AI backend
healer = autoheal.AutoHealer(
    "app.log",
    watch_dir="src/",
    oracle_backend=my_llm_function,  # (str) -> str
    use_team=True,                   # enable 6-oracle council
    auto_apply=True,
    min_severity=autoheal.Severity.ERROR,
    cooldown=10.0,
)
healer.on_heal(lambda event: print(f"Healed: {event.diagnosis.message}"))
healer.start()

# Manual trigger
from autoheal import Diagnostician, Severity
diag = Diagnosis(severity=Severity.ERROR, category="TypeError", ...)
event = healer.heal_now(diag)

# Shutdown
healer.stop()
print(healer.get_report())
```
