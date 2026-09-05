# Defaults, Units, And Precedence

Source-audited on 2026-09-05. **An omitted-field code default is not the same as a shipped example value.** The example column below refers to `example/sample/dcbf.init_dataset.vasp.test.json`; compare each `sample_json` mode separately before copying it. None of the machine-specific paths or queues in examples is portable by implication.

## Precedence

- Direct CLI tools: explicit option > saved `~/.dcbf/cli_defaults.json` > built-in default.
- Sampling JSON: explicit field > code default.
- Within sampling selection, the active mode overrides common fields, then missing fields receive code defaults. Normalization also forces/ignores some values; see the interface-status table below. Per-generation YAML and cached results can survive a resume, so inspect them alongside the original JSON and `dcbf.runtime.json`.
- Coverage JSON: explicit `sampling.coverage_plot` field > coverage CLI default; scheduler executable/environment values are used when coverage-specific values are absent.
- Relative config paths normally resolve from the JSON directory. Relative `summary.output_dir` resolves from the parent of `run_dir`; generated workflow intermediates remain under `run_dir`.
- Always inspect `dcbf <command> -h` for the live `current:` CLI values.

## Sampling Parameter Matrix

Sources are relative to `$DCBF_ROOT/source/DCBF/dcbf/dcbf`: **B** = `bootstrap.py` defaults/normalization; **C** = `cli.py`; **P** = `encode/coverage_policy.py`; **S** = `encode/mlp_encode_sample_flow.py`; **M** = `encode/mean_select.py`; **H** = `encode/convergence_control.py`; **R** = `runtime_config.py`; **D** = `encode/data_distri.py`. The source index is in [source-audit.md](source-audit.md).

"Result" identifies fields that can change the sampled/labeled structures, rather than only presentation. Resource changes can still affect whether a job completes.

| Full JSON path | Omitted default | Sample value | Meaning / unit / condition | Result; source |
|---|---|---|---|---|
| `sampling.workflow.main_loop_npt` | null; at least one ensemble required | `[[200],[300]]` | Paired main schedule, K; inner [] skips this ensemble | Yes; R/C |
| `sampling.workflow.main_loop_nvt` | null; at least one ensemble required | null | Same NVT schedule rules | Yes; R/C |
| `sampling.workflow.sleep_time` | 10 | 10 | Outer orchestration poll seconds; not every worker/DFT poll interval | Timing; C |
| `sampling.workflow.max_gen` | 10 | 10 | Generations per main, ending at index max_gen-1 | Yes; C |
| `sampling.workflow.output_xyz_name` | all_sample_data.xyz | same | Final combined filename | Output; C |
| `sampling.structure_selection.common.size` | `"(1, 1, 1)"` | same | Sampling seed repetition tuple string | Yes; B/das/mkdir.py |
| `sampling.structure_selection.common.nvt_lattice_scaling_factor` | `[1]` | same | Linear cell factors; only NVT variants | Yes; B/das/mkdir.py |
| `sampling.structure_selection.common.npt_max_cell_volume_filter_factor` | 1.5 | same | NPT selected-frame volume/seed volume; null disables | Yes; npt_volume_filter.py |
| `sampling.structure_selection.common.mtp_type` | l2k2 | same | Sampling potential/descriptor type | Yes; B |
| `sampling.structure_selection.modes.mlp_encode_model.enabled` | mode selection requires modes mapping | true | Exactly one mode intended; bad enabled count falls back with warning | Yes; B |
| `sampling.structure_selection.modes.mlp_encode_model.encoding_cores` | 2 | 4 | External descriptor worker limit, not MD MPI ranks | Resources; B/S |
| `sampling.structure_selection.modes.mlp_encode_model.dimension_min_cover_workers` | 4 | 4 | 0 joint; nonzero per-dimension; -1 allocated/visible CPUs | May change IDs; B/S |
| `sampling.structure_selection.modes.mlp_encode_model.dq_width_method` | Freedman_Diaconis | same | FD, scott, self_input, std histogram rule | Yes; B/D |
| `sampling.structure_selection.modes.mlp_encode_model.dq_width` | 0.01 | same | Proposed width in descriptor units; only self_input | Yes when used; D |
| `sampling.structure_selection.modes.mlp_encode_model.dq_width_factor` | 1.0 | same | Dimensionless FD/Scott width multiplier | Yes when used; D |
| `sampling.structure_selection.modes.mlp_encode_model.body_list` | `[two,three]` | same | Enabled body descriptor groups | Yes; B/S |
| `sampling.structure_selection.modes.mlp_encode_model.selection_budget_schedule` | `[12,8,5]` | same | Candidate budgets paired with coverage stages; not DFT trigger | Yes; P/S |
| `sampling.structure_selection.modes.mlp_encode_model.coverage_threshold_schedule` | `[99.5,99.9,99.95]` | `[99.5,99.9,99.92]` | Percent; scalar or per-element stages | Yes; P/S |
| `sampling.structure_selection.modes.mlp_encode_model.coverage_rate_method` | mean | same | Mean/min across descriptor-component percentages | Yes; encode/coverage_rate.py |
| `sampling.structure_selection.modes.mlp_encode_model.selection_budget_scope` | per_configuration | same | Strict per-seed budget vs all_configurations shared FWSS count | Yes; P/S |
| `sampling.structure_selection.modes.mlp_encode_model.candidate_trigger` | 10 | same | Positive count or percentage of current training CFG frames | Yes; candidate_pool.py |
| `sampling.structure_selection.modes.mlp_encode_model.state_population` | 0 | 2 | Body database frequency <= t is insufficient; local environments | Yes; D/S |
| `sampling.structure_selection.modes.mlp_encode_model.report_state_population_zero_baseline` | false | true | Additional diagnostic t=0 coverage; extra calculation cost | Reporting; S |
| `sampling.structure_selection.modes.mlp_encode_model.mean_descriptor_enabled` | false | same | Enable structure-mean descriptor branch | Yes; M/S |
| `sampling.structure_selection.modes.mlp_encode_model.mean_descriptor_state_population` | 0 | omitted -> 0 | Separate cutoff for structure-mean samples; only if enabled | Yes; M |
| `sampling.structure_selection.modes.mlp_encode_model.mean_descriptor_low_coverage_threshold` | 90.0 | same | Percent; below this use ranked-list tail rule, not MD-time tail | Yes if mean enabled; M |
| `sampling.structure_selection.modes.mlp_encode_model.plateau_generations` | null | 7 | Recent metric entries, >=2; needs min_coverage_delta too | Yes; H |
| `sampling.structure_selection.modes.mlp_encode_model.min_coverage_delta` | null | 0.2 | Percentage-point signed delta; strict less-than plateau test | Yes; H |
| `sampling.structure_selection.modes.mlp_encode_model.report_per_configuration_details` | true | same | Per-seed coverage/count logging; next-seed log is separate | Reporting; S |
| `sampling.structure_selection.dft.calc_dir_num` | 5 | 10 | Number of DFT submission groups, not MPI ranks or total-label cap | Grouping; das/main_calc.py |
| `sampling.structure_selection.dft.force_threshold` | 20 | same | Strict max-force-norm filter, eV/A; minimum-force fallback when no parsed frame passes | Yes; scf_filter_sources.py |
| `sampling.structure_selection.dft.pending_warning_hours` | null | same | Warning after __start__; no abort/retry timeout | Reporting; das/work_dir.py |

