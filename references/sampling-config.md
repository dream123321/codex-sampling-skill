# Sampling JSON Reference

Use this reference for `dcbf run CONFIG.json`. Public sampling configs use `init_dataset`, `sampling`, and `training`; the bootstrapper converts them to the internal runtime layout.

## Top-Level Layout

```json
{
  "run_dir": "./workspace",
  "summary": {},
  "init_dataset": {},
  "sampling": {
    "workflow": {},
    "scheduler": {},
    "structure_selection": {},
    "coverage_plot": {}
  },
  "training": {}
}
```

- `run_dir`: generated workspace, relative to the JSON directory unless absolute.
- `summary.enabled`: collect the final summary bundle.
- `summary.output_dir`: summary directory, default `summary_bundle`.
- `init_dataset`: existing dataset or initial-dataset builder settings; see [dataset-builder.md](dataset-builder.md).
- `sampling.workflow`: main NPT/NVT schedule and loop control.
- `sampling.scheduler`: training, LAMMPS, and DFT resources/commands.
- `sampling.structure_selection`: one active DCBF/DAS selection mode.
- `sampling.coverage_plot`: optional post-sampling coverage analysis; see [coverage-pca.md](coverage-pca.md).
- `training`: optional final high-precision SUS2 training.

## Workflow

| Field | Meaning |
|---|---|
| `main_loop_npt` | Outer list creates `main_i`; each inner list contains NPT temperatures in K. `null` disables NPT globally and `[]` skips NPT only at that main index. |
| `main_loop_nvt` | Same structure for NVT. |
| `sleep_time` | Poll/wait interval used by generation orchestration, default 10. |
| `max_gen` | Maximum generation count inside each main-temperature loop, default 10. |
| `output_xyz_name` | Combined sampled dataset name, default `all_sample_data.xyz`. |

Schedule validation:

DCBF always continues the configured main loops automatically. Historical
`workflow.mode` values are silently ignored and are not written to
`dcbf.runtime.json`.

- NPT and NVT cannot both be `null`.
- If both are lists, outer lengths must match and must be non-empty.
- Every inner item must be a list of finite numeric temperatures.
- At one index, NPT and NVT cannot both be `[]`.

Example:

```json
"main_loop_npt": [[200], [], [600]],
"main_loop_nvt": [[], [300], [600]]
```

This creates NPT 200 K, then NVT 300 K, then both ensembles at 600 K.

The schedule selects temperatures only. MD steps, timestep, dump interval, thermostat/barostat, and NPT pressure are defined by the active `init/lmp_in.py` template.

### Recommended New-Case Temperatures

For a new generic dataset-construction case, recommend `100, 200, 300, 400, 500, 600, 700, 800, 900 K`. Ask whether this sequence applies to NPT, NVT, or both; do not choose the ensemble silently. This is a recommendation, not a built-in code default.

### Optional Parameter Menu

When the user chooses default parameters, retain the active example values and do not expand this menu. When the user asks to customize or view parameters, show only:

- MD: NPT/NVT duration, timestep, dump/trajectory interval, pressure, temperature schedule, and the selected standard/PLUMED/MCMD template.
- Selection: DCBF/DAS mode, coverage thresholds, selection budgets, `state_population`, `body_list`, `candidate_trigger`, plateau settings, and `max_gen`.

Read and report current values from the active JSON and `init/lmp_in.py`; do not duplicate a potentially stale default table in the intake response.

## Scheduler

| Field | Meaning |
|---|---|
| `submission_backend` | `bsub`/`lsf` or `sbatch`/`slurm`; aliases normalize to `bsub` or `sbatch`. |
| `train_sus_queue`, `train_sus_cores`, `train_sus_ptile` | Sampling-stage SUS2 training resources. |
| `train_env` | Shell setup before SUS2 training. |
| `sus2_mlp_exe` | `mlp-sus2` executable used for training and descriptors. Prefer the active `runtime/bin/mlp-sus2`. |
| `original_command` | Initial sampling-stage SUS2 training command prefix. |
| `subsequent_command` | Warm-start command prefix for later sampling updates. |
| `lmp_queue`, `lmp_cores`, `lmp_ptile` | SUS2MD/LAMMPS resources. |
| `lmp_env` | Shell setup before LAMMPS. |
| `lmp_exe` | LAMMPS launch command; `$NP` is populated from scheduler resources. |
| `scf_queue`, `scf_cores`, `scf_ptile` | DFT labeling resources. |
| `scf_cal_engine` | `vasp`, `abacus`, `cp2k`, or `qe`. |
| `dft_clean_dcbf_environment` | Clear bundled DCBF MPI/MKL/PLUMED/Python/Conda settings before `dft_env`. Default `false`; enable only when they conflict with the server DFT environment. |
| `dft_env` | DFT environment setup. Do not assume modules are portable across servers. |
| `dft_command` | Complete DFT launch command. |

