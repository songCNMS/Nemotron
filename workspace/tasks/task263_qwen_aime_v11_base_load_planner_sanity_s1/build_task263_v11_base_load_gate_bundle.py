#!/usr/bin/env python3
"""Build task263 V11 base-load/import gate evidence.

This task-owned helper is intentionally limited to import/preflight evidence:
it never launches SFT training, export, endpoint serving, AIME/task243 eval, or
30B/8-GPU work.  When ``--run-bridge-probe`` is supplied it invokes the existing
Qwen3-4B Megatron-Bridge import command and records either proof output or the
exact runtime blocker.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import shlex
import socket
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "task263_qwen_aime_v11_base_load_planner_sanity_s1"
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_ROOT = REPO_ROOT.parent / "outputs" / TASK_ID
DEFAULT_BASE_PATH = Path("/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507")
DEFAULT_TASK262_ROOT = Path(
    "/work-agents/intern_nemotron_worker_1/outputs/"
    "task262_qwen_aime_v11_data_split_sidecar_s1"
)
DEFAULT_SHARED_BOUNDARY = Path("/mnt/cephfs/data/processing/lei.song")
DEFAULT_SYNC_ROOT = Path("/root") / TASK_ID
DEFAULT_TRAIN_ENTRYPOINT = "src/nemotron/recipes/super3/stage1_sft/qwen_local_train.py"
DEFAULT_CONFIG = "src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml"
DEFAULT_IMPORT_SCRIPT = "scripts/import_qwen3_4b_local_to_megatron.py"
QWEN_MODEL_ENV_VAR = "SUPER3_M1_QWEN_HF_MODEL"


def utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def write_text(path: Path, text: str, *, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if executable:
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def write_json(path: Path, data: dict[str, Any]) -> None:
    write_text(path, json.dumps(data, indent=2, sort_keys=True) + "\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_sidecar(path: Path) -> str:
    digest = sha256_file(path)
    path.with_name(f"{path.name}.sha256").write_text(
        f"{digest}  {path.name}\n",
        encoding="utf-8",
    )
    return digest


def package_probe(names: list[str]) -> dict[str, dict[str, str | None]]:
    results: dict[str, dict[str, str | None]] = {}
    for name in names:
        try:
            spec = importlib.util.find_spec(name)
        except Exception as exc:  # noqa: BLE001 - exact blocker evidence
            results[name] = {
                "status": "error",
                "error_type": type(exc).__name__,
                "error": str(exc),
                "origin": None,
            }
            continue
        results[name] = {
            "status": "present" if spec is not None else "missing",
            "error_type": None,
            "error": None,
            "origin": spec.origin if spec is not None else None,
        }
    return results


def q(value: str | os.PathLike[str] | int | float) -> str:
    return shlex.quote(str(value))


def base_file_manifest(base_path: Path) -> dict[str, Any]:
    required_files = [
        "config.json",
        "tokenizer_config.json",
        "tokenizer.json",
        "model.safetensors.index.json",
    ]
    files: list[dict[str, Any]] = []
    missing: list[str] = []
    for name in required_files:
        path = base_path / name
        if not path.is_file():
            missing.append(str(path))
            continue
        files.append(
            {
                "path": str(path),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )

    shard_files = sorted(base_path.glob("model-*.safetensors"))
    shards = [
        {
            "path": str(path),
            "size_bytes": path.stat().st_size,
        }
        for path in shard_files
    ]
    return {
        "base_path": str(base_path),
        "required_files": files,
        "missing_required_files": missing,
        "model_shards_size_only": shards,
        "model_shards_total_size_bytes": sum(item["size_bytes"] for item in shards),
        "model_shards_count": len(shards),
    }


def load_task262_plan(task262_root: Path) -> dict[str, Any]:
    plan_path = task262_root / "v11_qwen_agentic_sft_blend_plan.json"
    manifest_path = task262_root / "manifest.json"
    report_path = task262_root / "task262_v11_data_split_sidecar_report.md"
    plan: dict[str, Any] = {}
    if plan_path.is_file():
        with plan_path.open(encoding="utf-8") as handle:
            loaded = json.load(handle)
        if isinstance(loaded, dict):
            plan = loaded
    return {
        "task262_root": str(task262_root),
        "plan_path": str(plan_path),
        "plan_exists": plan_path.is_file(),
        "plan_sha256": sha256_file(plan_path) if plan_path.is_file() else None,
        "manifest_path": str(manifest_path),
        "manifest_exists": manifest_path.is_file(),
        "manifest_sha256": sha256_file(manifest_path) if manifest_path.is_file() else None,
        "report_path": str(report_path),
        "report_exists": report_path.is_file(),
        "report_sha256": sha256_file(report_path) if report_path.is_file() else None,
        "plan": plan,
    }


def render_bridge_probe_script(*, repo_dir: Path, base_path: Path, output_dir: Path, log_path: Path) -> str:
    import_output = output_dir / "qwen3_4b_bridge_import_iter0"
    command = (
        "python3 "
        f"{q(repo_dir / DEFAULT_IMPORT_SCRIPT)} "
        f"--hf-path {q(base_path)} "
        f"--output-dir {q(import_output)}"
    )
    return f"""#!/usr/bin/env bash
