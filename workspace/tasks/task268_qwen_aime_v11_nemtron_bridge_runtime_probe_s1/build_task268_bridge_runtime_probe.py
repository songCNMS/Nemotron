#!/usr/bin/env python3
"""Build task268 NemTron Bridge runtime probe evidence.

This helper is intentionally limited to Qwen3-4B Bridge import/checkpoint-load
and fail-closed preflight evidence. It never launches SFT training, nonzero-LR
smoke, export, endpoint serving, AIME/task243 eval, promotion, task255 reuse, or
30B/8-GPU work.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import re
import shlex
import shutil
import socket
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1"
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_ROOT = REPO_ROOT.parent / "outputs" / TASK_ID
DEFAULT_BASE_PATH = Path("/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507")
DEFAULT_ROOT_RUN_PARENT = Path("/root") / TASK_ID
DEFAULT_IMAGE = "nvcr.io/nvidia/nemo:26.02.nemotron_3_super"
DEFAULT_IMPORT_SCRIPT = "scripts/import_qwen3_4b_local_to_megatron.py"
QWEN_MODEL_ENV_VAR = "SUPER3_M1_QWEN_HF_MODEL"


def utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def q(value: str | os.PathLike[str] | int | float) -> str:
    return shlex.quote(str(value))


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
    write_text(path.with_name(f"{path.name}.sha256"), f"{digest}  {path.name}\n")
    return digest


def run_command(
    command: list[str],
    *,
    log_path: Path,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        log.write("$ " + " ".join(q(part) for part in command) + "\n")
        log.flush()
        try:
            proc = subprocess.run(
                command,
                cwd=cwd,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
            rc = proc.returncode
        except FileNotFoundError as exc:
            log.write(f"COMMAND_EXCEPTION=FileNotFoundError: {exc}\n")
            rc = 127
        log.write(f"COMMAND_RC={rc}\n")
    return rc


def git_value(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()
    except Exception:  # noqa: BLE001 - report unknown rather than fail bundle
        return "UNKNOWN"


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


def base_file_manifest(base_path: Path, *, hash_model_shards: bool) -> dict[str, Any]:
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

    shards: list[dict[str, Any]] = []
    for path in sorted(base_path.glob("model-*.safetensors")):
        item: dict[str, Any] = {
            "path": str(path),
            "size_bytes": path.stat().st_size,
        }
        if hash_model_shards:
            item["sha256"] = sha256_file(path)
        shards.append(item)

    return {
        "base_path": str(base_path),
        "required_files": files,
        "missing_required_files": missing,
        "model_shards": shards,
        "model_shards_total_size_bytes": sum(item["size_bytes"] for item in shards),
        "model_shards_count": len(shards),
        "model_shards_hashed": hash_model_shards,
    }


def sync_repo_to_root(*, synced_repo: Path, log_path: Path) -> int:
    synced_repo.parent.mkdir(parents=True, exist_ok=True)
    rsync = shutil.which("rsync")
    if rsync:
        command = [
            rsync,
            "-a",
            "--exclude",
            ".git",
            "--exclude",
            "__pycache__",
            f"{REPO_ROOT}/",
            f"{synced_repo}/",
        ]
        return run_command(command, log_path=log_path, cwd=REPO_ROOT)

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        log.write("RSYNC_MISSING=1\n")
        log.write(f"COPY_SOURCE={REPO_ROOT}\n")
        log.write(f"COPY_DEST={synced_repo}\n")
        try:
            shutil.copytree(
                REPO_ROOT,
                synced_repo,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns(".git", "__pycache__"),
            )
            rc = 0
        except Exception as exc:  # noqa: BLE001 - exact blocker evidence
            log.write(f"COPY_EXCEPTION={type(exc).__name__}: {exc}\n")
            rc = 1
        log.write(f"COMMAND_RC={rc}\n")
    return rc


def write_bridge_import_script(
    *,
    script_path: Path,
    synced_repo: Path,
    base_path: Path,
    import_output_dir: Path,
    log_path: Path,
) -> None:
    command = (
        "python3 "
        f"{q(synced_repo / DEFAULT_IMPORT_SCRIPT)} "
        f"--hf-path {q(base_path)} "
        f"--output-dir {q(import_output_dir)}"
    )
    write_text(
        script_path,
        f"""#!/usr/bin/env bash
set -euo pipefail

cd {q(synced_repo)}
export PYTHONPATH="${{PWD}}/src${{PYTHONPATH:+:${{PYTHONPATH}}}}"
export {QWEN_MODEL_ENV_VAR}={q(base_path)}
mkdir -p {q(import_output_dir)} {q(log_path.parent)}