The rendered scheduler scripts export or derive `NP`, change to the submission directory, then run the configured commands. Validate environment-dependent libraries on a compute node, not only on the login node.

The old `clean_dft_environment` key is rejected. Use `dft_clean_dcbf_environment` only. Keep it `false` unless a compute-node check shows that the bundled environment conflicts with VASP, ABACUS, CP2K, or QE.

## Structure Selection Layout

```json
"structure_selection": {
  "common": {},
  "modes": {
    "mlp_encode_model": {"enabled": true},
    "das_adaptive": {"enabled": false},
    "das_fixed": {"enabled": false}
  },
  "dft": {}
}
```

Exactly one mode should be enabled. Invalid mode counts emit a warning and choose `mlp_encode_model`.

### Common Fields

| Field | Meaning |
|---|---|
| `size` | Repetition applied to sampling seed structures, written as a tuple string such as `"(1, 1, 1)"`. |
| `nvt_lattice_scaling_factor` | Cell scaling factors used for NVT seed variants. |
| `npt_max_cell_volume_filter_factor` | Maximum allowed NPT candidate cell volume divided by its seed volume. Default 1.5; null disables the filter. |
| `mtp_type` | Descriptor/potential family such as `l2k2` or `l2k3`. |

Element ordering is inferred from the initial dataset and sorted by atomic number. Every element present in `stru/` must also exist in the initial dataset.

The NPT cell-volume filter runs after DCBF coverage or DAS ambiguity/MBTR selection and before candidates enter the pool or DFT. It does not affect NVT candidates, raw trajectories, coverage values, selection budgets, plateau tests, or `stru.pkl`. Finite values from 1.1 upward are accepted; smaller numeric values fall back to 1.5 with a warning, and null disables the filter. If an otherwise non-empty selection is completely removed, the generation skips DFT and continues with the current MLIP instead of writing `__end__`.

## DCBF Descriptor Mode

Fields belong under `modes.mlp_encode_model`.

| Field | Meaning |
|---|---|
| `encoding_cores` | Worker/process count for descriptor encoding. Current examples use 4; if omitted, the code fallback remains 2. |
| `dimension_min_cover_workers` | Minimum-cover strategy. Sampling examples use 4; 0 uses the joint solver, 1 is serial per-dimension, positive N limits processes, and -1 uses allocated/visible CPUs. |
| `body_list` | Descriptor families to combine, normally `['two', 'three']`. |
| `dq_width_method` | Histogram method: `Freedman_Diaconis`, `self_input`, `scott`, or `std`. |
| `dq_width` | Explicit interval width used only by `self_input`. |
| `dq_width_factor` | Multiplies FD/Scott width. Larger values produce wider/fewer bins; smaller values produce narrower/more bins. |
| `selection_budget_schedule` | Maximum candidate budget associated with each coverage stage. |
| `coverage_threshold_schedule` | Staged coverage percentages; scalar stages apply to all elements, nested stages may specify per-element thresholds. |
| `coverage_rate_method` | `mean` averages descriptor-dimension coverages; `min` uses the worst dimension. |
| `coverage_calculation_mode` | `per_configuration` evaluates each seed separately; `global` evaluates the combined MD pool. |
| `candidate_trigger` | Minimum accumulated candidate-pool size before DFT and MLIP update. Below it, candidates remain pooled and the current model is reused. |
| `state_population` | Database bins with frequency `<= value` are treated as insufficient/uncovered for two/three-body selection. |
| `report_state_population_zero_baseline` | Also compute/log a diagnostic baseline with `state_population=0`; expensive and verbose, default false. |
| `mean_descriptor_enabled` | Enable mean-descriptor coverage and candidate selection. |
| `mean_descriptor_state_population` | Independent low-population threshold for the mean descriptor. |
| `mean_descriptor_low_coverage_threshold` | In per-configuration mode, below this percentage the mean-descriptor branch keeps the last 20 percent of its ranked budget; default 90. |
| `plateau_generations` | Number of recent generations used for optional plateau convergence; disabled when null. |
| `min_coverage_delta` | Each recent coverage improvement below this value counts toward plateau convergence; disabled when null. |
| `report_per_configuration_details` | Print per-seed coverage and selected counts. |

FD width is `2 * IQR * n^(-1/3) * dq_width_factor`; when IQR is zero, the implementation falls back to a Scott-style standard-deviation width.

