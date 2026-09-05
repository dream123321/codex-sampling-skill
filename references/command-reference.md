# Direct Command Reference

Use live help for exact saved `current:` values:

```bash
dcbf -h
dcbf -hh
dcbf COMMAND -h
```

For `train`, `relax`, `efs-distri`, `predict-xyz`, `plot-errors`, and `mp-search`, `dcbf COMMAND set key=value ...` writes user defaults to `~/.dcbf/cli_defaults.json`.

## `dcbf train DATA.xyz`

Creates one SUS2 training workspace from xyz/extxyz.

- `--template`: `l2k2`, `l2k3`, `l3k3`, `l4k3`, `l4k4`, or `l4k6`; default `l2k3`.
- `--min-dist`, `--max-dist`, `--radial-basis-size`: template overrides.
- `--backend`: `bsub`/`lsf` or `sbatch`/`slurm`.
- `--queue`, `--cores`, `--ptile`: scheduler resources.
- `--max-iter`: training limit, built-in default 6000.
- `--sus2-exe`, `--train-env`, `--work-dir`: executable, environment setup, and output directory.
- `--elements`: explicit species list; default infer from data.
- `--keep-order`: preserve explicit order instead of atomic-number sorting.
- `--submit`: submit after generating files; direct CLI built-in default is false.

The generated standard command includes `--do-lin`.

## `dcbf relax STRUCTURE...`

- `--model` is required unless saved as a default.
- `--elements`: required potential species order unless saved as a default.
- `--keep-order`: preserve the explicit potential species order.
- `--optimizer`: ASE optimizer, including BFGS, LBFGS, FIRE, MDMin, GPMin, line-search variants, and QuasiNewton.
- `--fmax`, `--steps`: force threshold and maximum optimization steps.
- `--relax-cell`, `--cell-filter exp|frechet`, `--pressure`: cell relaxation and external pressure in GPa.
- `--stress-weight`: stress contribution used by the SUS2 calculator.
- `--output`, `--output-format`, `--log-file`: output controls.
- `--single`: read only the first frame of each input.
- `--batch`: expand wildcard inputs explicitly.

## `dcbf efs-distri DATA.xyz`

Plots energy, force, and stress distributions.

- `--force-threshold`: remove frames above a maximum-force threshold.
- `--bins` or `--energy-bins`, `--force-bins`, `--stress-bins`: histogram resolution.
- `--density`, `--fit`: density normalization and optional normal fit.
- `--figsize`, `--dpi`, `--log-y`, `--output`: appearance/output.

## `dcbf predict-xyz STRUCTURE`

- `--calc-type`: `sus2`, `nep`, `mace`, `chgnet`, `dp`, `m3gnet`, or `mattersim`.
- `--model`, `--device`: model and calculator setup.
- `--elements`: required for `--calc-type sus2`; other calculators are unchanged.
- `--output`, `--format`, `--suffix`, `--append`: output controls.
- `--num-workers`: calculator worker count.
- `--split-workers`: split xyz into N files, predict in parallel, then concatenate.
- `--log-level`: `DEBUG`, `INFO`, `WARNING`, or `ERROR`.

## `dcbf plot-errors DFT.xyz MLIP.xyz`

Uses the bundled `sus2_plot_errors_v3.py` comparator.

- `--mlip-name`, `--elements`, `--keep-temp`.
- `--force-mode magnitude|components`, `--stress-unit eV|GPa`.
- `--num-processes`, `--skip-structure-indices`.
- `--axis-padding`, `--signed-axis-symmetric`.
- `--figsize`, `--dpi`, `--cmap`, `--scatter-size`, `--bins`, `--linewidth`.
- `--fontsize`, `--tick-labelsize`, `--legend-fontsize`, `--title-fontsize`, `--annotation-fontsize`, `--cbar-fontsize`, `--cbar-tick-size`.
- `--show-r2`, `--save-data`, `--output`.

## Workflow Commands

- `dcbf create-init`: copy bundled `example/sample` into the current directory. It refuses to overwrite existing target files.
- `dcbf run CONFIG.json`: prepare and launch one workflow.
- `dcbf run CONFIG.json --prepare-only`: materialize/validate without starting the sampling loop.
- `dcbf run CONFIG.json --foreground`: run orchestration in the current process instead of managed background mode.
- `dcbf reduce CONFIG.json`: run reduce; see `reduce.md`.
- `dcbf coverage-pca ...`: run coverage analysis. Standalone use requires
  `--model`, `--elements`, and `--mtp-type`; see `coverage-pca.md`.
- `dcbf raw-dft pack DIRECTORY [--output ARCHIVE]`: archive every regular file in one directory as `.tar.zst` with bundled zstd level 19 and one thread.
- `dcbf raw-dft verify ARCHIVE`: verify compression, member-path safety, SHA-256, and manifest metadata for `.tar.zst` or legacy `.tar.gz` archives.
- `dcbf raw-dft extract ARCHIVE [--output-dir DIR]`: verify first, then safely extract into a new directory. The destination must not already exist.
- `dcbf kill [RUN_DIR_OR_CONFIG]`: terminate the managed run identified by `pid.txt`. Confirm user intent first.

## Materials Project

```bash
dcbf mp-search Li P S Cl --api-key KEY --output-dir mp-stru --csv-name summary.csv
```

- Positional values are element symbols; combinations are searched.
- `--api-key` can be saved with `dcbf mp-search set api_key=...`.
- `--output-dir` controls the combination roots; `--csv-name` controls each summary filename.

`dcbf -hh` reveals internal benchmark/calibration and single-generation commands. Do not use them as normal user workflow entry points.

## Selection Diagnostics

The optimized selection path is intended to preserve the previous result while reducing interval lookup, coverage labeling, and greedy-cover runtime.

```bash
dcbf calibrate-selection \
  --cases 120 \
  --output benchmark_outputs/selection_calibration.json

dcbf benchmark-selection \
  --output benchmark_outputs/selection_profile.json
```

- `calibrate-selection` compares the active Python/compiled selection backend with the original min-cover behavior on randomized cases.
- `benchmark-selection` profiles legacy and current interval grouping, coverage labeling, and min-cover paths.
- These are advanced verification commands. They do not change sampling JSON or launch MD/DFT jobs.

See `selection-performance.md` before diagnosing a changed selection result or a slow descriptor-selection stage.
