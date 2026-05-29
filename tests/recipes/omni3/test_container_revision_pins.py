"""Static guards for Omni3 container upstream revision pins."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SFT_DOCKERFILE = REPO_ROOT / "src/nemotron/recipes/omni3/stage0_sft/Dockerfile"
RL_DOCKERFILE = REPO_ROOT / "src/nemotron/recipes/omni3/stage1_rl/Dockerfile"

LOWER_SHA_RE = re.compile(r"^[0-9a-f]{40}$")

EXPECTED_PINS = {
    "MEGATRON_BRIDGE_REF": "648756cb99eed872d9e577243495840b9395a6f7",
    "MEGATRON_LM_REF": "bdecae692af213add7d8434e129ae482465d9731",
    "NEMO_RL_REF": "98ba11c0a77e177a903cd3756570684437a08e8d",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_arg(text: str, name: str, expected: str) -> None:
    match = re.search(rf"^ARG {re.escape(name)}=(\S+)$", text, flags=re.MULTILINE)
    assert match, f"missing ARG {name}"
    assert match.group(1) == expected
    assert LOWER_SHA_RE.fullmatch(match.group(1))


def _assert_ref_guard(text: str, ref_arg: str) -> None:
    guard = f'test "$(git rev-parse HEAD)" = "${{{ref_arg}}}"'
    assert guard in text
    fail_fast_region = text[text.index(guard) : text.index(guard) + 320]
    assert "resolved to $(git rev-parse HEAD)" in fail_fast_region
    assert "exit 1" in fail_fast_region


def test_omni3_sft_dockerfile_pins_bridge_and_megatron_lm_heads() -> None:
    text = _read(SFT_DOCKERFILE)

    assert "ARG MEGATRON_BRIDGE_BRANCH=nemotron_3_omni" in text
    assert "ARG MEGATRON_LM_BRANCH=nemotron_3_omni" in text
    _assert_arg(text, "MEGATRON_BRIDGE_REF", EXPECTED_PINS["MEGATRON_BRIDGE_REF"])
    _assert_arg(text, "MEGATRON_LM_REF", EXPECTED_PINS["MEGATRON_LM_REF"])

    assert '--branch "${MEGATRON_BRIDGE_BRANCH}"' in text
    assert 'git fetch adlr "${MEGATRON_LM_BRANCH}"' in text
    assert 'git checkout "adlr/${MEGATRON_LM_BRANCH}"' in text
    _assert_ref_guard(text, "MEGATRON_BRIDGE_REF")
    _assert_ref_guard(text, "MEGATRON_LM_REF")


def test_omni3_rl_dockerfile_pins_nemo_rl_head() -> None:
    text = _read(RL_DOCKERFILE)

    assert "ARG NEMO_RL_BRANCH=nano-v3-omni" in text
    _assert_arg(text, "NEMO_RL_REF", EXPECTED_PINS["NEMO_RL_REF"])

    assert '--branch "${NEMO_RL_BRANCH}"' in text
    _assert_ref_guard(text, "NEMO_RL_REF")


def test_omni3_container_dockerfiles_do_not_clone_mutable_branches_directly() -> None:
    combined = "\n".join(_read(path) for path in (SFT_DOCKERFILE, RL_DOCKERFILE))

    assert "--branch nemotron_3_omni" not in combined
    assert "--branch nano-v3-omni" not in combined
    assert "--branch ${NEMO_RL_REF}" not in combined
