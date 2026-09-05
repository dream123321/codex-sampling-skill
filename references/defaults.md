# Defaults, Units, And Precedence

These defaults were verified against the current source and examples on 2026-09-05. Example JSON files and `~/.dcbf/cli_defaults.json` may override them.

## Precedence

- Direct CLI tools: explicit option > saved `~/.dcbf/cli_defaults.json` > built-in default.
- Sampling JSON: explicit field > code default.
- Coverage JSON: explicit `sampling.coverage_plot` field > coverage CLI default; scheduler executable/environment values are used when coverage-specific values are absent.
- Relative config paths normally resolve from the JSON directory. Relative `summary.output_dir` resolves from the parent of `run_dir`; generated workflow intermediates remain under `run_dir`.
- Always inspect `dcbf <command> -h` for the live `current:` CLI values.

## Sampling Defaults

```text
workflow.sleep_time = 10
workflow.max_gen = 10
workflow.output_xyz_name = all_sample_data.xyz

structure_selection common:
  size = (1, 1, 1)
  sort_ele = true
  nvt_lattice_scaling_factor = [1]
  mtp_type = l2k2

mlp_encode_model:
  encoding_cores = 4 in current examples; omitted-field code fallback = 2
  dimension_min_cover_workers = 4
  dq_width_method = Freedman_Diaconis
  dq_width = 0.01
  dq_width_factor = 1.0
  body_list = [two, three]
  selection_budget_schedule = [12, 8, 5]
  coverage_threshold_schedule = [99.5, 99.9, 99.95]
  coverage_rate_method = mean
  selection_budget_scope = per_configuration
  candidate_trigger = 10
  state_population = 0
  mean_descriptor_enabled = false
  mean_descriptor_state_population = 0
  mean_descriptor_low_coverage_threshold = 90.0
  plateau_generations = null
  min_coverage_delta = null
  report_per_configuration_details = true
  report_state_population_zero_baseline = false

dft:
  calc_dir_num = 5
  force_threshold = 20 eV/A
  pending_warning_hours = null

scheduler:
  dft_clean_dcbf_environment = false
```

Scheduler code defaults are queue `33`, cores `40`, and ptile `40` for training, LAMMPS, and SCF, with backend `bsub`. Real configs normally override these values.

`dimension_min_cover_workers=0` uses the original joint solver. `1`, positive `N`, and `-1` use serial per-dimension solving, at most `N` worker processes, and all scheduler-allocated or affinity-visible CPUs respectively. Sampling examples use `4`; every nonzero mode merges per-dimension results and applies deterministic global reverse pruning.

Coverage is always calculated separately for every seed configuration. `selection_budget_scope=per_configuration` gives each seed its own strict staged budget. `all_configurations` keeps per-seed coverage but applies one shared round budget with the existing FWSS selection semantics. The removed `coverage_calculation_mode` field is ignored with a migration warning.

## Reduce Defaults

```text
mode = candidate_only
encoding_cores = 5
xyz_io_mode = fast_extxyz
dimension_min_cover_workers = -1
state_population = 0
chunk_size = 1000000
append_current = true
keep_intermediate = false
output_xyz = dcbf_reduce_sample.xyz
remain_xyz = dcbf_reduce_remain.xyz
work_dir = .dcbf_reduce_work
```

Reduce examples may explicitly raise `encoding_cores` to match their scheduler allocation. This does not change the omitted-field code default of `5`.

## Final Training Defaults

```text
template_type = l2k3
work_dir = high_precision_training
model_name = trained.mtp
max_iter = 6000
submit = true
wait = true
predict.enabled = true
plot.enabled = true
```

The direct `dcbf train` baseline also uses `l2k3` and `max_iter=6000`, but saved CLI defaults can change other values.

## Coverage-PCA Defaults

```text
loop_select = middle-half
main_key = main
query = sus2md_1000.xyz
query_structures = all
out_dir = xyz_pca_coverage_results
body_list = [two, three]
descriptor_workers = 8
coverage_workers = 8
coverage_mode = 2d
coverage_grid = last-loop
pca_fit_source = query
width_factor = null -> 1D uses 1.0 and 2D uses 2.0
max_plot_points = 2000000
dpi = 300
axis_padding = 0.1
lammps_run_mode = scheduler
lammps_timeout_hours = 24
lammps_cores = scheduler.lmp_cores
```

## Dataset Builder Defaults

```text
enabled = false
dataset_mode = generated_only
output_xyz = init_dataset/init_dataset.xyz
report_path = init_dataset/build_report.json
reuse_if_exists = true

random displacement:
  supercell = [1, 1, 1]
  strain = [1.0]
  rattle_count = 0
  rattle_step = 0.005 A

phonon displacement:
  distance = 0.01 A
  include_in_initial_train_set = true

builder MD:
  parallel_workers = 1
  calc_type = nep
  device = cpu
  temperature = 300 K
  pressure = 1.01325 bar
  timestep = 1 fs
  npt_steps = 0
  nvt_steps = 0
  log_interval = 100
  traj_interval = 100
```

## Summary And Low-Disk Storage Defaults

```text
summary.enabled = false in code; current workflow examples set true
summary.output_dir = summary_bundle
runtime training CFG = workspace/.dcbf_runtime/training/train.cfg
training history = <summary>/datasets/training_history/xyz/
raw DFT archives = <summary>/raw_dft/<engine>/...
raw DFT compression = tar.zst, zstd level 19, one thread
```

Training-history shards and raw DFT archives use the resolved summary directory during the workflow. Do not treat `summary.enabled=false` as permission to delete that directory while a run is active. The runtime training CFG is retained after interruption and removed only after full workflow success.

The bundled DFT templates request standard charge density by default: VASP `LCHARG=.TRUE.` with `LAECHG=.FALSE.`, ABACUS `out_chg 1`, QE `disk_io='nowf'`, and CP2K `E_DENSITY_CUBE`. These files increase archive size. Raw DFT manifests record whether charge output was requested and found.

## Units

- Sampling temperature: K.
- LAMMPS `metal` timestep: ps inside `lmp_in.py`; builder ASE MD timestep: fs.
- LAMMPS `metal` pressure: bar. `1 kbar = 1000 bar`; `1 GPa = 10000 bar`.
- Builder `pressure`: bar.
- `force_threshold`: eV/A.
- Relaxation `pressure`: GPa.
- Plot stress unit: `eV` or `GPa` as selected.
- Coverage values and thresholds: percent from 0 to 100.

## Current Names Only

Do not use removed names. Important replacements are:

```text
iw_method / bw_method -> dq_width_method
iw / bw -> dq_width
iw_scale / bw_coff -> dq_width_factor
dynamic_iw -> dynamic_dq_width
coverage_count_threshold -> state_population
coverage_label -> coverage_mode
data_modes -> body_list
clean_dft_environment -> dft_clean_dcbf_environment
```

Sampling no longer accepts public top-level `parameter` or `sampling.parameter`; use `sampling.structure_selection`. Reduce intentionally retains its own top-level `parameter` block.
