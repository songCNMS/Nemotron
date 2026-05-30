from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = (
    REPO_ROOT
    / "usage-cookbook"
    / "Nemotron-3-Super/grpo-dapo/grpo_training_cookbook.ipynb"
)

NEMO_RL_REPO = "https://github.com/NVIDIA-NeMo/RL.git"
EXPECTED_REVISION = "bb0a7d43931950a74522e159f7117543a87b580b"
EXPECTED_BRANCH_GUIDE_URL = (
    "https://github.com/NVIDIA-NeMo/RL/blob/"
    f"{EXPECTED_REVISION}/docs/guides/nemotron-3-super.md"
)
EXPECTED_DOCKER_GUIDE_URL = (
    "https://github.com/NVIDIA-NeMo/RL/blob/"
    f"{EXPECTED_REVISION}/docs/docker.md"
)
MUTABLE_DOC_URL_PARTS = (
    "github.com/NVIDIA-NeMo/RL/blob/super-v3/docs/",
    "github.com/NVIDIA-NeMo/RL/blob/main/docs/",
)


def _notebook() -> dict[str, object]:
    data = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _cell_text(cell: dict[str, object], key: str) -> str:
    value = cell.get(key, [])
    if isinstance(value, list):
        return "".join(str(part) for part in value)
    return str(value)


def _notebook_source() -> str:
    notebook = _notebook()
    cells = notebook["cells"]
    assert isinstance(cells, list)
    return "\n".join(
        _cell_text(cell, "source") for cell in cells if isinstance(cell, dict)
    )


def _nemo_rl_setup_cells() -> list[dict[str, object]]:
    notebook = _notebook()
    cells = notebook["cells"]
    assert isinstance(cells, list)
    return [
        cell
        for cell in cells
        if isinstance(cell, dict) and NEMO_RL_REPO in _cell_text(cell, "source")
    ]


def _cells_containing(marker: str) -> list[dict[str, object]]:
    notebook = _notebook()
    cells = notebook["cells"]
    assert isinstance(cells, list)
    return [
        cell
        for cell in cells
        if isinstance(cell, dict) and marker in _cell_text(cell, "source")
    ]


def test_super_grpo_dapo_nemo_rl_checkout_uses_exact_revision() -> None:
    source = _notebook_source()

    assert re.fullmatch(r"[0-9a-f]{40}", EXPECTED_REVISION)
    assert EXPECTED_REVISION in source
    assert "NEMO_RL_SUPER_V3_REVISION" in source
    assert 'git checkout "${NEMO_RL_SUPER_V3_REVISION}"' in source
    assert 'test "$(git rev-parse HEAD)" = "${NEMO_RL_SUPER_V3_REVISION}"' in source


def test_super_grpo_dapo_preserves_super_v3_branch_context() -> None:
    source = _notebook_source()

    assert "NemoRL Super-v3 branch" in source
    assert EXPECTED_BRANCH_GUIDE_URL in source
    assert f"git clone -b super-v3 {NEMO_RL_REPO}" in source


def test_super_grpo_dapo_nemo_rl_docs_links_are_pinned() -> None:
    source = _notebook_source()

    assert EXPECTED_BRANCH_GUIDE_URL in source
    assert EXPECTED_DOCKER_GUIDE_URL in source
    for mutable_url_part in MUTABLE_DOC_URL_PARTS:
        assert mutable_url_part not in source


def test_super_grpo_dapo_pinned_docs_cells_are_markdown_and_clear() -> None:
    for expected_url in (EXPECTED_BRANCH_GUIDE_URL, EXPECTED_DOCKER_GUIDE_URL):
        cells = _cells_containing(expected_url)
        assert len(cells) == 1
        cell = cells[0]
        assert cell["cell_type"] == "markdown"
        assert cell.get("execution_count") is None
        assert cell.get("outputs", []) == []


def test_super_grpo_dapo_nemo_rl_setup_cell_is_guarded_and_outputs_are_clear() -> None:
    setup_cells = _nemo_rl_setup_cells()

    assert len(setup_cells) == 1
    setup_cell = setup_cells[0]
    setup_source = _cell_text(setup_cell, "source")
    assert setup_cell["cell_type"] == "code"
    assert setup_cell.get("outputs") == []
    assert EXPECTED_REVISION in setup_source
    assert "git clone -b super-v3" in setup_source
    assert "git checkout" in setup_source
    assert "git rev-parse HEAD" in setup_source
    assert "git submodule update --init --recursive" in setup_source


def test_super_grpo_dapo_has_no_branch_only_nemo_rl_setup_sequence() -> None:
    raw_text = NOTEBOOK.read_text(encoding="utf-8")
    assert "git clone --recursive -b super-v3" not in raw_text

    for cell in _nemo_rl_setup_cells():
        source = _cell_text(cell, "source")
        if "super-v3" in source and ("git clone" in source or "git checkout" in source):
            assert EXPECTED_REVISION in source
            assert "git checkout" in source
            assert "git rev-parse HEAD" in source


def test_super_grpo_dapo_context_is_present() -> None:
    source = _notebook_source()

    expected_context = (
        "# Nemotron Super V3 GRPO/DAPO Training with NemoRL",
        "GRPO/DAPO training",
        "DAPO-Math-17k",
        "pure NeMoRL",
    )
    for marker in expected_context:
        assert marker in source
