"""Static checks for Super3 Stage2 RL NeMo-Skills documentation link pins."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

RLVR_README = REPO_ROOT / "src/nemotron/recipes/super3/stage2_rl/stage1_rlvr/README.md"
NEMO_SKILLS_REVISION = "f53fb0b9d84a09411b0d13c21ea08a3ae9141d2a"
MUTABLE_NEMO_SKILLS_DOCKERFILE_LINK = (
    "https://github.com/NVIDIA-NeMo/Skills/blob/main/dockerfiles/Dockerfile.sandbox"
)
PINNED_NEMO_SKILLS_DOCKERFILE_LINK = (
    "https://github.com/NVIDIA-NeMo/Skills/blob/"
    f"{NEMO_SKILLS_REVISION}/dockerfiles/Dockerfile.sandbox"
)


def test_stage2_rlvr_nemo_skills_dockerfile_link_is_revision_pinned() -> None:
    text = RLVR_README.read_text(encoding="utf-8")

    assert MUTABLE_NEMO_SKILLS_DOCKERFILE_LINK not in text
    assert text.count(PINNED_NEMO_SKILLS_DOCKERFILE_LINK) == 1
    assert f"[NeMo-Skills Dockerfile]({PINNED_NEMO_SKILLS_DOCKERFILE_LINK})" in text


def test_stage2_rlvr_sandbox_context_is_preserved() -> None:
    text = RLVR_README.read_text(encoding="utf-8")

    assert "stage2_rl/stage1_rlvr/README.md" in RLVR_README.as_posix()
    for expected_context in (
        "# Stage 1: Multi-Environment RLVR",
        "## Prerequisites",
        "Sandbox container",
        "NeMo-Skills tools",
        "Lean4 proof verification",
        "run.env.sandbox.container=<sandbox-image>",
    ):
        assert expected_context in text
