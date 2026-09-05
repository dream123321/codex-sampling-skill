# Sampling Workflow And State

Audited against the 2026-09-05 source. Use this for execution order, unexpected selection, model reuse, resume, or stopping. Parameter values are in [defaults.md](defaults.md); numerical selection is in [selection-logic.md](selection-logic.md); source symbols and limitations are in [source-audit.md](source-audit.md).

## Active Call Path

```text
dcbf run JSON
  -> WorkspaceBootstrapper.prepare_workspace
       normalize config -> copy init/stru -> optional builder -> element check
       -> init/parameter.yaml + dcbf.runtime.json
  -> if prepare_only: return
  -> TrainingDatasetStore.ensure_initial
  -> for each paired main schedule:
       gen_while_loop -> run_monitored_generation -> GenerationRunner.run
         train or reuse -> multi-seed MD -> DCBF or DAS selection
         -> candidate-pool stage -> intermediate cleanup -> gen/__ok__
       __end__ or max_gen -> next main
  -> discard remaining untriggered candidates -> export final XYZ
  -> optional coverage query/PCA -> optional final high-precision training
  -> ArtifactBundler.collect -> training history complete / shared CFG cleanup
```

### Preparation Is Not A Pure Dry Run

`run_from_config` calls `prepare_workspace()` before testing `prepare_only`. Preparation copies files and calls `InitialDatasetBuilder.ensure_dataset()` when enabled. A new builder run can generate ASE MD candidates and submit/wait for DFT; a compatible completed dataset can be reused instead.

For **inspection only**, read/parse JSON, validate required files and schedule, and inspect executable/config provenance. Do not execute `dcbf run ... --prepare-only` with an enabled builder on the assumption that it cannot compute. Do not silently disable the builder and present that changed config as validation of the original. User approval for building/submitting the dataset covers the corresponding builder work; do not ask twice for already authorized work.

## Stage Inputs And Outputs

| Stage | Inputs and active behavior | Outputs / next decision |
|---|---|---|
| Normalize | Public `init_dataset`, `sampling`, `training`; merge selected mode over common fields, then fill omitted defaults | Internal dataset/workflow/parameter/scheduler; ignored and rejected keys are listed in defaults |
| Build initial data | Disabled builder uses labeled `xyz_input`; enabled builder generates candidates, deduplicates, and labels new structures | Builder dataset/report; initial dataset must contain every sampling-seed element |
| Establish training data | Initial labeled XYZ and persistent history manifest | One runtime `train.cfg`; generation training paths link to it |
| Enter main/gen | Paired NPT/NVT schedule and existing directory/marker state | `main_i/gen_j/parameter.yaml`; an existing generation YAML is not overwritten by schedule copying |
| Train or reuse | First `main_0/gen_0` trains; later generations normally copy existing models | `sus2/current_*.mtp`; DCBF uses one model, DAS requires at least three |
| Run MD | Seed files, current models, `init/lmp_in.py`, scheduler | `sus2-md/<seed>/npt/<temperature>` and/or `nvt/<scale>_<temperature>` trajectories/logs |
| Select | DCBF histogram/mean/AEE or DAS ambiguity/MBTR branch | `*_sample_filter.xyz`, DCBF `stru.pkl`, and NPT volume-filter report |
| Accumulate | Selected frames, per-generation addition marker, run-level pool | `candidate_selected.xyz`, `__candidate_selected_added__`, `candidate_pool.xyz` |
| Label and update | Triggered pool, DFT templates and scheduler | `dft/scf/filter/dir_*/N`, collected XYZ/source mapping, raw archives, appended training shard, updated models |
| Complete generation | Candidate stage has returned without an exception | Large MD/descriptor intermediates removed; generation `__ok__` written |
| Finish workflow | All configured mains have ended | Final labeled XYZ, optional analysis/training, summary and training-history cleanup |

## Initial Dataset And Seeds

- `generated_only` uses newly generated labeled structures, not an automatic prepend of `xyz_input`.
- `augment_existing` keeps existing labeled data, excludes geometric duplicates before new DFT, and merges successful new labels with existing structures winning duplicate conflicts.
- Random displacement, phonon displacement, and builder ASE MD are distinct construction methods. Builder ASE MD is not the main-loop LAMMPS runner.
- The public normalizer currently forces `include_source_structures=false` and `post_build_action=continue`. Do not offer these as effective public switches.
- The builder can read several structure formats, but the sampling MD `mkdir_vasp` entry enumerates top-level `.vasp` seeds. Verify usable sampling seeds exist; accepting an input during builder element checks does not prove the MD enumerator will use it.
- Every new main's `gen_0` starts from the original sampling seeds. Later generations in that same main read the previous `stru.pkl`.
- Ordinary SUS2MD, PLUMED, and MCMD all use the sampling LAMMPS path; install the chosen template as `init/lmp_in.py`. See [enhanced-sampling.md](enhanced-sampling.md).

## Training And Model Baselines

`pre_train_mlp` trains the first model(s), copies the previous generation's models for `gen>0`, and copies the preceding main's last models for a later main's `gen_0`. A triggered, collected candidate batch then retrains in the current generation using `subsequent_command`. Therefore, there need not be a new training job at the beginning of every generation.

Descriptor-model selection is deliberately separate:

| Condition | Candidate extraction | Coverage values used for decisions |
|---|---|---|
| `main==0` or `gen==0` | Current generation model | Current generation model |
| `main>0` AND `gen>0` | Current generation model | That main's `gen_0/sus2/current_0.mtp` |

