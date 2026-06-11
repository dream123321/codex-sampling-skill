---
name: dcbf-training
description: Use when preparing, running, explaining, or debugging DCBF one-button deployment workflows for chemical-bond-space sampling and SUS2/MLIP potential training. Covers dcbf create-init, seed structures, DFT engine setup with VASP as default, INCAR/POTCAR/KPOINTS requirements, multi-temperature NPT/NVT MD, fixed pressure points or continuous pressure ramps in generated lmp.in files, dcbf run, dcbf train, prediction, plotting, relaxation, reduction, and troubleshooting on the user's HPC deployment.
---

# DCBF Training

Use this skill for DCBF workflows that build sampled datasets and train SUS2/MLIP potentials. Treat the current deployment as the source of truth before changing configs or commands.

## Source of Truth

- Default deployment: `/work/phy-huangj/hj_mlp/ocbf_test/dcbf_one-button_deployment`.
- Activate with `source /work/phy-huangj/hj_mlp/ocbf_test/dcbf_one-button_deployment/activate.sh`.
- The CLI is `dcbf`; do not write `ocbf` commands unless the checked deployment only exposes the old name.
- If commands, defaults, or schema look stale, inspect the deployment first:
  - `dcbf -h`, `dcbf train -h`, `dcbf run -h`
  - `source/DCBF/example/sample/dcbf.init_dataset.vasp.test.json`
  - `source/DCBF/example/sample/init/lmp_in.py`
  - `source/DCBF/dcbf/dcbf/das/lmps_scripts.py`

See [references/current-paths.md](references/current-paths.md) for deployment paths and command defaults.

## Intake Order

Before preparing a DCBF sampling run, collect or infer the inputs in this order:

1. **Starter files**: if the workspace is not initialized, create the default template with `dcbf create-init`, then use the generated `stru/` and `init/` layout.
2. **Seed structures**: ask which seed structures to use, how many, format (`vasp`, `POSCAR`, `CONTCAR`, `cif`, `xyz`, `extxyz`), and whether they have been placed in `stru/`.
3. **DFT engine**: ask which engine to use. Default is VASP. For VASP, require `INCAR`, `POTCAR`, `KPOINTS` or `KSPACING`, `dft_env`, `dft_command`, queue, cores, and ptile.
4. **MD conditions**: ask temperatures, NPT/NVT choice, pressure mode, run length, and save interval. For pressure mode, explicitly ask whether the user wants fixed pressure points or continuous pressure ranges.
5. **Training**: ask whether to train after sampling, template (`l2k2`, `l2k3`, `l3k3`, `l4k3`, `l4k4`, `l4k6`), max iterations, queue, cores, submit/wait behavior, prediction, and error plotting.

Detailed intake prompts live in [references/parameter-intake.md](references/parameter-intake.md).

## Pressure And Temperature Rule

Do not silently assume a pressure workflow.

- Fixed pressure points: examples `1, 10, 50, 100 kbar`. Each temperature runs each pressure point as a constant-pressure NPT segment.
- Continuous pressure range: examples `1-400 kbar` or `1-50, 50-100, 100-400 kbar`. Each temperature runs each range as a pressure-ramp NPT segment.
- LAMMPS `metal` pressure is in `bar`; convert `kbar` to `bar` when writing `lmp.in`.
- If pressure is missing, ask for confirmation. If the user asks for a default, use `1 bar`.
- Ask how many ps each pressure condition should run and how many MD steps between saved structures.

When implementing multi-pressure behavior, modify generated `lmp.in` logic rather than pretending the current scalar pressure field already supports full pressure schedules. See [references/defaults.md](references/defaults.md) for the intended `lmp.in` pattern.

## Command Playbooks

### Initialize A Case

```bash
source /work/phy-huangj/hj_mlp/ocbf_test/dcbf_one-button_deployment/activate.sh
dcbf create-init
```

After initialization, check `stru/`, `init/`, and the JSON config before running. Do not overwrite existing user input files unless the user explicitly asks.

### Run Sampling

```bash
dcbf run dcbf.init_dataset.vasp.test.json --prepare-only
dcbf run dcbf.init_dataset.vasp.test.json
dcbf run dcbf.init_dataset.vasp.test.json --foreground
```

Use `--prepare-only` to verify generated files, especially `lmp.in`, DFT input files, and scheduler scripts, before submitting long jobs.

### Train A Potential Directly

Use this when the user already has an `xyz` or `extxyz` dataset:

```bash
dcbf train data.extxyz --template l2k3 --queue 33 --cores 40 --ptile 40 --submit
```

If the workflow is a generic DP/MACE/MatterSim/NEP training run under `/work/phy-huangj/hj_mlp`, prefer the separate `train-mlip-hpc` skill. Use this skill when the user specifically wants DCBF/SUS2 training or DCBF-generated datasets.

### Other Functions

- `dcbf mp-search`: search Materials Project seed structures.
- `dcbf reduce`: reduce redundant database structures.
- `dcbf predict-xyz`: write predicted `xyz/extxyz` using a trained model.
- `dcbf plot-errors`: compare DFT and MLIP outputs and generate error figures.
- `dcbf efs-distri`: plot energy/force/stress distributions.
- `dcbf relax`: relax structures with a trained model.
- `dcbf kill`: stop a managed background DCBF run.

Use [references/defaults.md](references/defaults.md) for command defaults and [references/parameter-intake.md](references/parameter-intake.md) for required fields.

## Safety Checks

- Verify the active deployment path and `dcbf --help` before running commands.
- Inspect `lmp.in` after generation whenever pressure schedules are involved.
- Confirm seed structure elements are included in the initial dataset; DCBF errors on missing elements.
- For VASP, check `INCAR`, `POTCAR`, and `KPOINTS` or `KSPACING` before submitting SCF tasks.
- For long runs, prefer `--prepare-only` first.
- Do not delete existing user files. Created scratch files can be replaced if they are clearly agent-generated.
