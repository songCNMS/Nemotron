#!/usr/bin/env python3
"""Task291 no-export/no-endpoint Qwen canary route probe.

This script is intended to run on the NemTron host after the repo has been
synced to a task-owned /root path. It loads the task285 Megatron checkpoint
directly, runs MCore in-process generation on the synthetic non-AIME canary
prompts, and writes retained completion artifacts or a precise blocker.
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


TASK_ID = "task291_qwen_aime_v11_no_export_canary_route_unblock_s1"
ROUTE_ID = "direct_in_process_mcore_static_engine_no_export_no_endpoint_topk1_greedy"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


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


FINAL_ANSWER_RE = re.compile(
    r"(?:Final\s+Answer\s*:\s*(?:\\boxed\{([^}]*)\}|([^\n]+)))|(?:\\boxed\{([^}]*)\})",
    re.IGNORECASE,
)


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--checkpoint-iter-dir", required=True)
    parser.add_argument("--base-model-path", required=True)
    parser.add_argument("--prompt-yaml", required=True)
    parser.add_argument("--source-head", required=True)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--top-k", type=int, default=1)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top-p", type=float, default=0.0)
    parser.add_argument("--random-seed", type=int, default=1234)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_root = Path(args.output_root)
    logs_dir = output_root / "logs"
    manifests_dir = output_root / "manifests"
    canary_dir = output_root / "canary"
    output_root.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    manifests_dir.mkdir(parents=True, exist_ok=True)
    canary_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_iter_dir = Path(args.checkpoint_iter_dir)
    base_model_path = Path(args.base_model_path)
    prompt_yaml = Path(args.prompt_yaml)
    start_time = time.time()

    command_manifest_path = manifests_dir / "command_env_manifest.json"
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
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "pythonpath": os.environ.get("PYTHONPATH"),
        "checkpoint_iter_dir": str(checkpoint_iter_dir),
        "base_model_path": str(base_model_path),
        "prompt_yaml": str(prompt_yaml),
        "sampling": {
            "max_tokens": args.max_tokens,
            "temperature": args.temperature,
            "top_k": args.top_k,
            "top_p": args.top_p,
            "random_seed": args.random_seed,
        },
        "route_adjustments": [
            "checkpoint model_config.attention_backend None is set in-memory to AttnBackend.auto",
            "MCore SamplingParams uses top_k=1 greedy branch to avoid torch.multinomial invalid-probability blocker",
        ],
        "boundary_confirmations": {
            "qwen3_4b_only": True,
            "one_gpu_max": os.environ.get("CUDA_VISIBLE_DEVICES") in {"0", "0,"},
            "no_training_or_optimizer_steps": True,
            "no_aime_task243_eval": True,
            "no_aime2025_train_prompts_or_labels": True,
            "no_task255_reuse": True,
            "no_export_or_conversion": True,
            "no_endpoint": True,
            "no_promotion": True,
            "no_shared_deletion": True,
            "no_30b": True,
            "no_8gpu": True,
        },
    }

    try:
        import torch

        command_manifest["torch"] = {
            "version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "cuda_device_count": torch.cuda.device_count(),
            "cuda_device_name_0": torch.cuda.get_device_name(0)
            if torch.cuda.is_available() and torch.cuda.device_count() > 0
            else None,
        }
        if os.environ.get("CUDA_VISIBLE_DEVICES") not in {"0", "0,"}:
            raise RuntimeError(
                f"task291 requires one visible GPU, got CUDA_VISIBLE_DEVICES={os.environ.get('CUDA_VISIBLE_DEVICES')!r}"
            )
        if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
            raise RuntimeError(
                f"task291 requires exactly one visible CUDA device, got available={torch.cuda.is_available()} count={torch.cuda.device_count()}"
            )
        if not checkpoint_iter_dir.is_dir():
            raise FileNotFoundError(f"checkpoint iter dir not found: {checkpoint_iter_dir}")
        if not base_model_path.is_dir():
            raise FileNotFoundError(f"base model path not found: {base_model_path}")
        if not prompt_yaml.is_file():
            raise FileNotFoundError(f"prompt yaml not found: {prompt_yaml}")
        write_json(command_manifest_path, jsonable(command_manifest))

        from transformers import AutoTokenizer

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
        from nemotron.recipes.super3.milestones.m1_eval_basket.qwen_aime2025_base_vs_ft_gate import (
            evaluate_v11_export_load_canary,
            load_v11_canary_prompt_set,
        )

        prompt_set = load_v11_canary_prompt_set(prompt_yaml)
        prompt_file_hash = sha256_file(prompt_yaml)
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
                    "prompt_sha256": hashlib.sha256(prompt_text.encode("utf-8")).hexdigest(),
                    "formatted_prompt": formatted_prompt,
                    "formatted_prompt_sha256": hashlib.sha256(
                        formatted_prompt.encode("utf-8")
                    ).hexdigest(),
                    "formatted_prompt_chars": len(formatted_prompt),
                    "hf_chat_template_used": True,
                }
            )
        prompt_manifest = {
            "schema_version": 1,
            "task_id": TASK_ID,
            "prompt_set_id": prompt_set["prompt_set_id"],
            "prompt_yaml": str(prompt_yaml),
            "prompt_yaml_sha256": prompt_file_hash,
            "non_aime_non_train_confirmation": prompt_set["non_aime_non_train_confirmation"],
            "generation_contract": prompt_set["generation_contract"],
            "route_sampling_override": {
                "reason": "no-export MCore local route repair; top_k=1 uses documented greedy branch",
                "temperature": args.temperature,
                "top_k": args.top_k,
                "top_p": args.top_p,
                "max_tokens": args.max_tokens,
            },
            "prompts": prompts,
        }
        prompt_manifest_path = manifests_dir / "canary_prompt_manifest.json"
        write_json(prompt_manifest_path, prompt_manifest)

        distributed_manifest: dict[str, Any] = {
            "dist_was_initialized_before_probe": dist.is_initialized(),
            "model_parallel_was_initialized_before_probe": parallel_state.model_parallel_is_initialized(),
            "backend": "nccl",
            "world_size": 1,
            "rank": 0,
            "tensor_model_parallel_size": 1,
            "pipeline_model_parallel_size": 1,
        }
        if not dist.is_initialized():
            torch.cuda.set_device(0)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", 0))
                _, port = s.getsockname()
            init_method = f"tcp://127.0.0.1:{port}"
            dist.init_process_group(
                backend="nccl",
                init_method=init_method,
                world_size=1,
                rank=0,
            )
            distributed_manifest["process_group_initialized_by_script"] = True
            distributed_manifest["init_method"] = init_method
        else:
            distributed_manifest["process_group_initialized_by_script"] = False
        if not parallel_state.model_parallel_is_initialized():
            parallel_state.initialize_model_parallel(
                tensor_model_parallel_size=1,
                pipeline_model_parallel_size=1,
                context_parallel_size=1,
                expert_model_parallel_size=1,
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
        write_json(command_manifest_path, jsonable(command_manifest))

        cfg, mlm_args = load_model_config(str(checkpoint_iter_dir))
        tokenizer = load_tokenizer(str(checkpoint_iter_dir))
        model = load_megatron_model(str(checkpoint_iter_dir), skip_temp_dist_context=True)
        model_obj = model[0] if isinstance(model, list) else model
        model_obj.eval()
        unwrapped_model = unwrap_model(model_obj)[0] if isinstance(unwrap_model(model_obj), list) else unwrap_model(model_obj)
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

        checkpoint_manifest = {
            "schema_version": 1,
            "task_id": TASK_ID,
            "checkpoint_iter_dir": str(checkpoint_iter_dir),
            "base_model_path": str(base_model_path),
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
            "params_dtype": str(getattr(model_config, "params_dtype", None)),
            "padded_vocab_size": padded_vocab_size,
            "raw_tokenizer_vocab_size": getattr(tokenizer, "vocab_size", None),
            "tokenizer_type": f"{type(tokenizer).__module__}.{type(tokenizer).__qualname__}",
            "tokenizer_vocab_size": getattr(tokenizer, "vocab_size", None),
            "tokenizer_eod": getattr(tokenizer, "eod", None),
            "tokenizer_bos": getattr(tokenizer, "bos", None),
        }
        checkpoint_manifest_path = manifests_dir / "checkpoint_load_manifest.json"
        write_json(checkpoint_manifest_path, jsonable(checkpoint_manifest))

        max_prompt_tokens = 0
        for prompt in prompts:
            token_count = len(tokenizer.tokenize(prompt["formatted_prompt"]))
            prompt["megatron_prompt_token_count"] = token_count
            max_prompt_tokens = max(max_prompt_tokens, token_count)
        write_json(prompt_manifest_path, prompt_manifest)

        inference_max_seq_length = max(max_prompt_tokens + args.max_tokens + 8, args.max_tokens + 512)
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
        controller = TextGenerationController(inference_wrapper, tokenizer)
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
        requests = engine.generate(prompts=formatted_prompts, sampling_params=sampling_params)

        result_rows: list[dict[str, Any]] = []
        full_rows: list[dict[str, Any]] = []
        marker_count = 0
        exact_matches = 0
        retained_count = 0
        for prompt, request in zip(prompts, requests):
            generated_text = request.generated_text or ""
            generated_tokens = (
                request.generated_tokens.detach().cpu().tolist()
                if request.generated_tokens is not None
                else []
            )
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
            marker_count += count_final_markers(generated_text)
            exact_matches += int(exact_match)
            retained_count += int(bool(generated_text.strip()))
            status = "ok" if generated_text.strip() else "empty"
            result_row = {
                "schema_version": 1,
                "task_id": TASK_ID,
                "prompt_set_id": prompt_set["prompt_set_id"],
                "prompt_id": prompt["id"],
                "status": status,
                "response_text": generated_text,
                "expected_answer": prompt["expected_answer"],
                "extracted_final_answer": extracted,
                "exact_expected_answer_match": exact_match,
                "completion_tokens": completion_tokens,
                "usage": {
                    "completion_tokens": completion_tokens,
                    "prompt_tokens": prompt.get("megatron_prompt_token_count"),
                },
                "finish_reason": "mcore_static_engine_completed",
                "route": ROUTE_ID,
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

        results_path = canary_dir / "canary_results.jsonl"
        full_path = canary_dir / "canary_full_completions.jsonl"
        append_jsonl(results_path, result_rows)
        append_jsonl(full_path, full_rows)
        canary_decision = evaluate_v11_export_load_canary(result_rows, prompt_set=prompt_set)
        canary_decision_path = canary_dir / "canary_decision.json"
        write_json(canary_decision_path, canary_decision.to_jsonable())

        summary = {
            "schema_version": 1,
            "task_id": TASK_ID,
            "disposition": "PASS" if canary_decision.passed else "REQUEST_CHANGES_CANARY_COMPLETIONS_RETAINED_BUT_DECISION_FAIL",
            "route": ROUTE_ID,
            "source_head": args.source_head,
            "output_root": str(output_root),
            "checkpoint_iter_dir": str(checkpoint_iter_dir),
            "base_model_path": str(base_model_path),
            "prompt_yaml": str(prompt_yaml),
            "prompt_yaml_sha256": prompt_file_hash,
            "prompts_requested": len(prompts),
            "completions_retained": retained_count,
            "exact_expected_answer_matches": exact_matches,
            "final_answer_marker_count": marker_count,
            "canary_pass": canary_decision.passed,
            "canary_decision": canary_decision.to_jsonable(),
            "sampling": {
                "max_tokens": args.max_tokens,
                "temperature": args.temperature,
                "top_k": args.top_k,
                "top_p": args.top_p,
                "random_seed": args.random_seed,
            },
            "route_adjustments": command_manifest["route_adjustments"],
            "elapsed_seconds": round(time.time() - start_time, 3),
            "boundary_confirmations": command_manifest["boundary_confirmations"],
            "artifact_paths": {
                "command_env_manifest": str(command_manifest_path),
                "prompt_manifest": str(prompt_manifest_path),
                "checkpoint_load_manifest": str(checkpoint_manifest_path),
                "canary_results": str(results_path),
                "canary_full_completions": str(full_path),
                "canary_decision": str(canary_decision_path),
                "canary_summary": str(canary_dir / "canary_summary.json"),
            },
        }
        summary_path = canary_dir / "canary_summary.json"
        write_json(summary_path, summary)

        inventory = file_inventory(output_root)
        checksum_manifest_path = manifests_dir / "checksum_manifest.json"
        write_json(
            checksum_manifest_path,
            {
                "schema_version": 1,
                "task_id": TASK_ID,
                "output_root": str(output_root),
                "files": inventory,
            },
        )
        print(f"TASK291_DISPOSITION={summary['disposition']}")
        print(f"TASK291_CANARY_PASS={canary_decision.passed}")
        print(f"TASK291_OUTPUT_ROOT={output_root}")
        return 0 if canary_decision.passed else 3
    except Exception as exc:  # noqa: BLE001
        blocker = {
            "schema_version": 1,
            "task_id": TASK_ID,
            "status": "BLOCK",
            "route": ROUTE_ID,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "source_head": args.source_head,
            "checkpoint_iter_dir": str(checkpoint_iter_dir),
            "base_model_path": str(base_model_path),
            "prompt_yaml": str(prompt_yaml),
            "elapsed_seconds": round(time.time() - start_time, 3),
            "boundary_confirmations": command_manifest["boundary_confirmations"],
        }
        blocker_path = canary_dir / "canary_blocker.json"
        write_json(blocker_path, jsonable(blocker))
        command_manifest["blocker_path"] = str(blocker_path)
        write_json(command_manifest_path, jsonable(command_manifest))
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
        print(f"TASK291_DISPOSITION=BLOCK")
        print(f"TASK291_BLOCKER={blocker_path}")
        print(f"TASK291_ERROR_TYPE={type(exc).__name__}")
        print(f"TASK291_ERROR={exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
