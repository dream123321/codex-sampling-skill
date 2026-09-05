#!/usr/bin/env python3
"""Read-only checks of documented sampling behavior in a trusted DCBF source tree."""

from __future__ import annotations

import argparse
import ast
from collections import Counter, OrderedDict
from contextlib import redirect_stdout
import io
import json
import math
from numbers import Real
from pathlib import Path
from types import SimpleNamespace


def tree(path):
    return ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))


def source_functions(root, relative, names, namespace, class_name=None):
    parsed = tree(root / relative)
    body = parsed.body
    if class_name:
        body = next(n for n in body if isinstance(n, ast.ClassDef) and n.name == class_name).body
    nodes = [n for n in body if isinstance(n, ast.FunctionDef) and n.name in names]
    if {n.name for n in nodes} != set(names):
        raise AssertionError(f"Missing audited functions in {relative}: {set(names) - {n.name for n in nodes}}")
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(relative), "exec"), namespace)


def equal(actual, expected):
    if actual != expected:
        raise AssertionError(f"Expected {expected!r}, got {actual!r}")


def raises_value_error(function, *args):
    try:
        function(*args)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def class_method(root, relative, class_name, method):
    cls = next(n for n in tree(root / relative).body if isinstance(n, ast.ClassDef) and n.name == class_name)
    return next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method)


def call_names(node):
    names = []
    for item in ast.walk(node):
        if isinstance(item, ast.Call):
            function = item.func
            if isinstance(function, ast.Name):
                names.append(function.id)
            elif isinstance(function, ast.Attribute):
                names.append(function.attr)
    return names


