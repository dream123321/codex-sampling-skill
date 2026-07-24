#!/usr/bin/env python3
"""Remember one verified DCBF deployment root per local or remote target."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile


SCHEMA_VERSION = 1
DEFAULT_REPOSITORY = "https://github.com/dream123321/DCBF"
DEFAULT_STATE_PATH = Path.home() / ".dcbf" / "dcbf_training_installations.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def resolve_state_path(raw_path: str | None) -> Path:
    configured = raw_path or os.environ.get("DCBF_SKILL_STATE_FILE")
    return Path(configured).expanduser() if configured else DEFAULT_STATE_PATH


def empty_state() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "last_target": None,
        "installations": {},
    }


def load_state(path: Path) -> dict:
    if not path.exists():
        return empty_state()
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Could not read installation state {path}: {exc}") from exc
    if state.get("schema_version") != SCHEMA_VERSION:
        raise SystemExit(
            f"Unsupported installation-state schema in {path}: "
            f"{state.get('schema_version')!r}"
        )
    if not isinstance(state.get("installations"), dict):
        raise SystemExit(f"Invalid installations mapping in {path}")
    return state


def write_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(state, indent=2, ensure_ascii=True) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        handle.write(payload)
        temporary_path = Path(handle.name)
    temporary_path.replace(path)


def normalize_target(raw_target: str | None) -> str:
    target = (raw_target or os.environ.get("DCBF_SKILL_TARGET") or "local").strip()
    if not target or any(char in target for char in "\r\n\t"):
        raise SystemExit("Target must be a non-empty single-line identifier")
    return target


def normalize_deployment_root(raw_path: str) -> str:
    root = raw_path.strip().rstrip("/\\")
    if not root:
        raise SystemExit("Deployment root must not be empty")
    is_posix_absolute = root.startswith("/")
    is_windows_absolute = bool(re.match(r"^[A-Za-z]:[\\/]", root))
    if not (is_posix_absolute or is_windows_absolute):
        raise SystemExit(
            "Deployment root must be absolute so it remains unambiguous across tasks"
        )
    return root


def selected_entry(state: dict, target: str) -> dict | None:
    entry = state["installations"].get(target)
    return dict(entry) if isinstance(entry, dict) else None


def emit(value: dict | list, as_json: bool) -> None:
    if as_json:
        print(json.dumps(value, indent=2, ensure_ascii=True))
        return
    if isinstance(value, list):
        if not value:
            print("No DCBF installations are remembered.")
            return
        for item in value:
            print(f"{item['target']}: {item['deployment_root']}")
        return
    for key, item in value.items():
        print(f"{key}: {item}")


def command_status(args: argparse.Namespace) -> int:
    state_path = resolve_state_path(args.state_file)
    state = load_state(state_path)
    target = normalize_target(args.target)
    entry = selected_entry(state, target)
    result = {
        "found": entry is not None,
        "target": target,
        "state_file": str(state_path),
    }
    if entry is not None:
        result.update(entry)
    emit(result, args.json)
    return 0 if entry is not None else 1


def command_remember(args: argparse.Namespace) -> int:
    state_path = resolve_state_path(args.state_file)
    state = load_state(state_path)
    target = normalize_target(args.target)
    entry = {
        "deployment_root": normalize_deployment_root(args.path),
        "source": args.source,
        "repository": args.repository,
        "version": args.version,
        "remembered_at": utc_now(),
    }
    state["installations"][target] = entry
    state["last_target"] = target
    write_state(state_path, state)
    result = {
        "remembered": True,
        "target": target,
        "state_file": str(state_path),
        **entry,
    }
    emit(result, args.json)
    return 0


def command_list(args: argparse.Namespace) -> int:
    state_path = resolve_state_path(args.state_file)
    state = load_state(state_path)
    items = [
        {"target": target, **entry}
        for target, entry in sorted(state["installations"].items())
        if isinstance(entry, dict)
    ]
    if args.json:
        emit(
            {
                "state_file": str(state_path),
                "last_target": state.get("last_target"),
                "installations": items,
            },
            True,
        )
    else:
        emit(items, False)
    return 0


def command_forget(args: argparse.Namespace) -> int:
    state_path = resolve_state_path(args.state_file)
    state = load_state(state_path)
    target = normalize_target(args.target)
    existed = state["installations"].pop(target, None) is not None
    if state.get("last_target") == target:
        state["last_target"] = next(iter(state["installations"]), None)
    write_state(state_path, state)
    emit(
        {
            "forgotten": existed,
            "target": target,
            "state_file": str(state_path),
        },
        args.json,
    )
    return 0 if existed else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Remember a verified DCBF deployment root per target machine."
    )
    parser.add_argument(
        "--state-file",
        help="override the state file; defaults to ~/.dcbf/dcbf_training_installations.json",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="show one remembered target")
    status.add_argument("--target", help="local or a stable user@host:port identifier")
    status.add_argument("--json", action="store_true")
    status.set_defaults(handler=command_status)

    remember = subparsers.add_parser("remember", help="record a verified deployment")
    remember.add_argument("--target", help="local or a stable user@host:port identifier")
    remember.add_argument("--path", required=True, help="absolute deployment root")
    remember.add_argument(
        "--source",
        choices=("existing", "github-release", "manual"),
        default="existing",
    )
    remember.add_argument("--repository", default=DEFAULT_REPOSITORY)
    remember.add_argument("--version")
    remember.add_argument("--json", action="store_true")
    remember.set_defaults(handler=command_remember)

    list_parser = subparsers.add_parser("list", help="list all remembered targets")
    list_parser.add_argument("--json", action="store_true")
    list_parser.set_defaults(handler=command_list)

    forget = subparsers.add_parser("forget", help="remove one remembered target")
    forget.add_argument("--target", help="local or a stable user@host:port identifier")
    forget.add_argument("--json", action="store_true")
    forget.set_defaults(handler=command_forget)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
