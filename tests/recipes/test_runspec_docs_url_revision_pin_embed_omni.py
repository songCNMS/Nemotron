"""Static checks for Embed/Omni3 run-spec docs URL revision pins."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

OLD_DOCS_URL = (
    "https://raw.githubusercontent.com/NVIDIA-NeMo/Nemotron/main/docs/runspec/v1/spec.md"
)
PINNED_DOCS_URL = (
    "https://raw.githubusercontent.com/NVIDIA-NeMo/Nemotron/"
    "510b6eec33edece3d212a3187b16db3d1b4a8a15/docs/runspec/v1/spec.md"
)

SCOPED_ROOTS = (
    REPO_ROOT / "src/nemotron/recipes/embed",
    REPO_ROOT / "src/nemotron/recipes/omni3",
)

EXPECTED_RUNSPEC_FILES = {
    "src/nemotron/recipes/embed/stage0_sdg/data_prep.py",
    "src/nemotron/recipes/embed/stage1_data_prep/data_prep.py",
    "src/nemotron/recipes/embed/stage2_finetune/train.py",
    "src/nemotron/recipes/embed/stage3_eval/eval.py",
    "src/nemotron/recipes/embed/stage4_export/export.py",
    "src/nemotron/recipes/embed/stage5_deploy/deploy.py",
    "src/nemotron/recipes/omni3/stage0_sft/data_prep.py",
    "src/nemotron/recipes/omni3/stage0_sft/train.py",
    "src/nemotron/recipes/omni3/stage1_rl/data_prep.py",
    "src/nemotron/recipes/omni3/stage1_rl/stage1_mpo/train.py",
    "src/nemotron/recipes/omni3/stage1_rl/stage2_text_rl/train.py",
    "src/nemotron/recipes/omni3/stage1_rl/stage3_vision_rl/train.py",
}

DOCS_LINE_RE = re.compile(r'^# docs = "([^"]+)"$', re.MULTILINE)
SHA_RE = re.compile(r"/Nemotron/([0-9a-f]{40})/docs/runspec/v1/spec\.md$")


def _relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _scoped_runspec_files() -> list[Path]:
    files: list[Path] = []
    for root in SCOPED_ROOTS:
        for path in sorted(root.rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            if "# [tool.runspec]" in text:
                files.append(path)
    return files


def test_scoped_embed_omni_runspec_files_are_guarded() -> None:
    files = _scoped_runspec_files()
    assert {_relative(path) for path in files} == EXPECTED_RUNSPEC_FILES

    for path in files:
        text = path.read_text(encoding="utf-8")
        rel_path = _relative(path)

        assert "# /// script" in text, rel_path
        assert '# schema = "1"' in text, rel_path
        assert '# name = "' in text, rel_path
        assert "# [tool.runspec.run]" in text, rel_path
        assert OLD_DOCS_URL not in text, rel_path

        docs_urls = DOCS_LINE_RE.findall(text)
        assert docs_urls == [PINNED_DOCS_URL], rel_path
        assert SHA_RE.search(docs_urls[0]), rel_path
