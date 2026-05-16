#!/usr/bin/env python3
# /// script
# dependencies = ["datasets>=2.14.0", "pyyaml>=6.0"]
# ///

"""Prepare public M0 data and environment assets for multi-environment RL."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from collections.abc import Iterable, Iterator, Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_REGISTRY_PATH = SCRIPT_DIR / "data_registry.yaml"
ENV_REGISTRY_PATH = SCRIPT_DIR / "environment_registry.yaml"
DEFAULT_OUTPUT_DIR = Path("data/super3/milestones/m0_data_env_foundation")

TOOL_CALL_RE = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)

SYSTEM_PROMPTS = {
    "search_grounded_qa": "You answer questions using the provided retrieved passages.",
    "code_execution_python": "You are a Python coding assistant. Return a complete solution.",
    "general_tool_calling": "You are a tool-using assistant. Use the available functions when needed.",
    "math_reasoning_numeric": "You are a careful reasoning assistant. Return the final numeric answer clearly.",
}

JsonDict = dict[str, Any]


def load_yaml(path: Path) -> JsonDict:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return data


def normalize_numeric_answer(text: Any) -> str:
    value = str(text).strip()
    if "####" in value:
        value = value.rsplit("####", 1)[1].strip()
    return value.replace(",", "").strip()


def parse_json_maybe(value: Any, default: Any) -> Any:
    if value is None:
        return default
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return default
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            return default
    return value


def source_id(row: Mapping[str, Any]) -> str:
    for key in ("id", "task_id", "source_file"):
        if row.get(key) is not None:
            return str(row[key])
    return ""


def base_metadata(spec: Mapping[str, Any], row: Mapping[str, Any]) -> JsonDict:
    return {
        "source_dataset": spec["hf_dataset"],
        "source_config": spec.get("hf_config"),
        "source_split": spec["hf_split"],
        "source_revision": spec["hf_revision"],
        "source_url": spec["source_url"],
        "source_id": source_id(row),
        "license": spec["license"],
        "domain": spec["domain"],
        "difficulty": spec.get("difficulty"),
        "reward_type": spec["reward_type"],
        "contamination": spec["contamination"],
        "data_stage": spec["milestone"],
        "use_stage": list(spec["use_stage"]),
    }


def make_record(
    *,
    spec: Mapping[str, Any],
    row: Mapping[str, Any],
    question: str,
    expected_answer: Any,
    input_messages: list[JsonDict],
    reward_config: JsonDict,
    extra_env_info: JsonDict | None = None,
    tools: list[JsonDict] | None = None,
) -> JsonDict:
    tools = tools or []
    return {
        "environment": spec["environment"],
        "milestone": spec["milestone"],
        "use_stage": list(spec["use_stage"]),
        "question": question,
        "expected_answer": expected_answer,
        "responses_create_params": {
            "input": input_messages,
            "tools": tools,
        },
        "reward_config": reward_config,
        "extra_env_info": extra_env_info or {},
        "metadata": base_metadata(spec, row),
    }


def hotpot_documents(row: Mapping[str, Any]) -> list[JsonDict]:
    context = row.get("context") or {}
    if not isinstance(context, Mapping):
        return []
    titles = context.get("title") or []
    sentence_groups = context.get("sentences") or []
    docs = []
    for title, sentences in zip(titles, sentence_groups):
        if isinstance(sentences, list):
            text = "\n".join(str(sentence) for sentence in sentences)
        else:
            text = str(sentences)
        docs.append({"title": str(title), "text": text})
    return docs


def format_documents_for_prompt(documents: Sequence[Mapping[str, Any]]) -> str:
    blocks = []
    for index, doc in enumerate(documents, start=1):
        blocks.append(f"[{index}] {doc.get('title', '')}\n{doc.get('text', '')}")
    return "\n\n".join(blocks)


def transform_hotpotqa_search(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    question = str(row["question"]).strip()
    expected_answer = str(row["answer"]).strip()
    documents = hotpot_documents(row)
    user_content = (
        "Answer the question using only the retrieved passages.\n\n"
        f"Question: {question}\n\n"
        f"Retrieved passages:\n{format_documents_for_prompt(documents)}"
    )
    return make_record(
        spec=spec,
        row=row,
        question=question,
        expected_answer=expected_answer,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": user_content},
        ],
        reward_config={
            "verifier": "normalized_exact_or_contains",
            "max_score": 1.0,
            "normalization": ["lowercase", "strip_articles", "strip_punctuation", "collapse_whitespace"],
        },
        extra_env_info={
            "context_documents": documents,
            "supporting_facts": row.get("supporting_facts"),
            "question_type": row.get("type"),
            "level": row.get("level"),
            "search_query": question,
        },
    )


def transform_mbpp_code_execution(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    question = str(row.get("prompt") or row.get("text") or "").strip()
    tests = list(row.get("test_list") or [])
    imports_value = row.get("test_imports")
    if imports_value is None:
        imports_value = row.get("test_setup_code")
    if isinstance(imports_value, str):
        imports = [imports_value] if imports_value.strip() else []
    else:
        imports = list(imports_value or [])
    user_content = (
        "Write a Python function or program for the task below. Return only executable Python code.\n\n"
        f"Task:\n{question}\n\n"
        "The solution will be checked with hidden and visible unit tests."
    )
    return make_record(
        spec=spec,
        row=row,
        question=question,
        expected_answer=str(row.get("code") or "").strip(),
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": user_content},
        ],
        reward_config={
            "verifier": "python_unit_tests",
            "max_score": 1.0,
            "timeout_s": 30,
            "sandbox": "python_subprocess_or_container",
        },
        extra_env_info={
            "task_id": row.get("task_id"),
            "test_imports": imports,
            "test_list": tests,
            "reference_code": row.get("code"),
        },
    )


def transform_gsm8k_numeric_reasoning(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    question = str(row["question"]).strip()
    expected_answer = normalize_numeric_answer(row["answer"])
    return make_record(
        spec=spec,
        row=row,
        question=question,
        expected_answer=expected_answer,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": question},
        ],
        reward_config={
            "verifier": "normalized_numeric_exact_match",
            "max_score": 1.0,
            "normalization": ["strip_commas", "strip_whitespace"],
        },
        extra_env_info={
            "reference_solution": row.get("answer"),
        },
    )


def parse_tool_calls(text: str) -> list[JsonDict]:
    calls = []
    for match in TOOL_CALL_RE.finditer(text):
        parsed = parse_json_maybe(match.group(1), default=None)
        if not isinstance(parsed, Mapping):
            continue
        if "function" in parsed:
            calls.append(dict(parsed))
        else:
            calls.append(
                {
                    "type": "function",
                    "function": {
                        "name": parsed.get("name"),
                        "arguments": parsed.get("arguments", {}),
                    },
                }
            )
    return calls


def strip_tool_call_blocks(text: str) -> str:
    return TOOL_CALL_RE.sub("", text).strip()


def convert_hermes_conversations(conversations: Iterable[Mapping[str, Any]]) -> tuple[list[JsonDict], JsonDict]:
    role_map = {
        "system": "system",
        "human": "user",
        "user": "user",
        "gpt": "assistant",
        "assistant": "assistant",
    }
    input_messages: list[JsonDict] = []
    expected_tool_calls: list[JsonDict] = []
    expected_assistant_content = ""

    for turn in conversations:
        raw_role = str(turn.get("from") or turn.get("role") or "").strip()
        role = role_map.get(raw_role)
        if role is None:
            continue
        content = str(turn.get("value") or turn.get("content") or "")
        if role == "assistant":
            expected_tool_calls = parse_tool_calls(content)
            expected_assistant_content = strip_tool_call_blocks(content)
            break
        input_messages.append({"role": role, "content": content})

    if not any(message["role"] == "system" for message in input_messages):
        input_messages.insert(0, {"role": "system", "content": SYSTEM_PROMPTS["general_tool_calling"]})

    return input_messages, {
        "expected_tool_calls": expected_tool_calls,
        "expected_assistant_content": expected_assistant_content,
    }


def transform_hermes_function_calling(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    conversations = row.get("conversations") or []
    if not isinstance(conversations, list):
        conversations = []
    input_messages, expected = convert_hermes_conversations(conversations)
    tools = parse_json_maybe(row.get("tools"), default=[])
    if isinstance(tools, Mapping):
        tools = [dict(tools)]
    if not isinstance(tools, list):
        tools = []
    question = next((message["content"] for message in input_messages if message["role"] == "user"), "")
    return make_record(
        spec=spec,
        row=row,
        question=question,
        expected_answer=expected["expected_tool_calls"] or expected["expected_assistant_content"],
        input_messages=input_messages,
        tools=tools,
        reward_config={
            "verifier": "tool_schema_and_argument_match",
            "max_score": 1.0,
            "match": ["tool_name", "json_arguments"],
            "allow_extra_assistant_text": False,
        },
        extra_env_info={
            "expected_tool_calls": expected["expected_tool_calls"],
            "expected_assistant_content": expected["expected_assistant_content"],
            "category": row.get("category"),
            "subcategory": row.get("subcategory"),
            "task": row.get("task"),
        },
    )


CONVERTERS = {
    "hotpotqa_search": transform_hotpotqa_search,
    "mbpp_code_execution": transform_mbpp_code_execution,
    "hermes_function_calling": transform_hermes_function_calling,
    "gsm8k_numeric_reasoning": transform_gsm8k_numeric_reasoning,
}


def iter_hf_rows(spec: Mapping[str, Any], *, streaming: bool) -> Iterator[Mapping[str, Any]]:
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError("Install the `datasets` package or run inside /work-agents/.venv") from exc

    config = spec.get("hf_config")
    kwargs = {
        "split": spec["hf_split"],
        "revision": spec["hf_revision"],
        "streaming": streaming,
    }
    if config:
        dataset = load_dataset(spec["hf_dataset"], config, **kwargs)
    else:
        dataset = load_dataset(spec["hf_dataset"], **kwargs)
    yield from dataset


def desired_counts(spec: Mapping[str, Any], args: argparse.Namespace) -> tuple[int, int]:
    train_rows = args.max_train_per_dataset
    val_rows = args.max_val_per_dataset
    if train_rows is None:
        train_rows = int(spec["default_train_rows"])
    if val_rows is None:
        val_rows = int(spec["default_val_rows"])
    if train_rows < 0 or val_rows < 0:
        raise ValueError("row counts must be non-negative")
    return train_rows, val_rows


def validate_registries(data_registry: Mapping[str, Any], env_registry: Mapping[str, Any]) -> None:
    env_ids = {env["id"] for env in env_registry.get("environments", [])}
    for spec in data_registry.get("datasets", []):
        if spec["environment"] not in env_ids:
            raise ValueError(f"{spec['id']} references unknown environment {spec['environment']}")
        if spec["converter"] not in CONVERTERS:
            raise ValueError(f"{spec['id']} references unknown converter {spec['converter']}")
        if spec.get("milestone", data_registry.get("milestone")) != data_registry.get("milestone"):
            raise ValueError(f"{spec['id']} milestone must match registry milestone")


def selected_specs(data_registry: Mapping[str, Any], dataset_ids: Sequence[str] | None) -> list[JsonDict]:
    specs = [dict(spec) for spec in data_registry.get("datasets", [])]
    for spec in specs:
        spec.setdefault("milestone", data_registry["milestone"])
    if not dataset_ids:
        return specs
    wanted = set(dataset_ids)
    selected = [spec for spec in specs if spec["id"] in wanted]
    missing = sorted(wanted - {spec["id"] for spec in selected})
    if missing:
        raise ValueError(f"unknown dataset ids: {', '.join(missing)}")
    return selected


def target_files(output_dir: Path, specs: Sequence[Mapping[str, Any]]) -> list[Path]:
    paths = []
    for env_id in sorted({spec["environment"] for spec in specs}):
        paths.append(output_dir / env_id / "train-split.jsonl")
        paths.append(output_dir / env_id / "val-split.jsonl")
    paths.extend(
        [
            output_dir / "manifest.json",
            output_dir / "dataset_registry.resolved.json",
            output_dir / "environment_registry.resolved.json",
            output_dir / "report.md",
        ]
    )
    return paths


def check_overwrite(paths: Sequence[Path], overwrite: bool) -> None:
    existing = [path for path in paths if path.exists()]
    if existing and not overwrite:
        formatted = "\n".join(f"  - {path}" for path in existing)
        raise FileExistsError(f"target files already exist; pass --overwrite to replace them:\n{formatted}")


def write_jsonl_line(path: Path, record: Mapping[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, sort_keys=True)
        f.write("\n")


def reset_target_files(paths: Sequence[Path]) -> None:
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".jsonl":
            path.write_text("", encoding="utf-8")


def prepare_assets(args: argparse.Namespace) -> JsonDict:
    data_registry = load_yaml(args.data_registry)
    env_registry = load_yaml(args.environment_registry)
    specs = selected_specs(data_registry, args.dataset_id)
    validate_registries(data_registry, env_registry)

    output_dir = args.output_dir
    paths = target_files(output_dir, specs)
    check_overwrite(paths, args.overwrite)
    reset_target_files(paths)

    manifest: JsonDict = {
        "schema_version": 1,
        "milestone": data_registry["milestone"],
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "output_dir": str(output_dir),
        "data_registry": str(args.data_registry),
        "environment_registry": str(args.environment_registry),
        "datasets": [],
        "files": [],
        "errors": [],
    }
    file_counts: dict[tuple[str, str], int] = defaultdict(int)

    for spec in specs:
        train_target, val_target = desired_counts(spec, args)
        split_counts = {"train": 0, "val": 0}
        converter = CONVERTERS[spec["converter"]]
        for raw_index, row in enumerate(iter_hf_rows(spec, streaming=not args.non_streaming)):
            if split_counts["train"] >= train_target and split_counts["val"] >= val_target:
                break
            try:
                record = converter(row, spec)
            except Exception as exc:  # noqa: BLE001 - keep data-prep running and report bad rows.
                manifest["errors"].append(
                    {
                        "dataset": spec["id"],
                        "source_row_index": raw_index,
                        "error": str(exc),
                    }
                )
                continue

            split = "train" if split_counts["train"] < train_target else "val"
            split_counts[split] += 1
            record["metadata"]["source_row_index"] = raw_index
            record["metadata"]["prepared_split"] = split
            record["metadata"]["prepared_by"] = "prepare_m0_assets.py"
            path = output_dir / spec["environment"] / f"{split}-split.jsonl"
            write_jsonl_line(path, record)
            file_counts[(spec["environment"], split)] += 1

        manifest["datasets"].append(
            {
                "id": spec["id"],
                "environment": spec["environment"],
                "domain": spec["domain"],
                "hf_dataset": spec["hf_dataset"],
                "hf_config": spec.get("hf_config"),
                "hf_split": spec["hf_split"],
                "hf_revision": spec["hf_revision"],
                "source_url": spec["source_url"],
                "license": spec["license"],
                "use_stage": spec["use_stage"],
                "train_rows": split_counts["train"],
                "val_rows": split_counts["val"],
            }
        )
        if split_counts["train"] < train_target or split_counts["val"] < val_target:
            manifest["errors"].append(
                {
                    "dataset": spec["id"],
                    "error": (
                        f"requested {train_target}/{val_target} train/val rows, "
                        f"prepared {split_counts['train']}/{split_counts['val']}"
                    ),
                }
            )

    for env_id, split in sorted(file_counts):
        manifest["files"].append(
            {
                "environment": env_id,
                "split": split,
                "path": str(output_dir / env_id / f"{split}-split.jsonl"),
                "rows": file_counts[(env_id, split)],
            }
        )

    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "dataset_registry.resolved.json", data_registry)
    write_json(output_dir / "environment_registry.resolved.json", env_registry)
    write_report(output_dir / "report.md", manifest)
    return manifest


def write_json(path: Path, data: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def write_report(path: Path, manifest: Mapping[str, Any]) -> None:
    lines = [
        "# M0 Data and Environment Foundation Report",
        "",
        f"- Generated: `{manifest['created_at_utc']}`",
        f"- Output directory: `{manifest['output_dir']}`",
        f"- Milestone: `{manifest['milestone']}`",
        "",
        "## Dataset Outputs",
        "",
        "| Dataset | Environment | Train | Val | License | Use stage |",
        "|---|---|---:|---:|---|---|",
    ]
    for dataset in manifest["datasets"]:
        use_stage = "<br>".join(dataset["use_stage"])
        lines.append(
            (
                f"| {dataset['id']} | {dataset['environment']} | {dataset['train_rows']} | "
                f"{dataset['val_rows']} | {dataset['license']} | {use_stage} |"
            )
        )
    lines.extend(["", "## Files", ""])
    for file_info in manifest["files"]:
        lines.append(
            "- `{environment}/{split}-split.jsonl`: {rows} rows".format(
                **file_info,
            )
        )
    if manifest["errors"]:
        lines.extend(["", "## Errors", ""])
        for error in manifest["errors"]:
            lines.append(f"- `{error.get('dataset', 'unknown')}`: {error['error']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--data-registry", type=Path, default=DATA_REGISTRY_PATH)
    parser.add_argument("--environment-registry", type=Path, default=ENV_REGISTRY_PATH)
    parser.add_argument("--dataset-id", action="append", help="Limit to one dataset id. May be passed multiple times.")
    parser.add_argument("--max-train-per-dataset", type=int, default=None)
    parser.add_argument("--max-val-per-dataset", type=int, default=None)
    parser.add_argument("--non-streaming", action="store_true", help="Use cached HF datasets instead of streaming.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite target files generated by this script.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = prepare_assets(args)
    except Exception as exc:  # noqa: BLE001 - CLI should render a concise error.
        print(f"prepare_m0_assets.py: error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"output_dir": manifest["output_dir"], "datasets": manifest["datasets"]}, indent=2))
    return 0 if not manifest["errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
