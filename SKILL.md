---
name: ocbf-sampling
description: Project-aware guidance for OCBF sampling workflows, JSON configuration, scheduler/task submission, and the helper commands create-init, mp-search, and train. Use when Codex needs to prepare, review, explain, or troubleshoot an OCBF sampling run, identify the minimum missing parameters before running `ocbf run`, adapt example configs, choose defaults, or explain which queue/engine/environment settings the user still needs to provide.
---

# OCBF Sampling

## Overview

Use this skill to work on OCBF sampling and submission tasks with the minimum necessary questioning.
Treat the current packaged deployment as the default source of truth, but remain usable for other OCBF trees.

Load these references first when relevant:

- For project-aware paths and preferred discovery order: [references/current-paths.md](references/current-paths.md)
- For code-derived defaults and scheduler behavior: [references/defaults.md](references/defaults.md)
- For the minimum parameter checklist by task: [references/parameter-intake.md](references/parameter-intake.md)

## Workflow

1. Rebuild context from files before asking questions.
2. Prefer the current package docs and examples over memory:
   - `ocbf_parameter_guide_complete.html`
   - `README.md`
   - `example/sample/ocbf.init_dataset.vasp.test.json`
   - `example/sample_json/ocbf.annotated.jsonc`
3. Identify which task the user actually wants:
   - `ocbf run` sampling workflow
   - `create-init`
   - `mp-search`
   - `train`
   - explanation/debugging of the above
4. Ask only for blocking inputs that cannot be discovered from the package, examples, or code defaults.
5. Auto-fill non-blocking fields from current defaults/examples and state those assumptions explicitly.

## Minimal Question Policy

- Do not ask for parameters that can be discovered from the package or inferred safely from the current example flow.
- Do ask for parameters that change the actual submission target or make the run impossible.
- When the user says to use defaults, use current code defaults or example defaults and list them clearly.
- When adapting an example, preserve the example structure and only ask for the fields that must change.

## Task Playbooks

### `ocbf run` / JSON sampling

1. Check whether the user wants:
   - a new config from scratch,
   - an adaptation of the packaged example,
   - or a review of an existing config.
2. For a new or adapted run, ask only for the blocking fields listed in [references/parameter-intake.md](references/parameter-intake.md).
3. Default the remaining sampling fields from code defaults unless the user requests a different policy.
4. Surface assumptions explicitly, especially for:
   - `parameter.*`
   - `scheduler.*`
   - whether `dataset.builder`, `training`, or `summary` are enabled

### `create-init`

- Usually ask nothing.
- Only ask a follow-up if the target directory already contains conflicting paths or if the user wants a non-default source template.

### `mp-search`

- Treat element list and API key as the main blocking inputs.
- Default `output_dir` to `mp-stru` and `csv_name` to `summary.csv` unless the user asks to override.
- Remind the user that network access to Materials Project is required.

### `train`

- Treat input xyz/extxyz as the main blocking input.
- Default template/backend/queue/cores/ptile/train env unless the user asks to override them.
- Ask for explicit `elements` only if the user wants a fixed ordering or the inferred order is likely to be wrong for their case.

## Submission Guidance

- Always determine or confirm:
  - DFT engine
  - submission backend
  - queue/partition
  - core count and ptile/tasks-per-node
  - `dft_env` and `dft_command`
- Use scheduler normalization defaults only when the user does not provide an override and the default is safe.
- If the user’s cluster conventions are unclear, ask for the submission backend and the actual DFT launch command before fabricating them.

## Assumption Reporting

Whenever defaults are auto-filled, summarize them as concrete assumptions instead of hiding them.

Good pattern:

```text
Assumptions used:
- submission_backend=bsub
- train_sus_queue=33
- train_sus_cores=40
- parameter.sample.n=5
- parameter.candidate_trigger=10
```

## What Not To Do

- Do not treat stale memory as truth when the package files disagree.
- Do not ask the user to restate fields that are already visible in their JSON or example directory.
- Do not silently invent cluster commands when `dft_command` or backend choice is genuinely unknown.
- Do not expose passwords, tokens, or other secrets in the skill or its references.
