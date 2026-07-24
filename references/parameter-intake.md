# Parameter Intake

Discover values from the workspace and config before asking. Ask only for choices that materially affect cost or scientific intent.

## Installation First

Before task questions, run the installation state gate from `SKILL.md`.

- Valid remembered path: use it without asking again.
- No remembered path: ask whether to install from GitHub or register an existing deployment.
- Stale remembered path: explain that validation failed and ask for a replacement path or permission to reinstall.
- Different target host: use a separate installation entry.

Do not mix installation questions with the scientific sampling questionnaire unless the user has already answered one of them.

## Explicit Invocation Starter

After installation is resolved, when the user invokes `$dcbf` without a complete request, begin with at most three questions:

1. Which DCBF goal should be handled?
   - build or expand a training dataset
   - run database reduction
   - analyze a dataset
   - train or use a potential
   - install, inspect, debug, resume, or manage DCBF
2. What deployment, config, workspace, dataset, or model is the target?
3. Should the result stop at explanation/inspection, edit files, run `--prepare-only`, submit, submit and monitor, or resume?

Adapt the wording and choices to the user's language. Do not ask for information already present in the invocation or conversation. Once the task category is known, use only the matching section below instead of presenting the full checklist.

Do not present the initial-dataset builder, PLUMED, or MCMD as peer task categories. The builder prepares the starting dataset; standard SUS2MD, PLUMED, and MCMD are sampling-mode choices inside dataset construction.

## Build Or Expand A Training Dataset

Ask one grouped questionnaire. Omit values already available from the request, active config, or workspace:

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

Active sampling always uses SUS2/LAMMPS. Use the standard `init/lmp_in.py` for ordinary SUS2MD. PLUMED and MCMD replace that active template with their corresponding examples; they do not create separate DCBF workflows.

### Response Branches

- **Default**: retain the active example's MD duration, timestep, dump interval, selection mode, thresholds, budgets, `state_population`, `candidate_trigger`, `max_gen`, final training, and output settings. Do not ask about them again.
- **Custom**: expand only the MD or selection fields named by the user.
- **View parameters**: read the active JSON and `init/lmp_in.py`, then show the MD and selection groups with their current values. Do not paste the complete JSON.
- **Default and submit**: populate required paths/resources, run `dcbf run CONFIG.json --prepare-only`, and submit and monitor after validation succeeds.
- **Prepare only**: stop after validation and report the generated paths and checks.

## NPT/NVT Schedule Questions

Use this section only for custom MD settings or validation:

- Is the entire ensemble disabled (`null`) or skipped only at selected main indices (`[]`)?
- When both lists exist, do they have equal outer length?
- Does every main index contain at least one non-empty ensemble?
- What temperature values belong to each main index?
- If coverage query is enabled, is it acceptable to run the last non-empty NPT temperature and the last non-empty NVT temperature for every selected query structure?

Example:

```json
"main_loop_npt": [[200], [], [600]],
"main_loop_nvt": [[], [300], [600]]
```

This produces `main_0=NPT 200 K`, `main_1=NVT 300 K`, and `main_2=NPT+NVT 600 K`.

## DCBF Selection Questions

Use this section only for custom selection settings or a request to view parameters:

- `coverage_calculation_mode`: per configuration or global?
- Enable mean descriptor coverage?
- Use two-body, three-body, or both?
- What does `state_population` need to represent scientifically: any occupied state (`0`) or a minimum database population (`1`, `2`, ...)?
- What staged coverage thresholds and structure budgets are intended?
- Should plateau convergence be enabled? If yes, choose both `plateau_generations` and `min_coverage_delta`.
- For per-configuration mean descriptors, keep the default low-coverage cutoff of 90 percent?
- How many candidates must accumulate before DFT (`candidate_trigger`)?

### Initial Dataset Construction Questions

- Choose from-scratch `generated_only`, an existing labeled xyz with the builder disabled, or `augment_existing`.
- Provide `xyz_input` for the existing-data and augment-existing paths.
- Enable random displacement, phonon displacement, MD, or a combination?
- Supercell, strain list, displacement counts, displacement magnitude, and random seed.
- Builder MD calculator/model, element mapping, temperature, pressure, timestep, NPT/NVT steps, intervals, and worker count.
- DFT task count and force threshold for newly generated candidates.

Keep values from the active example when the user chooses defaults. Ask for builder details only when the user requests customization or when an enabled method is missing a required model/input.

## Coverage-PCA Questions

- Input `all_sample_data.xyz` path and `main` frame label availability.
- Explicit query file or automatic LAMMPS query generation?
- Query structures: all, first, index, exact labels, or globs?
- Loop selection: `all`, `middle-half`, `uniform-half`, or explicit main values.
- Primary mode: 2D grid coverage (default) or 1D mean descriptor coverage.
- Grid: `last-loop` (default), `query`, or `current-loop`.
- PCA fit source: `query` (default), `input`, or `combined`.
- Whether a shared `width_factor` override is scientifically justified.
- Plot elements, maximum displayed points, axis padding, and tick visibility.

## Database Reduction Questions

First ask which reduce function is intended:

```text
请选择 reduce 模式：

1. candidate_only
   候选集自蒸馏。只分析 input_xyz 自身的描述符状态，从候选集中选出能够代表这些状态的较小结构子集。
2. reference_guided
   参考数据库引导筛选。以 current_xyz 为已有训练集，从 input_xyz 中选择能够补充现有数据库缺失或低布居状态的新结构。
```

- `candidate_only`: self-distill one candidate dataset. With `state_population=0/1`, retain at least one representative contribution for each occupied state; values greater than one use greedy multi-cover.
- `reference_guided`: use `current_xyz` as the existing database and select structures from `input_xyz` that visit missing or insufficiently populated states. Bins with database population `<= state_population` are insufficient.
- Input, current/reference, interval-reference, MTP, full element mapping, and output paths.
- `state_population`, body list, dq-width method/factor, chunk size, append behavior, and intermediate-file retention.
- Use the bundled universal potential or a custom model?

## Direct Training Questions

- Dataset path and element order.
- Template (`l2k2`, `l2k3`, `l3k3`, `l4k3`, `l4k4`, or `l4k6`).
- Optional distance/radial overrides.
- Scheduler resources and backend.
- Maximum iterations; current default is 6000.
- Generate only or submit now?
- For workflow training: wait, predict, plot errors, and output names?

## Submission Decision

Distinguish explicitly among:

- inspect/explain only
- edit config only
- `--prepare-only`
- submit and return
- submit and monitor/wait
- resume an existing workspace

Do not infer permission to submit expensive jobs from a request to inspect or prepare configuration.
