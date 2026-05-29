"""Static checks for Nano3/Super3 run-spec docs URL revision pins."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNSPEC_DOC_REVISION = "510b6eec33edece3d212a3187b16db3d1b4a8a15"
PINNED_RUNSPEC_DOC_URL = (
    "https://raw.githubusercontent.com/NVIDIA-NeMo/Nemotron/"
    f"{RUNSPEC_DOC_REVISION}/docs/runspec/v1/spec.md"
)
MUTABLE_RUNSPEC_DOC_URL = (
    "https://raw.githubusercontent.com/NVIDIA-NeMo/Nemotron/"
    "main/docs/runspec/v1/spec.md"
)
MUTABLE_RUNSPEC_DOC_FRAGMENT = "/Nemotron/main/docs/runspec/v1/spec.md"

RECIPE_ROOTS = (
    REPO_ROOT / "src/nemotron/recipes/nano3",
    REPO_ROOT / "src/nemotron/recipes/super3",
)
SPEC_DOC = REPO_ROOT / "docs/runspec/v1/spec.md"

EXPECTED_RECIPE_DOC_FILES = {
    "src/nemotron/recipes/nano3/stage0_pretrain/data_prep.py",
    "src/nemotron/recipes/nano3/stage0_pretrain/train.py",
    "src/nemotron/recipes/nano3/stage1_sft/data_prep.py",
    "src/nemotron/recipes/nano3/stage1_sft/train.py",
    "src/nemotron/recipes/nano3/stage2_rl/data_prep.py",
    "src/nemotron/recipes/nano3/stage2_rl/train.py",
    "src/nemotron/recipes/super3/stage0_pretrain/data_prep.py",
    "src/nemotron/recipes/super3/stage0_pretrain/train.py",
    "src/nemotron/recipes/super3/stage1_sft/data_prep.py",
    "src/nemotron/recipes/super3/stage1_sft/train.py",
    "src/nemotron/recipes/super3/stage2_rl/data_prep.py",
    "src/nemotron/recipes/super3/stage2_rl/stage1_rlvr/data_prep.py",
    "src/nemotron/recipes/super3/stage2_rl/stage1_rlvr/train.py",
    "src/nemotron/recipes/super3/stage2_rl/stage2_swe1/data_prep.py",
    "src/nemotron/recipes/super3/stage2_rl/stage2_swe1/train.py",
    "src/nemotron/recipes/super3/stage2_rl/stage2_swe2/data_prep.py",
    "src/nemotron/recipes/super3/stage2_rl/stage2_swe2/train.py",
    "src/nemotron/recipes/super3/stage2_rl/stage3_rlhf/data_prep.py",
    "src/nemotron/recipes/super3/stage2_rl/stage3_rlhf/train.py",
    "src/nemotron/recipes/super3/stage2_rl/train.py",
}

RUNSPEC_DOCS_RE = re.compile(r'^# docs = "([^"]+)"$', re.MULTILINE)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _recipe_python_files() -> list[Path]:
    files: list[Path] = []
    for root in RECIPE_ROOTS:
        files.extend(root.rglob("*.py"))
    return sorted(files)


def _recipe_files_with_runspec_docs_url() -> dict[str, list[str]]:
    files: dict[str, list[str]] = {}
    for path in _recipe_python_files():
        text = _read(path)
        urls = RUNSPEC_DOCS_RE.findall(text)
        if urls:
            files[_relative(path)] = urls
    return files


def test_nano3_super3_runspec_docs_urls_are_exact_revision_pins() -> None:
    recipe_docs_urls = _recipe_files_with_runspec_docs_url()

    assert set(recipe_docs_urls) == EXPECTED_RECIPE_DOC_FILES
    for rel_path, urls in recipe_docs_urls.items():
        path = REPO_ROOT / rel_path
        text = _read(path)
        assert urls == [PINNED_RUNSPEC_DOC_URL], rel_path
        assert "# /// script" in text, rel_path
        assert "# [tool.runspec]" in text, rel_path
        assert '# schema = "1"' in text, rel_path
        assert re.search(r'^# name = "[^"]+"$', text, re.MULTILINE), rel_path


def test_runspec_spec_doc_uses_exact_revision_pin_examples() -> None:
    text = _read(SPEC_DOC)

    assert text.count(PINNED_RUNSPEC_DOC_URL) == 2
    assert MUTABLE_RUNSPEC_DOC_URL not in text
    assert MUTABLE_RUNSPEC_DOC_FRAGMENT not in text
    assert "# /// script" in text
    assert '# schema = "1"' in text
    assert '# name = "nano3/pretrain"' in text


def test_scoped_files_do_not_reference_mutable_runspec_doc_url() -> None:
    scoped_files = [SPEC_DOC, *_recipe_python_files()]

    for path in scoped_files:
        text = _read(path)
        assert MUTABLE_RUNSPEC_DOC_URL not in text, _relative(path)
        assert MUTABLE_RUNSPEC_DOC_FRAGMENT not in text, _relative(path)
