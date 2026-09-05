# Coverage-PCA Reference

`dcbf coverage-pca` converts loop and query structures to SUS2 descriptors, fits one shared PCA basis per element, computes both 1D and 2D FD-grid coverage, and writes figures, CSV, remarks, and PCA point files.

## Inputs And Loop Mapping

```bash
dcbf coverage-pca \
  --input all_sample_data.xyz \
  --query query.xyz \
  --model current.mtp \
  --elements Si \
  --mtp-type l2k2.mtp
```

- `--input` is one xyz/traj containing an integer-like frame info key, default `main`.
- Cumulative mapping is fixed: `main=-1 -> init`, `main=0 -> loop-1`, `main=1 -> loop-2`, and `main=k -> loop-(k+1)`.
- Each displayed loop is cumulative. For example, `loop-3` contains frames with `main=-1,0,1,2`.
- `--main-key` changes the frame info key.
- `--query` is the target B/AIMD dataset whose descriptor points are tested against each cumulative input loop.
- `--run-dir` resolves relative paths from a DCBF workspace, uses its
  `all_sample_data.xyz` when `--input` is omitted, and reads the model element
  order and MTP type from `dcbf.runtime.json` or `init/parameter.yaml`.

`--loop-select` accepts:

- `all`: init and every available loop.
- `middle-half`: init, the central 50 percent of loop positions, and the final loop; when there are three or fewer loops, use all.
- `uniform-half`: init and roughly half of all loops, uniformly spaced, including the final loop.
- `[-1,0,2,8]` or `-1,0,2,8`: explicit `main` values; missing values are an error.

## Elements And Descriptors

- `--elements`: descriptor element/type order. It is required for standalone
  use and preserves the explicit SUS2/MTP type mapping order.
- `--plot-elements`: subset to plot and print; default is every resolved element.
- `--body-list`: descriptor bodies to combine, default `two three`.
- `--model`: potential used for descriptor conversion. The hidden legacy
  `--mtp` spelling remains accepted.
- `--mtp-type`: `l2k2.mtp` or `l2k3.mtp`; required for standalone use.
- `--element-model`: legacy descriptor element mapping mode, `1` or `2`.
- `--mlp-exe`: explicit SUS2 executable. Resolution is CLI value, workflow scheduler value, current deployment `runtime/bin/mlp-sus2`, then PATH.
- `--descriptor-workers` and `--coverage-workers`: independent worker counts, both default 8.

The full `--elements` order is retained for descriptor/MTP type mapping. Coverage is calculated only for elements with non-empty descriptor data in the query and every selected cumulative input loop. Missing elements are skipped with an explicit terminal message and are recorded in `coverage_remark.txt`; they are not assigned artificial zero coverage. Explicit `--plot-elements` are filtered by the same rule, and the command fails clearly if no requested element remains.

## Shared PCA

For each element, the selected fit data are standardized feature-by-feature, then NumPy SVD fits one PCA model. Every input loop and the query are transformed by that same scaler and PCA basis.

`--pca-fit-source` controls fit data:

| Value | PCA fit data |
|---|---|
| `query` | Query dataset only; current default. |
| `input` | All cumulative input-loop descriptor data. |
| `combined` | Input and query together. |

PCA fit source changes only the projection basis. It is separate from the coverage grid standard.

## Coverage Grid

`--coverage-grid` defines the FD-bin range and width source for both coverage calculations:

| Value | Grid standard |
|---|---|
| `query` | One fixed grid from the query dataset. |
| `current-loop` | Each cumulative input loop builds its own grid. Values across loops are less directly comparable. |
| `last-loop` | One fixed grid from the final selected input loop; current default. |

`--width-factor X` overrides both calculations. If omitted, 1D uses `1.0` and 2D uses `2.0`. Larger factors make wider/fewer bins; smaller factors make narrower/more bins.

## 2D And 1D Meaning

### 2D mode

The program bins the PC1-PC2 joint distribution. An input loop occupies some 2D cells; a query point is covered only when it falls in an occupied input cell inside the grid. Coverage is the covered-query-point fraction. Blue/red point labels are these strict 2D booleans.