set +e
{command} > {q(log_path)} 2>&1
rc=$?
set -e
echo "BRIDGE_IMPORT_COMMAND={command}" >> {q(log_path)}
echo "BRIDGE_IMPORT_RC=$rc" >> {q(log_path)}
exit "$rc"
""",
        executable=True,
    )


def write_fail_closed_preflight_script(
    *,
    script_path: Path,
    synced_repo: Path,
    import_log_path: Path,
    preflight_log_path: Path,
) -> None:
    write_text(
        script_path,
        f"""#!/usr/bin/env bash
set -euo pipefail

cd {q(synced_repo)}
export PYTHONPATH="${{PWD}}/src${{PYTHONPATH:+:${{PYTHONPATH}}}}"
python3 - <<'PY' > {q(preflight_log_path)} 2>&1
import importlib.util
import re
from pathlib import Path

import_log_path = Path({str(import_log_path)!r})
errors = []

for package in ("megatron", "megatron.bridge", "nemo"):
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

if errors:
    print("TASK268_FAIL_CLOSED_PREFLIGHT=BLOCK")
    for error in errors:
        print(f"- {{error}}")
    raise SystemExit(2)

print("TASK268_FAIL_CLOSED_PREFLIGHT=PASS")
PY
""",
        executable=True,
    )


def command_rc_from_log(log_path: Path) -> int | None:
    if not log_path.is_file():
        return None
    text = log_path.read_text(encoding="utf-8", errors="replace")
    matches = re.findall(r"COMMAND_RC=(-?\\d+)", text)
    return int(matches[-1]) if matches else None


def bridge_rc_from_log(log_path: Path) -> int | None:
    if not log_path.is_file():
        return None
    text = log_path.read_text(encoding="utf-8", errors="replace")
    matches = re.findall(r"BRIDGE_IMPORT_RC=(-?\\d+)", text)
    return int(matches[-1]) if matches else None


def render_report(manifest: dict[str, Any]) -> str:
    base = manifest["base_files"]
    env = manifest["environment"]
    paths = manifest["paths"]
    probes = manifest["probe_results"]
    lines = [
        "# task268 NemTron Bridge Runtime Probe Report",
        "",
        f"- Task: `{TASK_ID}`",
        f"- Generated: `{manifest['generated_at_utc']}`",
        f"- Disposition: `{manifest['disposition']}`",
        f"- Blocker: `{manifest['blocker']['summary']}`",
        f"- Repo head: `{manifest['git']['head']}`",
        f"- Base main: `{manifest['git']['origin_main']}`",
        "",
        "## Paths",
        "",
        f"- Local output root: `{paths['output_root']}`",
        f"- Task-owned root run path: `{paths['root_run_root']}`",
        f"- Synced repo: `{paths['synced_repo']}`",
        f"- Bridge import output path: `{paths['bridge_import_output_dir']}`",
        "",
        "## Runtime",
        "",
        f"- Host: `{env['hostname']}`",
        f"- Python: `{env['python_executable']}`",
        f"- Platform: `{env['platform']}`",
        f"- Requested image: `{env['requested_image']}`",
        "",
        "| Package | Status | Origin / Error |",
        "|---|---|---|",
    ]
    for name, result in env["packages"].items():
        detail = result.get("origin") or result.get("error") or ""
        lines.append(f"| `{name}` | `{result['status']}` | `{detail}` |")

    lines.extend(
        [
            "",
            "## Probe Return Codes",
            "",
            f"- Repo sync rc: `{probes.get('repo_sync_rc')}`",
            f"- Docker version rc: `{probes.get('docker_version_rc')}`",
            f"- Docker image inspect rc: `{probes.get('docker_image_inspect_rc')}`",
            f"- Local Bridge import rc: `{probes.get('local_bridge_import_rc')}`",
            f"- Fail-closed preflight rc: `{probes.get('fail_closed_preflight_rc')}`",
            "",
            "## Base Files",
            "",
            f"- Qwen3-4B base path: `{base['base_path']}`",
            f"- Missing required files: `{len(base['missing_required_files'])}`",
            f"- Safetensor shards: `{base['model_shards_count']}` files, "
            f"`{base['model_shards_total_size_bytes']}` bytes total",
            f"- Safetensor shard hashes recorded: `{base['model_shards_hashed']}`",
            "",
            "| File | Size | SHA256 |",
            "|---|---:|---|",
        ]
    )
    for item in base["required_files"]:
        lines.append(f"| `{item['path']}` | {item['size_bytes']} | `{item['sha256']}` |")
    for item in base["model_shards"]:
        digest = item.get("sha256", "size-only")
        lines.append(f"| `{item['path']}` | {item['size_bytes']} | `{digest}` |")

    lines.extend(
        [
            "",
            "## Artifact Checksums",
            "",
            "| Artifact | SHA256 |",
            "|---|---|",
        ]
    )
    for path, digest in sorted(manifest["artifact_checksums"].items()):
        lines.append(f"| `{path}` | `{digest}` |")

    lines.extend(
        [
            "",
            "## Boundary Confirmation",
            "",
            "- No SFT training, nonzero-LR smoke, export, endpoint serving, live "
            "AIME/task243 eval, promotion/go-no-go, task255 reuse, AIME2025 train "
            "prompt/label use, 30B/8-GPU launch, or shared deletion/overwrite was "
            "performed.",
            "",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--base-path", type=Path, default=DEFAULT_BASE_PATH)
    parser.add_argument("--root-run-root", type=Path, default=None)
    parser.add_argument("--image", default=DEFAULT_IMAGE)
    parser.add_argument("--hash-model-shards", action="store_true")
    parser.add_argument("--skip-local-bridge-import", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    run_id = utc_now_compact()
    output_root = args.output_root.resolve()
    root_run_root = args.root_run_root or DEFAULT_ROOT_RUN_PARENT / f"run_{run_id}"
    synced_repo = root_run_root / "Nemotron"
    bridge_import_output_dir = root_run_root / "qwen3_4b_bridge_import_iter0"

    logs_dir = output_root / "logs"
    scripts_dir = output_root / "scripts"
    manifests_dir = output_root / "manifests"
    reports_dir = output_root / "reports"

    sync_log = logs_dir / f"sync_repo_to_root_{run_id}.log"
    docker_version_log = logs_dir / f"docker_version_{run_id}.log"
    docker_image_log = logs_dir / f"docker_image_inspect_{run_id}.log"
    bridge_log = logs_dir / f"bridge_import_probe_{run_id}.log"
    preflight_log = logs_dir / f"fail_closed_preflight_{run_id}.log"
    bridge_script = scripts_dir / f"run_bridge_import_probe_{run_id}.sh"
    preflight_script = scripts_dir / f"run_fail_closed_preflight_{run_id}.sh"
    manifest_path = manifests_dir / f"task268_bridge_runtime_manifest_{run_id}.json"
    report_path = reports_dir / f"task268_bridge_runtime_report_{run_id}.md"
    inventory_path = manifests_dir / f"artifact_inventory_{run_id}.sha256"

    sync_rc = sync_repo_to_root(synced_repo=synced_repo, log_path=sync_log)
    write_bridge_import_script(
        script_path=bridge_script,
        synced_repo=synced_repo,
        base_path=args.base_path,
        import_output_dir=bridge_import_output_dir,
        log_path=bridge_log,
    )
    write_fail_closed_preflight_script(
        script_path=preflight_script,
        synced_repo=synced_repo,
        import_log_path=bridge_log,
        preflight_log_path=preflight_log,
    )

    docker_version_rc = run_command(["docker", "version"], log_path=docker_version_log, cwd=REPO_ROOT)
    docker_image_rc = run_command(
        ["docker", "image", "inspect", args.image, "--format", "{{.Id}} {{.Size}}"],
        log_path=docker_image_log,
        cwd=REPO_ROOT,
    )

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

    local_bridge_rc: int | None
    if args.skip_local_bridge_import:
        write_text(bridge_log, "LOCAL_BRIDGE_IMPORT_SKIPPED=1\nBRIDGE_IMPORT_RC=SKIPPED\n")
        local_bridge_rc = None
    else:
        local_bridge_rc = run_command([str(bridge_script)], log_path=logs_dir / f"bridge_script_wrapper_{run_id}.log")
        local_bridge_rc = bridge_rc_from_log(bridge_log) if bridge_rc_from_log(bridge_log) is not None else local_bridge_rc

    preflight_wrapper_log = logs_dir / f"preflight_script_wrapper_{run_id}.log"
    preflight_wrapper_rc = run_command([str(preflight_script)], log_path=preflight_wrapper_log)
    preflight_rc = command_rc_from_log(preflight_wrapper_log)
    if preflight_rc is None:
        preflight_rc = preflight_wrapper_rc

    base_files = base_file_manifest(args.base_path, hash_model_shards=args.hash_model_shards)

    positive_bridge_proof = False
    if bridge_log.is_file():
        bridge_text = bridge_log.read_text(encoding="utf-8", errors="replace")
        positive_bridge_proof = (
            "BRIDGE_IMPORT_RC=0" in bridge_text
            and ("IMPORT_DONE" in bridge_text or re.search(r"successfully loaded checkpoint", bridge_text, re.I))
        )

    if positive_bridge_proof and preflight_rc == 0:
        disposition = "BRIDGE_IMPORT_PREFLIGHT_PASS"
        blocker_summary = "none"
    elif docker_version_rc != 0:
        disposition = "NEMTRON_BRIDGE_RUNTIME_BLOCKED"
        blocker_summary = "Docker daemon/runtime unavailable for requested NeMo image"
    elif docker_image_rc != 0:
        disposition = "NEMTRON_BRIDGE_RUNTIME_BLOCKED"
        blocker_summary = "Requested NeMo/Megatron-Bridge image unavailable locally"
    else:
        disposition = "NEMTRON_BRIDGE_RUNTIME_BLOCKED"
        blocker_summary = "Bridge import/preflight failed; inspect logs for exact blocker"

    manifest: dict[str, Any] = {
        "schema_version": 1,
        "task_id": TASK_ID,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "disposition": disposition,
        "blocker": {
            "summary": blocker_summary,
            "smallest_remediation": (
                "Provide a task-owned NemTron/NeMo/Megatron-Bridge runtime with "
                f"Docker daemon access or preloaded image {args.image}, then rerun "
                "the generated Bridge import and fail-closed preflight scripts. "
                "Do not proceed to training/eval/export without lead clearance."
            ),
        },
        "git": {
            "head": git_value(["rev-parse", "HEAD"]),
            "origin_main": git_value(["rev-parse", "origin/main"]),
            "branch": git_value(["rev-parse", "--abbrev-ref", "HEAD"]),
        },
        "paths": {
            "output_root": str(output_root),
            "root_run_root": str(root_run_root),
            "synced_repo": str(synced_repo),
            "bridge_import_output_dir": str(bridge_import_output_dir),
            "manifest": str(manifest_path),
            "report": str(report_path),
            "artifact_inventory": str(inventory_path),
            "sync_log": str(sync_log),
            "docker_version_log": str(docker_version_log),
            "docker_image_inspect_log": str(docker_image_log),
            "bridge_import_script": str(bridge_script),
            "bridge_import_log": str(bridge_log),
            "bridge_script_wrapper_log": str(logs_dir / f"bridge_script_wrapper_{run_id}.log"),
            "fail_closed_preflight_script": str(preflight_script),
            "fail_closed_preflight_log": str(preflight_log),
            "preflight_script_wrapper_log": str(preflight_wrapper_log),
        },
        "environment": {
            "hostname": socket.gethostname(),
            "python_executable": sys.executable,
            "python_version": sys.version,
            "platform": platform.platform(),
            "cwd": str(Path.cwd()),
            "requested_image": args.image,
            "packages": packages,
        },
        "base_files": base_files,
        "probe_results": {
            "repo_sync_rc": sync_rc,
            "docker_version_rc": docker_version_rc,
            "docker_image_inspect_rc": docker_image_rc,
            "local_bridge_import_rc": local_bridge_rc,
            "fail_closed_preflight_rc": preflight_rc,
            "positive_bridge_proof": positive_bridge_proof,
        },
        "commands": {
            "sync_repo_to_root": str(sync_log),
            "docker_version": "docker version",
            "docker_image_inspect": f"docker image inspect {args.image} --format '{{{{.Id}}}} {{{{.Size}}}}'",
            "bridge_import_probe": str(bridge_script),
            "fail_closed_preflight": str(preflight_script),
        },
        "artifact_checksums": {},
    }

    stable_artifact_paths = [
        sync_log,
        docker_version_log,
        docker_image_log,
        bridge_script,
        bridge_log,
        logs_dir / f"bridge_script_wrapper_{run_id}.log",
        preflight_script,
        preflight_log,
        preflight_wrapper_log,
    ]
    checksums: dict[str, str] = {}
    for path in stable_artifact_paths:
        if path.exists():
            checksums[str(path)] = sha256_sidecar(path)
    manifest["artifact_checksums"] = checksums
    write_json(manifest_path, manifest)
    write_text(report_path, render_report(manifest))

    artifact_paths = [*stable_artifact_paths, manifest_path, report_path]
    sha256_sidecar(manifest_path)
    sha256_sidecar(report_path)

    inventory_lines = [
        f"{sha256_file(path)}  {path}"
        for path in artifact_paths
        if path.exists()
    ]
    write_text(inventory_path, "\n".join(inventory_lines) + "\n")
    sha256_sidecar(inventory_path)

    print(f"DISPOSITION={disposition}")
    print(f"MANIFEST={manifest_path}")
    print(f"REPORT={report_path}")
    print(f"INVENTORY={inventory_path}")
    print(f"SYNCED_REPO={synced_repo}")
    return 0 if disposition == "BRIDGE_IMPORT_PREFLIGHT_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