def audit(deployment):
    source = deployment / "source/DCBF/dcbf/dcbf"
    if not source.is_dir():
        raise ValueError("--source-root must contain source/DCBF/dcbf/dcbf")
    checks = []

    def check(name, function):
        try:
            function()
        except Exception as exc:
            checks.append({"name": name, "passed": False, "error": f"{type(exc).__name__}: {exc}"})
        else:
            checks.append({"name": name, "passed": True})

    env = {"math": math, "Real": Real, "OrderedDict": OrderedDict, "Counter": Counter}
    source_functions(source, "runtime_config.py", {"build_md_loop_schedule", "_strip_json_comments"}, env)
    source_functions(source, "candidate_pool.py", {"resolve_candidate_trigger"}, env)
    source_functions(source, "selection/core.py", {"frequency_counter"}, env)
    source_functions(source, "encode/find_min_cover_set.py", {"select_last_fraction", "fwss"}, env)
    source_functions(source, "encode/convergence_control.py", {"evaluate_metric_convergence"}, env)
    source_functions(source, "encode/coverage_policy.py", {
        "_as_float_list", "normalize_coverage_thresholds", "validate_selection_schedules",
        "determine_structure_budget", "stable_unique", "strict_budget_selection",
        "aggregate_element_coverages", "scalar_thresholds_for_mean_descriptor",
        "select_per_configuration_candidates",
    }, env)
    source_functions(source, "encode/mlp_encode_sample_flow.py", {
        "_rates_reach_thresholds", "_next_md_configurations",
    }, env)

    schedule = env["build_md_loop_schedule"]
    check("paired ensemble skips", lambda: equal(schedule([[200], [], [600]], [[], [300], [600]]), [
        {"npt": [200], "nvt": []}, {"npt": [], "nvt": [300]}, {"npt": [600], "nvt": [600]},
    ]))
    check("single ensemble", lambda: equal(schedule(None, [[300]]), [{"npt": [], "nvt": [300]}]))
    for name, npt, nvt in [
        ("both null", None, None), ("outer mismatch", [[200]], [[300], [400]]),
        ("both skipped", [[]], [[]]), ("empty outer", [], None),
        ("bad sublist", [300], None), ("nonfinite temperature", [[float("inf")]], None),
    ]:
        check(f"reject {name}", lambda npt=npt, nvt=nvt: raises_value_error(schedule, npt, nvt))

    budget = env["determine_structure_budget"]
    for value, expected in [(99.4, 12), (99.5, 8), (99.9, 5), (99.95, 0)]:
        check(f"budget boundary {value}", lambda value=value, expected=expected: equal(
            budget([value], [12, 8, 5], [99.5, 99.9, 99.95])[0], expected))
    check("nested thresholds", lambda: equal(budget([99.0, 99.9], [8, 3], [[98, 99], [99, 99.9]])[:2], (0, True)))
    check("zero strict budget", lambda: equal(env["strict_budget_selection"]([3, 3, 4], 0), []))
    check("stable strict dedup", lambda: equal(env["strict_budget_selection"]([3, 3, 4, 5], 2), [3, 4]))
    check("tail is list fraction, not budget fraction", lambda: equal(env["select_last_fraction"](list(range(13)), 5), [10, 11, 12]))
    check("tail limited by budget", lambda: equal(env["select_last_fraction"](list(range(13)), 1), [12]))
    check("tail at least one provisional", lambda: equal(env["select_last_fraction"]([9], 0), [9]))

    def fwss_is_approximate():
        with redirect_stdout(io.StringIO()):
            _, _, selected = env["fwss"]([[i] for i in range(13)], list(range(13)), 5)
        equal(len(selected), 5)
        with redirect_stdout(io.StringIO()):
            _, _, selected = env["fwss"]([[i] for i in range(12)], list(range(12)), 5)
        if len(selected) <= 5:
            raise AssertionError("The documented shared-FWSS over-budget example changed")
    check("FWSS not a strict cap", fwss_is_approximate)

    def per_seed_budget():
        selected, budgets = env["select_per_configuration_candidates"](
            {"A": [0, 1, 2], "B": [3, 4]},
            {"two": {"A": [80], "B": [100]}}, ["two"],
            {"A": [1, 2], "B": [3, 4]}, [0, 3],
            {"A": [80], "B": [100]}, True, [2], [99.9], 1,
        )
        equal(selected, [0, 1])
        equal(dict(budgets), {"A": 2, "B": 0})
    check("mean priority and per-seed strict budget", per_seed_budget)

    trigger = env["resolve_candidate_trigger"]
    check("integer trigger", lambda: equal(trigger(10, 3635)[0], 10))
    check("percent trigger rounds up", lambda: equal(trigger("1%", 3635)[0], 37))
    check("percent trigger minimum one", lambda: equal(trigger("1%", 0)[0], 1))
    check("trigger rejects zero", lambda: raises_value_error(trigger, 0, 10))

    convergence = env["evaluate_metric_convergence"]
    history = [{"gen": i, "metric": 99 - i} for i in range(7)]
    check("declines can plateau", lambda: equal(convergence(history, 99.95, 7, .2)["plateau_converged"], True))
    check("plateau disabled by omission", lambda: equal(convergence(history, 99.95)["converged"], False))
    check("hard threshold equality", lambda: equal(convergence([{"gen": 0, "metric": 99.95}], 99.95)["hard_converged"], True))
    check("plateau strict delta comparison", lambda: equal(convergence(
        [{"gen": 0, "metric": 90}, {"gen": 1, "metric": 91}], 99, 2, 1)["plateau_converged"], False))

    def seeds():
        names, _ = env["_next_md_configurations"](
            {"A": [0], "B": [1], "C": [2]}, True,
            {"A": [100], "B": [100], "C": [100]},
            {"two": {"A": [100], "B": [99.9], "C": [100]},
             "three": {"A": [99], "B": [99.9]}},
            ["two", "three"], 99.9, [99.9],
        )
        equal(names, ["A", "C"])
    check("seeds use all hard metrics, missing rates fail", seeds)

    def early_candidate_branch(selected_count, candidate_count, report=None):
        touched = []
        local = {
            "touch": lambda path, marker: touched.append(marker),
            "load_npt_volume_filter_report": lambda path: report,
        }
        source_functions(source, "generation.py", {"_run_candidate_batch_stage"}, local, "GenerationRunner")
        runner = SimpleNamespace(
            _append_generation_selection_to_candidate_pool=lambda: (selected_count, candidate_count),
            _candidate_trigger_threshold=lambda: (10, "10", 100),
            logger=SimpleNamespace(info=lambda *args: None), workspace="unused-in-memory",
        )
        local["_run_candidate_batch_stage"](runner)
        return touched
    check("zero current selection ends despite full old pool", lambda: equal(early_candidate_branch(0, 50), ["__end__"]))
    check("all-volume-filtered selection does not end", lambda: equal(early_candidate_branch(0, 50, {
        "enabled": True, "original_selected_count": 3, "kept_count": 0,
    }), []))
    check("below-trigger selection returns without DFT", lambda: equal(early_candidate_branch(3, 9), []))

    def active_calls():
        names = call_names(class_method(source, "generation.py", "GenerationRunner", "run"))
        if "_run_candidate_batch_stage" not in names:
            raise AssertionError("Candidate stage dispatch changed")
        if any(name in names for name in ("_run_scf_stage_with_encoding", "_run_scf_stage_without_encoding")):
            raise AssertionError("Legacy SCF stage became active")
        if "check_dft_finish" in call_names(tree(source / "generation.py")):
            raise AssertionError("DFT-specific wait is now called; update failure documentation")
    check("active dispatch and generic SCF wait", active_calls)

    def prepare_order():
        method = class_method(source, "cli.py", "DCBFApplication", "run_from_config")
        prepare = next(n.lineno for n in ast.walk(method) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "prepare_workspace")
        guard = next(n.lineno for n in method.body if isinstance(n, ast.If) and isinstance(n.test, ast.Name) and n.test.id == "prepare_only")
        if prepare >= guard:
            raise AssertionError("prepare-only ordering changed; update side-effect warning")
        calls = call_names(class_method(source, "bootstrap.py", "WorkspaceBootstrapper", "prepare_workspace"))
        if "ensure_dataset" not in calls:
            raise AssertionError("Builder call path changed")
    check("builder precedes prepare-only guard", prepare_order)

    syntax_files = list(source.rglob("*.py"))
    check("source Python parses", lambda: [tree(path) for path in syntax_files])
    examples = deployment / "source/DCBF/example"
    paths = sorted([*examples.glob("sample/*.json"), *examples.glob("sample_json/*.json"), *examples.glob("sample_json/*.jsonc")])
    parsed_examples = {}
    for path in paths:
        def parse_example(path=path):
            parsed_examples[path.relative_to(examples).as_posix()] = json.loads(env["_strip_json_comments"](path.read_text(encoding="utf-8-sig")))
        check(f"parse example {path.relative_to(examples)}", parse_example)
    if not paths:
        checks.append({"name": "examples exist", "passed": False, "error": "No sample/sample_json files found"})

    bootstrap_class = next(n for n in tree(source / "bootstrap.py").body if isinstance(n, ast.ClassDef) and n.name == "WorkspaceBootstrapper")
    defaults = next(ast.literal_eval(n.value) for n in bootstrap_class.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "DEFAULT_PARAMETER_VALUES" for t in n.targets))
    keys = ["encoding_cores", "dimension_min_cover_workers", "coverage_threshold_schedule", "state_population", "plateau_generations", "min_coverage_delta", "report_state_population_zero_baseline"]
    expected_code = [2, 4, [99.5, 99.9, 99.95], 0, None, None, False]
    check("documented omitted defaults", lambda: equal([defaults[k] for k in keys], expected_code))
    main_sample = parsed_examples.get("sample/dcbf.init_dataset.vasp.test.json", {})
    mode = main_sample.get("sampling", {}).get("structure_selection", {}).get("modes", {}).get("mlp_encode_model", {})
    expected_sample = [4, 4, [99.5, 99.9, 99.92], 2, 7, .2, True]
    check("documented main sample values", lambda: equal([mode.get(k) for k in keys], expected_sample))
    scheduler = main_sample.get("sampling", {}).get("scheduler", {})
    scheduler_keys = ["submission_backend", "train_sus_cores", "lmp_cores", "scf_cores", "dft_clean_dcbf_environment"]
    check("documented main sample scheduler", lambda: equal(
        [scheduler.get(k) for k in scheduler_keys], ["bsub", 56, 56, 28, False]))
    comparison = {name: {
        "enabled_modes": [k for k, v in cfg.get("sampling", {}).get("structure_selection", {}).get("modes", {}).items() if v.get("enabled")],
        "mlp_encode_model": {k: cfg.get("sampling", {}).get("structure_selection", {}).get("modes", {}).get("mlp_encode_model", {}).get(k, defaults[k]) for k in keys},
    } for name, cfg in parsed_examples.items()}
    return {
        "passed": all(item["passed"] for item in checks), "checks": checks,
        "python_files_parsed": len(syntax_files), "source_defaults": {k: defaults[k] for k in keys},
        "example_comparison": comparison,
        "limits": "Read-only source/default and isolated-function checks; no scientific-engine, scheduler, full-MD, or crash-recovery validation.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True, help="trusted DCBF deployment root")
    parser.add_argument("--json", action="store_true", help="print full evidence and example comparison")
    args = parser.parse_args()
    try:
        result = audit(args.source_root.resolve())
    except Exception as exc:
        result = {"passed": False, "error": f"{type(exc).__name__}: {exc}"}
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=True))
    else:
        for item in result.get("checks", []):
            print(f"{'PASS' if item['passed'] else 'FAIL'} {item['name']}" + (f": {item['error']}" if not item["passed"] else ""))
        if result.get("error"):
            print(result["error"])
        print("Audit passed" if result["passed"] else "Audit failed")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
