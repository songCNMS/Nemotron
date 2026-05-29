"""Static docs checks for Omni3 Stage1 RL source revision pins."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_PREP_DIR = REPO_ROOT / "src/nemotron/recipes/omni3/stage1_rl/config/data_prep"
DATA_BLEND_RAW = DATA_PREP_DIR / "data_blend_raw.json"
DOC_RL = REPO_ROOT / "docs/nemotron/omni3/rl.md"
DOC_DATA_PREP = REPO_ROOT / "docs/nemotron/omni3/rl/data-prep.md"

LOWER_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _load_yaml(path: Path) -> dict[str, object]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{path}: top-level YAML must be a mapping"
    return data


def _source_pin(config_name: str) -> tuple[str, str]:
    data = _load_yaml(DATA_PREP_DIR / f"{config_name}.yaml")
    source_uri = data["source_uri"]
    source_revision = data["source_revision"]
    assert isinstance(source_uri, str)
    assert isinstance(source_revision, str)
    return source_uri, source_revision


def _runtime_source_pins() -> dict[str, tuple[str, str]]:
    pins = {
        config_name: _source_pin(config_name)
        for config_name in ("mpo", "text", "vision")
    }

    blend = json.loads(DATA_BLEND_RAW.read_text(encoding="utf-8"))
    datasets = blend["datasets"]
    assert len(datasets) == 1
    text_uri, text_revision = pins["text"]
    assert datasets[0]["path"] == text_uri
    assert datasets[0]["revision"] == text_revision
    return pins


def test_omni3_rl_docs_show_runtime_source_revision_pins() -> None:
    docs = {
        "rl.md": DOC_RL.read_text(encoding="utf-8"),
        "rl/data-prep.md": DOC_DATA_PREP.read_text(encoding="utf-8"),
    }

    for config_name, (source_uri, source_revision) in _runtime_source_pins().items():
        assert LOWER_SHA_RE.match(source_revision), config_name
        for doc_name, doc_text in docs.items():
            assert source_uri in doc_text, f"{doc_name} missing {source_uri}"
            assert source_revision in doc_text, (
                f"{doc_name} missing {config_name} revision {source_revision}"
            )


def test_data_prep_yaml_snippets_include_mpo_and_vision_revision_pins() -> None:
    doc_text = DOC_DATA_PREP.read_text(encoding="utf-8")

    for config_name in ("vision", "mpo"):
        data = _load_yaml(DATA_PREP_DIR / f"{config_name}.yaml")
        expected_snippet = "\n".join(
            [
                f"# {config_name}.yaml",
                f"stage: {data['stage']}",
                f"dataset_name: {data['dataset_name']}",
                f"source_uri: {data['source_uri']}",
                f"source_revision: {data['source_revision']}",
            ]
        )
        assert expected_snippet in doc_text


def test_rl_overview_table_includes_runtime_source_revision_pins() -> None:
    doc_text = DOC_RL.read_text(encoding="utf-8")

    for config_name, (source_uri, source_revision) in _runtime_source_pins().items():
        expected_row_fragment = (
            f"| `{config_name}.yaml` | `{source_uri}` @ `{source_revision}`"
        )
        assert expected_row_fragment in doc_text
