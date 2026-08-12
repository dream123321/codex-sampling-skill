---
name: dcbf
description: Use when installing, preparing, running, explaining, reviewing, or debugging the current DCBF one-button deployment for constructing and expanding MLIP training datasets, DCBF/DAS active sampling with standard SUS2MD or PLUMED/MCMD LAMMPS modes, DFT labeling, candidate-only or reference-guided database reduction, coverage analysis, SUS2 training, prediction, relaxation, and plotting on HPC systems. On first use for a target machine, ask whether to install the GitHub release or register an existing deployment, then remember the verified installation directory.
---

# DCBF

Treat the active deployment, its CLI help, and its example JSON files as the source of truth. This skill records the current public interface but must not override newer code discovered in the deployment.

## Installation State Gate

Run this gate before normal task intake whenever `$dcbf` is explicitly invoked:

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
   - task type:
     1. build or expand a training dataset with DCBF/DAS
     2. distill or select database structures with `reduce`
     3. analyze a dataset with `coverage-pca` or `efs-distri`
     4. train or use a potential with `train`, `predict-xyz`, `relax`, or `plot-errors`
     5. install, inspect, debug, resume, or manage DCBF
   - target: deployment root, JSON config, workspace, dataset, or model path
   - execution level: explain only, inspect, edit, `--prepare-only`, submit, submit and monitor, or resume
3. Ask in the user's language. Put the recommended/default choice first when offering choices.
4. Ask only what is not already known. Infer elements, scheduler settings, existing model paths, and run state from supplied files when inexpensive.
5. If the user already supplied a concrete task and enough information, proceed without a ceremonial questionnaire.
6. Always obtain explicit intent before submitting expensive jobs, killing jobs, deleting files, or publishing artifacts.

For a vague invocation, a suitable first response is:

```text
这次想处理哪类 DCBF 工作？

1. 构建或扩充训练数据集
   新建、续跑或排查 DCBF/DAS 主动学习采样。
2. 数据库筛选与蒸馏（reduce）
   对候选结构自身去冗余，或者参考现有训练集筛选新增结构。
3. 数据集分析
   coverage-pca 或能量、力、应力分布分析。
4. 训练或使用势函数
   train、predict-xyz、relax、plot-errors。
5. 安装、检查或管理 DCBF

目标配置、workspace、数据集或模型路径是什么？
这次希望我只解释/检查，还是修改、prepare-only、提交并等待或续跑？
```

After the first answers, load only the relevant section of [references/parameter-intake.md](references/parameter-intake.md) and ask the next smallest set of missing questions.

For dataset construction, treat the initial-dataset builder and active sampling as parts of one workflow. Active sampling always uses SUS2/LAMMPS; standard SUS2MD, PLUMED, and MCMD are alternative LAMMPS sampling modes, not top-level DCBF task categories.

When the user selects dataset construction, collect the required decisions once instead of giving a long tutorial or asking a second advanced-settings question:

```text
可以，我会基于 DCBF 默认模板准备。请一次性确认：

1. 初始数据集构建
   选择：从头构建、使用已有带标签数据集、在已有数据集上继续增广。
   请提供种子结构和已有数据集路径。

2. SUS2-MD 采样
   选择：普通 SUS2MD（推荐）、PLUMED、MCMD。
   再选择 NPT、NVT 或两者。推荐温度为 100–900 K，间隔 100 K。

3. 服务器和 DFT
   提供 LSF/Slurm、训练/MD/DFT 的队列和核数、DFT 引擎、环境与运行命令。
   DFT 模板、赝势和基组等文件需要提供到 init/。

4. 参数设置与执行
   默认：保留模板中的 MD 时长和 DCBF/DAS 筛选参数。
   自定义：请说明需要修改的 MD 或筛选参数。
   不确定：回复“查看参数”，我会列出可调参数和当前默认值。
   同时选择：仅 prepare-only，或检查通过后提交并监控。
```

Inspect existing files first and omit anything already known. If the user chooses defaults, do not ask again about MD duration, timestep, dump interval, selection mode, thresholds, budgets, `state_population`, `candidate_trigger`, or `max_gen`. If the user chooses custom settings, expand only the named MD or selection fields. If the user asks to view parameters, show those two groups with values read from the active template.

Treat “default and submit” as explicit submission intent: fill the required paths/resources, run `--prepare-only`, and submit and monitor only after that validation succeeds. A `prepare-only` choice stops after validation.

When the user selects `reduce`, ask which function is intended:

```text
请选择 reduce 模式：

1. candidate_only
   候选集自蒸馏：只分析 input_xyz 自身，从中选择能够代表其描述符状态的较小结构子集。
2. reference_guided
   参考数据库引导筛选：以 current_xyz 为已有训练集，从 input_xyz 中选择补充缺失或低布居状态的新结构。
```

## Source Of Truth

- Repository: `https://github.com/dream123321/DCBF`.
- Installation source: the latest GitHub one-button release unless the user names a specific package or existing deployment.
- Active deployment: the validated path remembered for the current target.
- Current source, CLI help, and example configs were cross-checked against a live one-button deployment on 2026-08-12.
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

- Building or expanding a training dataset:
  - Sampling JSON, scheduler, selection modes, thresholds, and training block: [references/sampling-config.md](references/sampling-config.md).
  - Initial dataset construction and `augment_existing`: [references/dataset-builder.md](references/dataset-builder.md).
  - Standard SUS2MD, PLUMED, and MCMD sampling templates: [references/enhanced-sampling.md](references/enhanced-sampling.md).
- PCA coverage CLI/JSON, 1D/2D meanings, grids, PCA fit, and automatic query MD: [references/coverage-pca.md](references/coverage-pca.md).
- Candidate-only self-distillation and reference-guided reduce: [references/reduce.md](references/reduce.md).
- Direct CLI commands and option meanings: [references/command-reference.md](references/command-reference.md).
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
- Use current names only: `body_list`, `dq_width_method`, `dq_width`, `dq_width_factor`, `dynamic_dq_width`, `state_population`, `dimension_min_cover_workers`, `dft_clean_dcbf_environment`, and reduce `xyz_io_mode`.
- Do not restore removed `iw_*`, `bw_*`, `coverage_count_threshold`, `coverage_label`, `data_modes`, `loops`, old reduce modes, or the rejected `clean_dft_environment` name.
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

Build or expand a training dataset:

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
