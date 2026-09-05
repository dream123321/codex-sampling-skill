# Descriptor Selection Logic

Use this reference to explain why structures were selected or retained for MD. This describes the active sampling code audited on 2026-09-05, not the independent PCA visualization or all reduce branches.

## What Is Counted

- Two/three-body descriptors: one row per atomic local environment, separated by central element. Each descriptor dimension has its own histogram.
- Mean descriptor: one row per structure, obtained by averaging selected descriptor components across atoms. The extraction selects the supported two-, three-, and four-body component indices for the mean representation; it is not simply the two-body coverage averaged over elements. Its stored outer list has one group.
- `state_population` is the database histogram's local-environment count cutoff for body descriptors. `mean_descriptor_state_population` is separate and counts structure-mean samples.
- Sampling coverage uses original descriptor components, **not PCA coordinates**. `coverage-pca` is a post-processing tool with separate grids, widths and display rules.

## Database Histogram And Boundaries

For each element/component, `data_base_distribution` derives a bin count from the database descriptor range:

```text
FD proposed width = 2 * IQR * N^(-1/3) * dq_width_factor
bin_count = max(1, ceil(database_range / proposed_width))
actual edges = numpy.histogram(database_values, bins=bin_count)
```

The histogram rescales equal-width bins over its chosen range: the actual spacing need not exactly equal the proposed FD width. Zero IQR falls back to Scott-style standard-deviation width; constant/very small data use one bin. `self_input` uses `dq_width` to obtain the bin count; `scott` uses its standard-deviation formula; `std` uses standard deviation divided by ten. The multiplier is used by FD/Scott, not every method.

Database bins with `frequency <= state_population` are insufficient. Values outside the database range also count as uncovered. Thus 0 excludes empty bins; 1 excludes bins with at most one sample; 2 and 10 exclude bins with at most two and ten samples. This is not the candidate-only reduce multicover target.

For selection classes outside the database range, `freq_intervals_stru_cluster` uses the database's effective width to build intervals across the MD range, keeps their out-of-range portions, and combines them with insufficient database intervals. Do not replace this with an assumed infinite fixed lattice anchored at the database minimum. Interval-edge behavior must be compared against `selection_core.label_covered_values` and the actual grouping helper, not a newly invented formula.

## Coverage Aggregation

For a component, coverage is the percentage of MD descriptor **sample values** labeled covered. For an element/body, `coverage_rate_method=mean` averages its component percentages and `min` takes the lowest component percentage. It is not the fraction of unique occupied bins.

The grouping stage combines all trajectory frame-index ranges belonging to the same seed, including its ensembles/temperatures/scales. Coverage is always calculated per seed; `selection_budget_scope` only changes budgeting. Missing element rows produce the default 100 entry, so a 100 value alone does not prove that element was sampled.

Across enabled bodies and seeds, threshold/budget aggregation generally takes element-wise minima. Nested threshold schedules retain per-element hard targets for body gating and seed continuation. Mean thresholds use the maximum element threshold at each stage. Whole-main convergence reduces to the minimum body metric against the maximum scheduled threshold; it is not identical to every per-element hard comparison when thresholds differ by element.

The model used for coverage can differ from the model used to construct candidate classes when `main>0 AND gen>0`; see [sampling-workflow.md](sampling-workflow.md).

## Mean-Descriptor Candidates

For each seed:

1. Construct classes of structure indices visiting current-model insufficient/out-of-range mean states.
2. Compute the seed's coverage using the applicable coverage model. If it reaches the final mean target, do not generate mean candidates.
3. Solve minimum cover jointly or per dimension, then rank the solution by its contribution counts through FWSS.
4. Determine the staged mean budget. If coverage is below `mean_descriptor_low_coverage_threshold`, select the **tail of this ranked minimum-cover list**.
5. Otherwise use the existing FWSS/short-solution path. Merge seeds' selected indices; whole mean-metric convergence can empty this result.

For a nonempty ranked list of length `L`, the tail branch uses:

```text
keep = min(L, ceil(0.2 * L), max(1, int(mean_budget)))
selected = ranked_list[-keep:]
```

