# GitHub One-Button Installation

Use the official repository:

```text
https://github.com/dream123321/DCBF
```

The stable latest-release asset URL is:

```text
https://github.com/dream123321/DCBF/releases/latest/download/dcbf_one-button_deployment.tar.gz
```

It redirects to the newest release that contains the asset. Record the resolved release tag when practical.

## First-Use Decision

For each local or remote target:

1. Query `scripts/dcbf_installation_state.py`.
2. If a valid root is remembered, activate it and continue without another installation question.
3. Otherwise ask whether to:
   - install the latest GitHub one-button package
   - register an existing deployment root
   - only explain the workflow without installing

Ask separately for the intended installation parent directory when installation is requested. Downloading the package and running `install.sh` require explicit user intent.

## Install Latest Release

Before downloading, check the platform and available disk space:

```bash
uname -m
ldd --version | head -n 1
df -h .
```

The package requires GNU libc 2.17 or newer and is large. Then, from the chosen installation parent:

```bash
curl -fL --retry 3 \
  https://github.com/dream123321/DCBF/releases/latest/download/dcbf_one-button_deployment.tar.gz \
  -o dcbf_one-button_deployment.tar.gz

tar -xzf dcbf_one-button_deployment.tar.gz
cd dcbf_one-button_deployment
bash install.sh
source activate.sh
bash verify.sh
dcbf -h
```

If `curl` is unavailable, use:

```bash
wget -O dcbf_one-button_deployment.tar.gz \
  https://github.com/dream123321/DCBF/releases/latest/download/dcbf_one-button_deployment.tar.gz
```

Do not overwrite or delete an existing deployment unless the user explicitly asks. Install into a new directory when upgrading an active production environment, verify it, then switch the remembered root.

## Register An Existing Deployment

Validate the supplied root on the machine where it is installed:

```bash
test -f "$DCBF_ROOT/activate.sh"
test -f "$DCBF_ROOT/install.sh"
test -f "$DCBF_ROOT/verify.sh"
test -x "$DCBF_ROOT/runtime/bin/mlp-sus2"
test -x "$DCBF_ROOT/runtime/bin/lmp_mpi"
test -d "$DCBF_ROOT/source/DCBF"

source "$DCBF_ROOT/activate.sh"
bash "$DCBF_ROOT/verify.sh"
dcbf -h
dcbf coverage-pca -h
```

Also check which package is active:

```bash
command -v dcbf
python -c 'import dcbf; print(dcbf.__file__)'
```

This catches source/runtime mismatches and accidentally activated older deployments.

## Remember The Root

Use one entry per target machine:

```bash
python scripts/dcbf_installation_state.py remember \
  --target local \
  --path /absolute/path/dcbf_one-button_deployment \
  --source github-release \
  --version v3-YYYYMMDD
```

Remote example:

```bash
python scripts/dcbf_installation_state.py remember \
  --target user@login.example:22 \
  --path /work/user/app/dcbf_one-button_deployment \
  --source existing
```

The record is local skill state. It does not copy DCBF, activate a shell, or verify a remote filesystem by itself; validation is the agent's responsibility before `remember`.

## External DFT Requirement

The one-button package supplies DCBF, SUS2, LAMMPS, MPI/runtime libraries, and Python dependencies. VASP, ABACUS, CP2K, or QE still requires the user's own installation, input templates, pseudopotentials or basis files, scheduler environment, and executable command.