Full source-default snapshot for convenient comparison:

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

### Scheduler Fields

All fields below are under `sampling.scheduler`. Brace notation expands to separate full paths (for example `sampling.scheduler.train_sus_cores`). Scheduler allocation is not a substitute for matching MPI ranks in the command string.

| JSON field(s) | Omitted default | Sample value | Meaning / effect / source |
|---|---|---|---|
| `submission_backend` | bsub | bsub | Submission API; lsf/slurm aliases accepted; R |
| `{train_sus,lmp,scf}_queue` | 33 each | 256G56c each | Queue/partition, must be valid on target; R |
| `{train_sus,lmp,scf}_cores` | 40 each | train_sus=56, lmp=56, scf=28 | Allocated tasks, not descriptor workers; R |
| `{train_sus,lmp,scf}_ptile` | 40 each | 56 each | Per-node task layout; R |
| `train_env`, `lmp_env` | empty string | deployment activation | Setup for each engine; machine-specific; R |
| `sus2_mlp_exe` | required by scheduler-spec construction | package runtime executable | External descriptor executable; training prefixes are separate; R |
| `original_command`, `subsequent_command` | required by scheduler-spec construction | inspect current template strings | Initial/warm-start training prefixes; their max-iter is not training.max_iter; R/das/train_mlp.py |
| `lmp_exe` | required by scheduler-spec construction | inspect current template string | Full LAMMPS launch command, usually using $NP; R |
| `scf_cal_engine` | provide explicitly for scheduler-spec construction | vasp | vasp/abacus/cp2k/qe; normalization has abacus env fallback but must not be treated as a complete portable setup; R |
| `dft_clean_dcbf_environment` | false | false | Clean conflicting bundled environment BEFORE dft_env; R |
| `dft_env`, `dft_command` | engine-specific, machine-bound fallback | inspect current init/template | DFT setup and full command; verify with user, never copy server paths blindly; R |

### DAS Fields

Paths in this table start with `sampling.structure_selection.modes.`. Inactive mode blocks in the sample contain example values but are not executed. Defaults come from B; consumers are `generation._select_by_ambiguity`, `das/das_update_ambiguity.py`, and `das/sample_xyz.py`.

