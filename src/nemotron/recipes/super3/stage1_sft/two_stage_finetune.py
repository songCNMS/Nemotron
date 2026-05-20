# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Two-stage SFT finetune driver (task013 Session 2a).

Plan §5.1 calls for a two-stage SFT loss schedule:

  Stage A (token-level loss) → checkpoint → Stage B (sample-level loss
                                                     from Stage A checkpoint)

task013 Session 1 (PR #44) landed the math + dispatch layer:

- ``sample_level_loss.py`` — pure-torch helper computing per-sample
  mean → batch mean (no length-domination)
- ``sample_level_step.py`` — Megatron-Bridge ``forward_step`` adapter
- ``step_dispatch._STEP_FUNCTIONS`` — registry mapping short names
  (`gpt_step` / `super3_sample_level_step`) to module attrs

This module is the **driver** that runs the two-stage sequence: load
Stage A config → invoke ``run_finetune`` with ``step_function=gpt_step``
→ capture Stage A's saved checkpoint path → invoke ``run_finetune``
again with ``step_function=super3_sample_level_step`` and
``checkpoint.pretrained_checkpoint`` overridden to Stage A's output.

Sandbox-runnable when *finetune_fn* is injected. Production uses the
default ``run_finetune`` from ``train.py`` — that needs CUDA + nvcr
Megatron-Bridge container and stays Session 2b cluster territory.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# A finetune_fn matches ``train.run_finetune`` signature: takes a config
# path + recipe_builder + optional CLI overrides + tags. Returns None;
# its side effect is writing a checkpoint to the path declared in the
# config's ``checkpoint.save`` field.
FinetuneFn = Callable[..., None]


@dataclass(frozen=True)
class StageInvocation:
    """Captured arguments of one ``finetune_fn`` call.

    Drivers record this for telemetry / debugging; tests assert against
    these to verify the driver dispatched correctly.
    """

    stage: str  # "a" | "b"
    config_path: Path
    step_function: str
    cli_overrides: tuple[str, ...]
    expected_checkpoint_save: str | None


@dataclass(frozen=True)
class TwoStageResult:
    """Output of one two-stage finetune run.

    Carries the resolved checkpoint paths so downstream pipelines (eval,
    RLVR) can pick up the right artifact without re-reading config
    files. ``invocations`` records what was dispatched so tests + audit
    have a clean inspection point.
    """

    stage_a_checkpoint_save: str
    stage_b_checkpoint_save: str
    invocations: tuple[StageInvocation, StageInvocation]


def _read_yaml(config_path: Path) -> dict[str, Any]:
    """Load a YAML config to a plain dict without any framework deps.

    The driver inspects two fields: ``step_function`` (for sanity check)
    and ``checkpoint.save`` (to thread Stage A → Stage B). Both are
    plain scalars; full OmegaConf interpolation isn't needed at the
    driver layer — ``run_finetune`` does that downstream.
    """
    import yaml

    if not config_path.exists():
        raise FileNotFoundError(f"two-stage config not found: {config_path}")
    with config_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{config_path}: YAML root must be a mapping")
    return data


def _extract_checkpoint_save(config: dict[str, Any], config_path: Path) -> str:
    """Pull ``checkpoint.save`` out of a config dict.

    Stage A's saved checkpoint becomes Stage B's ``pretrained_checkpoint``;
    the driver needs to read it from the YAML without invoking the full
    recipe build (which loads CUDA-only Megatron modules).
    """
    checkpoint_block = config.get("checkpoint")
    if not isinstance(checkpoint_block, dict):
        raise ValueError(
            f"{config_path}: 'checkpoint' block missing or not a mapping"
        )
    save_path = checkpoint_block.get("save")
    if not isinstance(save_path, str) or not save_path.strip():
        raise ValueError(
            f"{config_path}: 'checkpoint.save' must be a non-empty string"
        )
    return save_path


def _extract_step_function(config: dict[str, Any], default: str) -> str:
    """Pull ``step_function`` from a config; fall back to *default*.

    Matches ``train.run_finetune``'s own resolution
    (``OmegaConf.select(config, "step_function", default=None) or "gpt_step"``).
    Used by the driver to sanity-check that Stage A is on ``gpt_step``
    and Stage B is on ``super3_sample_level_step`` before invoking, so a
    misconfigured YAML is caught early.
    """
    value = config.get("step_function")
    if value is None:
        return default
    return str(value)


def run_two_stage_finetune(
    stage_a_config_path: Path | str,
    stage_b_config_path: Path | str,
    *,
    finetune_fn: FinetuneFn | None = None,
    recipe_builder: Any = None,
    cli_overrides: Sequence[str] | None = None,
) -> TwoStageResult:
    """Run the Stage A → Stage B finetune sequence.

    *stage_a_config_path* / *stage_b_config_path* are paths to YAML
    files in ``stage1_sft/config/``; defaults ship as
    ``stage_a_default.yaml`` and ``stage_b_default.yaml``. The driver:

    1. Loads Stage A YAML, asserts ``step_function`` resolves to
       ``gpt_step`` (or absent, which defaults to gpt_step). Invokes
       *finetune_fn* with the path and the operator-supplied
       *cli_overrides*.
    2. Reads ``checkpoint.save`` from Stage A YAML → that's Stage A's
       output checkpoint.
    3. Loads Stage B YAML, asserts ``step_function`` is
       ``super3_sample_level_step``. Invokes *finetune_fn* a second
       time with Stage A's checkpoint threaded in as an additional
       ``checkpoint.pretrained_checkpoint=...`` Hydra-style CLI
       override.

    *finetune_fn* defaults to ``train.run_finetune`` at call time
    (lazy import — Megatron deps only load in cluster). Tests inject
    a fake recording the calls.

    *recipe_builder* defaults to ``train._default_recipe_builder``
    (lazy). Tests pass a no-op stand-in.
    """
    stage_a_path = Path(stage_a_config_path)
    stage_b_path = Path(stage_b_config_path)
    overrides: tuple[str, ...] = tuple(cli_overrides or ())

    stage_a_config = _read_yaml(stage_a_path)
    stage_a_step = _extract_step_function(stage_a_config, default="gpt_step")
    if stage_a_step != "gpt_step":
        raise ValueError(
            f"Stage A config {stage_a_path} must use step_function=gpt_step "
            f"(plan §5.1 calls for token-level loss in Stage A); got {stage_a_step!r}"
        )
    stage_a_checkpoint_save = _extract_checkpoint_save(stage_a_config, stage_a_path)

    stage_b_config = _read_yaml(stage_b_path)
    stage_b_step = _extract_step_function(stage_b_config, default="gpt_step")
    if stage_b_step != "super3_sample_level_step":
        raise ValueError(
            f"Stage B config {stage_b_path} must use "
            f"step_function=super3_sample_level_step (plan §5.1 calls for "
            f"sample-level loss in Stage B); got {stage_b_step!r}"
        )
    stage_b_checkpoint_save = _extract_checkpoint_save(stage_b_config, stage_b_path)

    if finetune_fn is None or recipe_builder is None:
        # Lazy import: avoids loading Megatron / torch when the driver
        # is imported in a sandbox / planning context.
        from nemotron.recipes.super3.stage1_sft.train import (  # type: ignore
            _default_recipe_builder,
            run_finetune,
        )
        finetune_fn = finetune_fn or run_finetune
        recipe_builder = recipe_builder or _default_recipe_builder

    # ---- Stage A ----
    invocation_a = StageInvocation(
        stage="a",
        config_path=stage_a_path,
        step_function=stage_a_step,
        cli_overrides=overrides,
        expected_checkpoint_save=stage_a_checkpoint_save,
    )
    finetune_fn(
        stage_a_path,
        recipe_builder,
        cli_overrides=list(overrides) or None,
        tags=["task013", "stage-a", "token-level"],
    )

    # ---- Stage B ----
    stage_b_overrides = (
        *overrides,
        f"checkpoint.pretrained_checkpoint={stage_a_checkpoint_save}",
    )
    invocation_b = StageInvocation(
        stage="b",
        config_path=stage_b_path,
        step_function=stage_b_step,
        cli_overrides=stage_b_overrides,
        expected_checkpoint_save=stage_b_checkpoint_save,
    )
    finetune_fn(
        stage_b_path,
        recipe_builder,
        cli_overrides=list(stage_b_overrides),
        tags=["task013", "stage-b", "sample-level"],
    )

    return TwoStageResult(
        stage_a_checkpoint_save=stage_a_checkpoint_save,
        stage_b_checkpoint_save=stage_b_checkpoint_save,
        invocations=(invocation_a, invocation_b),
    )


__all__ = [
    "FinetuneFn",
    "StageInvocation",
    "TwoStageResult",
    "run_two_stage_finetune",
]
