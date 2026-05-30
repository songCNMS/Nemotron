"""Tests for the SFT forward_step dispatch registry (task013 Session 1).

Verifies ``step_dispatch._STEP_FUNCTIONS`` + ``_load_forward_step``. The
actual ``finetune(...)`` call needs CUDA + the nvcr Megatron-Bridge
container, so the cluster path stays out of these tests — we exercise
the dispatch surface only. ``step_dispatch`` is intentionally
dependency-light (just ``importlib``) so the tests don't have to stub
megatron-bridge / torch / omegaconf.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest
import yaml

from nemotron.recipes.super3.stage1_sft.step_dispatch import (
    _STEP_FUNCTIONS,
    _load_forward_step,
)


def test_registry_carries_gpt_step_and_sample_level() -> None:
    """Default + plan §5.1 entries are present. The plan §5.1 row points
    at the in-repo sample-level adapter, not an upstream symbol."""
    assert "gpt_step" in _STEP_FUNCTIONS
    assert "super3_packed_seq_compat_gpt_step" in _STEP_FUNCTIONS
    assert "super3_sample_level_step" in _STEP_FUNCTIONS
    assert _STEP_FUNCTIONS["super3_packed_seq_compat_gpt_step"].startswith(
        "nemotron.recipes.super3.stage1_sft.packed_compat_step"
    )
    assert _STEP_FUNCTIONS["super3_sample_level_step"].startswith(
        "nemotron.recipes.super3.stage1_sft.sample_level_step"
    )


def test_load_forward_step_by_module_attr_spec() -> None:
    """Operators can pass a fully-qualified ``module:attr`` (or
    ``module.attr``) spec — useful for custom step functions that
    aren't in the static registry."""
    stub = types.ModuleType("nemotron_test_step_module")
    stub.my_step = lambda data_iterator, model: ("o", "l")
    sys.modules["nemotron_test_step_module"] = stub
    try:
        resolved = _load_forward_step("nemotron_test_step_module:my_step")
        assert resolved is stub.my_step

        resolved_dotted = _load_forward_step("nemotron_test_step_module.my_step")
        assert resolved_dotted is stub.my_step
    finally:
        sys.modules.pop("nemotron_test_step_module", None)


def test_load_forward_step_unknown_name_raises_with_choices() -> None:
    """Unknown name surfaces the registry options in the error so
    operators see what they meant to type."""
    with pytest.raises(ValueError, match="Unknown step function"):
        _load_forward_step("does_not_exist")


def test_load_forward_step_routes_gpt_step_to_upstream() -> None:
    """``gpt_step`` short name resolves to megatron-bridge's
    forward_step. We stub the upstream module so the resolution can
    happen without the real package installed."""
    target = "megatron.bridge.training.gpt_step"
    pre_existing = target in sys.modules
    if not pre_existing:
        # Stub minimum surface area: the module must expose a
        # ``forward_step`` attribute that _import_attr can grab.
        for parent in ("megatron", "megatron.bridge", "megatron.bridge.training", target):
            sys.modules.setdefault(parent, types.ModuleType(parent))
        sys.modules[target].forward_step = lambda data_iterator, model: ("o", "l")
    try:
        resolved = _load_forward_step("gpt_step")
        assert resolved is sys.modules[target].forward_step
    finally:
        if not pre_existing:
            for parent in (
                "megatron.bridge.training.gpt_step",
                "megatron.bridge.training",
                "megatron.bridge",
                "megatron",
            ):
                sys.modules.pop(parent, None)


def test_load_forward_step_routes_sample_level_to_adapter() -> None:
    """``super3_sample_level_step`` resolves to our in-repo adapter,
    not the upstream gpt_step. Verifies plan §5.1 wiring."""
    torch = pytest.importorskip("torch")  # adapter imports torch
    del torch  # only need the import-skip side effect
    from nemotron.recipes.super3.stage1_sft import sample_level_step

    resolved = _load_forward_step("super3_sample_level_step")
    assert resolved is sample_level_step.forward_step


def test_load_forward_step_routes_packed_seq_compat_to_adapter() -> None:
    from nemotron.recipes.super3.stage1_sft import packed_compat_step

    resolved = _load_forward_step("super3_packed_seq_compat_gpt_step")
    assert resolved is packed_compat_step.forward_step


def test_tiny_sft_smoke_config_uses_packed_seq_compat_step() -> None:
    config = yaml.safe_load(
        Path("src/nemotron/recipes/super3/stage1_sft/config/test.yaml").read_text(
            encoding="utf-8"
        )
    )

    assert config["step_function"] == "super3_packed_seq_compat_gpt_step"
