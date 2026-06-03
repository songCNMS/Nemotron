#!/usr/bin/env python3
"""Task306 30B no-export/no-endpoint corrected AIME2025 eval.

Run this on NemTron from a task-owned /root repo sync. The script loads the
task301 30B Megatron checkpoint directly, generates completions for the task300
corrected AIME2025 30x1 cache through the task304 8-rank in-process MCore route,
and scores with the same parser/normalizer/denominator as the task300 base
runner.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import platform
import re
import socket
import sqlite3
import sys
import time
import traceback
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any


TASK_ID = "task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1"
ROUTE_ID = (
    "direct_in_process_mcore_static_engine_no_export_no_endpoint_"
    "30b_tp4_pp2_ep4_etp1_topk1_greedy_corrected_aime25"
)
BASE_SCORE = {"correct": 15, "total": 30, "accuracy": 0.5}
DEFAULT_BASE_ARTIFACT_ROOT = Path(
    "/work-agents/intern_nemotron_worker_3/outputs/"
    "task300_qwen_aime_v11_30b_same_harness_testing_s1/"
    "run_20260602T152008Z/eval/qwen30b_base_aime2025_30x1_20260602T152351Z"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(jsonable(data), indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(jsonable(row), sort_keys=True, ensure_ascii=False) + "\n")


def jsonable(value: Any) -> Any:
    try:
        import torch

        if isinstance(value, torch.dtype):
            return str(value)
        if isinstance(value, torch.Tensor):
            return value.detach().cpu().tolist()
    except Exception:
        pass
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    return repr(value)


def rank_env() -> dict[str, int]:
    return {
        "rank": int(os.environ.get("RANK", "0")),
        "local_rank": int(os.environ.get("LOCAL_RANK", "0")),
        "world_size": int(os.environ.get("WORLD_SIZE", "1")),
    }


def is_rank0() -> bool:
    return rank_env()["rank"] == 0


def append_rank_event(path: Path, event: str, **data: Any) -> None:
    row = {
        "time_unix": round(time.time(), 3),
        "event": event,
        **rank_env(),
        **data,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(jsonable(row), sort_keys=True, ensure_ascii=False) + "\n")


def cache_values(path: Path) -> list[dict[str, Any]]:
    connection = sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True)
    try:
        rows = connection.execute("select value from Cache").fetchall()
    finally:
        connection.close()
    return [json.loads(row[0]) for row in rows]


def first_pre_block(markup: str) -> str:
    match = re.search(r"<pre>(.*?)</pre>", markup or "", re.S)
    return html.unescape(match.group(1)) if match else ""


def html_value(markup: str, label: str) -> str | None:
    match = re.search(rf"<p>{re.escape(label)}:\s*(.*?)</p>", markup or "", re.S)
    return html.unescape(match.group(1)).strip() if match else None


def boxed_values(text: str) -> list[str]:
    values = []
    for pattern in ("\\boxed", "\\\\boxed"):
        index = 0
        while True:
            start = text.find(pattern, index)
            if start < 0:
                break
            open_brace = text.find("{", start)
            if open_brace < 0:
                break
            depth = 0
            for offset in range(open_brace, len(text)):
                if text[offset] == "{":
                    depth += 1
                elif text[offset] == "}":
                    depth -= 1
                    if depth == 0:
                        values.append(text[open_brace + 1 : offset])
                        index = offset + 1
                        break
            else:
                index = open_brace + 1
    deduped = []
    for value in values:
        if value not in deduped:
            deduped.append(value)
    return deduped


def normalize_answer(value: str | None) -> str:
    value = value or ""
    value = html.unescape(value)
    value = value.strip().strip("$").strip()
    value = value.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    value = value.replace("\\left", "").replace("\\right", "")
    value = value.replace("\\,", "").replace("\\!", "")
    value = value.replace("\u2212", "-")
    value = re.sub(r"\\text\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\s+", "", value)
    return value


def problem_from_prompt(prompt: str) -> str:
    if "Question:" in prompt:
        return prompt.split("Question:", 1)[-1].strip()
    return prompt.strip()


def load_aime_rows(score_cache: Path, limit: int) -> list[dict[str, Any]]:
    rows = []
    per_prompt_counts: Counter[str] = Counter()
    prompt_indices: dict[str, int] = {}
    for item in cache_values(score_cache):
        markup = item.get("html", "")
        prompt = first_pre_block(markup)
        expected = html_value(markup, "Correct Answer")
        if not prompt or expected is None:
            continue
        if prompt not in prompt_indices:
            prompt_indices[prompt] = len(prompt_indices) + 1
        per_prompt_counts[prompt] += 1
        rows.append(
            {
                "task": "aime25",
                "sample_id": (
                    f"aime_{prompt_indices[prompt]:02d}"
                    f"_r{per_prompt_counts[prompt]:02d}"
                ),
                "problem": problem_from_prompt(prompt),
                "original_prompt": prompt,
                "expected_answer": expected,
                "old_score": item.get("score"),
                "cache_key": item.get("key"),
            }
        )
        if limit and len(rows) >= limit:
            break
    return rows


def prompt_for(row: dict[str, Any], variant: str) -> str:
    if variant == "original":
        return row["original_prompt"]
    if variant == "concise_boxed":
        return (
            "Solve the following math problem. Keep the solution concise. "
            "End with exactly one final line of the form \\boxed{answer}. "
            "Do not write anything after the boxed answer.\n\n"
            f"Problem: {row['problem']}"
        )
    if variant == "answer_only":
        return (
            "Solve the problem internally. Return only the final answer inside "
            "\\boxed{answer}; do not include explanation or any extra text.\n\n"
            f"Problem: {row['problem']}"
        )
    raise ValueError(f"unknown prompt variant: {variant}")


def build_chat_prompt(hf_tokenizer: Any, prompt: str) -> str:
    messages = [{"role": "user", "content": prompt}]
    try:
        return hf_tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
            truncate_history_thinking=False,
        )
    except TypeError:
        try:
            return hf_tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False,
            )
        except TypeError:
            return hf_tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )


def detokenize_generated_tokens(tokenizer: Any, tokens: list[int]) -> str:
    if not tokens:
        return ""
    try:
        return tokenizer.detokenize(tokens, skip_special_tokens=True)
    except TypeError:
        return tokenizer.detokenize(tokens)


def file_inventory(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        if path.name == "checksum_manifest.json":
            continue
        rows.append(
            {
                "path": str(path),
                "relative_path": str(path.relative_to(root)),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return rows


def load_base_results(base_artifact_root: Path) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    summary_path = base_artifact_root / "summary.json"
    results_path = base_artifact_root / "results.jsonl"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.is_file() else None
    results: list[dict[str, Any]] = []
    if results_path.is_file():
        with results_path.open(encoding="utf-8") as f:
            results = [json.loads(line) for line in f if line.strip()]
    return summary, results


def summarize_task(items: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(items)
    ok_items = [item for item in items if item.get("status") == "ok"]
    correct_rows = sum(bool(item.get("correct")) for item in items)
    parsed_rows = sum(bool(item.get("parsed")) for item in items)
    old_scores = [
        float(item["old_score"])
        for item in items
        if isinstance(item.get("old_score"), (int, float))
    ]
    completion_tokens = [
        item.get("usage", {}).get("completion_tokens")
        for item in ok_items
        if item.get("usage", {}).get("completion_tokens") is not None
    ]
    return {
        "task": "aime25",
        "rows": total,
        "status_counts": dict(Counter(item.get("status") for item in items)),
        "finish_reason_counts": dict(Counter(item.get("finish_reason") for item in items)),
        "parsed_rows": parsed_rows,
        "parsed_rate": parsed_rows / total if total else None,
        "correct_rows": correct_rows,
        "exact_normalized_accuracy": correct_rows / total if total else None,
        "contains_expected_rows": sum(bool(item.get("contains_expected")) for item in items),
        "source_cache_old_score_mean": mean(old_scores) if old_scores else None,
        "successful_responses": len(ok_items),
        "avg_completion_tokens": mean(completion_tokens) if completion_tokens else None,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--checkpoint-iter-dir", required=True, type=Path)
    parser.add_argument("--base-model-path", required=True, type=Path)
    parser.add_argument("--aime-score-cache", required=True, type=Path)
    parser.add_argument("--base-artifact-root", type=Path, default=DEFAULT_BASE_ARTIFACT_ROOT)
    parser.add_argument("--source-head", required=True)
    parser.add_argument("--aime-prompt-variant", default="original", choices=("original",))
    parser.add_argument("--aime-limit-rows", type=int, default=30)
    parser.add_argument("--max-tokens", type=int, default=8192)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--top-k", type=int, default=1)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top-p", type=float, default=0.0)
    parser.add_argument("--random-seed", type=int, default=1234)
    parser.add_argument("--tensor-model-parallel-size", type=int, default=4)
    parser.add_argument("--pipeline-model-parallel-size", type=int, default=2)
    parser.add_argument("--expert-model-parallel-size", type=int, default=4)
    parser.add_argument("--expert-tensor-parallel-size", type=int, default=1)
    parser.add_argument("--context-parallel-size", type=int, default=1)
    parser.add_argument("--rank-timeout-minutes", type=int, default=60)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    env = rank_env()
    rank = env["rank"]
    local_rank = env["local_rank"]
    world_size = env["world_size"]
    output_root = args.output_root
    eval_dir = output_root / "aime_eval"
    manifests_dir = output_root / "manifests"
    logs_dir = output_root / "logs"
    rank_logs_dir = logs_dir / "ranks"
    blockers_dir = output_root / "blockers"
    for path in (eval_dir, manifests_dir, logs_dir, rank_logs_dir, blockers_dir):
        path.mkdir(parents=True, exist_ok=True)
    rank_log = rank_logs_dir / f"rank{rank:02d}_events.jsonl"
    start_time = time.time()

    command_manifest_path = manifests_dir / f"command_env_manifest_rank{rank}.json"
    expected_world = (
        args.tensor_model_parallel_size
        * args.pipeline_model_parallel_size
        * args.context_parallel_size
    )
    command_manifest: dict[str, Any] = {
        "schema_version": 1,
        "task_id": TASK_ID,
        "route": ROUTE_ID,
        "source_head": args.source_head,
        "argv": sys.argv,
        "host": socket.gethostname(),
        "platform": platform.platform(),
        "python": sys.executable,
        "python_version": sys.version,
        "cwd": os.getcwd(),
        "rank_env": env,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "pythonpath": os.environ.get("PYTHONPATH"),
        "checkpoint_iter_dir": str(args.checkpoint_iter_dir),
        "base_model_path": str(args.base_model_path),
        "aime_score_cache": str(args.aime_score_cache),
        "base_artifact_root": str(args.base_artifact_root),
        "sampling": {
            "max_tokens": args.max_tokens,
            "temperature": args.temperature,
            "top_k": args.top_k,
            "top_p": args.top_p,
            "random_seed": args.random_seed,
            "batch_size": args.batch_size,
        },
        "parallelism": {
            "world_size": world_size,
            "expected_world_size": expected_world,
            "tensor_model_parallel_size": args.tensor_model_parallel_size,
            "pipeline_model_parallel_size": args.pipeline_model_parallel_size,
            "expert_model_parallel_size": args.expert_model_parallel_size,
            "expert_tensor_parallel_size": args.expert_tensor_parallel_size,
            "context_parallel_size": args.context_parallel_size,
        },
        "route_adjustments": [
            "distributed torchrun route uses task301 checkpoint parallelism TP=4 PP=2 EP=4 ETP=1",
            "load_megatron_model receives explicit mp_overrides matching task301 checkpoint parallelism",
            "checkpoint model_config.attention_backend None is set in-memory to AttnBackend.auto",
            "MCore SamplingParams uses top_k=1 greedy branch to mirror deterministic endpoint temperature=0 intent without endpoint launch",
            "if MCore request.generated_text is empty, response_text falls back to checkpoint tokenizer detokenize(generated_tokens)",
        ],
        "boundary_confirmations": {
            "qwen3_30b_only": True,
            "no_training_or_optimizer_steps": True,
            "no_aime2025_train_prompts_or_labels": True,
            "aime2025_eval_input_only": True,
            "no_task255_reuse": True,
            "no_export_or_conversion": True,
            "no_endpoint": True,
            "no_production_endpoint": True,
            "no_promotion": True,
            "no_shared_deletion": True,
            "no_main_push_or_merge": True,
        },
    }

    try:
        append_rank_event(rank_log, "start")
        import torch

        command_manifest["torch"] = {
            "version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "cuda_device_count": torch.cuda.device_count(),
        }
        if world_size != expected_world:
            raise RuntimeError(
                f"task306 requires world_size={expected_world} for TP*PP*CP, got {world_size}"
            )
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is not available")
        if local_rank >= torch.cuda.device_count():
            raise RuntimeError(
                f"local_rank={local_rank} but cuda_device_count={torch.cuda.device_count()}"
            )
        torch.cuda.set_device(local_rank)
        command_manifest["torch"]["current_device"] = torch.cuda.current_device()
        command_manifest["torch"]["current_device_name"] = torch.cuda.get_device_name(
            torch.cuda.current_device()
        )
        if args.batch_size < 1:
            raise ValueError("--batch-size must be positive")
        for path, label in (
            (args.checkpoint_iter_dir, "checkpoint iter dir"),
            (args.base_model_path, "base model path"),
            (args.base_artifact_root, "base artifact root"),
        ):
            if not path.is_dir():
                raise FileNotFoundError(f"{label} not found: {path}")
        if not args.aime_score_cache.is_file():
            raise FileNotFoundError(f"aime score cache not found: {args.aime_score_cache}")
        write_json(command_manifest_path, command_manifest)

        from transformers import AutoTokenizer

        import datetime
        import torch.distributed as dist
        from megatron.bridge.training.model_load_save import (
            load_megatron_model,
            load_model_config,
            load_tokenizer,
        )
        from megatron.core import parallel_state
        from megatron.core.inference.contexts import StaticInferenceContext
        from megatron.core.inference.engines.static_engine import StaticInferenceEngine
        from megatron.core.inference.model_inference_wrappers.gpt.gpt_inference_wrapper import (
            GPTInferenceWrapper,
        )
        from megatron.core.inference.model_inference_wrappers.inference_wrapper_config import (
            InferenceWrapperConfig,
        )
        from megatron.core.inference.sampling_params import SamplingParams
        from megatron.core.inference.text_generation_controllers.text_generation_controller import (
            TextGenerationController,
        )
        from megatron.core.transformer.enums import AttnBackend
        from megatron.core.utils import get_model_config
        from megatron.core.utils import unwrap_model

        if not dist.is_initialized():
            dist.init_process_group(
                backend="nccl",
                init_method="env://",
                timeout=datetime.timedelta(minutes=args.rank_timeout_minutes),
            )
        append_rank_event(rank_log, "dist_initialized")

        base_summary, base_results = load_base_results(args.base_artifact_root)
        source_cache_sha = sha256_file(args.aime_score_cache)
        base_file_hashes = {
            path.name: sha256_file(path)
            for path in sorted(args.base_artifact_root.iterdir())
            if path.is_file()
        }

        hf_tokenizer = AutoTokenizer.from_pretrained(
            str(args.base_model_path), trust_remote_code=False
        )
        rows = load_aime_rows(args.aime_score_cache, args.aime_limit_rows)
        if len(rows) != args.aime_limit_rows:
            raise RuntimeError(
                f"expected {args.aime_limit_rows} AIME rows, loaded {len(rows)}"
            )
        prompts: list[dict[str, Any]] = []
        for row in rows:
            prompt_text = prompt_for(row, args.aime_prompt_variant)
            formatted_prompt = build_chat_prompt(hf_tokenizer, prompt_text)
            prompts.append(
                {
                    **row,
                    "prompt": prompt_text,
                    "prompt_variant": args.aime_prompt_variant,
                    "max_tokens": args.max_tokens,
                    "prompt_sha256": hashlib.sha256(prompt_text.encode("utf-8")).hexdigest(),
                    "formatted_prompt": formatted_prompt,
                    "formatted_prompt_sha256": hashlib.sha256(
                        formatted_prompt.encode("utf-8")
                    ).hexdigest(),
                    "formatted_prompt_chars": len(formatted_prompt),
                    "hf_chat_template_used": True,
                    "hf_chat_template_enable_thinking_false": True,
                }
            )

        base_by_sample = {row.get("sample_id"): row for row in base_results}
        prompt_token_matches = []
        for prompt in prompts:
            base_row = base_by_sample.get(prompt["sample_id"], {})
            base_prompt_tokens = (base_row.get("usage") or {}).get("prompt_tokens")
            prompt_token_matches.append(
                {
                    "sample_id": prompt["sample_id"],
                    "local_formatted_prompt_tokens": None,
                    "base_prompt_tokens": base_prompt_tokens,
                    "matches_base": None,
                }
            )

        distributed_manifest: dict[str, Any] = {
            "dist_was_initialized_before_probe": dist.is_initialized(),
            "model_parallel_was_initialized_before_probe": parallel_state.model_parallel_is_initialized(),
            "backend": "nccl",
            "world_size": world_size,
            "rank": rank,
            "local_rank": local_rank,
            "tensor_model_parallel_size": args.tensor_model_parallel_size,
            "pipeline_model_parallel_size": args.pipeline_model_parallel_size,
            "context_parallel_size": args.context_parallel_size,
            "expert_model_parallel_size": args.expert_model_parallel_size,
            "expert_tensor_parallel_size": args.expert_tensor_parallel_size,
        }
        if not parallel_state.model_parallel_is_initialized():
            parallel_state.initialize_model_parallel(
                tensor_model_parallel_size=args.tensor_model_parallel_size,
                pipeline_model_parallel_size=args.pipeline_model_parallel_size,
                context_parallel_size=args.context_parallel_size,
                expert_model_parallel_size=args.expert_model_parallel_size,
                expert_tensor_parallel_size=args.expert_tensor_parallel_size,
            )
            distributed_manifest["model_parallel_initialized_by_script"] = True
        else:
            distributed_manifest["model_parallel_initialized_by_script"] = False
        try:
            from megatron.core.tensor_parallel import model_parallel_cuda_manual_seed

            model_parallel_cuda_manual_seed(args.random_seed)
            distributed_manifest["model_parallel_cuda_manual_seed"] = args.random_seed
        except Exception as seed_exc:  # noqa: BLE001
            distributed_manifest["model_parallel_cuda_manual_seed_error"] = repr(seed_exc)
        command_manifest["distributed"] = distributed_manifest
        write_json(command_manifest_path, command_manifest)
        append_rank_event(rank_log, "model_parallel_initialized")

        cfg, mlm_args = load_model_config(str(args.checkpoint_iter_dir))
        tokenizer = load_tokenizer(str(args.checkpoint_iter_dir))
        append_rank_event(rank_log, "checkpoint_config_tokenizer_loaded")
        mp_overrides = {
            "tensor_model_parallel_size": args.tensor_model_parallel_size,
            "pipeline_model_parallel_size": args.pipeline_model_parallel_size,
            "context_parallel_size": args.context_parallel_size,
            "expert_model_parallel_size": args.expert_model_parallel_size,
            "expert_tensor_parallel_size": args.expert_tensor_parallel_size,
            "sequence_parallel": True,
            "virtual_pipeline_model_parallel_size": None,
            "hierarchical_context_parallel_sizes": None,
            "perform_initialization": False,
        }
        command_manifest["load_megatron_model_mp_overrides"] = mp_overrides
        write_json(command_manifest_path, command_manifest)
        append_rank_event(rank_log, "load_megatron_model_start", mp_overrides=mp_overrides)
        model = load_megatron_model(
            str(args.checkpoint_iter_dir),
            mp_overrides=mp_overrides,
            skip_temp_dist_context=True,
        )
        model_obj = model[0] if isinstance(model, list) else model
        model_obj.eval()
        append_rank_event(rank_log, "checkpoint_model_loaded")
        unwrapped_once = unwrap_model(model_obj)
        unwrapped_model = unwrapped_once[0] if isinstance(unwrapped_once, list) else unwrapped_once
        model_config = get_model_config(model_obj)
        attention_backend_before = repr(getattr(model_config, "attention_backend", None))
        if getattr(model_config, "attention_backend", None) is None:
            model_config.attention_backend = AttnBackend.auto
        attention_backend_after = repr(getattr(model_config, "attention_backend", None))

        padded_vocab_size = (
            getattr(model_config, "padded_vocab_size", None)
            or getattr(model_config, "vocab_size", None)
            or getattr(tokenizer, "vocab_size", None)
        )
        if padded_vocab_size is None:
            raise RuntimeError("could not resolve padded vocab size from model config or tokenizer")

        max_prompt_tokens = 0
        for prompt, match_row in zip(prompts, prompt_token_matches):
            token_count = len(tokenizer.tokenize(prompt["formatted_prompt"]))
            prompt["megatron_prompt_token_count"] = token_count
            match_row["local_formatted_prompt_tokens"] = token_count
            match_row["matches_base"] = (
                match_row["base_prompt_tokens"] == token_count
                if match_row["base_prompt_tokens"] is not None
                else None
            )
            max_prompt_tokens = max(max_prompt_tokens, token_count)

        prompt_manifest = {
            "schema_version": 1,
            "task_id": TASK_ID,
            "source_cache": str(args.aime_score_cache),
            "source_cache_sha256": source_cache_sha,
            "base_artifact_root": str(args.base_artifact_root),
            "base_score": BASE_SCORE,
            "base_summary": base_summary,
            "base_file_hashes": base_file_hashes,
            "prompt_variant": args.aime_prompt_variant,
            "row_count": len(prompts),
            "hf_chat_template_used": True,
            "hf_chat_template_enable_thinking_false": True,
            "prompt_token_match_against_task300_base": prompt_token_matches,
            "prompt_token_mismatch_count": sum(
                1 for row in prompt_token_matches if row["matches_base"] is False
            ),
            "prompts": [
                {
                    key: prompt[key]
                    for key in (
                        "sample_id",
                        "expected_answer",
                        "prompt_sha256",
                        "formatted_prompt_sha256",
                        "formatted_prompt_chars",
                        "megatron_prompt_token_count",
                    )
                }
                for prompt in prompts
            ],
        }
        prompt_manifest_path = manifests_dir / "aime_prompt_manifest.json"
        if is_rank0():
            write_json(prompt_manifest_path, prompt_manifest)

        checkpoint_manifest = {
            "schema_version": 1,
            "task_id": TASK_ID,
            "rank": rank,
            "checkpoint_iter_dir": str(args.checkpoint_iter_dir),
            "base_model_path": str(args.base_model_path),
            "load_megatron_model": "PASS",
            "model_return_type": f"{type(model).__module__}.{type(model).__qualname__}",
            "model_list_len": len(model) if isinstance(model, list) else None,
            "model0_type": f"{type(model_obj).__module__}.{type(model_obj).__qualname__}",
            "unwrapped_model_type": f"{type(unwrapped_model).__module__}.{type(unwrapped_model).__qualname__}",
            "model_device": str(next(model_obj.parameters()).device),
            "model_dtype": str(next(model_obj.parameters()).dtype),
            "model_eval": not model_obj.training,
            "cfg_type": f"{type(cfg).__module__}.{type(cfg).__qualname__}",
            "mlm_args_present": mlm_args is not None,
            "attention_backend_before": attention_backend_before,
            "attention_backend_after": attention_backend_after,
            "hidden_size": getattr(model_config, "hidden_size", None),
            "num_layers": getattr(model_config, "num_layers", None),
            "num_attention_heads": getattr(model_config, "num_attention_heads", None),
            "seq_length": getattr(model_config, "seq_length", None),
            "tensor_model_parallel_size": getattr(
                model_config, "tensor_model_parallel_size", None
            ),
            "pipeline_model_parallel_size": getattr(
                model_config, "pipeline_model_parallel_size", None
            ),
            "expert_model_parallel_size": getattr(
                model_config, "expert_model_parallel_size", None
            ),
            "expert_tensor_parallel_size": getattr(
                model_config, "expert_tensor_parallel_size", None
            ),
            "sequence_parallel": getattr(model_config, "sequence_parallel", None),
            "params_dtype": str(getattr(model_config, "params_dtype", None)),
            "padded_vocab_size": padded_vocab_size,
            "raw_tokenizer_vocab_size": getattr(tokenizer, "vocab_size", None),
            "tokenizer_type": f"{type(tokenizer).__module__}.{type(tokenizer).__qualname__}",
            "tokenizer_vocab_size": getattr(tokenizer, "vocab_size", None),
            "tokenizer_eod": getattr(tokenizer, "eod", None),
            "tokenizer_bos": getattr(tokenizer, "bos", None),
            "pipeline_stage": {
                "is_first": parallel_state.is_pipeline_first_stage(),
                "is_last": parallel_state.is_pipeline_last_stage(),
                "tensor_rank": parallel_state.get_tensor_model_parallel_rank(),
                "pipeline_rank": parallel_state.get_pipeline_model_parallel_rank(),
                "expert_rank": parallel_state.get_expert_model_parallel_rank(),
            },
        }
        checkpoint_manifest_path = manifests_dir / f"checkpoint_load_manifest_rank{rank}.json"
        write_json(checkpoint_manifest_path, checkpoint_manifest)

        inference_max_seq_length = max(
            max_prompt_tokens + args.max_tokens + 8,
            args.max_tokens + 512,
        )
        wrapper_config = InferenceWrapperConfig(
            hidden_size=int(getattr(model_config, "hidden_size")),
            params_dtype=getattr(model_config, "params_dtype"),
            inference_batch_times_seqlen_threshold=int(
                getattr(model_config, "inference_batch_times_seqlen_threshold", 512)
            ),
            padded_vocab_size=int(padded_vocab_size),
            inference_max_requests=args.batch_size,
            inference_max_seq_length=inference_max_seq_length,
            fp32_residual_connection=bool(
                getattr(model_config, "fp32_residual_connection", False)
            ),
            fp8=getattr(model_config, "fp8", None),
        )
        inference_context = StaticInferenceContext.from_config(wrapper_config)
        inference_wrapper = GPTInferenceWrapper(model_obj, wrapper_config, inference_context)
        controller = TextGenerationController(
            inference_wrapper,
            tokenizer,
            pp_group=parallel_state.get_pipeline_model_parallel_group(),
        )
        engine = StaticInferenceEngine(
            controller,
            max_batch_size=args.batch_size,
            random_seed=args.random_seed,
            legacy=True,
        )
        sampling_params = SamplingParams(
            temperature=args.temperature,
            top_k=args.top_k,
            top_p=args.top_p,
            return_log_probs=False,
            return_segments=False,
            num_tokens_to_generate=args.max_tokens,
        )

        result_rows: list[dict[str, Any]] = []
        full_rows: list[dict[str, Any]] = []
        parser_rows: list[dict[str, Any]] = []
        for start_index in range(0, len(prompts), args.batch_size):
            chunk = prompts[start_index : start_index + args.batch_size]
            formatted_prompts = [prompt["formatted_prompt"] for prompt in chunk]
            batch_start = time.time()
            append_rank_event(
                rank_log,
                "generation_batch_start",
                start_index=start_index,
                batch_size=len(chunk),
            )
            with torch.inference_mode():
                requests = engine.generate(
                    prompts=formatted_prompts,
                    sampling_params=sampling_params,
                )
            batch_latency = round(time.time() - batch_start, 4)
            append_rank_event(
                rank_log,
                "generation_batch_done",
                start_index=start_index,
                batch_size=len(chunk),
                latency_sec=batch_latency,
            )
            for prompt, request in zip(chunk, requests):
                generated_tokens = (
                    request.generated_tokens.detach().cpu().tolist()
                    if request.generated_tokens is not None
                    else []
                )
                generated_text = request.generated_text or ""
                response_text_source = "request.generated_text"
                if not generated_text.strip() and generated_tokens:
                    generated_text = detokenize_generated_tokens(tokenizer, generated_tokens)
                    response_text_source = "generated_tokens_detokenize_fallback"
                completion_tokens = (
                    int(request.generated_length)
                    if request.generated_length is not None
                    else len(generated_tokens)
                )
                finish_reason = "length" if completion_tokens >= args.max_tokens else "stop"
                boxed = boxed_values(generated_text)
                prediction = boxed[-1] if boxed else None
                expected = prompt.get("expected_answer")
                result_row = {
                    "task": "aime25",
                    "sample_id": prompt["sample_id"],
                    "prompt_variant": args.aime_prompt_variant,
                    "max_tokens": args.max_tokens,
                    "expected_answer": expected,
                    "old_score": prompt.get("old_score"),
                    "status": "ok" if generated_text.strip() else "empty",
                    "latency_sec": batch_latency,
                    "finish_reason": finish_reason,
                    "response_chars": len(generated_text),
                    "response_sha256": hashlib.sha256(
                        generated_text.encode("utf-8")
                    ).hexdigest(),
                    "response_tail": generated_text[-1200:],
                    "boxed_values": boxed,
                    "parsed": prediction is not None,
                    "prediction": prediction,
                    "normalized_prediction": normalize_answer(prediction),
                    "normalized_expected": normalize_answer(expected),
                    "contains_expected": bool(
                        expected and normalize_answer(expected) in normalize_answer(generated_text)
                    ),
                    "correct": normalize_answer(prediction) == normalize_answer(expected),
                    "usage": {
                        "prompt_tokens": prompt.get("megatron_prompt_token_count"),
                        "completion_tokens": completion_tokens,
                        "total_tokens": (
                            prompt.get("megatron_prompt_token_count", 0) + completion_tokens
                        ),
                        "reasoning_tokens": 0,
                    },
                    "route": ROUTE_ID,
                    "response_text_source": response_text_source,
                    "rank": rank,
                }
                result_rows.append(result_row)
                full_rows.append(
                    {
                        **result_row,
                        "raw_prompt": prompt["prompt"],
                        "formatted_prompt": prompt["formatted_prompt"],
                        "formatted_prompt_sha256": prompt["formatted_prompt_sha256"],
                        "generated_tokens": generated_tokens,
                        "full_text": prompt["formatted_prompt"] + generated_text,
                    }
                )
                parser_rows.append(
                    {
                        "sample_id": result_row["sample_id"],
                        "status": result_row["status"],
                        "finish_reason": result_row["finish_reason"],
                        "boxed_values": result_row["boxed_values"],
                        "prediction": result_row["prediction"],
                        "normalized_prediction": result_row["normalized_prediction"],
                        "expected_answer": result_row["expected_answer"],
                        "normalized_expected": result_row["normalized_expected"],
                        "parsed": result_row["parsed"],
                        "correct": result_row["correct"],
                        "contains_expected": result_row["contains_expected"],
                        "response_chars": result_row["response_chars"],
                        "response_sha256": result_row["response_sha256"],
                        "usage": result_row["usage"],
                        "response_text_source": result_row["response_text_source"],
                        "rank": rank,
                    }
                )
                print(
                    "progress "
                    f"{len(result_rows)}/{len(prompts)} aime25 {prompt['sample_id']} "
                    f"{finish_reason} parsed={result_row['parsed']} "
                    f"correct={result_row['correct']} source={response_text_source}",
                    flush=True,
                )

        result_rows = sorted(result_rows, key=lambda item: str(item["sample_id"]))
        full_rows = sorted(full_rows, key=lambda item: str(item["sample_id"]))
        parser_rows = sorted(parser_rows, key=lambda item: str(item["sample_id"]))
        rank_results_path = eval_dir / f"results_rank{rank}.jsonl"
        rank_full_path = eval_dir / f"full_completions_rank{rank}.jsonl"
        rank_parser_path = eval_dir / f"parser_diagnostics_rank{rank}.jsonl"
        write_jsonl(rank_results_path, result_rows)
        write_jsonl(rank_full_path, full_rows)
        write_jsonl(rank_parser_path, parser_rows)
        rank_task_summary = summarize_task(result_rows)
        write_json(
            eval_dir / f"rank{rank}_summary.json",
            {
                "schema_version": 1,
                "task_id": TASK_ID,
                "rank": rank,
                "route": ROUTE_ID,
                "summary": rank_task_summary,
                "runtime_sec": round(time.time() - start_time, 3),
            },
        )

        dist.barrier()
        if is_rank0():
            selected_rank = 0
            selected_results_path = eval_dir / f"results_rank{selected_rank}.jsonl"
            selected_full_path = eval_dir / f"full_completions_rank{selected_rank}.jsonl"
            selected_parser_path = eval_dir / f"parser_diagnostics_rank{selected_rank}.jsonl"
            result_rows = [
                json.loads(line)
                for line in selected_results_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            full_rows = [
                json.loads(line)
                for line in selected_full_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            parser_rows = [
                json.loads(line)
                for line in selected_parser_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            results_path = eval_dir / "results.jsonl"
            full_path = eval_dir / "full_completions.jsonl"
            parser_path = eval_dir / "parser_diagnostics.jsonl"
            write_jsonl(results_path, result_rows)
            write_jsonl(full_path, full_rows)
            write_jsonl(parser_path, parser_rows)

            task_summary = summarize_task(result_rows)
            ft_correct = int(task_summary["correct_rows"])
            ft_total = int(task_summary["rows"])
            prompt_mismatch_count = int(prompt_manifest["prompt_token_mismatch_count"])
            if ft_total != BASE_SCORE["total"]:
                disposition = "HOLD"
                disposition_reason = "FT denominator does not match accepted base denominator"
            elif prompt_mismatch_count:
                disposition = "HOLD"
                disposition_reason = "Prompt tokenization mismatched accepted base artifacts"
            elif ft_correct >= BASE_SCORE["correct"]:
                disposition = "PASS"
                disposition_reason = "FT exact-normalized score is >= accepted base"
            else:
                disposition = "FAIL"
                disposition_reason = "FT exact-normalized score is below accepted base"

            protocol_proof = {
                "accepted_base": BASE_SCORE,
                "base_artifact_root": str(args.base_artifact_root),
                "base_summary": base_summary,
                "base_file_hashes": base_file_hashes,
                "same_aime_score_cache": True,
                "aime_score_cache_sha256": source_cache_sha,
                "same_prompt_variant": args.aime_prompt_variant == "original",
                "same_row_count_and_denominator": len(result_rows) == BASE_SCORE["total"],
                "same_parser_normalizer": (
                    "boxed_values, normalize_answer, correct, contains_expected copied "
                    "from task300/task247 corrected AIME runner"
                ),
                "same_all_request_denominator": True,
                "same_max_tokens": args.max_tokens == 8192,
                "prompt_token_mismatch_count": prompt_mismatch_count,
                "prompt_tokens_match_task300_base": prompt_mismatch_count == 0,
                "generation_backend": (
                    "MCore in-process static engine; no export and no endpoint by task306 "
                    "boundary preference"
                ),
                "base_generation_backend": (
                    "SGLang /v1/chat/completions endpoint from task300 artifact"
                ),
                "sampling_exact_parameter_match": False,
                "sampling_semantic_match": (
                    "deterministic greedy intent: task300 used temperature=0/top_p=1e-5; "
                    "task306 local MCore uses top_k=1 greedy branch with temperature=1/top_p=0"
                ),
                "selected_rank_policy": "rank0 aggregate; no best-correct rank selection",
            }

            summary = {
                "schema_version": 1,
                "task_id": TASK_ID,
                "disposition": disposition,
                "disposition_reason": disposition_reason,
                "route": ROUTE_ID,
                "source_head": args.source_head,
                "model": "task301-qwen3-30b-a3b-v11-ft-iter0000035",
                "checkpoint_iter_dir": str(args.checkpoint_iter_dir),
                "base_model_path": str(args.base_model_path),
                "output_root": str(output_root),
                "selected_rank": selected_rank,
                "protocol": {
                    "aime_prompt_variant": args.aime_prompt_variant,
                    "aime_max_tokens": args.max_tokens,
                    "temperature": args.temperature,
                    "top_k": args.top_k,
                    "top_p": args.top_p,
                    "tasks": ["aime25"],
                    "transport": "no_export_no_endpoint_mcore_static_engine",
                    "parallelism": command_manifest["parallelism"],
                },
                "total_requests": len(result_rows),
                "by_task": {"aime25": task_summary},
                "accepted_base_comparison": {
                    "base_correct": BASE_SCORE["correct"],
                    "base_total": BASE_SCORE["total"],
                    "base_accuracy": BASE_SCORE["accuracy"],
                    "ft_correct": ft_correct,
                    "ft_total": ft_total,
                    "ft_accuracy": task_summary["exact_normalized_accuracy"],
                    "delta_correct": ft_correct - BASE_SCORE["correct"],
                    "delta_accuracy": (
                        task_summary["exact_normalized_accuracy"] - BASE_SCORE["accuracy"]
                        if task_summary["exact_normalized_accuracy"] is not None
                        else None
                    ),
                },
                "rank_summaries": [
                    json.loads(path.read_text(encoding="utf-8"))
                    for path in sorted(eval_dir.glob("rank*_summary.json"))
                ],
                "protocol_proof": protocol_proof,
                "runtime_sec": round(time.time() - start_time, 3),
                "boundary_confirmations": command_manifest["boundary_confirmations"],
                "artifact_paths": {
                    "summary": str(eval_dir / "summary.json"),
                    "results": str(results_path),
                    "full_completions": str(full_path),
                    "parser_diagnostics": str(parser_path),
                    "rank_results_glob": str(eval_dir / "results_rank*.jsonl"),
                    "rank_full_completions_glob": str(
                        eval_dir / "full_completions_rank*.jsonl"
                    ),
                    "command_env_manifests_glob": str(
                        manifests_dir / "command_env_manifest_rank*.json"
                    ),
                    "prompt_manifest": str(prompt_manifest_path),
                    "checkpoint_load_manifests_glob": str(
                        manifests_dir / "checkpoint_load_manifest_rank*.json"
                    ),
                    "checksum_manifest": str(manifests_dir / "checksum_manifest.json"),
                },
            }
            summary_path = eval_dir / "summary.json"
            write_json(summary_path, summary)

            checksum_manifest_path = manifests_dir / "checksum_manifest.json"
            write_json(
                checksum_manifest_path,
                {
                    "schema_version": 1,
                    "task_id": TASK_ID,
                    "output_root": str(output_root),
                    "files": file_inventory(output_root),
                },
            )
            print(f"TASK306_DISPOSITION={disposition}")
            print(f"TASK306_FT_SCORE={ft_correct}/{ft_total}")
            print(f"TASK306_OUTPUT_ROOT={output_root}")
        dist.barrier()
        return 0
    except Exception as exc:  # noqa: BLE001
        blocker = {
            "schema_version": 1,
            "task_id": TASK_ID,
            "status": "BLOCK",
            "route": ROUTE_ID,
            "rank": rank,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "source_head": args.source_head,
            "checkpoint_iter_dir": str(args.checkpoint_iter_dir),
            "base_model_path": str(args.base_model_path),
            "aime_score_cache": str(args.aime_score_cache),
            "base_artifact_root": str(args.base_artifact_root),
            "elapsed_seconds": round(time.time() - start_time, 3),
            "boundary_confirmations": command_manifest["boundary_confirmations"],
        }
        blocker_path = blockers_dir / f"aime_blocker_rank{rank}.json"
        write_json(blocker_path, blocker)
        command_manifest["blocker_path"] = str(blocker_path)
        write_json(command_manifest_path, command_manifest)
        checksum_manifest_path = manifests_dir / "checksum_manifest.json"
        write_json(
            checksum_manifest_path,
            {
                "schema_version": 1,
                "task_id": TASK_ID,
                "output_root": str(output_root),
                "files": file_inventory(output_root),
            },
        )
        print("TASK306_DISPOSITION=BLOCK")
        print(f"TASK306_BLOCKER={type(exc).__name__}: {exc}")
        print(f"TASK306_OUTPUT_ROOT={output_root}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
