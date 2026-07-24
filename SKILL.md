---
name: dcbf-training
description: Use when installing, preparing, running, explaining, reviewing, or debugging the current DCBF one-button deployment, including initial-dataset generation, DCBF/DAS sampling, SUS2MD/LAMMPS schedules, DFT labeling, SUS2 training, coverage-pca, database reduce, prediction, relaxation, plotting, PLUMED, and MCMD workflows on HPC systems. On first use for a target machine, ask whether to install the GitHub release or register an existing deployment, then remember the verified installation directory.
---

# DCBF Training

Treat the active deployment, its CLI help, and its example JSON files as the source of truth. This skill records the current public interface but must not override newer code discovered in the deployment.

## Installation State Gate

Run this gate before normal task intake whenever `$dcbf-training` is explicitly invoked:

1. Use `local` for local work or a stable endpoint such as `user@host:port` for remote work.
2. Query the remembered installation:

```bash
python scripts/dcbf_installation_state.py status --target TARGET --json
```

3. If an entry exists, validate it on that target:
   - `activate.sh`, `install.sh`, and `verify.sh` exist
   - `runtime/bin/mlp-sus2`, `runtime/bin/lmp_mpi`, and `source/DCBF` exist
   - after activation, `dcbf -h` succeeds
4. If valid, use it and do not ask about installation again.
5. If no entry exists, or the path is stale, ask one short first-use question:

```text
这台机器上的 DCBF 是需要我从 GitHub 一键安装，还是已经安装好了？如果已安装，请给我部署根目录。
```

6. For an existing installation, validate and remember it:

```bash
python scripts/dcbf_installation_state.py remember \
  --target TARGET --path DEPLOYMENT_ROOT --source existing
```

7. For a new installation, obtain explicit permission for the download and target directory, follow [references/installation.md](references/installation.md), run `verify.sh`, and remember the verified root with `--source github-release`.
8. A path explicitly supplied in the current request overrides a remembered path. Validate it and update that target's entry.

The state file stores only target identifiers, deployment roots, source labels, versions, and timestamps. Never store passwords, SSH keys, GitHub tokens, scheduler credentials, or Materials Project API keys.

## Explicit Invocation Intake

After the installation gate, address the user directly and make the interaction active:

1. If the request is empty, only names the skill, or is too vague to identify the work, ask 1-3 short questions before reading remote files, editing configs, or running jobs.
2. Ask for the missing parts of:
   - task type: new sampling, inspect/debug/resume, dataset builder, coverage-pca, reduce, train, relax/predict/plot, or PLUMED/MCMD
   - target: deployment root, JSON config, workspace, dataset, or model path
   - execution level: explain only, inspect, edit, `--prepare-only`, submit, submit and monitor, or resume
3. Ask in the user's language. Put the recommended/default choice first when offering choices.
4. Ask only what is not already known. Infer elements, scheduler settings, existing model paths, and run state from supplied files when inexpensive.
5. If the user already supplied a concrete task and enough information, proceed without a ceremonial questionnaire.
6. Always obtain explicit intent before submitting expensive jobs, killing jobs, deleting files, or publishing artifacts.

For a vague invocation, a suitable first response is:

```text
你这次想处理哪类 DCBF 任务：新建采样、检查/续跑、coverage-pca、reduce、训练，还是 PLUMED/MCMD？
目标配置、workspace、数据集或模型路径是什么？
这次希望我只解释/检查，还是修改、prepare-only、提交并等待？
```

After the first answers, load only the relevant section of [references/parameter-intake.md](references/parameter-intake.md) and ask the next smallest set of missing questions.

## Source Of Truth

- Repository: `https://github.com/dream123321/DCBF`.
- Installation source: the latest GitHub one-button release unless the user names a specific package or existing deployment.
- Active deployment: the validated path remembered for the current target.
- Current GitHub source and a live one-button deployment were cross-checked on 2026-07-24.
- CLI: `dcbf`.
- Verify current commands and saved defaults before editing a config:

```bash
source "$DCBF_ROOT/activate.sh"
dcbf -h
dcbf -hh
dcbf train -h
dcbf coverage-pca -h
dcbf reduce -h
```

CLI defaults for `train`, `relax`, `efs-distri`, `predict-xyz`, `plot-errors`, and `mp-search` may be overridden by `~/.dcbf/cli_defaults.json`. The `current:` values printed by `dcbf <command> -h` take precedence over reference prose.

Read [references/current-paths.md](references/current-paths.md) for verified paths, runtime binaries, examples, and output locations.

