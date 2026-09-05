# Source Audit And Verification Map

Audit date: 2026-09-05. The comparison source was a user-supplied temporary low-disk deployment; it is deliberately not an installation-state entry or a hard-coded path in this skill. Local snapshot hashes for bootstrap, generation, the active descriptor flow, and the main sample JSON matched the remote files when this audit was implemented.

## Evidence Levels

- **Control-flow audited**: active calls, conditions, defaults, and output responsibilities were inspected. This is not a scientific validation of a potential or DFT parser.
- **Pure-function checked**: the companion script executes selected existing source functions in isolation, without importing the full DCBF application or starting jobs.
- **Static boundary checked**: caller order and inactive legacy branches were inspected; no production scheduler/MD/DFT test is implied.
- Full numerical equivalence of real trajectories, all four DFT engines, all DAS clustering inputs, crash recovery at every write boundary, and optional analysis success remain outside this documentation-only validation.

## Source-To-Behavior Index

Paths below are relative to `$DCBF_ROOT/source/DCBF/dcbf/dcbf/`. Locate symbols in the active version instead of relying on line numbers that drift.

| Files / symbols | Behavior recorded in the skill | Evidence |
|---|---|---|
| `cli.py`: `run_from_config`, managed-run entry | Builder precedes prepare-only return; main loop, pool leftovers, export, coverage, final training, cleanup | Control-flow / static |
| `bootstrap.py`: normalization, defaults, `prepare_workspace`, `write_parameter_yaml` | Public schema, forced/ignored values, builder activation, elements, runtime and generation configs | Control-flow; defaults checked |
| `runtime_config.py`: `build_md_loop_schedule`, scheduler normalization/rendering | Paired ensemble skips, queue/resources, DFT cleaner order, machine-specific command defaults | Control-flow; schedule checked |
| `dataset_builder.py`: `ensure_dataset`, generation, dedup, SCF methods | generated_only/augment_existing, per-strain rattle, phonon, ASE MD, reuse and label merge | Control-flow; no new MD/DFT run |
| `das/gen_while_loop.py`: `check_run_position`, `copy_init`, `gen_while_loop` | Resume directory/marker precedence, main/gen cap, existing YAML, monitored generation child | Control-flow |
| `generation.py`: `run`, training/MD/select/candidate/collect methods | Actual active stage chain, pool decisions, DFT resume, collection/archive/update | Control-flow; early pool branches checked |
| `das/train_mlp.py`: `pre_train_mlp`, `update_mlp_from_current_batch`, script rendering | First training vs copy/reuse, warm updates, shared CFG and merge marker | Control-flow; exit-code handling inspected, not assumed |
| `das/mkdir.py`, `das/lmps_scripts.py`, `das/lmps_bsub.py` | .vasp seed enumeration, previous stru.pkl, MD directories, model reruns, templates and markers | Control-flow/template inspection |
| `das/work_dir.py`, `das/other.py` | Task polling, failed markers, started-task warning hours, runtime-error/step logging | Control-flow; not real queue validation |
| `encode/cfg_descriptor_encode.py`, `mlp_mul_encode.py`, `file_conversion.py`, `extract_md_out.py` | CFG/descriptor execution and trajectory conversion, frame ordering and worker boundaries | Call/data-path inspection |
| `encode/descriptor_store.py`, `mlp_encoding_extract.py`, `mean_encoding_extract.py` | Numeric/mmap stores, metadata, element/body mapping, mean over selected components | Data-path inspection |
| `encode/data_distri.py`, `coverage_rate.py`, `compact_indices.py`, `selection/core.py` | Bin counts/edges, low-frequency intervals, sample-weighted coverage and compact grouping; encode/selection_core.py re-exports selection/core.py | Control/numerical-expression inspection |
| `encode/mlp_encode_sample_flow.py` | Current/gen-0 descriptor models, per-seed coverage, element gating, selection, logs, cleanup | Control-flow; seed function checked |
| `encode/mean_select.py`, `find_min_cover_set.py` | Per-seed mean cutoff, ranked-list tail, FWSS, candidate union | Control-flow; tail and FWSS checks |
| `encode/coverage_policy.py`, `convergence_control.py` | Threshold stages, strict per-seed budgets, aggregation, signed plateau | Pure-function checks plus control-flow |
| `encode/dimension_min_cover.py` | Per-dimension solve, union, reverse prune, CPU/memory worker limits | Control-flow; no full solver-equivalence claim |
| `encode/mlp_return_strupkl.py`, `selected_frames.py`, `npt_volume_filter.py` | Seed continuation separate from final selected frames; post-selection volume filter | Control-flow; seed decisions checked |
| `das/calc_ensemble_ambiguity.py`, `das_update_ambiguity.py`, `sample_xyz.py`, `descriptor_encoder_xyz.py`, `scf_lmp_data.py` | DAS uncertainty, adaptive/fixed routing, MBTR/Birch, selected-file seed behavior | Call/parameter-path inspection; numerical DAS not rerun |
| `candidate_pool.py`, `training_dataset.py` | Count/percentage trigger, append markers, shared CFG and persistent shards | Control-flow; trigger checked |
| `das/main_calc.py`, `gen_calc_file.py` | DFT grouping, input generation and submission scripts | Control/template inspection |
| `das/{vasp,abacus,cp2k,qe}_main_xyz.py`, engine collectors, `scf_filter_sources.py` | __ok__-gated parse, source mapping, force filter and minimum-force fallback | Collector/control-path inspection; engine convergence not revalidated |
| `raw_dft_archive.py`, `artifact_bundle.py`, `core_hours.py` | Raw/excluded archives, summary placement, cleanup boundaries, accounting | Static/control inspection; storage reference |
| `memory_guard.py` | Stage report, process-tree memory, allocation guards, parent supervision | Control-flow inspection; no deliberate OOM run |
| `high_precision_training.py`, CLI/default helpers, `coverage_pca.py` | Post-sampling analysis/training ordering, submit/wait behavior, separate visualization semantics | Public-interface and caller inspection |
| `reduce.py`, `fast_extxyz.py` | Distinct population modes, I/O backends, model fallback, approximate chunk size | Related-interface check, not changed by this skill update |

