#!/usr/bin/env python3

"""Local-path Qwen3 4B SFT entry for M1 Agentic SFT debug runs."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

# torch / megatron / nemotron.kit are only needed at runtime when the recipe
# is built; deferring their imports lets unit tests poke at `resolve_qwen_hf_model`
# without pulling the whole training stack into the test environment.
from omegaconf import DictConfig, OmegaConf

logger: logging.Logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path(__file__).parent / "config" / "m1_agentic_train.yaml"
QWEN_MODEL_ENV_VAR = "SUPER3_M1_QWEN_HF_MODEL"


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


def _qwen_local_recipe_builder(config: DictConfig) -> "ConfigContainer":
    """Build a Qwen3 4B SFT config from a local HF model directory."""
    import torch
    from megatron.bridge import AutoBridge
    from megatron.bridge.recipes.common import _sft_common
    from megatron.bridge.training.config import ConfigContainer  # noqa: F401

    hf_model = resolve_qwen_hf_model()
    cfg = _sft_common()
    cfg.model = AutoBridge.from_hf_pretrained(hf_model, trust_remote_code=True).to_megatron_provider(
        load_weights=False
    )
    cfg.tokenizer.tokenizer_model = OmegaConf.select(config, "tokenizer.tokenizer_model", default=hf_model)

    seq_length = int(OmegaConf.select(config, "dataset.seq_length", default=4096))
    cfg.model.seq_length = seq_length
    cfg.model.tensor_model_parallel_size = 2
    cfg.model.pipeline_model_parallel_size = 1
    cfg.model.pipeline_model_parallel_layout = None
    cfg.model.pipeline_dtype = None
    cfg.model.virtual_pipeline_model_parallel_size = None
    cfg.model.context_parallel_size = 1
    cfg.model.sequence_parallel = False

    cfg.validation.eval_interval = int(OmegaConf.select(config, "validation.eval_interval", default=100))
    cfg.train.manual_gc = False
    cfg.train.manual_gc_interval = 0

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