set -euo pipefail

cd {q(repo_dir)}
export PYTHONPATH="${{PWD}}/src${{PYTHONPATH:+:${{PYTHONPATH}}}}"
export {QWEN_MODEL_ENV_VAR}={q(base_path)}
mkdir -p {q(import_output.parent)} {q(log_path.parent)}

set +e
{command} > {q(log_path)} 2>&1
rc=$?
set -e
echo "BRIDGE_IMPORT_COMMAND={command}" >> {q(log_path)}
echo "BRIDGE_IMPORT_RC=$rc" >> {q(log_path)}
exit "$rc"
"""


def render_fail_closed_preflight_script(
    *,
    repo_dir: Path,
    manifest_path: Path,
    import_log_path: Path,
    preflight_log_path: Path,
) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail

cd {q(repo_dir)}
export PYTHONPATH="${{PWD}}/src${{PYTHONPATH:+:${{PYTHONPATH}}}}"
python3 - <<'PY' > {q(preflight_log_path)} 2>&1
import importlib.util
import json
import re
from pathlib import Path

manifest_path = Path({str(manifest_path)!r})
import_log_path = Path({str(import_log_path)!r})
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
errors = []

for package in ("megatron", "megatron.bridge"):
    try:
        spec = importlib.util.find_spec(package)
    except Exception as exc:
        errors.append(f"{{package}} import probe errored: {{type(exc).__name__}}: {{exc}}")
        continue
    if spec is None:
        errors.append(f"{{package}} is missing")

if not import_log_path.is_file():
    errors.append(f"missing Bridge import log: {{import_log_path}}")
else:
    text = import_log_path.read_text(encoding="utf-8", errors="replace")
    if "IMPORT_DONE" not in text and not re.search(r"successfully loaded checkpoint", text, re.I):
        errors.append("no Bridge-approved import proof or positive checkpoint-load line found")
    if "BRIDGE_IMPORT_RC=0" not in text:
        errors.append("Bridge import command did not complete with rc=0")

schedule = manifest["schedule"]
if schedule["optimizer_lr"] <= 0:
    errors.append("optimizer_lr must be positive")
if schedule["train_iters"] < 2:
    errors.append("train_iters must be >= 2")
if schedule["lr_decay_iters"] <= schedule["train_iters"]:
    errors.append("lr_decay_iters must be greater than train_iters to avoid the task255 zero-LR shape")
if schedule["first_logged_step_expected_lr"] <= 0:
    errors.append("first logged step expected LR must be positive")
if schedule["lr_warmup_iters"] != 0:
    errors.append("lr_warmup_iters must be 0 for this bounded smoke shape")

if errors:
    print("TASK263_FAIL_CLOSED_PREFLIGHT=BLOCK")
    for error in errors:
        print(f"- {{error}}")
    raise SystemExit(2)

print("TASK263_FAIL_CLOSED_PREFLIGHT=PASS")
PY
"""


