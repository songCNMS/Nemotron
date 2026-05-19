#!/usr/bin/env python3
# /// script
# [tool.runspec]
# name = "super3/sft-test"
#
# [tool.runspec.run]
# launch = "torchrun"
#
# [tool.runspec.config]
# dir = "./config"
# default = "test"
#
# [tool.runspec.resources]
# nodes = 1
# gpus_per_node = 1
# ///

# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Integration-test SFT script for Nemotron Super3.

Uses the same tiny Super3-architecture model as the pretrain integration test
(~7M params, single GPU) with full-parameter SFT (no LoRA) and packed sequences.

Exercises all Super3-specific code paths:

- Hybrid Mamba + Attention layers  (pattern ``MEM*EME``)
- Mixture-of-Experts with latent routing  (``moe_latent_size``)
- Multi-Token Prediction  (``mtp_num_layers=2``)
- Shared expert  (``moe_shared_expert_intermediate_size``)
- Packed-sequence finetuning with custom dataset builder

The full training pipeline (wandb, artifact resolution, lineage, checkpointing,
HF conversion) is identical to the production ``train.py`` — only the model is
smaller.

Usage::

    torchrun --nproc_per_node=1 test_train.py
    torchrun --nproc_per_node=1 test_train.py --config config/test.yaml
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from megatron.bridge.recipes.utils.optimizer_utils import distributed_fused_adam_with_cosine_annealing
from megatron.bridge.training.config import (
    CheckpointConfig,
    ConfigContainer,
    FinetuningDatasetConfig,
    LoggerConfig,
    RNGConfig,
    TokenizerConfig,
    TrainingConfig,
)
from megatron.core.distributed import DistributedDataParallelConfig
from omegaconf import DictConfig, OmegaConf

from nemotron.kit.train_script import parse_config_and_overrides
from nemotron.recipes.super3.smoke_runtime import patch_dataset_helper_compile_if_prebuilt
from nemotron.recipes.super3.stage1_sft.train import run_finetune
from nemotron.recipes.super3.tiny_model import make_tiny_super3_model

logger: logging.Logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Recipe builder
# ---------------------------------------------------------------------------

def _tiny_recipe_builder(config: DictConfig) -> ConfigContainer:  # noqa: ARG001
    """Build a single-GPU Super3 SFT config with the tiny provider.

    Uses full-parameter SFT (no LoRA) with packed sequences, matching the
    production Super3 SFT recipe but at tiny scale.
    """
    seq_length = OmegaConf.select(config, "dataset.seq_length", default=4096)

    opt_cfg, scheduler_cfg = distributed_fused_adam_with_cosine_annealing(
        lr_warmup_iters=0,
        lr_decay_iters=1,
        max_lr=1e-5,
        min_lr=0.0,
    )
    opt_cfg.use_distributed_optimizer = False

    cfg = ConfigContainer(
        train=TrainingConfig(
            train_iters=1,
            eval_interval=1,
            eval_iters=1,
            global_batch_size=1,
            micro_batch_size=1,
        ),
        model=make_tiny_super3_model(seq_length=int(seq_length)),
        optimizer=opt_cfg,
        scheduler=scheduler_cfg,
        ddp=DistributedDataParallelConfig(
            check_for_nan_in_grad=True,
            use_distributed_optimizer=False,
        ),
        dataset=FinetuningDatasetConfig(
            seq_length=int(seq_length),
            dataloader_type="batch",
            do_validation=False,
            do_test=False,
        ),
        logger=LoggerConfig(log_interval=1, log_timers_to_tensorboard=True),
        tokenizer=TokenizerConfig(
            tokenizer_type="HuggingFaceTokenizer",
            tokenizer_model="nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16",
        ),
        checkpoint=CheckpointConfig(
            save_interval=1,
            save=None,
            load=None,
            ckpt_format="torch_dist",
            fully_parallel_save=True,
        ),
        rng=RNGConfig(seed=5678),
        mixed_precision="bf16_mixed",
    )

    # Disable TP comm overlap (meaningless at TP=1).
    cfg.comm_overlap = None

    return cfg


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

DEFAULT_CONFIG_PATH = Path(__file__).parent / "config" / "test.yaml"


def main() -> None:
    """Entry point for tiny Super3 integration-test SFT."""
    patch_dataset_helper_compile_if_prebuilt()

    try:
        config_path, cli_overrides = parse_config_and_overrides(
            default_config=DEFAULT_CONFIG_PATH,
        )
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)

    run_finetune(config_path, _tiny_recipe_builder, cli_overrides, tags=["test"])


if __name__ == "__main__":
    main()
