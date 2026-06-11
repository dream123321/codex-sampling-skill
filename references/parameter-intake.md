# Parameter Intake

Use this checklist before generating a DCBF sampling config, modifying `lmp.in`, or launching jobs.

## 1. Starter Files

If the workspace is not initialized, use:

```bash
source /work/phy-huangj/hj_mlp/ocbf_test/dcbf_one-button_deployment/activate.sh
dcbf create-init
```

Then inspect the generated layout before editing:

- `stru/`: seed structures
- `init/`: DFT and LAMMPS templates
- JSON config file, usually based on the generated or example DCBF config

Do not overwrite existing user files unless the user explicitly asks.

## 2. Seed Structures

Ask or infer:

- Which seed structures should be used?
- Are they already in the generated `stru/` directory?
- Are there one or many structures?
- Format: `vasp`, `POSCAR`, `CONTCAR`, `cif`, `xyz`, or `extxyz`.
- Do all seed structures contain the same intended element set?

## 3. DFT Engine

Ask which calculator will label selected structures.

- Default: `vasp`.
- Other possible engines in the codebase: `cp2k`, `qe`, `abacus`.

For VASP, require:

- `init/INCAR`
- `init/POTCAR`
- `init/KPOINTS`, or an `INCAR` using `KSPACING`
- `sampling.scheduler.dft_env`
- `sampling.scheduler.dft_command`
- SCF queue, cores, and ptile
- `sampling.structure_selection.dft.calc_dir_num`
- `sampling.structure_selection.dft.force_threshold`

For CP2K/QE/ABACUS, inspect the corresponding template files and pseudo/basis maps under `init/` before writing commands.

## 4. Initial Dataset Builder

Ask whether the initial dataset comes from:

- Existing `xyz/extxyz` via `init_dataset.xyz_input`
- Random displacement
- Phonon displacement
- Short MD using `init_dataset.builder.construction_methods.md`

For builder MD, collect:

- Temperature in K
- Pressure in bar if NPT is used; default is about 1 bar when the user confirms default pressure
- Step counts and trajectory interval
- Calculator/model used for fast MD (`nep`, `mace`, `chgnet`, `dp`, `m3gnet`, `mattersim`, or `sus2`)

## 5. Sampling MD Conditions

For main DCBF sampling, always ask:

- Temperature list or range, for example `300, 500, 700 K`.
- Ensemble: NPT or NVT. Multi-pressure requests imply NPT.
- Pressure mode:
  - fixed pressure points, for example `1, 10, 50, 100 kbar`
  - continuous pressure ranges, for example `1-400 kbar`
- For each pressure point or pressure range:
  - duration in ps
  - save interval in MD steps
- Time step, if not using the template value.

Pressure units:

- User-facing pressure may be in `bar` or `kbar`.
- LAMMPS `metal` pressure is `bar`.
- Convert `1 kbar` to `1000 bar` when writing `lmp.in`.

## 6. Structure Selection Mode

Ask or infer which mode is intended:

- `mlp_encode_model`: descriptor coverage mode for DCBF chemical-bond-space selection.
- `das_adaptive`: adaptive uncertainty sampling.
- `das_fixed`: fixed threshold uncertainty sampling.

Only one mode should be enabled. If none or multiple are enabled, the current code warns and defaults toward `mlp_encode_model`.

For `mlp_encode_model`, ask about:

- `body_list`, commonly `["two", "three"]`
- `selection_budget_schedule`
- `coverage_threshold_schedule`
- `coverage_calculation_mode`, commonly `per_configuration`
- `mean_descriptor_enabled`, normally false unless the user asks for mean descriptor coverage

## 7. Training

Ask whether training should happen after sampling or directly from an existing dataset.

For `dcbf train` or `training.enabled=true`, collect:

- Input dataset path if not using sampling output
- Template: `l2k2`, `l2k3`, `l3k3`, `l4k3`, `l4k4`, `l4k6`
- Element order if the user needs a fixed order
- `r_max` if overriding
- `max_iter`
- Queue, cores, ptile
- Submit now or only generate files
- Predict after training?
- Plot errors after prediction?

## 8. Minimal Question Set

If the user gives no details, ask these first:

1. Should I run `dcbf create-init` to create the default files?
2. Which seed structures should be used, and are they in the generated `stru/` directory?
3. Which DFT engine should label selected structures? Default VASP.
4. For VASP, where are `INCAR`, `POTCAR`, and `KPOINTS` or `KSPACING`?
5. What temperatures should MD run?
6. Pressure mode: fixed pressure points or continuous pressure ranges?
7. How many ps for each pressure condition?
8. How many MD steps between saved structures?
9. Should sampling output be trained into a SUS2 potential automatically?
