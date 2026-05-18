#!/usr/bin/env python3
# /// script
# [tool.runspec]
# schema = "1"
# docs = "https://raw.githubusercontent.com/NVIDIA-NeMo/Nemotron/main/docs/runspec/v1/spec.md"
# name = "super3/sft"
# image = "nvcr.io/nvidia/nemo:26.02.nemotron_3_super"
# setup = "NeMo and all training dependencies are pre-installed in the image."
#
# [tool.runspec.run]
# launch = "torchrun"
#
# [tool.runspec.config]
# dir = "./config"
# default = "default"
# format = "omegaconf"
#
# [tool.runspec.resources]
# nodes = 4
# gpus_per_node = 8
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

"""SFT (Supervised Fine-Tuning) script for Nemotron Super3.

Uses Megatron-Bridge's ConfigContainer for full training configuration.
Dynamically loads the recipe function specified in the YAML config.

CLI:
    nemotron super3 sft              # local execution
    nemotron super3 sft --run dgx    # submit to cluster

Execution logic: src/nemotron/cli/commands/super3/sft.py

Direct usage:
    python /path/to/train.py --config /path/to/sft.yaml
    python /path/to/train.py --config /path/to/sft.yaml train.train_iters=5000
"""

from __future__ import annotations

import json
import logging
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import torch
from megatron.bridge.data.datasets.packed_sequence import PackedSequenceSpecs
from megatron.bridge.training.config import ConfigContainer, FinetuningDatasetConfig
from megatron.bridge.training.finetune import finetune
from megatron.bridge.training.gpt_step import forward_step as _gpt_step_forward_step
from megatron.bridge.training.pretrain import pretrain

from nemotron.recipes.super3.stage1_sft.step_dispatch import (
    _STEP_FUNCTIONS,
    _import_attr,
    _load_forward_step,
)
from megatron.bridge.training.utils.omegaconf_utils import (
    apply_overrides,
    create_omegaconf_dict_config,
    parse_hydra_overrides,
)
from omegaconf import DictConfig, OmegaConf

from nemotron.kit.recipe_loader import extract_recipe_config, import_recipe_function
from nemo_runspec.artifacts import setup_artifact_tracking
from nemotron.kit.train_script import load_omegaconf_yaml, parse_config_and_overrides
from nemotron.kit.wandb_kit import (
    _get_manifest_tracker,
    _resolve_to_lustre_path,
    patch_checkpoint_logging_both,
    patch_manifest_checkpoint_logging,
    patch_wandb_checkpoint_logging,
    patch_wandb_http_handler_skip_digest_verification,
    patch_wandb_init_for_lineage,
    patch_wandb_local_file_handler_skip_digest_verification,
    patch_wandb_runid_for_seeded_random,
)

logger: logging.Logger = logging.getLogger(__name__)


# Default config path relative to this file
DEFAULT_CONFIG_PATH = Path(__file__).parent / "config" / "default.yaml"

DEFAULT_RECIPE_TARGET = "megatron.bridge.recipes.nemotronh.nemotron_3_super.nemotron_3_super_sft_config"


# Backwards-compatible export — call sites outside this module that
# already imported `forward_step` from here keep working unchanged.
forward_step = _gpt_step_forward_step


def convert_megatron_to_hf(
    megatron_checkpoint_path: str,
    hf_model_id: str,
    output_dir: str | None = None,
) -> str:
    """Convert a Megatron checkpoint to HuggingFace format using Megatron-Bridge.

    Finds the latest iter_XXXXXX checkpoint in the save directory and converts
    it to HuggingFace format. All ranks must call this function together since
    export_ckpt creates its own gloo distributed context internally.

    Args:
        megatron_checkpoint_path: Directory containing Megatron checkpoints (with iter_* subdirs).
        hf_model_id: HuggingFace model ID for the base architecture (e.g. the original
            pretrained model). Needed to reconstruct tokenizer and config.
        output_dir: Where to write the HF checkpoint. Defaults to ``{save_dir}-hf``.

    Returns:
        Path to the HF checkpoint directory.
    """
    megatron_path = Path(megatron_checkpoint_path)

    if megatron_path.is_dir():
        iter_dirs = [d for d in megatron_path.iterdir() if d.is_dir() and d.name.startswith("iter_")]
        if iter_dirs:
            iter_dirs.sort(key=lambda x: int(x.name.split("_")[1]))
            megatron_path = iter_dirs[-1]
            logger.info(f"Using checkpoint iteration: {megatron_path.name}")

    if output_dir is None:
        output_dir = str(Path(megatron_checkpoint_path).parent / f"{Path(megatron_checkpoint_path).name}-hf")
    output_path = Path(output_dir)

    if (output_path / "config.json").exists():
        logger.info(f"HF checkpoint already exists at {output_path}, skipping conversion")
        return str(output_path)

    logger.info(f"Converting Megatron checkpoint to HuggingFace format...")
    logger.info(f"  Source: {megatron_path}")
    logger.info(f"  HF model ID: {hf_model_id}")
    logger.info(f"  Output: {output_path}")

    from megatron.bridge import AutoBridge

    bridge = AutoBridge.from_hf_pretrained(hf_model_id, trust_remote_code=True)
    bridge.export_ckpt(
        megatron_path=str(megatron_path),
        hf_path=str(output_path),
    )

    logger.info(f"Conversion complete: {output_path}")
    return str(output_path)


