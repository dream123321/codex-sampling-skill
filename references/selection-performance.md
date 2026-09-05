# Selection Performance And Validation

The current DCBF source includes an optimized structure-selection core. It accelerates:

- descriptor values mapped to histogram intervals
- covered/uncovered value labeling
- greedy minimum-cover selection

The active implementation uses NumPy-based interval lookup and an optional compiled exact backend for integer structure indices. If the compiled extension is unavailable or the input is incompatible, it falls back to the Python implementation.

The optimized joint solver is intended to preserve the original selection result. It does not alter `selection_budget_schedule`, `coverage_threshold_schedule`, `state_population`, or the total-budget truncation.

## Per-Dimension Minimum Cover

Sampling and reduce expose `dimension_min_cover_workers`:

```json
"dimension_min_cover_workers": 4
```

- `0`: original joint minimum cover across elements and descriptor dimensions.
- `1`: serial per-dimension solving.
- Positive `N`: per-dimension solving with at most `N` worker processes.
- `-1`: scheduler-allocated CPUs when detectable, otherwise affinity-visible CPUs.

Sampling examples use `4`; reduce defaults to `-1`. Every nonzero mode unions the per-dimension solutions and applies deterministic global reverse pruning. A structure is removed only while the solver's task requirements remain satisfied. The result may contain different structure identities/counts than the joint solver. Sampling then applies budgets: the final candidate subset need not retain all solver coverage requirements. Sampling's low-population-state detection and candidate-only reduce's multicover targets are distinct.

## Memory-Aware Execution

The current descriptor path builds compact numeric stores and uses memory-mapped data when it does not fit the store's RAM allowance. It can read selected columns/frames without decoding every legacy Python-list pickle; the optional mean representation still uses its dedicated compressed data. Descriptor execution, numeric-store preparation and minimum-cover are separate stages, so an external-encoding completion log does not mean selection is finished.

`dimension_min_cover_workers` is a requested limit. Actual workers are capped by task count, visible/allocated CPUs, and, when the descriptor guard is active, the estimated per-task memory budget. A configured 4 or -1 does not guarantee that many simultaneous workers.

The guard uses process-tree memory and available/cgroup/scheduler information, with an internal 80% available-memory allowance. It publishes `.descriptor_stage.json` and records exceptions in `memory_failure.json` and `__error__`. Generation supervision polls the child, limits in-flight work, and can terminate its owned process group on failure. Do not invent JSON memory settings for these internal controls, and do not identify every -9 exit or failure record as confirmed OOM.

Read the error's stage, input, processed count, requested/effective workers and memory information. Preserve those reports while investigating. This audit did not deliberately exhaust server memory or test every scheduler/cgroup variant.

## Advanced Commands

The commands are hidden from ordinary `dcbf -h` and shown by:

```bash
dcbf -hh
```

Validate result equivalence:

```bash
dcbf calibrate-selection \
  --cases 120 \
  --output benchmark_outputs/selection_calibration.json
```

The report should contain `"passed": true`. A failure means the active backend did not exactly reproduce the legacy min-cover result for at least one randomized case; investigate before trusting a production selection run.

Profile performance:

```bash
dcbf benchmark-selection \
  --output benchmark_outputs/selection_profile.json
```

The report records legacy/current timings, speedups, backend choice, profiles, and correctness checks.

## Debugging Rule

When the user reports that selected structure indices changed:

1. Verify the active deployment with `command -v dcbf` and `python -c 'import dcbf; print(dcbf.__file__)'`.
2. Compare `dimension_min_cover_workers`; use `0` when exact comparison with the original joint strategy is required.
3. For joint-solver regressions, run `calibrate-selection`.
4. Compare effective `parameter.yaml`, descriptor inputs, element order, interval-width settings, and random/input ordering.
5. Only blame the optimized selector after equivalent inputs and solver modes have been established.

Do not substitute benchmark-generated random cases for a scientific regression test. For important workflows, rerun a small fixed real dataset and compare selected indices and output structures.