For `dimension_min_cover_workers != 0`, DCBF solves descriptor dimensions independently, unions their selected structures, and applies deterministic global reverse pruning. It preserves the required coverage and `state_population` targets, but selected structure identities and counts can differ from the original joint solver.

`state_population` examples:

- `0`: only empty database bins are uncovered.
- `1`: bins containing zero or one local environment are uncovered.
- `2`: bins containing at most two are uncovered.
- `10`: bins containing at most ten are uncovered; this is much stricter and normally increases selection.

For scalar schedules such as thresholds `[99.5, 99.9, 99.95]` and budgets `[20, 15, 10]`:

- coverage below 99.5 uses budget 20
- 99.5 to below 99.9 uses 15
- 99.9 to below 99.95 uses 10
- reaching the final threshold produces no budget from that metric

The final total budget/union logic remains authoritative; changing staged budgets does not bypass later deduplication or candidate-pool handling.

### Per-Configuration Continuation

In `per_configuration` mode, the next `stru.pkl` contains only configurations that have not reached the final hard threshold for every enabled metric:

- mean descriptor, when enabled
- each body in `body_list`

Equal to the threshold counts as reached. A configuration can continue MD even if its current generation contributes no DFT candidate. Conversely, a configuration that produced a candidate can stop MD once all enabled hard thresholds are reached. Plateau convergence remains the existing whole-loop termination mechanism and does not replace this hard per-seed test.

## DAS Modes

### `das_adaptive`

- `mlp_nums`: ensemble model count; DAS requires at least 3.
- `af_default`, `af_limit`, `af_failed`: starting, limiting, and failed ambiguity thresholds.
- `over_fitting_factor`: factor used while adapting the ambiguity threshold.
- `af_adaptive`: optional explicit adaptive value; normally null.
- `ambiguity_histogram_max`, `ambiguity_histogram_bins`: public histogram range/count names.
- `sample.n`, `cluster_threshold_init`, `k`, `clustering_by_ambiguity`: MBTR/Brich clustering and sampling controls.

### `das_fixed`

- `mlp_nums`: ensemble model count.
- `threshold_low`, `threshold_high`: fixed ambiguity acceptance range.
- `select_stru_num`: optional fixed selected count.
- Histogram and `sample` fields have the same role as adaptive DAS.

Do not mix DAS fields into the DCBF descriptor mode.

## DFT Selection Fields

| Field | Meaning |
|---|---|
| `calc_dir_num` | Number of DFT task directories/batches. |
| `force_threshold` | Maximum-force filter in eV/A used when collecting labeled structures. |
| `pending_warning_hours` | Optional warning time for unstarted/uncompleted DFT tasks. `null` disables it. |

## Coverage Plot Block

`sampling.coverage_plot.enabled=true` runs coverage analysis after sampling and before final training. Use [coverage-pca.md](coverage-pca.md) for every supported field. Coverage failures are logged as warnings so the workflow can continue to final training and bundling.

## Final Training Block

| Field | Meaning |
|---|---|
| `enabled` | Run high-precision SUS2 training after sampling. |
| `input_xyz` | Training dataset override; null uses the sampling output. |
| `work_dir` | Output root, default `high_precision_training`. |
| `template_type` | `l2k2`, `l2k3`, `l3k3`, `l4k3`, `l4k4`, or `l4k6`. |
| `r_max` | Optional radial-cutoff override; must be positive. |
| `model_name` | Final potential name, default `trained.mtp`. |
| `elements` | Optional explicit element mapping; otherwise infer from input. |
| `sort_ele` | Sort inferred/provided elements by atomic number. |
| `submit` | Submit through the configured scheduler. |
| `wait` | Wait for completion before prediction/plotting/bundling. |
| `command_prefix` | Complete custom training command prefix; null builds the standard SUS2 command. |
| `max_iter` | Maximum training iterations, default 6000. |

The standard command includes `--do-lin`.

### `training.predict`

- `enabled`, `input_xyz`, `calc_type`, `output_dir`, `output_format`, `suffix`, `device`, `num_workers`, `chunksize`, and `log_level` control post-training prediction.
- Default calculator is `sus2`; default output format is `extxyz`.

### `training.plot`

- `enabled`, `output`, `mlip_name`, `force_mode`, `num_processes`, `keep_temp`, `show_r2`, `save_data`, `stress_unit`, `cmap`, and `skip_structure_indices` control comparison behavior.
- `axis_padding` and `signed_axis_symmetric` control limits.
- `figsize`, `dpi`, `scatter_size`, `bins`, `linewidth`, and font-size fields control appearance.
- The implementation uses `sus2_plot_errors_v3.py`.
