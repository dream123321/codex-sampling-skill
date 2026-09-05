# Current DCBF Deployment

Verified against the current source deployment on 2026-09-05. For normal use, the remembered and revalidated installation for the target machine takes precedence.

## Deployment

- Repository: `https://github.com/dream123321/DCBF`
- Latest-release asset: `https://github.com/dream123321/DCBF/releases/latest/download/dcbf_one-button_deployment.tar.gz`
- Active root: the deployment recorded for the current target by `scripts/dcbf_installation_state.py`
- Activate: `source "$DCBF_ROOT/activate.sh"`
- Verify: `bash "$DCBF_ROOT/verify.sh"`
- SUS2: `runtime/bin/mlp-sus2`
- LAMMPS: `runtime/bin/lmp_mpi`
- MPI: `runtime/bin/mpirun`
- Python: `runtime/dcbf_env/bin/python`
- Installed package: `runtime/dcbf_env/lib/python3.10/site-packages/dcbf`

The package is relocatable through `activate.sh`; prefer paths under the active deployment instead of site-specific external binaries.

## Public Commands

```text
dcbf create-init
dcbf mp-search
dcbf run CONFIG.json
dcbf train DATA.xyz
dcbf reduce CONFIG.json
dcbf raw-dft pack|verify|extract ...
dcbf coverage-pca --input all_sample_data.xyz --query query.xyz --model current.mtp --elements Si --mtp-type l2k2.mtp
dcbf relax STRUCTURE
dcbf efs-distri DATA.xyz
dcbf predict-xyz DATA.xyz
dcbf plot-errors DFT.xyz MLIP.xyz
dcbf kill [RUN_DIR_OR_CONFIG]
```

Use `dcbf -hh` only when internal advanced commands are required.

## Files To Inspect

- Main example: `source/DCBF/example/sample/dcbf.init_dataset.vasp.test.json`
- Annotated config: `source/DCBF/example/sample_json/dcbf.annotated.jsonc`
- Algorithm examples: `source/DCBF/example/sample_json/`
- Seed/template tree: `source/DCBF/example/sample/{stru,init}`
- Reduce examples: `source/DCBF/example/reduce/`
- Runnable Si reduce example: `source/DCBF/example/Si_reduce_example/`
- Sampling schema/defaults: `source/DCBF/dcbf/dcbf/bootstrap.py`
- MD schedule and scheduler: `source/DCBF/dcbf/dcbf/runtime_config.py`
- Coverage implementation: `source/DCBF/dcbf/dcbf/coverage_pca.py`
- Reduce implementation: `source/DCBF/dcbf/dcbf/reduce.py`
- Dataset builder: `source/DCBF/dcbf/dcbf/dataset_builder.py`
- Persistent training data: `source/DCBF/dcbf/dcbf/training_dataset.py`
- Raw DFT archive handling: `source/DCBF/dcbf/dcbf/raw_dft_archive.py`
- Final bundle and coverage cleanup: `source/DCBF/dcbf/dcbf/artifact_bundle.py`
- Direct CLI parsers: `source/DCBF/dcbf/dcbf/{cli.py,high_precision_cli.py,cli_defaults.py}`
- Selection core and diagnostics: `source/DCBF/dcbf/dcbf/selection/{core.py,benchmark.py,calibrate.py}`

## Workflow Outputs

- Runtime config: `workspace/dcbf.runtime.json`
- Effective sampling parameters: `workspace/init/parameter.yaml`
- Sampling log: `workspace/app.log`
- Combined dataset: `workspace/all_sample_data.xyz` unless `output_xyz_name` changes it
- Shared runtime training CFG: `workspace/.dcbf_runtime/training/train.cfg`
- Per-loop data: `workspace/main_*/gen_*`
- Sampling MD: `workspace/main_*/gen_*/sus2-md/`
- DFT: `workspace/main_*/gen_*/dft/`
- Final training: `workspace/high_precision_training/`
- Coverage query: `workspace/coverage_query_lammps/`
- Coverage results: `workspace/xyz_pca_coverage_results/`
- Summary bundle: `<workspace-parent>/summary_bundle/` for the default relative `summary.output_dir`
- Training-history XYZ shards: `<summary>/datasets/training_history/xyz/`
- Training-history manifest: `<summary>/datasets/training_history/manifest.json`
- Raw DFT archives: `<summary>/raw_dft/<engine>/.../task_<id>.tar.zst`
- Raw excluded-task diagnostics: `<summary>/raw_dft_excluded/<engine>/.../task_<id>.tar.zst`

Relative `summary.output_dir` is resolved from the workspace parent, not from the workspace or JSON directory. For `run_dir=./workspace` and `output_dir=summary_bundle`, the two directories are siblings.

The summary bundle normally contains `datasets/`, `models/`, `reports/`, `logs/`, `sources/`, `analysis/`, and raw DFT archives. `datasets/all.xyz` is assembled deterministically from the initial and per-generation history shards. During a run, the shared `train.cfg` is retained after failure or interruption and can be rebuilt from those shards; it is removed only after the complete workflow and final bundle collection succeed.

Workflow coverage export under `<summary>/analysis/coverage/` contains final PCA figures, `coverage_summary.csv`, `coverage_remark.txt`, `query_manifest.json`, and `query.xyz.gz`. Rebuildable descriptor caches, split XYZ, PCA text, query run directories, and the uncompressed workspace query are cleaned only after the summary manifest is published. Standalone `dcbf coverage-pca` output is not subject to this workflow bundling cleanup.

## Source And Runtime Edits

The active CLI imports the installed runtime package, not the source tree directly. For production fixes:

1. Change the source copy.
2. Verify the installed file has no independent changes.
3. Synchronize the corresponding runtime file.
4. Run the bundled Python `-m py_compile` on both copies.
5. Compare hashes.

Already-running Python processes keep modules loaded in memory; a new process is required to observe code changes.
