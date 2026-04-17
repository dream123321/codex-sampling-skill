# Parameter Intake

Ask only for blocking inputs. Default everything else from code or the closest packaged example and report those assumptions.

## `ocbf run`

### Blocking questions

- What is the input data source?
  - existing `xyz/extxyz`, or
  - build from `stru` plus `init`
- Which DFT engine?
  - `abacus`, `cp2k`, `qe`, or `vasp`
- Which submission backend?
  - `bsub/lsf` or `sbatch/slurm`
- What queue/partition and how many cores/ptile for:
  - training
  - LAMMPS
  - DFT
- What are the actual DFT environment setup and launch command?
  - `dft_env`
  - `dft_command`
- What is the main loop schedule?
  - `main_loop_npt`, or
  - `main_loop_nvt`

### Usually ask only if the user has not implied them

- Whether `dataset.builder.enabled` should be `true` or `false`
- Whether `training.enabled` should be `true` or `false`
- Whether `summary.enabled` should be `true` or `false`
- Whether they want to start from the packaged example and edit a few fields, instead of building a new config from scratch

### Usually safe to default

- `parameter.*` defaults from `bootstrap.py`
- `sample.*`
- `candidate_trigger`
- `coverage_*`
- `dft.calc_dir_num`
- `dft.force_threshold`
- `training.predict.*`
- `training.plot.*`

## `create-init`

### Blocking questions

- None by default.

### Ask only when needed

- Is the target directory empty enough to avoid collisions?
- Do they want a non-default template source instead of packaged `example/sample`?

## `mp-search`

### Blocking questions

- Which element list?
- What is the Materials Project API key?

### Optional questions

- Override `output_dir`?
- Override `csv_name`?

### Safe defaults

- `output_dir=mp-stru`
- `csv_name=summary.csv`

## `train`

### Blocking questions

- Which input `xyz/extxyz` file?

### Optional questions

- Override `template`?
- Override backend / queue / cores / ptile?
- Override `sus2_exe` or `train_env`?
- Need explicit `elements` ordering?

### Safe defaults

- CLI defaults from `cli_defaults.py`
- Infer `elements` from the input dataset if the user does not care about a manual ordering

## Assumption pattern

When auto-filling fields, summarize them clearly before presenting final commands/config:

- “I used `submission_backend=bsub` because you did not specify a backend.”
- “I kept `training.enabled=false` because you only asked for sampling.”
- “I used default `candidate_trigger=10` and `sample.n=5`.”
