from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
VALOR32K_CONFIG = (
    REPO_ROOT / "src/nemotron/recipes/omni3/stage0_sft/config/valor32k.yaml"
)


def test_valor32k_config_comment_uses_operator_dataset_env_var() -> None:
    text = VALOR32K_CONFIG.read_text(encoding="utf-8")

    assert "/lustre/fs1/portfolios/coreai/" not in text
    assert "users/chcui" not in text
    assert "OMNI3_VALOR32K_ENERGON_PATH" in text

    config = yaml.safe_load(text)
    assert config["dataset"]["path"] == (
        "${oc.env:OMNI3_VALOR32K_ENERGON_PATH,/datasets/valor32k/energon}"
    )
