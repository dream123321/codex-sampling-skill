# Reduce Reference

Run database distillation with:

```bash
dcbf reduce reduce.json
```

Only `candidate_only` and `reference_guided` are valid modes. Old `direct` and `incremental` names are rejected.

## Mode Semantics

### `candidate_only`

Self-distills `reduce.input_xyz`. It builds descriptor histograms from the candidate set itself and greedily selects a smaller structure subset that represents its occupied descriptor states.

Use this mode for candidate-set self-reduction. For selection against an existing database, use `reference_guided` rather than relying on reference paths in a `candidate_only` config.

### `reference_guided`

Uses `reduce.current_xyz` as the existing database and selects structures from `reduce.input_xyz` that add descriptor-space coverage by visiting missing or insufficiently populated states. `interval_ref_xyz` defines the interval/reference baseline and defaults to `current_xyz`. Large inputs are processed in chunks.

## Configuration

```json
{
  "parameter": {
    "sort_ele": true,
    "ele": ["Si"],
    "mtp_type": "l2k2",
    "body_list": ["two", "three"],
    "dq_width_method": "Freedman_Diaconis",
    "dq_width": 0.01,
    "dq_width_factor": 1.0,
    "dynamic_dq_width": false
  },
  "scheduler": {
    "sus2_mlp_exe": "/ACTIVE_DEPLOYMENT/runtime/bin/mlp-sus2"
  },
  "reduce": {
    "mode": "candidate_only",
    "input_xyz": "md.xyz",
    "state_population": 0,
    "encoding_cores": 5,
    "xyz_io_mode": "fast_extxyz",
    "dimension_min_cover_workers": -1,
    "append_current": false,
    "output_xyz": "sample.xyz",
    "remain_xyz": "remain.xyz",
    "report_json": "report.json",
    "work_dir": "work"
  }
}
```

## Parameter Meanings

| Field | Meaning |
|---|---|
| `parameter.ele` / `reduce.ele` | Complete potential species mapping. It must match custom MTP `species_count`. |
| `sort_ele` | Sort the supplied/inferred mapping by atomic number. Disable only when a custom model requires explicit order. |
| `mtp_type` | Descriptor type. The bundled universal potential forces its own compatible type. |
| `body_list` | Descriptor families, normally `two` and `three`. |
| `dq_width_method` | `Freedman_Diaconis`, `self_input`, `scott`, or `std`. |
| `dq_width` | Explicit width only for `self_input`. |
| `dq_width_factor` | FD/Scott width multiplier. |
| `dynamic_dq_width` | In reference-guided mode, recompute interval widths as the staged reference grows; false fixes them from the interval reference. |
| `scheduler.sus2_mlp_exe` | Descriptor executable. If omitted, resolve the active deployment runtime/PATH default. |
| `mtp_path` | Custom MTP path. |
| `use_universal_potential` | Force use of the bundled universal reduce model and element mapping. Missing custom MTP or element mapping also activates bundled assets. |
| `input_xyz` | Candidate structures. Required in both modes. |
| `current_xyz` | Existing dataset. Required in `reference_guided`. |
| `interval_ref_xyz` | Grid/reference source; defaults to `current_xyz` in `reference_guided`. |
| `chunk_size` | Approximate reference-guided chunk target, default 1,000,000. Code derives chunk count using floor division then distributes frames; it is not a strict maximum per chunk. |
| `encoding_cores` | Descriptor process count, default 5. |
| `xyz_io_mode` | Structure I/O backend: `fast_extxyz`, `auto`, or `ase`; default `fast_extxyz`. |
| `dimension_min_cover_workers` | Minimum-cover strategy, default `-1`: 0 joint, 1 serial per-dimension, positive N limited parallelism, or -1 allocated/visible CPUs. |
| `state_population` | State-population target/threshold; details below. |
| `append_current` | Prepend `current_xyz` to selected candidates in `output_xyz`, default true. |
| `keep_intermediate` | Keep descriptor intermediates, default false. |
| `output_xyz` | Selected output; default `dcbf_reduce_sample.xyz`. |
| `remain_xyz` | Unselected candidate frames; default `dcbf_reduce_remain.xyz`. |
| `report_json` | Counts, effective settings, paths, timing, and selection basis. |
| `work_dir` | Temporary/intermediate root, default `.dcbf_reduce_work`. |

## XYZ I/O And Minimum Cover

- `fast_extxyz`: fastest strict path for standard EXTXYZ. It indexes frame byte ranges, copies original frame blocks, and generates CFG shards in parallel with `encoding_cores`, preserving headers, labels, and numeric text.
- `auto`: try the fast path and fall back to ASE for unsupported or nonstandard XYZ/EXTXYZ and `.traj` inputs.
- `ase`: force the legacy ASE read-and-reserialize path.

Use `auto` when input compatibility is uncertain. Strict `fast_extxyz` raises an error instead of silently changing backends.

For nonzero `dimension_min_cover_workers`, reduce unions independently solved descriptor dimensions and then applies deterministic global reverse pruning. Coverage and population targets are retained, although selected structures can differ from `dimension_min_cover_workers=0`.

## `state_population`

In reference-guided selection, database bins with frequency `<= state_population` are treated as insufficient, so candidates visiting them can be selected.

In candidate-only self-deduplication:

- `0` or `1`: retain at least one representative contribution for every occupied bin.
- `2`: target `min(bin_frequency, 2)` local-environment contributions per occupied bin.
- `10`: target up to ten contributions per occupied bin.

For values greater than one, greedy multi-cover counts repeated local environments from one structure, capped by each bin's remaining target. It is not simply a minimum number of distinct structures per bin.

## Outputs And Labels

`sample.xyz` and `remain.xyz` preserve the original atoms and any existing energy, force, stress, and info labels. Reduce does not calculate missing labels; unlabeled inputs can still be reduced and remain unlabeled.

`report.json` records the requested and effective XYZ I/O backend, fallback reasons, and minimum-cover mode, worker counts, task counts, and timing.

For `reference_guided` with `append_current=true`, output is the existing dataset followed by newly selected candidate structures. `remain.xyz` contains only unselected candidates.