## Load The Relevant Reference

- Sampling JSON, scheduler, selection modes, thresholds, and training block: [references/sampling-config.md](references/sampling-config.md).
- Initial dataset construction and `augment_existing`: [references/dataset-builder.md](references/dataset-builder.md).
- PCA coverage CLI/JSON, 1D/2D meanings, grids, PCA fit, and automatic query MD: [references/coverage-pca.md](references/coverage-pca.md).
- Reduce modes and `state_population`: [references/reduce.md](references/reduce.md).
- Direct CLI commands and option meanings: [references/command-reference.md](references/command-reference.md).
- PLUMED and MCMD templates: [references/enhanced-sampling.md](references/enhanced-sampling.md).
- Stable defaults, units, path precedence, and removed names: [references/defaults.md](references/defaults.md).
- Questions to collect before preparing or submitting work: [references/parameter-intake.md](references/parameter-intake.md).
- GitHub installation and remembered-path behavior: [references/installation.md](references/installation.md).
- Selection acceleration and advanced validation: [references/selection-performance.md](references/selection-performance.md).

## Operating Procedure

1. Resolve and validate the remembered deployment for the current target. Ask the first-use installation question only when no valid entry exists.
2. Inspect the live command help, the requested JSON, and `source/DCBF/example/` before changing parameters.
3. Infer cheap facts from files: elements, scheduler backend, existing model paths, available seed structures, and previous run state.
4. Explain parameter effects before changing expensive sampling, DFT, or training settings.
5. Validate with `dcbf run CONFIG.json --prepare-only` before a new long run unless the user explicitly requests immediate submission.
6. Inspect generated `dcbf.runtime.json`, `init/parameter.yaml`, scheduler scripts, and `lmp.in` files before submission.
7. After source edits, synchronize the installed runtime only when required, then run `py_compile` and focused behavioral checks.

## Public Configuration Rules

- Use `sampling.structure_selection`; top-level `parameter` and `sampling.parameter` are rejected for sampling configs.
- Enable exactly one selection mode: `mlp_encode_model`, `das_adaptive`, or `das_fixed`. Invalid mode counts warn and fall back to `mlp_encode_model`.
- Use current names only: `body_list`, `dq_width_method`, `dq_width`, `dq_width_factor`, `dynamic_dq_width`, and `state_population`.
- Do not restore removed `iw_*`, `bw_*`, `coverage_count_threshold`, `coverage_label`, `data_modes`, `loops`, or old reduce modes.
- Elements are normally inferred and sorted by atomic number. When a custom MTP contains a fixed species mapping, provide the complete element order and use `sort_ele=false` only when that mapping requires it.
- Relative JSON paths resolve from the JSON directory unless a feature explicitly resolves output under `run_dir`.
- Do not copy hard-coded paths from an example blindly. Point executables and environment setup to the active deployment runtime.

## Quick Playbooks

Initialize a case:

```bash
source "$DCBF_ROOT/activate.sh"
dcbf create-init
```

`create-init` aborts if any target template path already exists; do not overwrite user inputs.

Validate and run sampling:

```bash
dcbf run dcbf.init_dataset.vasp.test.json --prepare-only
dcbf run dcbf.init_dataset.vasp.test.json
dcbf run dcbf.init_dataset.vasp.test.json --foreground
```

Train from one existing dataset:

```bash
dcbf train data.extxyz --template l2k3 --max-iter 6000 --submit
```

Analyze coverage:

```bash
dcbf coverage-pca --input all_sample_data.xyz --query query.xyz \
  --model current.mtp --elements Si --mtp-type l2k2.mtp
```

Reduce a dataset:

```bash
dcbf reduce reduce.json
```

## Submission And Safety

Before submitting sampling, DFT, LAMMPS/SUS2MD, or training jobs, confirm or discover:

- config, deployment, and workspace paths
- backend (`bsub` or `sbatch`), queue/partition, cores, and ptile
- DFT engine, input templates, environment, executable command, and pseudopotential/basis files
- seed structures, element consistency, and intended supercell size
- NPT/NVT temperatures, MD duration, timestep, dump interval, and pressure encoded by `init/lmp_in.py`
- selection mode, coverage thresholds, budgets, and candidate trigger
- whether to prepare only, submit, wait, resume, or merely inspect

Do not delete existing user files, kill jobs, publish releases, or submit expensive work without explicit user intent. Preserve unrelated modifications in dirty worktrees and live workspaces.