For `L=13` and budget 5, keep the last 3 ranked structures, not 1 (=20% of budget), and not the last 20% of chronological MD frames. Equality to the low-coverage cutoff uses the normal branch. Final strict budgeting may still remove these provisional candidates, including when the final budget is zero.

The low-coverage rule is applied per seed in the current mean branch under both budget scopes. The merged `all_configurations` path passes `apply_low_coverage_rule=False` to avoid applying it again. It does not truncate two/three-body candidates by 20%.

## Body Candidates And Minimum Cover

For each seed/body, build classes from current-model descriptor values. Compare that seed's element coverage against its final per-element targets and disable the classes of elements already at target. Find representative structure indices from the remaining classes.

- Joint mode (`dimension_min_cover_workers=0`) uses the ordinary greedy cover solver.
- Nonzero modes solve element/component tasks independently, union the solutions, then reverse-prune redundant structures globally while retaining the task requirements. With per-configuration budgets, task keys include the seed; with shared budgets, corresponding tasks can be merged across seeds.
- Sampling's class-cover requirement is representation of the insufficient states, not a guarantee that the newly selected batch fills each state above `state_population`. Candidate-only reduce separately constructs population targets for multicover.
- Greedy/reverse-pruned results are approximations, not proof of the globally smallest structural subset. Different solver modes may select different IDs/counts.

See [selection-performance.md](selection-performance.md) for allocation/memory worker limits and backend validation.

## Budgets Are Applied After Candidate Discovery

`determine_structure_budget` uses the first stage at which any relevant element coverage is below its threshold. Equal-to-threshold moves to the next stage; reaching every final element target gives zero budget.

| Scope | Final merge and truncation |
|---|---|
| `per_configuration` | Each seed gets the maximum of its mean/body staged budgets. Mean candidates come first, then ranked AEE candidates not already present. Stable deduplication followed by `[:budget]` makes the cap strict per seed. The round total can exceed one seed's budget. |
| `all_configurations` | Worst per-seed coverage determines one shared budget. Existing FWSS chooses a high-frequency prefix plus strided samples; it is an approximate count and can exceed the requested number. |

Do not claim a strict shared cap where FWSS has no final slice. Do not claim that minimum-cover population/coverage guarantees survive this later budget truncation. Subsequent convergence, NPT volume filtering, DFT success and force filtering can further reduce the output.

## Seeds, Logging, And Termination

`_next_md_configurations` checks every enabled mean/body hard metric for each seed. Only seeds failing at least one are written to `stru.pkl`; equality passes, missing/malformed coverage is not a hard pass. This is independent of either budget scope and does not use candidate-source membership.

The script writes `stru.pkl` and logs provisional selected counts **before** whole-main convergence can empty the selection and before NPT volume filtering. For final DFT-candidate counts, inspect the actual `N_sample_filter.xyz`, filter report, and candidate-pool log.

`evaluate_metric_convergence` tests hard coverage OR plateau. Plateau needs both parameters and at least `plateau_generations>=2` history entries. It takes the last N metric entries and tests all N-1 signed differences with strict `< min_coverage_delta`; it does not take absolute values, require nonnegative improvement, or independently ensure consecutive generation numbers. Decreasing coverage can satisfy it.

Overall DCBF convergence requires the body metric and enabled mean metric each to converge; disabled mean is treated as converged. Zero candidates then normally cause `__end__`, but zero can also arise without this convergence test. Consult the workflow state table instead of interpreting every zero selection as a successful hard-coverage proof.

## Keep The Three Population Meanings Separate

| Operation | Meaning of `state_population=t` |
|---|---|
| Sampling body coverage/selection | Database frequency `<=t` is insufficient; choose representatives subject to gating and budgets |
| Reference-guided reduce | Reference frequency `<=t` identifies insufficient states; select candidates using the staged reference logic |
| Candidate-only self-reduce | For t=0/1 retain one contribution per occupied state; for t>1 target `min(original frequency,t)` local-environment contributions |

For candidate-only self-reduce, one structure can contribute multiple local environments to one state. None of these meanings is simply "keep t different structures per bin". A higher t need not produce a strictly larger final selected set in budgeted sampling.