def run_command(command: list[str], *, cwd: Path, log_path: Path) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        log.write("$ " + " ".join(q(part) for part in command) + "\n")
        log.flush()
        proc = subprocess.run(
            command,
            cwd=cwd,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        log.write(f"COMMAND_RC={proc.returncode}\n")
    return proc.returncode


def run_generated_script(path: Path) -> int:
    """Run a generated script that owns its own log redirection."""

    proc = subprocess.run([str(path)], cwd=REPO_ROOT, text=True, check=False)
    return proc.returncode


def schedule_manifest(*, task262: dict[str, Any]) -> dict[str, Any]:
    datasets = task262.get("plan", {}).get("datasets")
    raw_rows = None
    if isinstance(datasets, list):
        rows = [item.get("rows") for item in datasets if isinstance(item, dict)]
        if rows and all(isinstance(row, int) for row in rows):
            raw_rows = sum(rows)

    global_batch_size = 2
    train_iters = 2
    lr_decay_iters = 20
    optimizer_lr = 5e-6
    return {
        "status": "PLAN_ONLY_BLOCKED_BEFORE_TRAINING",
        "resource_shape": {
            "nodes": 1,
            "gpus_per_node": 2,
            "nproc_per_node": 2,
            "cuda_visible_devices": "0,1",
        },
        "input_data_state": {
            "task262_plan_rows": raw_rows,
            "packed_train_rows_required_before_launch": True,
            "train_iters_formula_after_v11_packing": (
                "max(2, ceil(packed_train_rows / global_batch_size))"
            ),
        },
        "train_iters": train_iters,
        "global_batch_size": global_batch_size,
        "micro_batch_size": 1,
        "seq_length": 8192,
        "optimizer_lr": optimizer_lr,
        "scheduler_min_lr": 5e-7,
        "lr_warmup_iters": 0,
        "lr_decay_iters": lr_decay_iters,
        "first_logged_step_expected_lr": optimizer_lr,
        "why_nonzero_lr": (
            "warmup is 0, optimizer_lr is positive, and lr_decay_iters is "
            "strictly greater than train_iters; this avoids task255's "
            "train_iters=1/lr_decay_iters=1 zero-LR shape."
        ),
        "abort_if": [
            "missing Bridge import/checkpoint-load proof",
            "raw HF path is passed as a Megatron checkpoint root without Bridge import proof",
            "packed train rows are missing or zero",
            "train_iters < 2",
            "lr_decay_iters <= train_iters",
            "first logged learning rate <= 0",
            "first train/valid loss or PPL is NaN/Inf",
            "first train/valid loss or PPL is random-init-scale",
        ],
    }


def render_report(manifest: dict[str, Any]) -> str:
    disposition = manifest["disposition"]
    blocker = manifest["blocker"]
    base = manifest["base_files"]
    env = manifest["environment"]
    schedule = manifest["schedule"]
    paths = manifest["paths"]
    checksums = manifest["artifact_checksums"]
    lines = [
        "# task263 V11 Base-Load Gate Report",
        "",
        f"- Task: `{TASK_ID}`",
        f"- Generated: `{manifest['generated_at_utc']}`",
        f"- Disposition: `{disposition}`",
        f"- Current blocker: `{blocker['summary']}`",
        f"- Repo head: `{manifest['git']['head']}`",
        f"- Base main: `{manifest['git']['origin_main']}`",
        "",
        "## Paths",
        "",
        f"- Local output root: `{paths['output_root']}`",
        f"- NemTron task-owned run root: `{paths['nemtron_run_root']}`",
        f"- Synced repo: `{paths['synced_repo']}`",
        f"- Bridge import log: `{paths['bridge_import_log']}`",
        f"- Fail-closed preflight log: `{paths['fail_closed_preflight_log']}`",
        "",
        "## Base Files",
        "",
        f"- Qwen3-4B base path: `{base['base_path']}`",
        f"- Required-file missing count: `{len(base['missing_required_files'])}`",
        f"- Safetensor shards: `{base['model_shards_count']}` files, "
        f"`{base['model_shards_total_size_bytes']}` bytes total",
        "",
        "| File | Size | SHA256 |",
        "|---|---:|---|",
    ]
    for item in base["required_files"]:
        lines.append(f"| `{item['path']}` | {item['size_bytes']} | `{item['sha256']}` |")

    lines.extend(
        [
            "",
            "## Environment Probe",
            "",
            f"- Host: `{env['hostname']}`",
            f"- Python: `{env['python_executable']}`",
            f"- Platform: `{env['platform']}`",
            "",
            "| Package | Status | Origin / Error |",
            "|---|---|---|",
        ]
    )
    for name, result in env["packages"].items():
        detail = result.get("origin") or result.get("error") or ""
        lines.append(f"| `{name}` | `{result['status']}` | `{detail}` |")

    lines.extend(
        [
            "",
            "## Schedule",
            "",
            f"- Status: `{schedule['status']}`",
            f"- Resource shape: `{schedule['resource_shape']}`",
            f"- `train_iters`: `{schedule['train_iters']}`",
            f"- `global_batch_size`: `{schedule['global_batch_size']}`",
            f"- `optimizer.lr`: `{schedule['optimizer_lr']}`",
            f"- `scheduler.min_lr`: `{schedule['scheduler_min_lr']}`",
            f"- `scheduler.lr_warmup_iters`: `{schedule['lr_warmup_iters']}`",
            f"- `scheduler.lr_decay_iters`: `{schedule['lr_decay_iters']}`",
            f"- First logged step expected LR: `{schedule['first_logged_step_expected_lr']}`",
            f"- Nonzero-LR rationale: {schedule['why_nonzero_lr']}",
            "",
            "## Fail-Closed Conditions",
            "",
        ]
    )
    for condition in schedule["abort_if"]:
        lines.append(f"- {condition}")

    lines.extend(
        [
            "",
            "## Artifact Checksums",
            "",
            "| Artifact | SHA256 |",
            "|---|---|",
        ]
    )
    for path, digest in sorted(checksums.items()):
        lines.append(f"| `{path}` | `{digest}` |")

    lines.extend(
        [
            "",
            "## Boundary Confirmation",
            "",
            "- No SFT training, export, endpoint serving, live AIME/task243 eval, "
            "promotion/go-no-go, task255 checkpoint/export reuse, AIME2025 train "
            "prompt/label use, 30B/8-GPU launch, or shared deletion was performed.",
            "- Smallest remediation: rerun the generated Bridge import probe inside "
            "`nvcr.io/nvidia/nemo:26.02.nemotron_3_super` or another task-owned "
            "NemTron/NeMo environment where `megatron.bridge` is installed, then "
            "rerun the fail-closed preflight and only proceed to bounded smoke "
            "after lead clearance.",
            "",
        ]
    )
    return "\n".join(lines)


def git_value(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()
    except Exception:  # noqa: BLE001 - report unknown rather than fail bundle
        return "UNKNOWN"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--base-path", type=Path, default=DEFAULT_BASE_PATH)
    parser.add_argument("--task262-root", type=Path, default=DEFAULT_TASK262_ROOT)
    parser.add_argument("--nemtron-run-root", type=Path, default=None)
    parser.add_argument("--synced-repo", type=Path, default=None)
    parser.add_argument("--run-bridge-probe", action="store_true")
    parser.add_argument("--run-fail-closed-preflight", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    run_id = utc_now_compact()
    output_root = args.output_root.resolve()
    manifests_dir = output_root / "manifests"
    logs_dir = output_root / "logs"
    scripts_dir = output_root / "scripts"
    reports_dir = output_root / "reports"
    nemtron_run_root = args.nemtron_run_root or DEFAULT_SYNC_ROOT / f"run_{run_id}"
    synced_repo = args.synced_repo or nemtron_run_root / "Nemotron"

    bridge_import_log = logs_dir / f"bridge_import_probe_{run_id}.log"
    fail_closed_log = logs_dir / f"fail_closed_preflight_{run_id}.log"
    bridge_script = scripts_dir / f"run_bridge_import_probe_{run_id}.sh"
    preflight_script = scripts_dir / f"run_fail_closed_preflight_{run_id}.sh"
    manifest_path = manifests_dir / f"v11_base_load_gate_manifest_{run_id}.json"
    inventory_path = manifests_dir / f"artifact_inventory_{run_id}.sha256"
    report_path = reports_dir / f"task263_v11_base_load_gate_report_{run_id}.md"

    task262 = load_task262_plan(args.task262_root)
    base_files = base_file_manifest(args.base_path)
    packages = package_probe(
        [
            "megatron",
            "megatron.bridge",
            "nemo",
            "torch",
            "transformers",
            "safetensors",
            "cosmos_xenna",
            "pyarrow",
            "omegaconf",
        ]
    )
    bridge_missing = packages["megatron.bridge"]["status"] != "present"
    schedule = schedule_manifest(task262=task262)

    write_text(
        bridge_script,
        render_bridge_probe_script(
            repo_dir=synced_repo,
            base_path=args.base_path,
            output_dir=nemtron_run_root,
            log_path=bridge_import_log,
        ),
        executable=True,
    )

    preliminary_manifest: dict[str, Any] = {
        "schema_version": 1,
        "task_id": TASK_ID,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "disposition": "NEMTRON_NEMO_RUNTIME_BLOCKED" if bridge_missing else "PREFLIGHT_READY",
        "blocker": {
            "summary": (
                "megatron.bridge missing in current runtime"
                if bridge_missing
                else "Bridge package present; inspect bridge import probe result"
            ),
            "smallest_remediation": (
                "Run the generated scripts inside a task-owned NemTron/NeMo "
                "environment with Megatron-Bridge installed; do not train until "
                "the import proof and fail-closed preflight pass and lead clears."
            ),
        },
        "git": {
            "head": git_value(["rev-parse", "HEAD"]),
            "origin_main": git_value(["rev-parse", "origin/main"]),
            "branch": git_value(["rev-parse", "--abbrev-ref", "HEAD"]),
        },
        "paths": {
            "output_root": str(output_root),
            "nemtron_run_root": str(nemtron_run_root),
            "synced_repo": str(synced_repo),
            "bridge_import_script": str(bridge_script),
            "bridge_import_log": str(bridge_import_log),
            "fail_closed_preflight_script": str(preflight_script),
            "fail_closed_preflight_log": str(fail_closed_log),
            "manifest": str(manifest_path),
            "artifact_inventory": str(inventory_path),
            "report": str(report_path),
            "shared_boundary": str(DEFAULT_SHARED_BOUNDARY),
        },
        "base_files": base_files,
        "task262": task262,
        "environment": {
            "hostname": socket.gethostname(),
            "python_executable": sys.executable,
            "python_version": sys.version,
            "platform": platform.platform(),
            "cwd": str(Path.cwd()),
            "packages": packages,
        },
        "schedule": schedule,
        "commands": {
            "bridge_import_probe": str(bridge_script),
            "fail_closed_preflight": str(preflight_script),
        },
        "probe_results": {},
        "artifact_checksums": {},
    }
    write_json(manifest_path, preliminary_manifest)
    write_text(
        preflight_script,
        render_fail_closed_preflight_script(
            repo_dir=synced_repo,
            manifest_path=manifest_path,
            import_log_path=bridge_import_log,
            preflight_log_path=fail_closed_log,
        ),
        executable=True,
    )

    probe_results: dict[str, Any] = {}
    if args.run_bridge_probe:
        rc = run_generated_script(bridge_script)
        probe_results["bridge_import_probe_rc"] = rc
        if rc == 0:
            preliminary_manifest["disposition"] = "BRIDGE_IMPORT_PROOF_READY"
            preliminary_manifest["blocker"]["summary"] = "none"
        else:
            preliminary_manifest["disposition"] = "NEMTRON_NEMO_RUNTIME_BLOCKED"
            preliminary_manifest["blocker"]["summary"] = (
                "Bridge import probe failed; inspect log for exact runtime blocker"
            )

    if args.run_fail_closed_preflight:
        rc = run_generated_script(preflight_script)
        probe_results["fail_closed_preflight_rc"] = rc
        if rc == 0 and preliminary_manifest["disposition"] == "BRIDGE_IMPORT_PROOF_READY":
            preliminary_manifest["disposition"] = "FAIL_CLOSED_PREFLIGHT_PASS"

    preliminary_manifest["probe_results"] = probe_results
    artifacts = [bridge_script, preflight_script, bridge_import_log, fail_closed_log]
    checksums: dict[str, str] = {}
    for path in artifacts:
        if path.exists():
            checksums[str(path)] = sha256_sidecar(path)
    preliminary_manifest["artifact_checksums"] = checksums
    write_json(manifest_path, preliminary_manifest)
    sha256_sidecar(manifest_path)
    write_text(report_path, render_report(preliminary_manifest))
    sha256_sidecar(report_path)
    inventory_targets = [
        manifest_path,
        report_path,
        bridge_script,
        preflight_script,
        bridge_import_log,
        fail_closed_log,
    ]
    inventory_lines = [
        f"{sha256_file(path)}  {path}"
        for path in inventory_targets
        if path.exists()
    ]
    write_text(inventory_path, "\n".join(inventory_lines) + "\n")
    sha256_sidecar(inventory_path)

    print(
        json.dumps(
            {
                "disposition": preliminary_manifest["disposition"],
                "manifest": str(manifest_path),
                "report": str(report_path),
                "bridge_import_log": str(bridge_import_log),
                "fail_closed_preflight_log": str(fail_closed_log),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
