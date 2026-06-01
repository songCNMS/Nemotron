#!/usr/bin/env python3
"""Build a task-owned HotpotQA JSONL cache from pinned HF Parquet files."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq
import yaml
from huggingface_hub import hf_hub_download

TASK_ID = "task251_qwen_aime_v10_hotpotqa_loader_unblock_s1"
REPO_ID = "hotpotqa/hotpot_qa"
REVISION = "1908d6afbbead072334abe2965f91bd2709910ab"
CONFIG = "distractor"
DEFAULT_OUTPUT_ROOT = Path(f"/work-agents/intern_nemotron_worker_2/outputs/{TASK_ID}")
DEFAULT_REGISTRY = Path("src/nemotron/recipes/super3/milestones/m0_data_env/data_registry.yaml")
SOURCE_FILES = {
    "train": [
        "distractor/train-00000-of-00002.parquet",
        "distractor/train-00001-of-00002.parquet",
    ],
    "validation": [
        "distractor/validation-00000-of-00001.parquet",
    ],
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parquet_row_count(path: Path) -> int:
    return pq.ParquetFile(path).metadata.num_rows


def iter_parquet_rows(paths: list[Path], *, limit: int) -> Any:
    emitted = 0
    for path in paths:
        parquet = pq.ParquetFile(path)
        for row_group_index in range(parquet.num_row_groups):
            for row in parquet.read_row_group(row_group_index).to_pylist():
                yield row
                emitted += 1
                if emitted >= limit:
                    return


def write_jsonl_cache(paths: list[Path], output_path: Path, *, limit: int) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    with output_path.open("w", encoding="utf-8") as f:
        for row in iter_parquet_rows(paths, limit=limit):
            json.dump(row, f, ensure_ascii=False, sort_keys=True)
            f.write("\n")
            rows += 1
    if rows != limit:
        raise RuntimeError(f"{output_path} wrote {rows} rows, expected {limit}")
    return {
        "path": str(output_path),
        "rows": rows,
        "sha256": sha256_file(output_path),
    }


def download_source_files() -> dict[str, list[dict[str, Any]]]:
    downloaded: dict[str, list[dict[str, Any]]] = {}
    for split, filenames in SOURCE_FILES.items():
        downloaded[split] = []
        for filename in filenames:
            local_path = Path(
                hf_hub_download(
                    repo_id=REPO_ID,
                    repo_type="dataset",
                    filename=filename,
                    revision=REVISION,
                )
            )
            downloaded[split].append(
                {
                    "split": split,
                    "hf_path": filename,
                    "local_hf_cache_path": str(local_path),
                    "rows": parquet_row_count(local_path),
                    "sha256": sha256_file(local_path),
                }
            )
    return downloaded


def build_registry_override(
    *,
    source_registry_path: Path,
    output_path: Path,
    train_cache_path: Path,
    validation_cache_path: Path,
    manifest_path: Path,
) -> None:
    registry = yaml.safe_load(source_registry_path.read_text(encoding="utf-8"))
    for dataset in registry["datasets"]:
        if dataset["id"] == "m0_search_hotpotqa":
            dataset["trust_remote_code"] = False
            dataset["local_jsonl_files"] = {
                "train": str(train_cache_path),
                "validation": str(validation_cache_path),
            }
            dataset["standard_format_cache_manifest"] = str(manifest_path)
            dataset["standard_format_cache_source"] = "task251 pinned HotpotQA Parquet to JSONL"
            break
    else:
        raise RuntimeError("m0_search_hotpotqa not found in source registry")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml.safe_dump(registry, sort_keys=False), encoding="utf-8")


def build_cache(args: argparse.Namespace) -> dict[str, Any]:
    output_root: Path = args.output_root
    cache_dir = output_root / "hotpotqa_standard_cache"
    manifest_path = cache_dir / "manifest.json"
    registry_override_path = cache_dir / "data_registry.hotpotqa_standard_cache.yaml"
    if cache_dir.exists() and not args.overwrite:
        raise FileExistsError(f"{cache_dir} exists; pass --overwrite to rebuild")

    source_files = download_source_files()
    train_sources = [Path(info["local_hf_cache_path"]) for info in source_files["train"]]
    validation_sources = [Path(info["local_hf_cache_path"]) for info in source_files["validation"]]
    train_cache_path = cache_dir / f"hotpotqa_{CONFIG}_train_smoke{args.max_train_rows}.jsonl"
    validation_cache_path = cache_dir / f"hotpotqa_{CONFIG}_validation_smoke{args.max_validation_rows}.jsonl"

    cache_files = {
        "train": write_jsonl_cache(train_sources, train_cache_path, limit=args.max_train_rows),
        "validation": write_jsonl_cache(
            validation_sources,
            validation_cache_path,
            limit=args.max_validation_rows,
        ),
    }

    build_registry_override(
        source_registry_path=args.repo_root / DEFAULT_REGISTRY,
        output_path=registry_override_path,
        train_cache_path=train_cache_path,
        validation_cache_path=validation_cache_path,
        manifest_path=manifest_path,
    )

    manifest = {
        "schema_version": 1,
        "task_id": TASK_ID,
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cache_scope": "capped task251 smoke cache for task248 local prep",
        "source": {
            "repo_id": REPO_ID,
            "config": CONFIG,
            "revision": REVISION,
            "source_url": f"https://huggingface.co/datasets/{REPO_ID}/tree/{REVISION}/{CONFIG}",
        },
        "requested_rows": {
            "train": args.max_train_rows,
            "validation": args.max_validation_rows,
        },
        "source_files": source_files,
        "cache_files": cache_files,
        "registry_override": {
            "path": str(registry_override_path),
            "sha256": sha256_file(registry_override_path),
            "hotpotqa_loader": "local_jsonl_files",
            "trust_remote_code": False,
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--max-train-rows", type=int, default=100)
    parser.add_argument("--max-validation-rows", type=int, default=25)
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main() -> int:
    manifest = build_cache(build_parser().parse_args())
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
