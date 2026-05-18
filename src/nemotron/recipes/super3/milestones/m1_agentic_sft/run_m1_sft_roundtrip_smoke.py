#!/usr/bin/env python3
# /// script
# dependencies = ["jinja2>=3.0.0", "pyarrow>=14.0.0", "numpy>=1.24.0"]
# ///

"""Lightweight M1 Agentic SFT JSONL -> packed Parquet round-trip smoke.

The production `nemotron super3 data prep sft -c agentic_v0` path requires the
Xenna pipeline runtime plus a HuggingFace tokenizer. This smoke keeps the same
M1 JSONL contract and Super3 chat template, but uses a deterministic local
tokenizer so CPU workspaces can catch schema/template/filtering issues before
launching the full data-prep job.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import sys
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq
from jinja2.sandbox import ImmutableSandboxedEnvironment

REPO_ROOT = Path(__file__).resolve().parents[6]
# Super3 ships its own jinja that starts as a verbatim copy of nano3
# (see `task012_super3_chat_template`). Switching here keeps the
# roundtrip smoke aligned with the data-prep configs in
# `stage1_sft/config/data_prep/*.yaml`, which all declare
# `chat_template: super3`.
SUPER3_TEMPLATE = REPO_ROOT / "src/nemotron/data_prep/templates/super3.jinja"
CHAT_TEMPLATE_MODULE = REPO_ROOT / "src/nemotron/data_prep/core/chat_template.py"
DEFAULT_OUTPUT_DIR = Path("../outputs/task005_m1_sft_roundtrip_smoke")
USED_IN_TAG = "super3_agentic_sft_v0"
TOKEN_RE = re.compile(r"\S+|\s+")

JsonDict = dict[str, Any]


class SmokeTokenizer:
    """Small tokenizer facade that supports the methods used by chat_template.py."""

    def __init__(self, template_text: str):
        self._template = ImmutableSandboxedEnvironment(
            trim_blocks=True,
            lstrip_blocks=True,
        ).from_string(template_text)
        self._vocab: dict[str, int] = {}

    def apply_chat_template(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        tokenize: bool = False,
        add_generation_prompt: bool = False,
        tools: Sequence[Mapping[str, Any]] | None = None,
        chat_template_kwargs: Mapping[str, Any] | None = None,
    ) -> str | list[int]:
        rendered = self._template.render(
            messages=list(messages),
            tools=list(tools or []),
            add_generation_prompt=add_generation_prompt,
            chat_template_kwargs=dict(chat_template_kwargs or {}),
        )
        return self.encode(rendered, add_special_tokens=False) if tokenize else rendered

    def encode(self, text: str, add_special_tokens: bool = False) -> list[int]:  # noqa: ARG002
        token_ids: list[int] = []
        for token in TOKEN_RE.findall(text):
            token_id = self._vocab.get(token)
            if token_id is None:
                token_id = len(self._vocab) + 1
                self._vocab[token] = token_id
            token_ids.append(token_id)
        return token_ids


def load_chat_template_helpers() -> Any:
    spec = importlib.util.spec_from_file_location("_m1_roundtrip_chat_template", CHAT_TEMPLATE_MODULE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load chat template helpers from {CHAT_TEMPLATE_MODULE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_jsonl(path: Path) -> list[JsonDict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                row = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: expected JSON object")
            rows.append(row)
    return rows


def row_matches_used_in(row: Mapping[str, Any], used_in_filter: str | None) -> bool:
    if not used_in_filter:
        return True
    used_in = row.get("used_in")
    if isinstance(used_in, list):
        return used_in_filter in used_in
    if isinstance(used_in, str):
        return used_in_filter in {value.strip() for value in used_in.split(",")}
    return False


def tokenize_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    tokenizer: SmokeTokenizer,
    used_in_filter: str | None,
    max_records: int | None,
) -> tuple[list[list[int]], list[list[int]], JsonDict]:
    helpers = load_chat_template_helpers()
    sequences: list[list[int]] = []
    loss_masks: list[list[int]] = []
    counts: Counter[str] = Counter()
    errors: list[JsonDict] = []

    for row_index, row in enumerate(rows):
        if max_records is not None and sum(counts.values()) >= max_records:
            break
        if not row_matches_used_in(row, used_in_filter):
            continue
        messages = row.get("messages")
        if not isinstance(messages, list) or not messages:
            errors.append({"row_index": row_index, "error": "missing messages"})
            continue
        tools = row.get("tools")
        if not isinstance(tools, list):
            tools = []

        is_valid, validation_error = helpers.validate_conversation(messages, tools)
        if not is_valid:
            errors.append({"row_index": row_index, "error": validation_error or "invalid conversation"})
            continue

        try:
            local_messages = helpers.replace_json_args(messages)
            masked = helpers.create_masked_messages(local_messages, tokenizer, tools)
        except Exception as exc:  # noqa: BLE001 - smoke should report row-level failures.
            errors.append({"row_index": row_index, "error": f"{type(exc).__name__}: {exc}"})
            continue

        for chunks, _original_messages in masked:
            processed_chunks = helpers.split_system_user_chunks(chunks)
            input_ids: list[int] = []
            mask: list[int] = []
            for chunk in processed_chunks:
                chunk_ids = tokenizer.encode(str(chunk["content"]), add_special_tokens=False)
                input_ids.extend(chunk_ids)
                mask.extend([1 if chunk["role"] == "assistant" else 0] * len(chunk_ids))
            if not input_ids:
                errors.append({"row_index": row_index, "error": "empty tokenized sequence"})
                continue
            if not any(mask):
                errors.append({"row_index": row_index, "error": "no assistant loss tokens"})
                continue
            sequences.append(input_ids)
            loss_masks.append(mask)
            env = row.get("metadata", {}).get("m0_environment") or row.get("environment") or "unknown"
            counts[str(env)] += 1

    return sequences, loss_masks, {"counts": dict(sorted(counts.items())), "errors": errors}


def align_loss_mask(mask: Sequence[int], seq_len: int) -> list[int]:
    if seq_len <= 0:
        return []
    if seq_len == 1:
        return [0]
    return [int(value) for value in mask[1:seq_len]] + [0]


def pack_sequences(
    sequences: Sequence[Sequence[int]],
    loss_masks: Sequence[Sequence[int]],
    *,
    pack_size: int,
) -> list[JsonDict]:
    bins: list[JsonDict] = []
    current_ids: list[int] = []
    current_mask: list[int] = []
    current_starts: list[int] = []

    def flush() -> None:
        nonlocal current_ids, current_mask, current_starts
        if current_ids:
            bins.append(
                {
                    "input_ids": current_ids,
                    "loss_mask": current_mask,
                    "seq_start_id": current_starts,
                }
            )
        current_ids = []
        current_mask = []
        current_starts = []

    for input_ids, mask in zip(sequences, loss_masks):
        seq = list(input_ids[:pack_size])
        seq_mask = list(mask[: len(seq)])
        if not seq:
            continue
        if current_ids and len(current_ids) + len(seq) > pack_size:
            flush()
        if not current_ids:
            current_starts = [0]
        else:
            current_starts.append(len(current_ids))
        current_ids.extend(seq)
        current_mask.extend(align_loss_mask(seq_mask, len(seq)))
    flush()
    return bins


def write_packed_parquet(path: Path, bins: Sequence[Mapping[str, Sequence[int]]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_arrays(
        [
            pa.array([row["input_ids"] for row in bins], type=pa.list_(pa.int32())),
            pa.array([row["loss_mask"] for row in bins], type=pa.list_(pa.uint8())),
            pa.array([row["seq_start_id"] for row in bins], type=pa.list_(pa.int32())),
        ],
        names=["input_ids", "loss_mask", "seq_start_id"],
    )
    pq.write_table(table, path, compression="zstd")


def verify_parquet(path: Path) -> JsonDict:
    table = pq.read_table(path)
    rows = table.to_pylist()
    if not rows:
        raise ValueError(f"{path} contains no packed rows")
    total_tokens = 0
    total_loss_tokens = 0
    for row_index, row in enumerate(rows):
        input_ids = row["input_ids"]
        loss_mask = row["loss_mask"]
        starts = row["seq_start_id"]
        if len(input_ids) != len(loss_mask):
            raise ValueError(f"row {row_index}: input_ids/loss_mask length mismatch")
        if not starts or starts[0] != 0:
            raise ValueError(f"row {row_index}: seq_start_id must start at 0")
        if any(starts[i] >= starts[i + 1] for i in range(len(starts) - 1)):
            raise ValueError(f"row {row_index}: seq_start_id must be strictly increasing")
        total_tokens += len(input_ids)
        total_loss_tokens += sum(int(value) for value in loss_mask)
    if total_loss_tokens <= 0:
        raise ValueError("packed parquet has no assistant loss tokens")
    return {"packed_rows": len(rows), "total_tokens": total_tokens, "total_loss_tokens": total_loss_tokens}


def write_report(path: Path, summary: Mapping[str, Any]) -> None:
    lines = [
        "# M1 Agentic SFT Roundtrip Smoke",
        "",
        f"- Input JSONL: `{summary['input_jsonl']}`",
        f"- Output parquet: `{summary['parquet_path']}`",
        f"- Pack size: `{summary['pack_size']}`",
        f"- Status: `{summary['status']}`",
        "",
        "## Environment counts",
        "",
    ]
    for env, count in summary["environment_counts"].items():
        lines.append(f"- `{env}`: {count}")
    lines.extend(
        [
            "",
            "## Packed summary",
            "",
            f"- Packed rows: `{summary['parquet']['packed_rows']}`",
            f"- Total tokens: `{summary['parquet']['total_tokens']}`",
            f"- Total loss tokens: `{summary['parquet']['total_loss_tokens']}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> JsonDict:
    if args.output_dir.exists():
        if not args.overwrite:
            raise FileExistsError(f"output directory exists; pass --overwrite: {args.output_dir}")
        shutil.rmtree(args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows = read_jsonl(args.m1_jsonl)
    tokenizer = SmokeTokenizer(SUPER3_TEMPLATE.read_text(encoding="utf-8"))
    sequences, loss_masks, tokenization = tokenize_rows(
        rows,
        tokenizer=tokenizer,
        used_in_filter=args.used_in_filter,
        max_records=args.max_records,
    )
    if tokenization["errors"]:
        raise ValueError(f"tokenization/validation errors: {tokenization['errors'][:5]}")
    if not sequences:
        raise ValueError("no records were tokenized")

    missing_envs = sorted(set(args.require_environment or []) - set(tokenization["counts"]))
    if missing_envs:
        raise ValueError(f"required environments missing from smoke input: {missing_envs}")

    bins = pack_sequences(sequences, loss_masks, pack_size=args.pack_size)
    if not bins:
        raise ValueError("packing produced no bins")

    split_dir = args.output_dir / "splits" / "train"
    parquet_path = split_dir / "shard_000000.parquet"
    write_packed_parquet(parquet_path, bins)
    parquet_summary = verify_parquet(parquet_path)

    metadata = {
        "type": "SFTDataArtifact",
        "tokenizer_uri": "smoke://deterministic-whitespace-tokenizer",
        "pack_size": args.pack_size,
        "total_sequences": len(sequences),
        "total_packed_sequences": parquet_summary["packed_rows"],
        "source_jsonl": str(args.m1_jsonl),
    }
    (args.output_dir / "splits" / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary = {
        "status": "pass",
        "input_jsonl": str(args.m1_jsonl),
        "output_dir": str(args.output_dir),
        "parquet_path": str(parquet_path),
        "pack_size": args.pack_size,
        "records_tokenized": len(sequences),
        "environment_counts": tokenization["counts"],
        "parquet": parquet_summary,
        "metadata_path": str(args.output_dir / "splits" / "metadata.json"),
    }
    (args.output_dir / "roundtrip_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(args.output_dir / "report.md", summary)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--m1-jsonl", type=Path, required=True, help="M1 agentic_sft_v0_train.jsonl path.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--max-records", type=int, default=None)
    parser.add_argument("--pack-size", type=int, default=4096)
    parser.add_argument("--used-in-filter", default=USED_IN_TAG)
    parser.add_argument("--require-environment", action="append", default=[])
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        summary = run(args)
    except Exception as exc:  # noqa: BLE001 - CLI should render concise failure.
        print(f"run_m1_sft_roundtrip_smoke.py: error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
