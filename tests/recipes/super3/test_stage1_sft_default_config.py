"""Static guards for generic Super3 stage1 SFT data-prep defaults."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from nemotron.data_prep.core.chat_sft_shard_core import _matches_used_in_filter

yaml = pytest.importorskip("yaml")


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage1_sft/config/data_prep/default.yaml"
)
SUPER3_BLEND = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage1_sft/config/data_prep/data_blend_raw.json"
)


def test_super3_stage1_sft_default_uses_super3_blend() -> None:
    config = yaml.safe_load(DEFAULT_CONFIG.read_text(encoding="utf-8"))
    blend_path = config["blend_path"]

    assert "/super3/stage1_sft/config/data_prep/data_blend_raw.json" in blend_path
    assert "/nano3/" not in blend_path


def test_super3_stage1_sft_default_has_no_nano_used_in_filter() -> None:
    config = yaml.safe_load(DEFAULT_CONFIG.read_text(encoding="utf-8"))

    assert config["used_in_filter"] is None


def test_super3_stage1_sft_blend_has_datasets() -> None:
    blend = json.loads(SUPER3_BLEND.read_text(encoding="utf-8"))

    assert isinstance(blend.get("datasets"), list)
    assert blend["datasets"], "Super3 stage1 SFT blend must not be empty"


def test_used_in_filter_rejects_missing_used_in_when_configured() -> None:
    assert _matches_used_in_filter(None, "nano_v3") is False
    assert _matches_used_in_filter(["super3"], "nano_v3") is False
    assert _matches_used_in_filter(["nano_v3"], "nano_v3") is True
