# Current DCBF Deployment

Use these paths unless the user gives a newer deployment.

## Deployment

- Root: `/work/phy-huangj/hj_mlp/ocbf_test/dcbf_one-button_deployment`
- Source root: `/work/phy-huangj/hj_mlp/ocbf_test/dcbf_one-button_deployment/source/DCBF`
- Activate: `source /work/phy-huangj/hj_mlp/ocbf_test/dcbf_one-button_deployment/activate.sh`
- Verify: `bash /work/phy-huangj/hj_mlp/ocbf_test/dcbf_one-button_deployment/verify.sh`
- CLI: `dcbf`
- Runtime binaries:
  - SUS2: `/work/phy-huangj/hj_mlp/ocbf_test/dcbf_one-button_deployment/runtime/bin/mlp-sus2`
  - LAMMPS: `/work/phy-huangj/hj_mlp/ocbf_test/dcbf_one-button_deployment/runtime/bin/lmp_mpi`
  - MPI: `/work/phy-huangj/hj_mlp/ocbf_test/dcbf_one-button_deployment/runtime/bin/mpirun`

## Useful Files To Inspect

- Example config: `source/DCBF/example/sample/dcbf.init_dataset.vasp.test.json`
- Annotated configs: `source/DCBF/example/sample_json/`
- Seed structures: `source/DCBF/example/sample/stru/`
- Initial calculation templates: `source/DCBF/example/sample/init/`
- LAMMPS template: `source/DCBF/example/sample/init/lmp_in.py`
- LAMMPS writer: `source/DCBF/dcbf/dcbf/das/lmps_scripts.py`
- MD directory creation: `source/DCBF/dcbf/dcbf/das/mkdir.py`
- Run loop: `source/DCBF/dcbf/dcbf/das/gen_while_loop.py`
- Training implementation: `source/DCBF/dcbf/dcbf/high_precision_training.py`
- Direct train CLI: `source/DCBF/dcbf/dcbf/high_precision_cli.py`

## Confirmed CLI Commands

```bash
dcbf create-init
dcbf mp-search
dcbf run CONFIG.json
dcbf train DATA.extxyz
dcbf reduce CONFIG.json
dcbf relax STRUCTURE
dcbf efs-distri DATA.extxyz
dcbf predict-xyz STRUCTURE_OR_XYZ
dcbf plot-errors DFT.extxyz MLIP.extxyz
dcbf kill [RUN_DIR_OR_CONFIG]
```

## Direct Training Defaults

Current `dcbf train -h` defaults:

- `template=l2k3`
- `backend=bsub`
- `queue=33`
- `cores=40`
- `ptile=40`
- `max_iter=3000`
- `sus2_exe=/work/phy-huangj/hj_mlp/ocbf_test/dcbf_one-button_deployment/runtime/bin/mlp-sus2`
- `train_env=source /work/phy-huangj/hj_mlp/ocbf_test/dcbf_one-button_deployment/activate.sh`
- `submit=False` unless `--submit` is passed

## Workflow Outputs

- Sampling output: `all_sample_data.xyz` unless the config changes `sampling.workflow.output_xyz_name`.
- Managed run files: `pid.txt`, `dcbf_managed.log`, and app logs under the run directory.
- High precision training root: `high_precision_training/` by default.
- Model output: `trained.mtp` by default.
- Training report: `high_precision_training/training_report.json`.
- Prediction output: `high_precision_training/prediction/`.
- Error figure: `high_precision_training/sus2_errors.jpg` by default.
