# dcbf

Codex skill for installing and operating the DCBF one-button deployment. It treats DCBF/DAS active sampling, initial-dataset generation, DFT labeling, and standard SUS2MD or PLUMED/MCMD LAMMPS modes as one training-dataset construction workflow. It also covers the two database-reduction functions (`candidate_only` self-distillation and `reference_guided` incremental selection), coverage analysis, low-disk training history, raw DFT archive recovery, SUS2 training, prediction, plotting, relaxation, and troubleshooting.

On first use for each local or remote target, the skill asks whether to install the latest GitHub release or use an existing deployment. After validation, it remembers that target's deployment root and reuses it on later requests.