## Existing Code Is Not Necessarily Active

- `GenerationRunner.run` calls `_run_candidate_batch_stage`; the older `_run_scf_stage_with_encoding` and `_run_scf_stage_without_encoding` methods are not the active stage dispatch. Do not use them to explain candidate-trigger behavior.
- `check_dft_finish` / `is_dft_invalid_dir` remain defined, but the inspected generation SCF waits call `check_finish`. Do not claim known-invalid CP2K tasks are automatically skipped by that wait.
- Later definitions can replace earlier helpers: repeated `parallel_process` definitions in descriptor files route to the last definition, not the earlier legacy Pool implementation.
- Removed public aliases inside legacy normalization/helpers do not override the public JSON rejection rules.
- Logging can occur before later truncation/filtering. Trace the writer of the final output rather than treating any selected_count log as the final DFT count.

## Repeatable Read-Only Check

```bash
python scripts/audit_sampling_source.py --source-root "$DCBF_ROOT" --json
```

The script parses source/examples, checks documented defaults, and runs selected pure source functions for schedule validation, budgets, mean-tail selection, plateau, trigger percentages, and seed continuation. It also exercises only the early-return candidate branches with in-memory test doubles. It does not execute builder, imports of the full application, MD, DFT, training, or scheduler submission. Run it only on a trusted source tree: selected function definitions are executed as Python.

An audit failure means an assumption/test no longer matches the source; inspect and update the documentation from code. Never edit scientific code just to make a documentation audit pass. `quick_validate.py` checks the skill package, not DCBF scientific correctness.

Recorded result for the 2026-09-05 snapshot: all 44 checks passed, including syntax parsing of 83 Python files and parsing of 6 sample/sample_json JSON or JSONC files. These counts describe this snapshot, not a promise that a later release has identical files or behavior.

## Updating This Reference

Resolve the live package path and compare source/runtime before diagnosing a running job. Record the inspection date and symbol-level evidence; use the user's actual JSON, effective generation YAML, runtime config, and current CLI help for live values. Compare sample and sample_json separately. Do not store a temporary audit deployment in installation memory or publish credentials, private workspace contents, or transient server paths.

The skill continues to use Latest only when installing a release. It does not add automatic release checks or upgrades for an already remembered installation.
