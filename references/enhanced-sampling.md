# PLUMED And MCMD Templates

These are three SUS2/LAMMPS active-sampling modes, not three different MLIP calculators. The active potential remains SUS2; the selected LAMMPS template changes the MD workflow.

The sampling workflow imports exactly one active LAMMPS template:

```text
init/lmp_in.py
```

Bundled alternatives are examples, not simultaneous plugins:

- normal SUS2MD: keep the standard `lmp_in.py`
- MCMD-style custom workflow: copy `lmp_in_mcmd.py` to `lmp_in.py`
- PLUMED metadynamics: copy `lmp_in_plumed.py` to `lmp_in.py`

Do not expect `lmp_in_mcmd.py` and `lmp_in_plumed.py` to be merged automatically.

## PLUMED Inputs

PLUMED mode also needs:

```text
init/input.plumed.tmpl
```

The workflow creates a local `input.plumed` in each run directory and replaces `__TEMP__` with that MD case's temperature. If the template refers to files such as `NDX_FILE=water.ndx`, place them in `init/` as well.

The bundled Si file is only a smoke-test example. Before scientific use, change collective variables, atom IDs/groups, `SIGMA`, `HEIGHT`, `PACE`, `BIASFACTOR`, walls, index files, and all system-specific settings according to the target structure and literature.

## Typical PLUMED Terms

- `UNITS LENGTH=A TIME=ps ENERGY=eV`: units for PLUMED input quantities.
- `DISTANCE ATOMS=i,j`: distance collective variable for the two listed LAMMPS atom IDs.
- `COORDINATION`: smooth coordination-number collective variable.
- `METAD ARG=...`: collective variables biased by metadynamics.
- `SIGMA`: Gaussian width in each CV's unit.
- `HEIGHT`: initial Gaussian energy height.
- `PACE`: MD steps between deposited hills.
- `BIASFACTOR`: well-tempered metadynamics bias factor.
- `TEMP=__TEMP__`: replaced by the workflow.
- `HILLS`, `COLVAR`, and `plumed.out`: bias history, CV history, and PLUMED log.

## Validation

Before active sampling:

1. Confirm the packaged LAMMPS reports the PLUMED fix/package.
2. Run a short scheduler smoke test with the same environment as sampling.
3. Check `log.lammps`, `plumed.out`, `COLVAR`, and `HILLS` for normal progress.
4. Confirm selected atom IDs remain correct after supercell construction and LAMMPS data conversion.
5. Inspect temperature, timestep, dump stride, and trajectory stability before increasing run length.

Template switching changes the MD physics. It does not change DCBF descriptor selection, DFT labeling, or final training logic.