| Path suffix | Code default / sample | Meaning and effect |
|---|---|---|
| `das_adaptive.enabled`, `das_fixed.enabled` | false / false | Choose one active mode; do not combine with DCBF |
| `das_adaptive.mlp_nums`, `das_fixed.mlp_nums` | 3 / 3 | Ensemble model count, >=3; changes uncertainty and cost |
| `das_adaptive.af_default` | 0.01 / same | Initial ambiguity threshold, force units eV/A |
| `das_adaptive.af_limit` | 0.2 / same | Adaptive threshold limiting value; can be updated from history |
| `das_adaptive.af_failed` | 0.5 / same | Failed/high-ambiguity boundary |
| `das_adaptive.over_fitting_factor` | 1.1 / same | Adaptive threshold multiplier |
| `das_adaptive.af_adaptive` | null / same | Adaptive state recorded by the workflow, not a guaranteed fixed user override |
| `das_fixed.threshold_low`, `das_fixed.threshold_high` | 0.08, 0.3 / same | Fixed ambiguity acceptance range, eV/A |
| `das_fixed.select_stru_num` | null / same | Selection-count state recorded by the workflow; not a fixed structural budget |
| `{das_adaptive,das_fixed}.ambiguity_histogram_max` | 1 / same | Histogram display range, internal end |
| `{das_adaptive,das_fixed}.ambiguity_histogram_bins` | 6 / same | Histogram bin count, internal num_elements |
| `{das_adaptive,das_fixed}.sample.n` | 5 / same | Clustering sample control; used with k, not a hard DFT budget |
| `{das_adaptive,das_fixed}.sample.k` | 2 / same | Cluster/sample multiplier; clustering called when n*k <= candidate count |
| `{das_adaptive,das_fixed}.sample.cluster_threshold_init` | 0.5 / same | Initial MBTR/Birch clustering threshold |
| `{das_adaptive,das_fixed}.sample.clustering_by_ambiguity` | true / same | Pick higher-ambiguity representatives within selected clusters |

`dimension_min_cover_workers=0` uses the original joint solver. `1`, positive `N`, and `-1` use serial per-dimension solving, at most `N` worker processes, and all scheduler-allocated or affinity-visible CPUs respectively. Sampling examples use `4`; every nonzero mode merges per-dimension results and applies deterministic global reverse pruning.

Coverage is always calculated separately for every seed configuration. `selection_budget_scope=per_configuration` gives each seed its own strict staged budget. `all_configurations` keeps per-seed coverage but applies one shared round budget with the existing FWSS selection semantics. The removed `coverage_calculation_mode` field is ignored with a migration warning.

For exact budget, grid, model-baseline, and plateau behavior, read [selection-logic.md](selection-logic.md). Increasing population strictness does not guarantee a larger budgeted output; candidate_trigger is not a count cap.

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

`training.submit=false` means execute locally, not prepare only. `training.wait=false` does not provide safe asynchronous finalization: model existence is still checked immediately. See the workflow reference before recommending either switch.

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

The audited sample overrides these substantially: builder is enabled, random strain is `[1.05,1.02,1.0,0.98,0.95]`, rattle_count is 10, phonon is disabled, and ASE/NEP MD is enabled with 5 workers, 400 K, 10000 NVT steps, log interval 1000 and trajectory interval 500. These are sample choices, not universal source defaults. The main sampling example uses NPT `[[200],[300]]`; the skill's 100-900 K recommendation is neither this template nor an automatic code default.

## Summary And Low-Disk Storage Defaults

```text
summary.enabled = false in code; current workflow examples set true
summary.output_dir = summary_bundle
runtime training CFG = workspace/.dcbf_runtime/training/train.cfg
training history = <summary>/datasets/training_history/xyz/
raw DFT archives = <summary>/raw_dft/<engine>/...
raw DFT compression = tar.zst, zstd level 19, one thread
```

Training-history shards and raw DFT archives use the resolved summary directory during the workflow. Do not treat `summary.enabled=false` as permission to delete that directory while a run is active. The runtime training CFG normally survives interruption; its deletion occurs at the end of the top-level finalization path, even when optional coverage failed with a warning. This is not an independent verification of all output artifacts.

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

| Interface status | Current sampling behavior |
|---|---|
| Public configurable | Use the fields and nesting above; reduce keeps its separate schema |
| Forced by normalization | sort_ele=true; workflow.output_xyz=true; builder.include_source_structures=false; builder.post_build_action=continue |
| Ignored | workflow.mode; coverage_calculation_mode (warning); dimension_min_cover_global_prune; obsolete init_threshold/threshold_coff removed during YAML writing |
| Rejected | sampling.parameter/top-level parameter; old iw/bw/population keys; report_zero_count_baseline; clean_dft_environment |
| Internal state, not new user switches | parameter.ele, dataset_xyz_input, mlp_MD, end.yaml, selection-count/adaptive records, descriptor-stage and memory-failure records |

`dynamic_dq_width` is a reduce option; do not present it as an effective sampling-grid freeze control. Legacy helper functions may still contain old aliases without making those names valid in a public sampling JSON.

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
