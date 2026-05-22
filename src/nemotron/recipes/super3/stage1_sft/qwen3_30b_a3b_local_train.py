#!/usr/bin/env python3

"""Local-path Qwen3 30B-A3B full-SFT entry for M1 Agentic SFT runs."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from omegaconf import DictConfig, OmegaConf

if TYPE_CHECKING:
    from megatron.bridge.training.config import ConfigContainer

logger: logging.Logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path(__file__).parent / "config" / "m1_agentic_train.yaml"
QWEN_MODEL_ENV_VAR = "SUPER3_M1_QWEN_HF_MODEL"


def resolve_qwen_hf_model() -> str:
    """Return the local Qwen3 30B-A3B HF directory from the operator env."""
    value = os.environ.get(QWEN_MODEL_ENV_VAR)
    if not value:
        raise ValueError(
            f"{QWEN_MODEL_ENV_VAR} is required; point it at a local "
            "Qwen3-30B-A3B-Instruct-2507 HF model directory."
        )
    return value


def _qwen30b_a3b_local_recipe_builder(config: DictConfig) -> ConfigContainer:
    """Build a full-SFT Qwen3 30B-A3B MoE config from a local HF model."""
    from megatron.bridge.recipes.qwen.qwen3_moe import _qwen3_moe_finetune_common
    from megatron.bridge.training.config import ConfigContainer  # noqa: F401

    hf_model = resolve_qwen_hf_model()
    seq_length = int(OmegaConf.select(config, "dataset.seq_length", default=4096))
    train_iters = int(OmegaConf.select(config, "train.train_iters", default=100))
    min_lr = OmegaConf.select(config, "optimizer.min_lr", default=None)
    if min_lr is None:
        min_lr = OmegaConf.select(config, "scheduler.min_lr", default=0.0)
    cfg = _qwen3_moe_finetune_common(
        hf_path=hf_model,
        pretrained_checkpoint=OmegaConf.select(config, "checkpoint.pretrained_checkpoint", default=None),
        packed_sequence=True,
        train_iters=train_iters,
        global_batch_size=int(OmegaConf.select(config, "train.global_batch_size", default=8)),
        micro_batch_size=int(OmegaConf.select(config, "train.micro_batch_size", default=1)),
        seq_length=seq_length,
        eval_interval=int(OmegaConf.select(config, "train.eval_interval", default=1000)),
        save_interval=int(OmegaConf.select(config, "checkpoint.save_interval", default=1000)),
        finetune_lr=float(OmegaConf.select(config, "optimizer.lr", default=5e-6)),
        min_lr=float(min_lr),
        lr_warmup_iters=int(OmegaConf.select(config, "scheduler.lr_warmup_iters", default=0)),
        lr_decay_iters=int(OmegaConf.select(config, "scheduler.lr_decay_iters", default=train_iters)),
    )

    cfg.tokenizer.tokenizer_model = OmegaConf.select(config, "tokenizer.tokenizer_model", default=hf_model)
    cfg.model.seq_length = seq_length
    cfg.model.tensor_model_parallel_size = 4
    cfg.model.pipeline_model_parallel_size = 2
    cfg.model.expert_model_parallel_size = 4
    cfg.model.expert_tensor_parallel_size = 1
    cfg.model.sequence_parallel = True
    cfg.peft = None

    return cfg


def main() -> None:
    """Entry point for local-path Qwen3 30B-A3B M1 Agentic SFT."""
    from nemotron.kit.train_script import parse_config_and_overrides
    from nemotron.recipes.super3.smoke_runtime import patch_dataset_helper_compile_if_prebuilt
    from nemotron.recipes.super3.stage1_sft.train import run_finetune

    patch_dataset_helper_compile_if_prebuilt()

    try:
        config_path, cli_overrides = parse_config_and_overrides(default_config=DEFAULT_CONFIG_PATH)
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)

    run_finetune(
        config_path,
        _qwen30b_a3b_local_recipe_builder,
        cli_overrides,
        tags=["m1", "agentic-sft", "qwen3-30b-a3b-local"],
    )


if __name__ == "__main__":
    main()
