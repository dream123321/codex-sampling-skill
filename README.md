# dcbf

Codex skill for installing and operating the DCBF one-button deployment. It treats DCBF/DAS active sampling, initial-dataset generation, DFT labeling, and standard SUS2MD or PLUMED/MCMD LAMMPS modes as one training-dataset construction workflow. It also covers the two database-reduction functions (`candidate_only` self-distillation and `reference_guided` incremental selection), coverage analysis, low-disk training history, raw DFT archive recovery, SUS2 training, prediction, plotting, relaxation, and troubleshooting.

On first use for each local or remote target, the skill asks whether to install the latest GitHub release or use an existing deployment. After validation, it remembers that target's deployment root and reuses it on later requests.

The source-audited references explain the [full sampling workflow](references/sampling-workflow.md), [descriptor selection and budgets](references/selection-logic.md), and [code defaults versus example values](references/defaults.md). See the [source audit](references/source-audit.md) for evidence boundaries and the read-only verification script. In particular, an enabled initial-dataset builder can run MD/DFT even with `--prepare-only`.
