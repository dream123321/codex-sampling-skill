# Low-Disk Storage And Recovery

The current DCBF workflow keeps persistent training history and raw DFT records outside the workspace so large intermediates can be cleaned without losing the data needed for audit or recovery. These storage changes do not alter sampling, coverage, selection, DFT label collection, or training algorithms.

## Summary Root

`summary.output_dir` defaults to `summary_bundle`. Absolute paths are used directly. Relative paths resolve from the parent of `run_dir`, not from the JSON directory or inside the workspace.

For this common layout:

```json
{
  "run_dir": "./workspace",
  "summary": {"enabled": true, "output_dir": "summary_bundle"}
}
```

the case directory contains sibling `workspace/` and `summary_bundle/` directories. Do not delete or move the summary root while the workflow is running.

## Training Dataset History

- Persistent shards: `<summary>/datasets/training_history/xyz/`
- Manifest: `<summary>/datasets/training_history/manifest.json`
- Active CFG: `workspace/.dcbf_runtime/training/train.cfg`
- Final workflow XYZ: `workspace/all_sample_data.xyz` or the configured `workflow.output_xyz_name`
- Bundled final dataset: `<summary>/datasets/all.xyz`

The manifest records the initial data and each successful main/generation shard with frame count and SHA-256. DCBF appends the corresponding CFG data to one shared runtime `train.cfg`; sampling training, candidate-trigger counting, and default final high-precision training use that same file.

After failure or interruption, the runtime CFG is normally retained and can be rebuilt from history shards. The ordinary resume size/manifest checks are not a full content-hash validation of the shared CFG; final history export checks shard integrity separately. Do not present every resume/rebuild path as complete checksum verification.

The top-level caller marks history complete and removes the shared CFG after its finalization path returns. Coverage and some plot exceptions are caught as warnings, and bundling can be disabled, so this is not proof that every optional artifact succeeded. `training.wait=false` also is not a supported assumption of safely detached finalization. Do not edit manifests/shards or clean CFG links during a live run.

## Raw DFT Archives

Successful selected tasks are archived under `<summary>/raw_dft/<engine>/...`; filtered or otherwise excluded task diagnostics are stored under `<summary>/raw_dft_excluded/<engine>/...`. Archives use `.tar.zst` with zstd level 19 and one thread. Each archive is verified before the large task files are cleaned; a verification failure leaves the source task intact.

The engine-specific retained files are:

- VASP: `POSCAR`, `vasprun.xml`, and `CHGCAR` when requested and present.
- ABACUS: `STRU`, `running_scf.log`, and charge files when requested and present.
- QE: `qe.in`, `logout`, schema data, and charge density when requested and present.
- CP2K: `cp2k.xyz`, `logout`, and electron-density cube files when requested and present.

The current bundled templates request standard charge density by default. VASP keeps `LAECHG=.FALSE.`, so all-electron `AECCAR*` output is not requested. Missing or unrequested charge output is recorded as a warning and in the manifest rather than silently assumed.

## Archive Commands

```bash
dcbf raw-dft pack task_1
dcbf raw-dft verify summary_bundle/raw_dft/vasp/main_0/gen_0/dir_1/task_1.tar.zst
dcbf raw-dft extract summary_bundle/raw_dft/vasp/main_0/gen_0/dir_1/task_1.tar.zst \
  --output-dir restored/task_1
```

`pack` archives every regular file in the directory and defaults to a sibling `DIRECTORY.tar.zst`. `verify` also accepts legacy `.tar.gz`. `extract` verifies before extraction and refuses an existing destination directory.

## Coverage Cleanup

Workflow summary export copies available final figures, `coverage_summary.csv`, and `coverage_remark.txt`; it also copies `query_manifest.json` and compresses `query.xyz` from the generated-query directory when present. Missing sources are recorded in the manifest, so these outputs are not guaranteed for an external query or failed optional analysis. After publishing the summary manifest, DCBF removes rebuildable workspace descriptor caches, split XYZ, PCA text, query run directories, and the uncompressed generated query. Manifest publication does not mean every optional file existed. Standalone `dcbf coverage-pca` keeps its normal full output.