### 1D mode

The program does not use PC1 or PC2 to calculate the number. It bins each original descriptor dimension separately, computes the query coverage fraction in every dimension, then averages those fractions. PCA is only the 2D display plane.

For colors in 1D mode, every query point receives the fraction of descriptor dimensions covered at that point. The program converts the reported average into a top-k count, ranks points by that score, and preserves all points already marked covered in earlier cumulative loops. This monotonic display prevents a point from changing from covered to uncovered in a later loop, but it is a visualization label rather than a strict multidimensional state test.

`--coverage-mode 2d` is the default. It controls the primary plot/CSV label and query colors; both 1D and 2D values are still printed and saved.

## Automatic Query MD

With `--run-dir`, an explicit query is preferred. Otherwise the command can generate `run_dir/coverage_query_lammps/query.xyz` from workspace structures and the current model.

- `--query-structures all|first|index:N|NAME|GLOB` selects seeds under `run_dir/stru`; multiple selectors are allowed.
- The program takes the last non-empty NPT temperature and the last non-empty NVT temperature from the workflow schedule.
- If only one ensemble exists, only that condition runs. If both exist, both run for every selected structure.
- Work directories are `coverage_query_lammps/runs/<structure>/<ensemble>`.
- All frames are concatenated without deduplication and record source, frame, ensemble, and temperature metadata.
- `query_manifest.json` records conditions and frame counts. A stale condition set forces regeneration.
- `--force-query` always regenerates.
- `--lammps-run-mode scheduler` is the default; `local` is for explicit debugging.
- `--lammps-cores` defaults to `scheduler.lmp_cores`; timeout defaults to 24 hours.

The active `init/lmp_in.py` controls MD length, timestep, dump stride, pressure, and integrator details.

## Plot And Output Options

- `--show-input`: draw current-loop points in addition to query points.
- `--no-plot`: compute CSV/txt only.
- `--max-plot-points`: plotted points per group/subplot; `0` disables downsampling, default 2,000,000.
- `--dpi`, `--show-ticks`, `--axis-padding`, `--element-label-x`, `--element-label-y`: figure controls.
- `--keep-out`: retain merged descriptor `.out` files.
- `--force-recompute`: ignore cached descriptor pickle files.

Standalone outputs include `combined_pca_coverage_<elements>.jpg`, `coverage_summary.csv`, `coverage_remark.txt`, and `pca_txt/<loop>/<element>_pca_{A,B}.txt`.

When coverage runs inside `dcbf run` with summary collection enabled, the persistent export under `<summary>/analysis/coverage/` is intentionally smaller: final PCA figures, `coverage_summary.csv`, `coverage_remark.txt`, `query_manifest.json`, and compressed `query.xyz.gz`. After the summary manifest is published, rebuildable descriptor caches, split XYZ, PCA text, query run directories, and the uncompressed workspace `query.xyz` are removed. This cleanup does not change coverage values or standalone command behavior.

## Workflow JSON

Supported `sampling.coverage_plot` fields are:

```text
enabled, query, query_xyz, query_structures, loop_select, coverage_mode,
coverage_grid, pca_fit_source, body_list, elements, plot_elements,
output_dir, width_factor, axis_padding, max_plot_points, dpi,
descriptor_workers, coverage_workers, mlp_exe, model, mtp_type,
element_model, show_input, no_plot, show_ticks, force_query,
force_recompute, keep_out, lammps_run_mode, lammps_timeout_hours,
lammps_cores, lammps_exe, lammps_env
```

`query_source` may still appear in an example, but the current implementation does not use it to choose the query. Use `query`/`query_xyz` for an explicit file, or omit both to allow `--run-dir` automatic query discovery/generation.

Removed fields such as `coverage_label`, `data_modes`, `loops`, `main_labels`, and label-variable options are rejected.

The legacy JSON field `mtp` remains accepted; when both `model` and `mtp` are
present, `model` takes precedence.
