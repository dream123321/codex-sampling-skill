# Defaults And Pressure MD Pattern

This reference records the intended behavior for DCBF MD and training workflows.

## Important Existing Defaults

- Deployment CLI: `dcbf`
- Direct train template: `l2k3`
- Direct train queue: `33`
- Direct train cores/ptile: `40/40`
- Direct train max iterations: `3000`
- Sampling example DFT engine: `vasp`
- VASP queue/cores/ptile in examples: `33/40/40`
- Builder MD default pressure in code: `1.01325 bar`
- User-facing default pressure, when requested: `1 bar`

## Current Code Caveat

The current sampling template historically uses `main_loop_npt` as a temperature list and `lammps_scripts(ensemble, temp, ...)` passes only temperature into `lmp.in`.

If the user asks for multiple pressures, check whether the active deployment has been updated. If not, implement or plan a code change that writes pressure segments into `lmp.in`.

## Desired `lmp.in` Behavior

Each temperature should produce one NPT task/input. Inside that `lmp.in`, run all requested pressure conditions in sequence.

Example for fixed pressure points at one temperature:

```lammps
variable T equal 300
variable dt equal 0.001
variable nevery equal 100
variable Tdamp equal "v_dt * 100"
variable Pdamp equal "v_dt * 1000"

velocity all create ${T} ${random} mom yes rot yes dist gaussian
thermo 100

fix 100 all npt temp ${T} ${T} ${Tdamp} aniso 1000.0 1000.0 ${Pdamp}
run 20000
unfix 100

fix 101 all npt temp ${T} ${T} ${Tdamp} aniso 10000.0 10000.0 ${Pdamp}
run 20000
unfix 101
```

Example for a continuous pressure ramp:

```lammps
variable T equal 300
variable dt equal 0.001
variable nevery equal 100
variable Tdamp equal "v_dt * 100"
variable Pdamp equal "v_dt * 1000"

velocity all create ${T} ${random} mom yes rot yes dist gaussian
thermo 100

fix 100 all npt temp ${T} ${T} ${Tdamp} aniso 1000.0 400000.0 ${Pdamp}
run 200000
unfix 100
```

For LAMMPS `metal`, pressure is in `bar`.

## Fixed Pressure Points

User input:

```text
temperatures = 300, 500 K
pressure mode = fixed pressure points
pressures = 1, 10, 50 kbar
duration = 20 ps per pressure point
save interval = 100 steps
```

Expected behavior:

- Generate one NPT input per temperature.
- Each temperature input contains three constant-pressure segments.
- Convert to bar:
  - `1 kbar -> 1000 bar`
  - `10 kbar -> 10000 bar`
  - `50 kbar -> 50000 bar`
- In each segment, `P_start = P_stop`.

## Continuous Pressure Ranges

User input:

```text
temperatures = 300, 500 K
pressure mode = continuous pressure ranges
pressure ranges = 1-400 kbar
duration = 200 ps per range
save interval = 100 steps
```

Expected behavior:

- Generate one NPT input per temperature.
- Each temperature input contains one pressure-ramp segment.
- Convert `1-400 kbar` to `1000-400000 bar`.
- In each segment, `P_start != P_stop`.

For multiple ranges such as `1-50, 50-100, 100-400 kbar`, write three sequential NPT segments.

## Step And Dump Conversion

If the template time step is `dt = 0.001 ps`, then:

```text
steps = duration_ps / dt_ps
```

Examples:

- `20 ps / 0.001 ps = 20000 steps`
- `200 ps / 0.001 ps = 200000 steps`

The save interval controls:

```lammps
variable nevery equal SAVE_INTERVAL_STEPS
```

If different pressure segments need different save intervals, either create segment-specific dump names or require one global interval to avoid dump collisions.

## Files To Modify For Native Support

If native pressure schedules are not implemented, the likely touch points are:

- `source/DCBF/example/sample/init/lmp_in.py`: replace fixed NPT pressure with pressure segment insertion.
- `source/DCBF/dcbf/dcbf/das/lmps_scripts.py`: pass pressure mode/ranges into `lammps_scripts()` and render NPT segments.
- `source/DCBF/dcbf/dcbf/das/mkdir.py`: pass pressure schedule from MD config to each generated NPT input.
- `source/DCBF/dcbf/dcbf/das/gen_while_loop.py`: preserve pressure schedule when copying/modifying generation configs.

Use `dcbf run --prepare-only` after changes and inspect generated `lmp.in` before submitting jobs.