def log_hf_checkpoint_artifact(
    hf_path: str,
    artifact_base_name: str = "super3-sft-model",
) -> None:
    """Log a converted HF checkpoint as a W&B artifact with ``-hf`` suffix.

    Creates a W&B reference artifact pointing to the HF checkpoint directory.
    The artifact is named ``{artifact_base_name}-hf`` with alias ``latest``.
    Only call this on rank 0.

    Args:
        hf_path: Local path to the HuggingFace checkpoint directory.
        artifact_base_name: Base name for the W&B artifact (``-hf`` is appended).
    """
    try:
        import wandb
    except ImportError:
        logger.warning("wandb not installed, skipping HF artifact logging")
        return

    if wandb.run is None:
        logger.info("No active wandb run, skipping HF artifact logging")
        return

    hf_path_resolved = str(Path(hf_path).resolve())
    absolute_path = _resolve_to_lustre_path(hf_path_resolved)
    artifact_name = f"{artifact_base_name}-hf"

    # Always write manifest if tracker is active
    tracker = _get_manifest_tracker()
    if tracker is not None:
        try:
            tracker.log_model_checkpoint(
                name=artifact_name,
                path=absolute_path,
                iteration=0,
            )
            logger.info(f"[ARTIFACT] HF manifest written: {artifact_name}")
        except Exception as e:
            logger.warning(f"[ARTIFACT] HF manifest failed: {e}")

    # Wandb on top (best-effort)
    if wandb.run is None:
        return

    try:
        metadata = {"absolute_path": absolute_path, "format": "huggingface"}
        artifact = wandb.Artifact(artifact_name, type="model", metadata=metadata)
        artifact.add_reference(f"file://{hf_path_resolved}", checksum=False)

        logged = wandb.run.log_artifact(artifact, aliases=["latest"])
        logged.wait()
        logger.info(f"[WANDB] HF checkpoint artifact committed: {artifact_name}:latest")
    except Exception as e:
        logger.error(f"[WANDB] Failed to log HF checkpoint artifact: {e}")


