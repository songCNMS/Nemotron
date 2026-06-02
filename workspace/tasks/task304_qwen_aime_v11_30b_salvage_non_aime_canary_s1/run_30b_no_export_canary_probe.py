#!/usr/bin/env python3
"""Task304 30B no-export/no-endpoint non-AIME canary probe.

Run on NemTron from a task-owned /root repo sync. This script is a 30B-specific
distributed adaptation of the task291 no-export canary route. It loads the
task301 Megatron checkpoint directly and attempts in-process MCore generation
for the approved synthetic non-AIME canary prompts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import socket
import sys
import time
import traceback
from pathlib import Path
from typing import Any


TASK_ID = "task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1"
ROUTE_ID = (
    "direct_in_process_mcore_static_engine_no_export_no_endpoint_"
    "30b_tp4_pp2_ep4_etp1_topk1_greedy"
)

FINAL_ANSWER_RE = re.compile(
    r"(?:Final\s+Answer\s*:\s*(?:\\boxed\{([^}]*)\}|([^\n]+)))|(?:\\boxed\{([^}]*)\})",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--checkpoint-iter-dir", required=True, type=Path)
    parser.add_argument("--base-model-path", required=True, type=Path)
    parser.add_argument("--prompt-yaml", required=True, type=Path)
    parser.add_argument("--source-head", required=True)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--top-k", type=int, default=1)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top-p", type=float, default=0.0)
    parser.add_argument("--random-seed", type=int, default=1234)
    parser.add_argument("--tensor-model-parallel-size", type=int, default=4)
    parser.add_argument("--pipeline-model-parallel-size", type=int, default=2)
    parser.add_argument("--expert-model-parallel-size", type=int, default=4)
    parser.add_argument("--expert-tensor-parallel-size", type=int, default=1)
    parser.add_argument("--context-parallel-size", type=int, default=1)
    parser.add_argument("--rank-timeout-minutes", type=int, default=30)
    return parser.parse_args()


def rank_env() -> dict[str, int]:
    return {
        "rank": int(os.environ.get("RANK", "0")),
        "local_rank": int(os.environ.get("LOCAL_RANK", "0")),
        "world_size": int(os.environ.get("WORLD_SIZE", "1")),
    }


def is_rank0() -> bool:
    return rank_env()["rank"] == 0


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(jsonable(data), indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(jsonable(row), sort_keys=True, ensure_ascii=True) + "\n")


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


def append_rank_event(path: Path, event: str, **data: Any) -> None:
    row = {
        "time_unix": round(time.time(), 3),
        "event": event,
        **rank_env(),
        **data,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(jsonable(row), sort_keys=True) + "\n")


def extract_final_answer(text: str) -> str | None:
    for match in FINAL_ANSWER_RE.finditer(text):
        for group in match.groups():
            if group and group.strip():
                return group.strip()
    return None


def normalize_answer(value: Any) -> str:
    text = str(value).strip().lower()
    text = text.replace("\\boxed", "")
    text = text.replace("{", "").replace("}", "")
    return re.sub(r"[^a-z0-9.+\\-_/]+", "", text)


def count_final_markers(text: str) -> int:
    return len(re.findall(r"Final\s+Answer\s*:", text, flags=re.IGNORECASE)) + len(
        re.findall(r"\\boxed\{", text)
    )


def degeneration_flags(text: str) -> dict[str, Any]:
    stripped = text.strip()
    words = re.findall(r"\S+", stripped)
    repeated_runs = 0
    prev = None
    current = 0
    for word in words:
        if word == prev:
            current += 1
        else:
            current = 1
            prev = word
        repeated_runs = max(repeated_runs, current)
    non_ascii = sum(1 for ch in stripped if ord(ch) > 127)
    return {
        "empty": not bool(stripped),
        "chars": len(text),
        "words": len(words),
        "non_ascii_chars": non_ascii,
        "mixed_script_flag": non_ascii > 0,
        "max_repeated_token_run": repeated_runs,
        "degeneration_flag": repeated_runs >= 8,
    }


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


def load_prompt_set(prompt_yaml: Path, base_model_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    from transformers import AutoTokenizer

    from nemotron.recipes.super3.milestones.m1_eval_basket.qwen_aime2025_base_vs_ft_gate import (
        load_v11_canary_prompt_set,
    )

    prompt_set = load_v11_canary_prompt_set(prompt_yaml)
    hf_tokenizer = AutoTokenizer.from_pretrained(str(base_model_path), trust_remote_code=False)
    prompts: list[dict[str, Any]] = []
    for prompt in prompt_set["prompts"]:
        prompt_text = str(prompt["prompt"])
        if "aime" in prompt_text.lower():
            raise RuntimeError(f"forbidden AIME text in canary prompt {prompt['id']}")
        formatted_prompt = build_chat_prompt(hf_tokenizer, prompt_text)
        prompts.append(
            {
                "id": str(prompt["id"]),
                "category": str(prompt["category"]),
                "prompt": prompt_text,
                "expected_answer": str(prompt["expected_answer"]),
                "prompt_sha256": sha256_text(prompt_text),
                "formatted_prompt": formatted_prompt,
                "formatted_prompt_sha256": sha256_text(formatted_prompt),
                "formatted_prompt_chars": len(formatted_prompt),
                "hf_chat_template_used": True,
            }
        )
    return prompt_set, prompts


def write_blocker(
    args: argparse.Namespace,
    canary_dir: Path,
    manifests_dir: Path,
    command_manifest: dict[str, Any],
    exc: BaseException,
    phase: str,
) -> None:
    rank = rank_env()["rank"]
    blocker = {
        "schema_version": 1,
        "task_id": TASK_ID,
        "status": "BLOCK",
        "route": ROUTE_ID,
        "phase": phase,
        "rank": rank,
        "error_type": type(exc).__name__,
        "error": str(exc),
        "traceback": traceback.format_exc(),
        "source_head": args.source_head,
        "checkpoint_iter_dir": str(args.checkpoint_iter_dir),
        "base_model_path": str(args.base_model_path),
        "prompt_yaml": str(args.prompt_yaml),
        "boundary_confirmations": command_manifest["boundary_confirmations"],
    }
    write_json(canary_dir / f"canary_blocker_rank{rank}.json", blocker)
    command_manifest["blocker_path"] = str(canary_dir / f"canary_blocker_rank{rank}.json")
    write_json(manifests_dir / f"command_env_manifest_rank{rank}.json", command_manifest)


def main() -> int:
    args = parse_args()
    env = rank_env()
    rank = env["rank"]
    local_rank = env["local_rank"]
    world_size = env["world_size"]
    start_time = time.time()
    output_root = args.output_root
    logs_dir = output_root / "logs"
    manifests_dir = output_root / "manifests"
    canary_dir = output_root / "canary"
    rank_logs_dir = logs_dir / "ranks"
    for path in (logs_dir, manifests_dir, canary_dir, rank_logs_dir):
        path.mkdir(parents=True, exist_ok=True)
    rank_log = rank_logs_dir / f"rank{rank:02d}_events.jsonl"

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
        "prompt_yaml": str(args.prompt_yaml),
        "parallelism": {
            "world_size": world_size,
            "expected_world_size_min": expected_world,
            "tensor_model_parallel_size": args.tensor_model_parallel_size,
            "pipeline_model_parallel_size": args.pipeline_model_parallel_size,
            "expert_model_parallel_size": args.expert_model_parallel_size,
            "expert_tensor_parallel_size": args.expert_tensor_parallel_size,
            "context_parallel_size": args.context_parallel_size,
        },
        "sampling": {
            "max_tokens": args.max_tokens,
            "temperature": args.temperature,
            "top_k": args.top_k,
            "top_p": args.top_p,
            "random_seed": args.random_seed,
        },
        "route_adjustments": [
            "distributed torchrun route uses task301 checkpoint parallelism TP=4 PP=2 EP=4 ETP=1",
            "load_megatron_model receives explicit mp_overrides matching task301 checkpoint parallelism",
            "checkpoint model_config.attention_backend None is set in-memory to AttnBackend.auto",
            "MCore SamplingParams uses top_k=1 greedy branch to avoid torch.multinomial invalid-probability blocker",
            "rank-local completion artifacts are retained because pipeline-parallel text may appear only on some ranks",
            "if MCore request.generated_text is empty, response_text falls back to checkpoint tokenizer detokenize(generated_tokens)",
        ],
        "boundary_confirmations": {
            "qwen3_30b_only": True,
            "no_training_or_optimizer_steps": True,
            "no_aime_task243_eval": True,
            "no_aime2025_train_prompts_or_labels": True,
            "no_task255_reuse": True,
            "no_export_or_conversion": True,
            "no_endpoint": True,
            "no_promotion": True,
            "no_shared_deletion": True,
            "no_main_push_or_merge": True,
        },
    }

    try:
        append_rank_event(rank_log, "start")
        if world_size < expected_world:
            raise RuntimeError(
                f"world_size={world_size} is below expected TP*PP*CP={expected_world}"
            )
        for path, label in (
            (args.checkpoint_iter_dir, "checkpoint iter dir"),
            (args.base_model_path, "base model path"),
        ):
            if not path.is_dir():
                raise FileNotFoundError(f"{label} not found: {path}")
        if not args.prompt_yaml.is_file():
            raise FileNotFoundError(f"prompt yaml not found: {args.prompt_yaml}")

        import datetime

        import torch
        import torch.distributed as dist

        command_manifest["torch"] = {
            "version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "cuda_device_count": torch.cuda.device_count(),
        }
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
        write_json(manifests_dir / f"command_env_manifest_rank{rank}.json", command_manifest)

        if not dist.is_initialized():
            dist.init_process_group(
                backend="nccl",
                init_method="env://",
                timeout=datetime.timedelta(minutes=args.rank_timeout_minutes),
            )
        append_rank_event(rank_log, "dist_initialized")

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
        from nemotron.recipes.super3.milestones.m1_eval_basket.qwen_aime2025_base_vs_ft_gate import (
            evaluate_v11_export_load_canary,
        )

        if not parallel_state.model_parallel_is_initialized():
            parallel_state.initialize_model_parallel(
                tensor_model_parallel_size=args.tensor_model_parallel_size,
                pipeline_model_parallel_size=args.pipeline_model_parallel_size,
                context_parallel_size=args.context_parallel_size,
                expert_model_parallel_size=args.expert_model_parallel_size,
                expert_tensor_parallel_size=args.expert_tensor_parallel_size,
            )
        try:
            from megatron.core.tensor_parallel import model_parallel_cuda_manual_seed

            model_parallel_cuda_manual_seed(args.random_seed)
            command_manifest["model_parallel_cuda_manual_seed"] = args.random_seed
        except Exception as seed_exc:  # noqa: BLE001
            command_manifest["model_parallel_cuda_manual_seed_error"] = repr(seed_exc)
        append_rank_event(rank_log, "model_parallel_initialized")

        prompt_set, prompts = load_prompt_set(args.prompt_yaml, args.base_model_path)
        prompt_file_hash = sha256_file(args.prompt_yaml)
        if is_rank0():
            prompt_manifest = {
                "schema_version": 1,
                "task_id": TASK_ID,
                "prompt_set_id": prompt_set["prompt_set_id"],
                "prompt_yaml": str(args.prompt_yaml),
                "prompt_yaml_sha256": prompt_file_hash,
                "non_aime_non_train_confirmation": prompt_set[
                    "non_aime_non_train_confirmation"
                ],
                "generation_contract": prompt_set["generation_contract"],
                "route_sampling_override": {
                    "reason": "no-export distributed MCore route; top_k=1 greedy branch",
                    "temperature": args.temperature,
                    "top_k": args.top_k,
                    "top_p": args.top_p,
                    "max_tokens": args.max_tokens,
                },
                "prompts": prompts,
            }
            write_json(manifests_dir / "canary_prompt_manifest.json", prompt_manifest)
        append_rank_event(rank_log, "prompts_loaded", prompt_count=len(prompts))

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
        append_rank_event(rank_log, "load_megatron_model_start", mp_overrides=mp_overrides)
        model = load_megatron_model(
            str(args.checkpoint_iter_dir),
            mp_overrides=mp_overrides,
            skip_temp_dist_context=True,
        )
        model_obj = model[0] if isinstance(model, list) else model
        model_obj.eval()
        append_rank_event(rank_log, "checkpoint_model_loaded")

        unwrapped = unwrap_model(model_obj)
        unwrapped_model = unwrapped[0] if isinstance(unwrapped, list) else unwrapped
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
            raise RuntimeError("could not resolve padded vocab size")

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
        write_json(
            manifests_dir / f"checkpoint_load_manifest_rank{rank}.json",
            checkpoint_manifest,
        )

        max_prompt_tokens = 0
        for prompt in prompts:
            token_count = len(tokenizer.tokenize(prompt["formatted_prompt"]))
            prompt["megatron_prompt_token_count"] = token_count
            max_prompt_tokens = max(max_prompt_tokens, token_count)

        inference_max_seq_length = max(
            max_prompt_tokens + args.max_tokens + 8, args.max_tokens + 512
        )
        wrapper_config = InferenceWrapperConfig(
            hidden_size=int(getattr(model_config, "hidden_size")),
            params_dtype=getattr(model_config, "params_dtype"),
            inference_batch_times_seqlen_threshold=int(
                getattr(model_config, "inference_batch_times_seqlen_threshold", 512)
            ),
            padded_vocab_size=int(padded_vocab_size),
            inference_max_requests=len(prompts),
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
            max_batch_size=len(prompts),
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
        formatted_prompts = [prompt["formatted_prompt"] for prompt in prompts]
        append_rank_event(rank_log, "generation_start", prompt_count=len(prompts))
        requests = engine.generate(prompts=formatted_prompts, sampling_params=sampling_params)
        append_rank_event(rank_log, "generation_done", request_count=len(requests))

        result_rows: list[dict[str, Any]] = []
        full_rows: list[dict[str, Any]] = []
        for prompt, request in zip(prompts, requests):
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
            extracted = extract_final_answer(generated_text)
            exact_match = (
                extracted is not None
                and normalize_answer(extracted) == normalize_answer(prompt["expected_answer"])
            )
            flags = degeneration_flags(generated_text)
            status = "ok" if generated_text.strip() else "empty"
            result_row = {
                "schema_version": 1,
                "task_id": TASK_ID,
                "rank": rank,
                "prompt_set_id": prompt_set["prompt_set_id"],
                "prompt_id": prompt["id"],
                "status": status,
                "response_text": generated_text,
                "response_sha256": sha256_text(generated_text),
                "expected_answer": prompt["expected_answer"],
                "extracted_final_answer": extracted,
                "exact_expected_answer_match": exact_match,
                "final_answer_marker_count": count_final_markers(generated_text),
                "completion_tokens": completion_tokens,
                "usage": {
                    "completion_tokens": completion_tokens,
                    "prompt_tokens": prompt.get("megatron_prompt_token_count"),
                },
                "finish_reason": "mcore_static_engine_completed",
                "response_text_source": response_text_source,
                "route": ROUTE_ID,
                "degeneration_flags": flags,
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

        write_jsonl(canary_dir / f"canary_results_rank{rank}.jsonl", result_rows)
        write_jsonl(canary_dir / f"canary_full_completions_rank{rank}.jsonl", full_rows)
        rank_summary = {
            "schema_version": 1,
            "task_id": TASK_ID,
            "rank": rank,
            "route": ROUTE_ID,
            "prompts_requested": len(prompts),
            "completions_retained": sum(bool(row["response_text"].strip()) for row in result_rows),
            "non_empty_responses": sum(row["status"] == "ok" for row in result_rows),
            "exact_expected_answer_matches": sum(
                bool(row["exact_expected_answer_match"]) for row in result_rows
            ),
            "final_answer_marker_count": sum(
                int(row["final_answer_marker_count"]) for row in result_rows
            ),
            "empty_count": sum(row["status"] == "empty" for row in result_rows),
            "mixed_script_count": sum(
                bool(row["degeneration_flags"]["mixed_script_flag"]) for row in result_rows
            ),
            "degeneration_count": sum(
                bool(row["degeneration_flags"]["degeneration_flag"]) for row in result_rows
            ),
            "elapsed_seconds": round(time.time() - start_time, 3),
        }
        write_json(canary_dir / f"rank{rank}_summary.json", rank_summary)

        import torch.distributed as dist

        dist.barrier()
        if is_rank0():
            all_rank_summaries = []
            for summary_path in sorted(canary_dir.glob("rank*_summary.json")):
                all_rank_summaries.append(json.loads(summary_path.read_text(encoding="utf-8")))
            candidate_summaries = sorted(
                all_rank_summaries,
                key=lambda item: (
                    int(item.get("completions_retained", 0)),
                    int(item.get("exact_expected_answer_matches", 0)),
                ),
                reverse=True,
            )
            selected_rank = int(candidate_summaries[0]["rank"]) if candidate_summaries else 0
            selected_results_path = canary_dir / f"canary_results_rank{selected_rank}.jsonl"
            selected_full_path = canary_dir / f"canary_full_completions_rank{selected_rank}.jsonl"
            selected_results = [
                json.loads(line)
                for line in selected_results_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            selected_full = [
                json.loads(line)
                for line in selected_full_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            write_jsonl(canary_dir / "canary_results.jsonl", selected_results)
            write_jsonl(canary_dir / "canary_full_completions.jsonl", selected_full)
            canary_decision = evaluate_v11_export_load_canary(
                selected_results, prompt_set=prompt_set
            )
            write_json(canary_dir / "canary_decision.json", canary_decision.to_jsonable())
            summary = {
                "schema_version": 1,
                "task_id": TASK_ID,
                "disposition": "PASS"
                if canary_decision.passed
                else "REQUEST_CHANGES_CANARY_COMPLETIONS_RETAINED_BUT_DECISION_FAIL",
                "route": ROUTE_ID,
                "source_head": args.source_head,
                "output_root": str(output_root),
                "checkpoint_iter_dir": str(args.checkpoint_iter_dir),
                "base_model_path": str(args.base_model_path),
                "prompt_yaml": str(args.prompt_yaml),
                "prompt_yaml_sha256": prompt_file_hash,
                "selected_rank": selected_rank,
                "rank_summaries": all_rank_summaries,
                "prompts_requested": len(prompts),
                "completions_retained": sum(
                    bool(row["response_text"].strip()) for row in selected_results
                ),
                "non_empty_responses": sum(row["status"] == "ok" for row in selected_results),
                "exact_expected_answer_matches": sum(
                    bool(row["exact_expected_answer_match"]) for row in selected_results
                ),
                "final_answer_marker_count": sum(
                    int(row["final_answer_marker_count"]) for row in selected_results
                ),
                "empty_count": sum(row["status"] == "empty" for row in selected_results),
                "mixed_script_count": sum(
                    bool(row["degeneration_flags"]["mixed_script_flag"])
                    for row in selected_results
                ),
                "degeneration_count": sum(
                    bool(row["degeneration_flags"]["degeneration_flag"])
                    for row in selected_results
                ),
                "canary_pass": canary_decision.passed,
                "canary_decision": canary_decision.to_jsonable(),
                "sampling": command_manifest["sampling"],
                "parallelism": command_manifest["parallelism"],
                "route_adjustments": command_manifest["route_adjustments"],
                "elapsed_seconds": round(time.time() - start_time, 3),
                "boundary_confirmations": command_manifest["boundary_confirmations"],
                "artifact_paths": {
                    "prompt_manifest": str(manifests_dir / "canary_prompt_manifest.json"),
                    "checkpoint_load_manifests_glob": str(
                        manifests_dir / "checkpoint_load_manifest_rank*.json"
                    ),
                    "canary_results": str(canary_dir / "canary_results.jsonl"),
                    "canary_full_completions": str(
                        canary_dir / "canary_full_completions.jsonl"
                    ),
                    "canary_decision": str(canary_dir / "canary_decision.json"),
                    "canary_summary": str(canary_dir / "canary_summary.json"),
                },
            }
            write_json(canary_dir / "canary_summary.json", summary)
            write_json(
                manifests_dir / "checksum_manifest.json",
                {
                    "schema_version": 1,
                    "task_id": TASK_ID,
                    "output_root": str(output_root),
                    "files": file_inventory(output_root),
                },
            )
            print(f"TASK304_DISPOSITION={summary['disposition']}")
            print(f"TASK304_CANARY_PASS={canary_decision.passed}")
            print(f"TASK304_OUTPUT_ROOT={output_root}")
        dist.barrier()
        return 0
    except Exception as exc:  # noqa: BLE001
        phase = "runtime"
        try:
            write_blocker(args, canary_dir, manifests_dir, command_manifest, exc, phase)
            write_json(
                manifests_dir / "checksum_manifest.json",
                {
                    "schema_version": 1,
                    "task_id": TASK_ID,
                    "output_root": str(output_root),
                    "files": file_inventory(output_root),
                },
            )
        except Exception:
            pass
        print("TASK304_DISPOSITION=BLOCK", flush=True)
        print(f"TASK304_BLOCKER={canary_dir / f'canary_blocker_rank{rank}.json'}", flush=True)
        print(f"TASK304_ERROR_TYPE={type(exc).__name__}", flush=True)
        print(f"TASK304_ERROR={exc}", flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
