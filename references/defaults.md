# Defaults

This file records current code-derived defaults that are safe to reuse when the user does not override them.

## `ocbf run` parameter defaults

Source: `bootstrap.py`

- `mlp_nums=3`
- `size="(1, 1, 1)"`
- `sort_ele=true`
- `nvt_lattice_scaling_factor=[1]`
- `das_ambiguity=true`
- `af_default=0.01`
- `af_limit=0.2`
- `af_failed=0.5`
- `over_fitting_factor=1.1`
- `af_adaptive=null`
- `threshold_low=0.08`
- `threshold_high=0.3`
- `select_stru_num=null`
- `end=1`
- `num_elements=6`
- `sample.n=5`
- `sample.cluster_threshold_init=0.5`
- `sample.k=2`
- `sample.clustering_by_ambiguity=true`
- `mlp_encode_model=true`
- `encoding_cores=2`
- `iw_method=Freedman_Diaconis`
- `iw=0.01`
- `iw_scale=1.0`
- `body_list=["two","three"]`
- `mtp_type=l2k2`
- `selection_budget_schedule=[20,15,10]`
- `coverage_threshold_schedule=[99.5,99.9,99.95]`
- `coverage_rate_method=mean`
- `candidate_trigger=10`
- `plateau_generations=null`
- `min_coverage_delta=null`
- `coverage_calculation_mode=per_configuration`
- `report_per_configuration_details=true`
- `dft.calc_dir_num=5`
- `dft.force_threshold=20`
- `dft.pending_warning_hours=null`

## Scheduler normalization behavior

Source: `runtime_config.py`

- `train_env` defaults to empty string if missing.
- `lmp_env` defaults to empty string if missing.
- `scf_cal_engine` falls back to `abacus` if missing.
- `submission_backend` aliases:
  - `lsf -> bsub`
  - `slurm -> sbatch`
- If no backend can be inferred, fallback backend is `bsub`.

### Engine default DFT settings

- `abacus`
  - `dft_env=module load compiler/2022.1.0 mpi/2021.6.0 mkl/2022.2.0`
    `export PATH=/work/phy-huangj/apps/il/abacus/3.6.5/bin:$PATH`
  - `dft_command=mpirun -n 40 abacus`
- `cp2k`
  - `dft_env=module purge`
    `module load cp2k/2024.1_oneapi-e5`
  - `dft_command=mpirun -n 40 cp2k.popt -i cp2k.inp`
- `qe`
  - `dft_env=module load compiler/2022.1.0 mpi/2021.6.0 mkl/2022.2.0`
    `export PATH=/work/phy-huangj/apps/qe/7.5/build-intel/bin:$PATH`
  - `dft_command=mpirun -n 40 pw.x -in qe.in`
- `vasp`
  - `dft_env=export PATH=/work/phy-huangj/app/vasp.5.4.4/bin:$PATH`
  - `dft_command=mpirun -n 40 vasp_std`

### SchedulerSpec numeric defaults

Used by `build_scheduler_spec` before merging user config:

- `train_sus_queue=33`
- `train_sus_cores=40`
- `train_sus_ptile=40`
- `lmp_queue=33`
- `lmp_cores=40`
- `lmp_ptile=40`
- `scf_queue=33`
- `scf_cores=40`
- `scf_ptile=40`
- `submission_backend=bsub`

## CLI persistent defaults

Source: `cli_defaults.py`

### `ocbf train`

- `template=l2k3`
- `min_dist=null`
- `max_dist=null`
- `radial_basis_size=null`
- `backend=bsub`
- `queue=33`
- `cores=40`
- `ptile=40`
- `max_iter=3000`
- `sus2_exe=/work/phy-huangj/app/SUS2-MLIP/bin/mlp-sus2`
- `train_env=null`
- `work_dir=null`
- `submit=false`
- `elements=null`
- `keep_order=false`

### `ocbf mp-search`

- `api_key=null`
- `output_dir=mp-stru`
- `csv_name=summary.csv`

## Post-sampling training defaults

Source: `high_precision_training.py`

- `enabled=false`
- `input_xyz=null`
- `work_dir=high_precision_training`
- `template_type=l2k3`
- `model_name=trained.mtp`
- `elements=null`
- `sort_ele=true`
- `r_max=null`
- `submit=true`
- `wait=true`
- `command_prefix=null`
- `max_iter=2000`

### `training.predict`

- `enabled=true`
- `input_xyz=null`
- `calc_type=sus2`
- `output_dir=prediction`
- `output_format=extxyz`
- `suffix=pred`
- `device=cpu`
- `num_workers=1`
- `chunksize=1`
- `log_level=INFO`

### `training.plot`

- `enabled=true`
- `output=sus2_errors.jpg`
- `mlip_name=SUS2`
- `force_mode=magnitude`
- `num_processes=8`
- `keep_temp=false`
- `show_r2=true`
- `save_data=false`
- `fontsize=30`
- `tick_labelsize=30`
- `legend_fontsize=20`
- `title_fontsize=32`
- `annotation_fontsize=20`
- `cbar_fontsize=28`
- `cbar_tick_size=22`
- `linewidth=4`
- `scatter_size=10`
- `bins=120`
- `dpi=300`
- `figsize=[30,10]`
