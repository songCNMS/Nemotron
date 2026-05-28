"""Static portability checks for Omni3 stage1 RL launch configs."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from omegaconf import OmegaConf

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
