"""Static guards for Super3 M1 Agentic SFT path examples."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCOPED_DOC_FILES = (
    REPO_ROOT / "src/nemotron/recipes/super3/stage1_sft/config/data_prep/agentic_v0.yaml",
    REPO_ROOT / "src/nemotron/recipes/super3/stage1_sft/README.md",
    REPO_ROOT / "src/nemotron/recipes/super3/milestones/m1_agentic_sft/README.md",
)


def test_m1_agentic_docs_do_not_use_named_user_examples() -> None:
    offenders = []
    for path in SCOPED_DOC_FILES:
        text = path.read_text(encoding="utf-8")
        if "/mnt/3fs/data/lei.song/nemotron" in text:
            offenders.append(path.relative_to(REPO_ROOT).as_posix())

    assert offenders == []


def test_m1_agentic_docs_use_nemo_run_dir_examples() -> None:
    for path in SCOPED_DOC_FILES:
        text = path.read_text(encoding="utf-8")

        assert "${NEMO_RUN_DIR:-.}/output/super3" in text
