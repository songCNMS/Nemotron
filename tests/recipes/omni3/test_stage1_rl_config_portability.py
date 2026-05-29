"""Static portability checks for Omni3 stage1 RL launch configs."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml
from omegaconf import OmegaConf

from nemotron.recipes.omni3.stage1_rl._data_prep_base import (
    Omni3RLDataPrepConfig,
    _prepare_text,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
MPO_DEFAULT = (
    REPO_ROOT / "src/nemotron/recipes/omni3/stage1_rl/stage1_mpo/config/default.yaml"
)
MPO_TINY = (
    REPO_ROOT / "src/nemotron/recipes/omni3/stage1_rl/stage1_mpo/config/tiny.yaml"
)
TEXT_DEFAULT = (
    REPO_ROOT / "src/nemotron/recipes/omni3/stage1_rl/stage2_text_rl/config/default.yaml"
)
DATA_PREP_DIR = REPO_ROOT / "src/nemotron/recipes/omni3/stage1_rl/config/data_prep"
DATA_PREP_MPO = DATA_PREP_DIR / "mpo.yaml"
DATA_PREP_TEXT = DATA_PREP_DIR / "text.yaml"
DATA_PREP_VISION = DATA_PREP_DIR / "vision.yaml"
DATA_BLEND_RAW = DATA_PREP_DIR / "data_blend_raw.json"

CONFIGS = (
    pytest.param("mpo-default", MPO_DEFAULT, id="mpo-default"),
    pytest.param("mpo-tiny", MPO_TINY, id="mpo-tiny"),
    pytest.param("text-default", TEXT_DEFAULT, id="text-default"),
)

BANNED_NAMED_USER_FRAGMENTS = (
    "/lustre/fs1/portfolios/coreai/users/aroshanghias",
    "users/aroshanghias",
)

COMMON_REQUIRED_ENV_KEYS = {
    "OMNI_SHARED_ROOT",
    "DATA_ROOT",
    "CHECKPOINT_ROOT",
    "CONTAINER_ROOT",
    "USER_ROOT",
    "CACHE_ROOT",
    "NEMORL",
    "CONTAINER",
    "JOB_NAME",
    "NUM_NODES",
    "MODEL_NAME",
    "TRAIN_DATA_PATH",
}
MPO_REQUIRED_ENV_KEYS = COMMON_REQUIRED_ENV_KEYS | {"DATA_PATH"}
TEXT_REQUIRED_ENV_KEYS = COMMON_REQUIRED_ENV_KEYS | {
    "MODEL_ROOT",
    "VALIDATION_DATA_PATH",
    "CONTEXT_PARALLEL_SIZE",
    "TRAIN_GLOBAL_BATCH_SIZE",
    "NUM_PROMPTS_PER_STEP",
    "NUM_GENERATIONS_PER_PROMPT",
    "WANDB_PROJECT",
}

OVERRIDE_ENV_BY_CONFIG_KEY = {
    "OMNI_SHARED_ROOT": "OMNI_SHARED_ROOT",
    "DATA_ROOT": "OMNI3_DATA_ROOT",
    "MODEL_ROOT": "OMNI3_MODEL_ROOT",
    "CHECKPOINT_ROOT": "OMNI3_CHECKPOINT_ROOT",
    "CONTAINER_ROOT": "OMNI3_CONTAINER_ROOT",
    "USER_ROOT": "OMNI3_USER_ROOT",
    "CACHE_ROOT": "OMNI3_CACHE_ROOT",
    "NEMORL": "OMNI3_RL_ROOT",
    "CONTAINER": "OMNI3_RL_SQSH",
}

PORTABLE_DEFAULT_BY_CONFIG_KEY = {
    "OMNI_SHARED_ROOT": "output/omni3",
    "DATA_ROOT": "output/omni3/stage1_rl/data",
    "MODEL_ROOT": "output/omni3/stage1_rl/checkpoints",
    "CHECKPOINT_ROOT": "output/omni3/stage1_rl/checkpoints",
    "CONTAINER_ROOT": "output/omni3/stage1_rl/containers",
    "USER_ROOT": "output/omni3",
    "CACHE_ROOT": "output/omni3/.cache",
}

LOWER_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_DATA_PREP_REVISIONS = {
    "hf://OpenGVLab/MMPR": "fe3f35704dcfc2709a072b07df0ecab6046b2c0c",
    "hf://OpenGVLab/MMPR-Tiny": "eb493212c9614b69ca49cd6e66719413c514459b",
    "hf://nvidia/Nemotron-3-Nano-RL-Training-Blend": (
        "ffd169f2b74bb492ec607d64bd56f7435054972b"
    ),
}


def _load_config(config_path: Path) -> dict:
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{config_path}: top-level YAML must be a mapping"
    return data


def _env_vars(config_path: Path) -> dict[str, str]:
    env_vars = _load_config(config_path)["run"]["env"]["env_vars"]
    assert isinstance(env_vars, dict), f"{config_path}: run.env.env_vars must be a mapping"
    return env_vars


@pytest.mark.parametrize(("config_name", "config_path"), CONFIGS)
def test_stage1_rl_configs_do_not_reference_named_user_lustre_fallbacks(
    config_name: str,
    config_path: Path,
) -> None:
    text = config_path.read_text(encoding="utf-8")
    for banned in BANNED_NAMED_USER_FRAGMENTS:
        assert banned not in text, f"{config_name} still references {banned}"


@pytest.mark.parametrize(("config_name", "config_path"), CONFIGS)
def test_stage1_rl_configs_keep_required_env_var_contract(
    config_name: str,
    config_path: Path,
) -> None:
    env_vars = _env_vars(config_path)
    required = TEXT_REQUIRED_ENV_KEYS if config_name == "text-default" else MPO_REQUIRED_ENV_KEYS
    assert required <= env_vars.keys()


@pytest.mark.parametrize(("config_name", "config_path"), CONFIGS)
def test_stage1_rl_configs_preserve_override_env_names(
    config_name: str,
    config_path: Path,
) -> None:
    env_vars = _env_vars(config_path)
    for config_key, env_name in OVERRIDE_ENV_BY_CONFIG_KEY.items():
        if config_key not in env_vars:
            continue
        value = env_vars[config_key]
        assert value.startswith(f"${{oc.env:{env_name},"), (
            f"{config_name}: {config_key} no longer preserves {env_name} as "
            "the first-choice override"
        )


@pytest.mark.parametrize(("config_name", "config_path"), CONFIGS)
def test_stage1_rl_no_env_defaults_are_run_dir_relative_or_user_cache(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    config_name: str,
    config_path: Path,
) -> None:
    run_dir = tmp_path / "nemo-run"
    monkeypatch.setenv("NEMO_RUN_DIR", str(run_dir))
    monkeypatch.setenv("USER", "portable-user")
    for env_name in set(OVERRIDE_ENV_BY_CONFIG_KEY.values()):
        monkeypatch.delenv(env_name, raising=False)

    env_vars = _env_vars(config_path)
    relevant_values = {
        key: env_vars[key]
        for key in (*PORTABLE_DEFAULT_BY_CONFIG_KEY, "CONTAINER")
        if key in env_vars
    }
    resolved = OmegaConf.to_container(OmegaConf.create(relevant_values), resolve=True)

    for config_key, relative_default in PORTABLE_DEFAULT_BY_CONFIG_KEY.items():
        if config_key not in resolved:
            continue
        assert resolved[config_key] == str(run_dir / relative_default), (
            config_name,
            config_key,
            resolved[config_key],
        )
    assert resolved["CONTAINER"] == (
        "/home/portable-user/.cache/nemotron/containers/omni3-rl.sqsh"
    )
    for value in resolved.values():
        assert not str(value).startswith("/lustre/fs1/portfolios/coreai/users")
        assert "aroshanghias" not in str(value)


@pytest.mark.parametrize(("config_name", "config_path"), CONFIGS)
def test_stage1_rl_env_overrides_win_over_portable_defaults(
    monkeypatch: pytest.MonkeyPatch,
    config_name: str,
    config_path: Path,
) -> None:
    env_vars = _env_vars(config_path)
    relevant_values = {
        config_key: env_vars[config_key]
        for config_key in OVERRIDE_ENV_BY_CONFIG_KEY
        if config_key in env_vars
    }
    for config_key, env_name in OVERRIDE_ENV_BY_CONFIG_KEY.items():
        if config_key in relevant_values:
            monkeypatch.setenv(env_name, f"/override/{env_name}")

    resolved = OmegaConf.to_container(OmegaConf.create(relevant_values), resolve=True)
    for config_key, env_name in OVERRIDE_ENV_BY_CONFIG_KEY.items():
        if config_key in resolved:
            assert resolved[config_key] == f"/override/{env_name}", (
                config_name,
                config_key,
            )


def test_mpo_tiny_keeps_tiny_job_name_and_one_node_defaults() -> None:
    env_vars = _env_vars(MPO_TINY)
    assert env_vars["JOB_NAME"] == (
        "${oc.env:OMNI3_MPO_JOB_NAME,mpo-nanov3omni-mmpr-public-tiny}"
    )
    assert env_vars["NUM_NODES"] == "${oc.env:OMNI3_MPO_NUM_NODES,1}"


def test_omni3_stage1_rl_data_prep_sources_are_revision_pinned() -> None:
    configs = [
        _load_config(DATA_PREP_MPO),
        _load_config(DATA_PREP_TEXT),
        _load_config(DATA_PREP_VISION),
    ]
    for data in configs:
        source_uri = data["source_uri"]
        expected_revision = EXPECTED_DATA_PREP_REVISIONS[source_uri]
        assert data["source_revision"] == expected_revision
        assert LOWER_SHA_RE.match(data["source_revision"])

    blend = json.loads(DATA_BLEND_RAW.read_text(encoding="utf-8"))
    datasets = blend["datasets"]
    assert len(datasets) == 1
    assert datasets[0]["path"] == "hf://nvidia/Nemotron-3-Nano-RL-Training-Blend"
    assert datasets[0]["revision"] == EXPECTED_DATA_PREP_REVISIONS[datasets[0]["path"]]
    assert LOWER_SHA_RE.match(datasets[0]["revision"])


def test_omni3_stage1_rl_data_prep_has_no_unpinned_hf_sources() -> None:
    for path in (DATA_PREP_MPO, DATA_PREP_TEXT, DATA_PREP_VISION):
        data = _load_config(path)
        assert data.get("source_uri")
        assert data.get("source_revision"), f"{path.name} missing source_revision"

    blend = json.loads(DATA_BLEND_RAW.read_text(encoding="utf-8"))
    for dataset in blend["datasets"]:
        assert dataset.get("path", "").startswith("hf://")
        assert dataset.get("revision"), "text blend HF dataset missing revision"


def test_text_data_prep_rejects_source_revision_without_matching_blend_row(
    tmp_path: Path,
) -> None:
    blend_path = tmp_path / "blend.json"
    blend_path.write_text(
        json.dumps(
            {
                "datasets": [
                    {
                        "name": "other",
                        "path": "hf://example/Other-Dataset",
                        "revision": "ffd169f2b74bb492ec607d64bd56f7435054972b",
                        "split": "train",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    cfg = Omni3RLDataPrepConfig(
        stage="text",
        dataset_name="text_only_rl_stage1",
        source_uri="hf://nvidia/Nemotron-3-Nano-RL-Training-Blend",
        source_revision="ffd169f2b74bb492ec607d64bd56f7435054972b",
        blend_path=blend_path,
        output_dir=tmp_path / "out",
    )

    with pytest.raises(ValueError, match="has no matching dataset row in blend"):
        _prepare_text(cfg, tracking=None)
