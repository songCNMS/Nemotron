#!/usr/bin/env python3

"""Local-path Qwen3 4B SFT entry for M1 Agentic SFT debug runs."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

# torch / megatron / nemotron.kit are only needed at runtime when the recipe
# is built; deferring their imports lets unit tests poke at `resolve_qwen_hf_model`
# without pulling the whole training stack into the test environment.
from omegaconf import DictConfig, OmegaConf

if TYPE_CHECKING:
    from megatron.bridge.training.config import ConfigContainer

logger: logging.Logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path(__file__).parent / "config" / "m1_agentic_train.yaml"
QWEN_MODEL_ENV_VAR = "SUPER3_M1_QWEN_HF_MODEL"
NEMOTRON_SUPER_TOKENIZER_DEFAULT = "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16"


def resolve_qwen_hf_model() -> str:
    """Return the local Qwen3 4B HF dir, requiring an explicit operator hint.

    A hardcoded fallback used to point at one engineer's home (`/mnt/3fs/data/
    lei.song/...`); other interns running this debug entry without the env var
    set would hit a "directory not found" deep inside the HF auto-bridge stack.
    Force an explicit `SUPER3_M1_QWEN_HF_MODEL` so the failure mode is obvious.
    """
    value = os.environ.get(QWEN_MODEL_ENV_VAR)
    if not value:
        raise ValueError(
            f"{QWEN_MODEL_ENV_VAR} is required — point it at a local Qwen3 4B HF model directory "
            "(e.g. one produced by scripts/import_qwen3_4b_local_to_megatron.py)"
        )
    return value


def resolve_qwen_tokenizer_model(config: DictConfig, hf_model: str) -> str:
    """Resolve the training tokenizer without falling back to Nemotron defaults."""

    tokenizer_model = OmegaConf.select(config, "tokenizer.tokenizer_model", default=None)
    if not tokenizer_model or tokenizer_model == NEMOTRON_SUPER_TOKENIZER_DEFAULT:
        return hf_model
    return str(tokenizer_model)


def _qwen_local_recipe_builder(config: DictConfig) -> ConfigContainer:
    """Build a Qwen3 4B SFT config from a local HF model directory."""
    from nemotron.recipes.super3.stage1_sft.qwen_chat_contract import validate_qwen_packed_sft_chat_contract

    hf_model = resolve_qwen_hf_model()
    tokenizer_model = resolve_qwen_tokenizer_model(config, hf_model)
    packed_sft_dir = OmegaConf.select(config, "dataset.super3_packed_sft_dir", default=None)
    if packed_sft_dir:
        metadata_path = validate_qwen_packed_sft_chat_contract(
            str(packed_sft_dir),
            tokenizer_model=tokenizer_model,
        )
        logger.info("Validated Qwen SFT chat contract in %s", metadata_path)

    import torch
    from megatron.bridge.recipes.qwen.qwen3 import qwen3_4b_finetune_config
    from megatron.bridge.training.config import ConfigContainer  # noqa: F401

    seq_length = int(OmegaConf.select(config, "dataset.seq_length", default=4096))
    cfg = qwen3_4b_finetune_config(
        hf_path=hf_model,
        peft=None,
        packed_sequence=True,
        seq_length=seq_length,
        train_iters=int(OmegaConf.select(config, "train.train_iters", default=1000)),
        global_batch_size=int(OmegaConf.select(config, "train.global_batch_size", default=4)),
        micro_batch_size=int(OmegaConf.select(config, "train.micro_batch_size", default=1)),
        eval_interval=int(OmegaConf.select(config, "train.eval_interval", default=100)),
        save_interval=int(OmegaConf.select(config, "checkpoint.save_interval", default=100)),
    )
    cfg.tokenizer.tokenizer_model = tokenizer_model

    cfg.model.seq_length = seq_length
    cfg.model.tensor_model_parallel_size = 2
    cfg.model.pipeline_model_parallel_size = 1
    cfg.model.pipeline_model_parallel_layout = None
    cfg.model.pipeline_dtype = None
    cfg.model.virtual_pipeline_model_parallel_size = None
    cfg.model.context_parallel_size = 1
    cfg.model.sequence_parallel = False

    cfg.train.eval_interval = int(OmegaConf.select(config, "train.eval_interval", default=100))
    cfg.train.manual_gc = False
    cfg.train.manual_gc_interval = 0
    optimizer_lr = OmegaConf.select(config, "optimizer.lr", default=None)
    if optimizer_lr is not None:
        cfg.optimizer.lr = float(optimizer_lr)
    scheduler_min_lr = OmegaConf.select(config, "scheduler.min_lr", default=None)
    if scheduler_min_lr is not None:
        cfg.optimizer.min_lr = float(scheduler_min_lr)
    lr_warmup_iters = OmegaConf.select(config, "scheduler.lr_warmup_iters", default=None)
    if lr_warmup_iters is not None:
        cfg.scheduler.lr_warmup_iters = int(lr_warmup_iters)
    lr_decay_iters = OmegaConf.select(config, "scheduler.lr_decay_iters", default=None)
    if lr_decay_iters is not None:
        cfg.scheduler.lr_decay_iters = int(lr_decay_iters)

    cfg.model.transformer_impl = "transformer_engine"
    cfg.model.cuda_graph_impl = "none"
    cfg.model.cuda_graph_scope = "full"
    cfg.model.cuda_graph_warmup_steps = 3
    cfg.model.attention_backend = None
    cfg.model.cross_entropy_loss_fusion = True
    cfg.model.cross_entropy_fusion_impl = "native"
    cfg.model.recompute_granularity = None
    cfg.model.recompute_modules = None
    cfg.model.fine_grained_activation_offloading = False
    cfg.model.offload_modules = None

    cfg.optimizer.use_precision_aware_optimizer = False
    cfg.optimizer.main_grads_dtype = torch.float32
    cfg.optimizer.main_params_dtype = torch.float32
    cfg.optimizer.exp_avg_dtype = torch.float32
    cfg.optimizer.exp_avg_sq_dtype = torch.float32

    cfg.ddp.grad_reduce_in_fp32 = False
    cfg.ddp.overlap_grad_reduce = False
    cfg.ddp.overlap_param_gather = False
    cfg.ddp.check_for_nan_in_grad = True
    cfg.ddp.use_distributed_optimizer = False

    return cfg


def main() -> None:
    """Entry point for local-path Qwen3 4B M1 Agentic SFT."""
    from nemotron.kit.train_script import parse_config_and_overrides
    from nemotron.recipes.super3.smoke_runtime import patch_dataset_helper_compile_if_prebuilt
    from nemotron.recipes.super3.stage1_sft.train import run_finetune

    patch_dataset_helper_compile_if_prebuilt()

    try:
        config_path, cli_overrides = parse_config_and_overrides(default_config=DEFAULT_CONFIG_PATH)
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)

    run_finetune(config_path, _qwen_local_recipe_builder, cli_overrides, tags=["m1", "agentic-sft", "qwen-local"])


if __name__ == "__main__":
    main()
