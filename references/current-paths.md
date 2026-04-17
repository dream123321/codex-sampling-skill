# Current Paths

Prefer these locations when the current project matches the packaged OCBF deployment used in recent sessions.

## Preferred package root

- `/public/home/huangjing/app/ocbf/app/ocbf_one-button_deployment/source/OCBF`

## Preferred docs

- `/public/home/huangjing/app/ocbf/app/ocbf_one-button_deployment/source/OCBF/ocbf_parameter_guide_complete.html`
- `/public/home/huangjing/app/ocbf/app/ocbf_one-button_deployment/source/OCBF/README.md`

## Preferred examples

- `/public/home/huangjing/app/ocbf/app/ocbf_one-button_deployment/source/OCBF/example/sample/ocbf.init_dataset.vasp.test.json`
- `/public/home/huangjing/app/ocbf/app/ocbf_one-button_deployment/source/OCBF/example/sample_json/ocbf.annotated.jsonc`

## Source code paths for defaults

- `/public/home/huangjing/app/ocbf/app/ocbf_one-button_deployment/source/OCBF/ocbf/ocbf/bootstrap.py`
- `/public/home/huangjing/app/ocbf/app/ocbf_one-button_deployment/source/OCBF/ocbf/ocbf/runtime_config.py`
- `/public/home/huangjing/app/ocbf/app/ocbf_one-button_deployment/source/OCBF/ocbf/ocbf/cli_defaults.py`
- `/public/home/huangjing/app/ocbf/app/ocbf_one-button_deployment/source/OCBF/ocbf/ocbf/high_precision_training.py`

## Fallback discovery rule

If the preferred package root is absent, search for an OCBF tree containing all of these:

- `ocbf_parameter_guide_complete.html`
- `README.md`
- `example/sample`
- `ocbf/ocbf/bootstrap.py`

Prefer `source/OCBF` first, then `source/OCBF_stability`.
