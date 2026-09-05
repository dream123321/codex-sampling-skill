# Initial Dataset Construction

Use `init_dataset.builder` to generate and label an initial dataset before active sampling. The builder can use random distortions, phonon-like displacements, ASE MD, or any combination.

## Required Intake And Defaults

Classify the initial dataset once:

- From scratch: seed structures are required; enable the builder with `generated_only`.
- Existing labeled dataset: `xyz_input` is required; disable the builder and use the dataset directly.
- Augment existing: both seed structures and `xyz_input` are required; enable `augment_existing`.

Seed structures belong under `stru/`. DFT templates, scheduler templates, pseudopotentials, basis files, and other engine-specific inputs belong under `init/`.

When the user chooses defaults, copy the active deployment's `source/DCBF/example/sample` settings and do not ask for every strain, displacement, supercell, MD, or random-seed value. Ask only when the user requests customization or an enabled construction method lacks a required model or input.

## Dataset Modes

| Mode | Behavior |
|---|---|
| `generated_only` | Build the training dataset only from newly generated structures. `xyz_input` is not prepended. |
| `augment_existing` | Keep the labeled `xyz_input`, label only newly generated candidates with DFT, remove geometric duplicates, and append unique successful structures. Existing structures win duplicate conflicts. |

`augment_existing` requires `init_dataset.xyz_input`, and `builder.output_xyz` must not be the same file.

## Public Layout

```json
"init_dataset": {
  "xyz_input": "./existing_dataset.xyz",
  "structure_source_dir": "./stru",
  "init_source_dir": "./init",
  "all_label": null,
  "builder": {
    "enabled": true,
    "dataset_mode": "augment_existing",
    "output_xyz": "init_dataset/final_dataset.xyz",
    "report_path": "init_dataset/build_report.json",
    "reuse_if_exists": true,
    "construction_methods": {
      "random_displacement": {},
      "phonon_displacement": {},
      "md": {}
    },
    "dft": {
      "calc_dir_num": 10,
      "force_threshold": 20
    }
  }
}
```

- `structure_source_dir` contains seed structures for building and later sampling.
- `init_source_dir` contains DFT templates, `lmp_in.py`, scheduler templates, and optional enhanced-sampling inputs.
- `all_label` optionally supplies a common `label` value while the final combined xyz is annotated. Initial frames receive `main=-1`; successful data from `main_i` receive `main=i`.
- `reuse_if_exists=true` reuses a compatible non-empty output/report instead of rebuilding.

## Random Displacement

| Field | Meaning |
|---|---|
| `enabled` | Enable random strain/rattle generation. |
| `supercell` | Three repetition integers or a 3x3 transformation matrix. |
| `strain` | Isotropic scale factors applied to every source structure. |
| `rattle_count` | Number of rattled variants per source AND strain factor; each factor also emits one un-rattled strained structure before deduplication. |
| `rattle_step` | Angstrom scale increment: rattle variant i uses `(i+1) * rattle_step`. |
| `seed` | Reproducible random seed. |

## Phonon Displacement

| Field | Meaning |
|---|---|
| `enabled` | Enable phonopy-like finite displacements. |
| `supercell` | Repetition or transformation matrix. |
| `distance` | Displacement distance in angstrom. |
| `diag`, `plusminus`, `trigonal`, `symprec` | Symmetry/displacement controls passed to the generator. |
| `include_in_initial_train_set` | Include generated phonon structures in the DFT candidate set. |

## Builder MD

| Field | Meaning |
|---|---|
| `enabled` | Enable ASE-based MD candidate generation. |
| `supercell` | Repeat each seed before MD. |
| `parallel_workers` | Process workers across independent seed structures. |
| `calc_type` | `nep`, `mace`, `dp`, `chgnet`, `m3gnet`, `mattersim`, or `sus2`. |
| `model` | Calculator model/potential path. |
| `ele_list` | Complete element mapping when the calculator requires one. |
| `device` | Calculator device, normally `cpu` or `cuda` when supported. |
| `temperature` | MD temperature in K. |
| `pressure` | NPT pressure in bar. |
| `timestep` | ASE MD timestep in fs. |
| `npt_steps`, `nvt_steps` | Number of steps; zero skips that ensemble. |
| `npt_type` | NPT integrator choice; current default is `berendsen`. |
| `ttime`, `ttime_factor`, `nhc_length` | Thermostat/barostat controls used by the selected integrator. |
| `log_interval`, `traj_interval` | Logging and trajectory stride in MD steps. |
| `seed` | Velocity/random seed. |

Builder MD is a short initial-dataset construction path and is distinct from sampling-stage SUS2MD/LAMMPS.

## DFT And Outputs

- `dft.calc_dir_num` controls the number of DFT task groups.
- `dft.force_threshold` uses strict maximum atomic-force norm in eV/A; if parsed structures exist but none pass, the shared collector retains the minimum-maximum-force fallback.
- Only newly generated structures are sent to DFT in `augment_existing` mode.
- The report records source, generated, DFT-success, deduplicated, and final counts.
- Builder work is under `run_dir/init_dataset_build`; the final dataset and report use the configured output paths.
- Element validation runs after building: every element in sampling seeds must exist in the final initial dataset.

The public normalizer forces `include_source_structures=false` and `post_build_action=continue`; these are not effective user switches in this version.

Stop before active sampling (NOT necessarily before builder computation):

```bash
dcbf run CONFIG.json --prepare-only
```

The CLI checks this flag only after `ensure_dataset()`. An enabled builder may run ASE MD and submit DFT during this command. For no-computation requests, inspect JSON/inputs statically and do not invoke it under the assumption of a pure dry run. See [sampling-workflow.md](sampling-workflow.md).