def _build_dataset_config(dataset_config: DictConfig, current_dataset: Any) -> FinetuningDatasetConfig:
    """Build a FinetuningDatasetConfig from YAML config.

    This creates a proper FinetuningDatasetConfig (not HFDatasetConfig) to avoid
    downloading HuggingFace datasets.

    Supports packed parquet specs (directory, glob, or file paths):
    - super3_packed_sft_dir: Single dir that auto-resolves to splits/train/ and splits/valid/
    - packed_sequence_specs.packed_train_data_path: Explicit path/glob for training data
    - packed_sequence_specs.packed_val_data_path: Explicit path/glob for validation data

    Args:
        dataset_config: The dataset section from YAML config (resolved)
        current_dataset: The current dataset config from the recipe (for defaults)

    Returns:
        A FinetuningDatasetConfig instance
    """

    def _bridge_packed_npy_path(path_value: str | None, split_name: str, pack_size: int) -> str | None:
        """Return a Megatron-Bridge readable packed .npy path.

        The Super3 data-prep CLI emits parquet shards with `input_ids`,
        `loss_mask`, and `seq_start_id` columns. Megatron-Bridge 0.3's
        `PackedSequenceSpecs` runtime accepts one `.npy` file containing the
        same list-of-dicts structure. Convert lazily at train startup so packed
        artifacts remain portable across Bridge builds.
        """
        if not path_value:
            return None

        path = Path(path_value)
        if path.suffix == ".npy":
            return str(path)

        if path.is_file() and path.suffix == ".parquet":
            parquet_files = [path]
            output_path = path.with_suffix(".npy")
        elif path.is_dir():
            npy_files = sorted(path.glob("*.npy"))
            if len(npy_files) == 1:
                return str(npy_files[0])
            parquet_files = sorted(path.glob("*.parquet"))
            output_path = path.parent / f"{path.name}_{pack_size}_{split_name}.npy"
        else:
            raise FileNotFoundError(f"Packed {split_name} data path does not exist: {path}")

        if not parquet_files:
            raise FileNotFoundError(f"No parquet files found for packed {split_name} data: {path}")

        newest_parquet_mtime = max(p.stat().st_mtime for p in parquet_files)
        if output_path.exists() and output_path.stat().st_mtime >= newest_parquet_mtime:
            return str(output_path)

        import numpy as np
        import pyarrow.parquet as pq

        rows: list[dict[str, list[int] | list[bool]]] = []
        for parquet_file in parquet_files:
            table = pq.read_table(parquet_file, columns=["input_ids", "loss_mask", "seq_start_id"])
            columns = table.to_pydict()
            for input_ids, loss_mask, seq_start_id in zip(
                columns["input_ids"],
                columns["loss_mask"],
                columns["seq_start_id"],
                strict=True,
            ):
                rows.append(
                    {
                        "input_ids": [int(x) for x in input_ids],
                        "loss_mask": [bool(x) for x in loss_mask],
                        "seq_start_id": [int(x) for x in seq_start_id],
                    }
                )

        if not rows:
            raise ValueError(f"Packed {split_name} parquet data produced zero rows: {path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(output_path, np.array(rows, dtype=object), allow_pickle=True)
        logger.info(
            "Converted packed %s parquet shards to Megatron-Bridge npy: %s (%d rows)",
            split_name,
            output_path,
            len(rows),
        )
        return str(output_path)

    def _bridge_packed_metadata_path(
        train_path_value: str | None,
        val_path_value: str | None,
        pack_size: int,
    ) -> str | None:
        """Create a metadata JSON file expected by current Bridge packed SFT."""
        packed_paths = [Path(p) for p in (train_path_value, val_path_value) if p]
        if not packed_paths:
            return None

        output_path = packed_paths[0].parent / f"packed_{pack_size}_metadata.json"
        newest_data_mtime = max(p.stat().st_mtime for p in packed_paths)
        if output_path.exists() and output_path.stat().st_mtime >= newest_data_mtime:
            return str(output_path)

        import numpy as np

        metadata = []
        for packed_path in packed_paths:
            rows = np.load(packed_path, allow_pickle=True)
            if len(rows) == 0:
                continue

            sample_counts = []
            packed_lengths = []
            max_sequence_length = 0
            for row in rows:
                input_ids = row["input_ids"]
                seq_start_id = list(row["seq_start_id"]) + [len(input_ids)]
                sample_counts.append(len(seq_start_id) - 1)
                packed_lengths.append(max(0, len(input_ids) - 1))
                for start, end in zip(seq_start_id[:-1], seq_start_id[1:], strict=True):
                    max_sequence_length = max(max_sequence_length, max(0, end - start - 1))

            metadata.append(
                {
                    "dataset_max_seqlen": max_sequence_length,
                    "max_samples_per_bin": max(sample_counts),
                    "packing_factor": round(sum(sample_counts) / len(sample_counts), 2),
                    "packing_efficiency": round(sum(packed_lengths) / len(packed_lengths) / pack_size * 100, 2),
                    "pack_size": pack_size,
                    "min_packed_seqlen": min(packed_lengths),
                }
            )

        output_path.write_text(json.dumps(metadata), encoding="utf-8")
        logger.info("Wrote Megatron-Bridge packed metadata: %s", output_path)
        return str(output_path)

    # Build PackedSequenceSpecs if provided
    packed_specs = None
    has_validation_data = True  # Track if we have validation data
    if "packed_sequence_specs" in dataset_config:
        specs_dict = dict(dataset_config["packed_sequence_specs"])
        packed_sequence_size = specs_dict.get("packed_sequence_size", -1)

        super3_dir = dataset_config.get("super3_packed_sft_dir")
        if super3_dir:
            if not specs_dict.get("packed_train_data_path"):
                train_dir = Path(f"{super3_dir}/train/")
                if train_dir.is_dir() and list(train_dir.glob("*.parquet")):
                    specs_dict["packed_train_data_path"] = str(train_dir)
                else:
                    raise FileNotFoundError(
                        f"No parquet files found in train split directory: {train_dir}. "
                        "Data prep may have failed or produced no training data."
                    )
            if not specs_dict.get("packed_val_data_path"):
                valid_dir = Path(f"{super3_dir}/valid/")
                if valid_dir.is_dir() and list(valid_dir.glob("*.parquet")):
                    specs_dict["packed_val_data_path"] = str(valid_dir)
                else:
                    logger.info(f"No validation data found in {valid_dir}, skipping validation split")
                    has_validation_data = False
            logger.info(f"Resolved super3_packed_sft_dir: train={specs_dict.get('packed_train_data_path')}, valid={specs_dict.get('packed_val_data_path')}")

        specs_dict["packed_train_data_path"] = _bridge_packed_npy_path(
            specs_dict.get("packed_train_data_path"),
            "train",
            int(packed_sequence_size),
        )
        specs_dict["packed_val_data_path"] = _bridge_packed_npy_path(
            specs_dict.get("packed_val_data_path"),
            "valid",
            int(packed_sequence_size),
        )
        if specs_dict.get("packed_metadata_path") is None:
            specs_dict["packed_metadata_path"] = _bridge_packed_metadata_path(
                specs_dict.get("packed_train_data_path"),
                specs_dict.get("packed_val_data_path"),
                int(packed_sequence_size),
            )

        packed_specs = PackedSequenceSpecs(
            packed_sequence_size=packed_sequence_size,
            packed_train_data_path=specs_dict.get("packed_train_data_path"),
            packed_val_data_path=specs_dict.get("packed_val_data_path"),
            packed_metadata_path=specs_dict.get("packed_metadata_path"),
        )

    return FinetuningDatasetConfig(
        dataset_root=dataset_config.get("dataset_root", getattr(current_dataset, "dataset_root", None)),
        seq_length=dataset_config.get("seq_length", getattr(current_dataset, "seq_length", 4096)),
        packed_sequence_specs=packed_specs,
        dataloader_type=dataset_config.get("dataloader_type", getattr(current_dataset, "dataloader_type", "batch")),
        do_validation=has_validation_data,
        do_test=False,
    )


RecipeBuilder = Callable[["DictConfig"], ConfigContainer]
"""Signature for a function that builds a ConfigContainer from a loaded config."""


def _default_recipe_builder(config: "DictConfig") -> ConfigContainer:
    """Build recipe from YAML ``recipe._target_`` (production path)."""
    recipe_target, recipe_kwargs = extract_recipe_config(
        config,
        default_target=DEFAULT_RECIPE_TARGET,
    )
    try:
        recipe_func = import_recipe_function(recipe_target)
    except Exception as e:
        logger.error(str(e))
        sys.exit(1)

    return recipe_func(**recipe_kwargs)


def run_finetune(
    config_path: Path,
    recipe_builder: RecipeBuilder,
    cli_overrides: list[str] | None = None,
    *,
    tags: list[str] | None = None,
) -> None:
    """Core SFT pipeline.

    Handles wandb patches, artifact resolution, lineage, config merging,
    dataset construction, finetuning, and optional HF checkpoint conversion.
    The *recipe_builder* callback is the only extension point.

    Args:
        config_path: Path to the YAML config file.
        recipe_builder: Callable that receives the loaded DictConfig and
            returns a fully-constructed ConfigContainer.
        cli_overrides: Optional Hydra-style command-line overrides.
    """
    config = load_omegaconf_yaml(config_path)

    # -------------------------------------------------------------------------
    # ARTIFACT TRACKING
    # -------------------------------------------------------------------------
    tracking = setup_artifact_tracking(config, artifacts_key="run")

    # Wandb bug workarounds (specific to this container version)
    if tracking.wandb:
        patch_wandb_http_handler_skip_digest_verification()
        patch_wandb_local_file_handler_skip_digest_verification()
        patch_wandb_runid_for_seeded_random()

    # Checkpoint logging patches
    if tracking.manifest and tracking.wandb:
        patch_checkpoint_logging_both()
    elif tracking.wandb:
        patch_wandb_checkpoint_logging()
    elif tracking.manifest:
        patch_manifest_checkpoint_logging()

    # Wandb lineage registration
    if tracking.wandb:
        patch_wandb_init_for_lineage(
            artifact_qualified_names=tracking.qualified_names,
            tags=["sft", *(tags or [])],
        )

    cfg: ConfigContainer = recipe_builder(config)

    merged_omega_conf, excluded_fields = create_omegaconf_dict_config(cfg)

    config_overrides = OmegaConf.to_container(config, resolve=False)
    config_overrides.pop("recipe", None)
    config_overrides.pop("run", None)
    config_overrides.pop("dataset", None)
    config_overrides.pop("convert_to_hf", None)

    if config_overrides:
        logger.debug(f"Merging config overrides: {list(config_overrides.keys())}")
        yaml_overrides_omega = OmegaConf.create(config_overrides)
        merged_omega_conf = OmegaConf.merge(merged_omega_conf, yaml_overrides_omega)
        logger.debug("Config overrides merged successfully.")

    if cli_overrides:
        logger.debug(f"Applying Hydra-style command-line overrides: {cli_overrides}")
        merged_omega_conf = parse_hydra_overrides(merged_omega_conf, cli_overrides)
        logger.debug("Hydra-style command-line overrides applied successfully.")

    final_overrides_as_dict = OmegaConf.to_container(merged_omega_conf, resolve=True)

    final_overrides_as_dict.pop("dataset", None)
    apply_overrides(cfg, final_overrides_as_dict, excluded_fields)

    if "dataset" in config:
        dataset_config = OmegaConf.to_container(config.dataset, resolve=True)
        dataset_config.pop("_target_", None)
        cfg.dataset = _build_dataset_config(dataset_config, cfg.dataset)
        logger.info(f"Built dataset config: {type(cfg.dataset).__name__}")

    logger.debug(f"checkpoint.pretrained_checkpoint = {cfg.checkpoint.pretrained_checkpoint}")
    logger.debug(f"dataset type = {type(cfg.dataset).__name__}")
    if hasattr(cfg.dataset, "packed_sequence_specs") and cfg.dataset.packed_sequence_specs:
        logger.debug(f"packed_sequence_specs.packed_train_data_path = {cfg.dataset.packed_sequence_specs.packed_train_data_path}")

    # task013: select forward_step via YAML `step_function:` key
    # (defaults to gpt_step → byte-for-byte identical to pre-task013).
    step_function_name = (
        OmegaConf.select(config, "step_function", default=None) or "gpt_step"
    )
    resolved_forward_step = _load_forward_step(step_function_name)
    logger.info(f"forward_step: {step_function_name} ({resolved_forward_step!r})")

    if (
        getattr(cfg.checkpoint, "finetune", True) is False
        and cfg.checkpoint.pretrained_checkpoint is None
        and cfg.checkpoint.load is None
    ):
        logger.info("checkpoint.finetune=false with no load checkpoint; running random-init smoke training loop")
        pretrain(config=cfg, forward_step_func=resolved_forward_step)
    else:
        finetune(config=cfg, forward_step_func=resolved_forward_step)

    # -------------------------------------------------------------------------
    # POST-TRAINING: Convert final checkpoint to HuggingFace format
    # -------------------------------------------------------------------------
    rank = torch.distributed.get_rank() if torch.distributed.is_initialized() else 0

    if torch.distributed.is_initialized():
        torch.distributed.destroy_process_group()

    convert_to_hf_cfg = OmegaConf.to_container(config.get("convert_to_hf", OmegaConf.create()), resolve=True) or {}
    if convert_to_hf_cfg.get("enabled", False):
        hf_model_id = convert_to_hf_cfg["hf_model_id"]
        hf_output_dir = convert_to_hf_cfg.get("output_dir", None)

        # All ranks participate: export_ckpt creates its own gloo context
        hf_path = convert_megatron_to_hf(
            megatron_checkpoint_path=cfg.checkpoint.save,
            hf_model_id=hf_model_id,
            output_dir=hf_output_dir,
        )

        # Only rank 0 publishes the W&B artifact
        if rank == 0:
            # Derive artifact name from the checkpoint save dir
            artifact_base_name = Path(cfg.checkpoint.save).name
            log_hf_checkpoint_artifact(hf_path, artifact_base_name=artifact_base_name)


def main() -> None:
    """Entry point for Nemotron Super3 supervised fine-tuning."""
    try:
        config_path, cli_overrides = parse_config_and_overrides(default_config=DEFAULT_CONFIG_PATH)
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)

    run_finetune(config_path, _default_recipe_builder, cli_overrides)


if __name__ == "__main__":
    main()
