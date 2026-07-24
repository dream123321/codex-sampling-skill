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

After installation is resolved, when the user invokes `$dcbf-training` without a complete request, begin with at most three questions:

1. What DCBF task should be handled?
2. What deployment, config, workspace, dataset, or model is the target?
3. Should the result stop at explanation/inspection, edit files, run `--prepare-only`, submit, submit and monitor, or resume?

Adapt the wording and choices to the user's language. Do not ask for information already present in the invocation or conversation. Once the task category is known, use only the matching section below instead of presenting the full checklist.

## New Sampling Case

Confirm or infer:

1. Deployment root, config path, `run_dir`, and whether to create templates with `dcbf create-init`.
2. Seed structures under `stru/`, their formats, elements, atom counts, and intended supercell size.
3. Existing labeled dataset or builder-generated dataset.
4. DFT engine (`vasp`, `abacus`, `cp2k`, or `qe`), templates, pseudopotentials/basis files, environment, command, queue, cores, and ptile.
5. Scheduler backend (`bsub` or `sbatch`) and resources for training, LAMMPS, and SCF.
6. NPT/NVT loop schedule, temperatures, timestep, run length, dump interval, and pressure behavior in `init/lmp_in.py`.
7. Selection mode and its thresholds/budgets.
8. Candidate trigger and maximum generations.
9. Coverage plotting and automatic query MD requirements.
10. Final training, prediction, plotting, and summary bundle requirements.

## NPT/NVT Schedule Questions

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

- `coverage_calculation_mode`: per configuration or global?
- Enable mean descriptor coverage?
- Use two-body, three-body, or both?
- What does `state_population` need to represent scientifically: any occupied state (`0`) or a minimum database population (`1`, `2`, ...)?
- What staged coverage thresholds and structure budgets are intended?
- Should plateau convergence be enabled? If yes, choose both `plateau_generations` and `min_coverage_delta`.
- For per-configuration mean descriptors, keep the default low-coverage cutoff of 90 percent?
- How many candidates must accumulate before DFT (`candidate_trigger`)?

## Dataset Builder Questions

- Use `generated_only` or `augment_existing`?
- Existing labeled `xyz_input` path, if augmenting.
- Enable random displacement, phonon displacement, MD, or a combination?
- Supercell, strain list, displacement counts, displacement magnitude, and random seed.
- Builder MD calculator/model, element mapping, temperature, pressure, timestep, NPT/NVT steps, intervals, and worker count.
- DFT task count and force threshold for newly generated candidates.

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

## Reduce Questions

- `candidate_only`: self-reduce one candidate dataset.
- `reference_guided`: select new candidates against an existing reference set.
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
