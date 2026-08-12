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

Sampling examples use `4`; reduce defaults to `-1`. Every nonzero mode unions the per-dimension solutions and applies deterministic global reverse pruning. A structure is removed only while all original coverage and state-population targets remain satisfied. The result may still contain different structure identities or a different count than the joint solver.

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