In the second row, the **current training dataset and current MD frames are re-encoded** with the gen-0 model for coverage. Neither the database nor its FD grid is frozen. The mean-descriptor branch follows the same condition. This difference can help explain discrepancies between reported coverage and current-model candidate classes; it is not PCA.

## Candidate Pool Decisions

The pool is rooted at the run workspace and can carry across generations and mains. It appends selected frames; it does not itself perform geometric deduplication. Within-generation selected indices are deduplicated elsewhere. `__candidate_selected_added__` prevents an ordinary resume from adding the same generation twice, but is not a general transaction or geometric-dedup guarantee.

`candidate_trigger` accepts a positive count or a percentage string. A percentage uses `ceil(current shared CFG frame count * percent / 100)`, with a minimum of one. For 3635 training frames and `"1%"`, the threshold is 37. This is a **minimum batch trigger**, not a maximum DFT budget.

The active candidate stage checks in this order:

1. Materialize this generation's selection and append it once to the pool.
2. If this generation selected zero, normally write `__end__` and return, even when old candidates remain pooled. Exception: a nonempty selection entirely removed by the NPT volume filter returns without `__end__`.
3. If pool size is below the trigger, skip DFT/update and retain the pool and current model.
4. Otherwise label the whole pool, collect/filter results, append the batch to training history, and update the models.
5. Clear the pool after the update and its validation return successfully.

After the last configured main, `run_from_config` logs and clears any remaining pool. It does not force one final sub-threshold DFT batch. Do not promise every selected candidate enters the final labeled dataset.

## Stopping And Failure States

| Event | Current behavior | Interpretation |
|---|---|---|
| DCBF hard coverage or enabled plateau convergence | Selection may be set empty after selection-count logging | Logged intermediate candidate counts can differ from final file count |
| Zero current selection | Candidate stage normally writes generation `__end__` | Can also result from budgets/no candidate classes, not proof that hard coverage was reached |
| NPT volume filter removes all selected frames | Skip DFT without `__end__` | Continue with current model; this does not undo previous hard-threshold seed decisions |
| `__end__` + completed generation | Stop this main's generation loop | Later configured mains still run |
| `max_gen` reached | Stop at `gen_(max_gen-1)` | Independent cap, not a convergence guarantee |
| `__failed__` in tasks passed to `check_finish` | Raise `RuntimeError`, even if `__ok__` also exists | Generic wait does not auto-skip CP2K invalid tasks |
| Lost atoms detected after MD wait | Log warning, then proceed to selection | MD scripts can write `__ok__` after an unsuccessful command; available trajectory conversion can still fail |
| Missing `__ok__` without `__failed__` | Keep waiting | `pending_warning_hours` warns only for started, unfinished SCF tasks; it is not a timeout |
| No successful SCF labels collected | Write unsuccessful paths and raise | A completion marker is not proof of SCF convergence or acceptable force |
| Descriptor exception/memory guard failure | Failure record, `__error__`, exception to parent | Inspect stage and error; not all such records indicate an actual OOM |
| Post-sampling coverage exception | Warning; continue to final training/bundling | Workflow completion alone does not prove coverage artifacts exist |

Training/MD/DFT generated scripts and validators must be inspected together. In this snapshot, sampling training and DFT scripts write `__ok__` after running the command without a general exit-code guard; model-file checks and limited `Killed`/`nan` log checks do not certify arbitrary failures. Do not infer robust failure handling merely from the existence of `check_finish` or old helper functions.

For DCBF `stru.pkl`, all enabled per-seed hard metrics must pass before removing that seed. This rule applies with either budget scope. Plateau is a whole-main termination mechanism, not a per-seed hard pass. DAS does not use this coverage rule; its seed/collection behavior follows its own ambiguity path.

## Resume And Finalization

- `check_run_position` chooses from existing main/gen directories; `gen_while_loop` skips a generation with `__ok__`. Existing markers/configs can therefore dominate edits to the original JSON. Inspect effective files before claiming a config edit will alter a resumed generation.
- One existing DCBF `*_sample_filter.xyz` is reused; multiple matches raise. A nonempty `candidate_selected.xyz` is also reused. These checks are not full content/model/config cache validation.
- Existing SCF directories are reused. All completed tasks skip resubmission; any started tasks cause the controller to wait on the existing set. If none started and `start_calc.py` exists, submit it once. Do not delete markers or resubmit blindly when jobs may still exist in the queue.
- `__candidate_batch_merged__` and the training-history manifest guard ordinary batch re-append; the pool is cleared only after update returns. Read the manifest and cached source mappings before recovery.
- DFT collection distinguishes completed, successfully parsed/converged, and force-accepted counts. Raw archives and source mappings are part of recovery, not disposable plotting output.
- The force test is strict `max(norm(force_i)) < force_threshold`. If parsed structures exist but none pass, `finalize_scf_collection` still selects the structure with the smallest maximum force as `minimum_force_fallback`. `force_count=0` can therefore coexist with one output/training structure; it is not a hard rejection of every over-threshold frame.
- `training.submit=false` executes training locally. `wait=false` skips waiting but the code still checks the model file and proceeds toward prediction/bundling; it is not a complete detached-finalization workflow.
- The top-level caller catches coverage failures and some plot failures. Shared CFG cleanup occurs when the finalization call path returns, not after an independent audit that every optional artifact succeeded. See [storage-and-recovery.md](storage-and-recovery.md).

These are source-audited behaviors, not a claim that all remote schedulers or scientific engines have been tested. Treat contradictions or suspicious behavior as findings to explain, not permission to modify sampling code.
