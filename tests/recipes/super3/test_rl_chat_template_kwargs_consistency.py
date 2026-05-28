"""Regression: Super3 RL configs must declare one Qwen
chat-template rendering contract.

Before PR C (chat-template consistency review follow-up), only SWE1
and SWE2 explicitly set ``chat_template_kwargs`` inside
``http_server_serving_chat_kwargs``. RLVR1 and RLHF inherited the
super3.jinja defaults silently, so the multi-turn history-truncation
behavior diverged across stages (SWE1/SWE2: preserve prior thinking;
RLVR1/RLHF: truncate to ``<think></think>``). This was a real
cross-stage inconsistency on the very kwargs the model is trained on.

The active Qwen target must not rely on implicit tokenizer defaults:
``policy.tokenizer.chat_template_kwargs`` and vLLM serving
``chat_template_kwargs`` must both be explicit and equal. A sibling
``policy.generation.vllm_cfg.enable_thinking`` must not conflict with
the nested Qwen kwargs.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from omegaconf import OmegaConf

from nemo_runspec.cli_context import GlobalContext
from nemo_runspec.config import parse_config

yaml = pytest.importorskip("yaml")


REPO_ROOT = Path(__file__).resolve().parents[3]

GENERIC_RL_CONFIG = (
    REPO_ROOT / "src/nemotron/recipes/super3/stage2_rl/config/default.yaml"
)
GENERIC_RL_CONFIG_DIR = GENERIC_RL_CONFIG.parent
GENERIC_RL_RUNSPEC_SCRIPT = (
    REPO_ROOT / "src/nemotron/recipes/super3/stage2_rl/train.py"
)
STAGE1_RLVR_CONFIG_DIR = (
    REPO_ROOT / "src/nemotron/recipes/super3/stage2_rl/stage1_rlvr/config"
)
STAGE2_SWE1_CONFIG_DIR = (
    REPO_ROOT / "src/nemotron/recipes/super3/stage2_rl/stage2_swe1/config"
)
STAGE3_RLHF_CONFIG_DIR = (
    REPO_ROOT / "src/nemotron/recipes/super3/stage2_rl/stage3_rlhf/config"
)

RL_CONFIGS = (
    GENERIC_RL_CONFIG,
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage2_rl/stage1_rlvr/config/default.yaml",
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage2_rl/stage2_swe1/config/default.yaml",
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage2_rl/stage2_swe2/config/default.yaml",
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage2_rl/stage3_rlhf/config/default.yaml",
)
RL_DEFAULT_OVERLAY_CONFIGS = (
    (GENERIC_RL_CONFIG_DIR, "tiny"),
    (STAGE1_RLVR_CONFIG_DIR, "small"),
    (STAGE1_RLVR_CONFIG_DIR, "smoke"),
    (STAGE1_RLVR_CONFIG_DIR, "rlvr2"),
    (STAGE1_RLVR_CONFIG_DIR, "rlvr3"),
    (STAGE2_SWE1_CONFIG_DIR, "small"),
    (STAGE3_RLHF_CONFIG_DIR, "small"),
)

EXPECTED_KWARGS = {
    # PR D: enable_thinking=false matches what SFT actually trains
    # against — no M0/M1 converter sets `reasoning_content` and the
    # CoT lives in content body, not inside `<think>...</think>`
    # blocks. With this kwarg false, the generation prompt is
    # `<|im_start|>assistant\n<think></think>` (closed empty), same as
    # SFT. Flipping back to true requires PR-D-followup: carry
    # reasoning_content through M0/M1 supervision builders.
    "enable_thinking": False,
    "truncate_history_thinking": False,
}

EXPECTED_HTTP_CHAT_SERVING_FIELDS = {
    "tool_parser": "qwen3_coder",
    "reasoning_parser": "nano_v3",
    "reasoning_parser_plugin": "nemo_rl/utils/nano_v3_reasoning_parser.py",
}


def _policy_block(config_path: Path) -> dict:
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{config_path}: top-level must be a mapping"
    policy = data.get("policy")
    assert isinstance(policy, dict), f"{config_path}: missing policy block"
    return policy


def _runspec_default_config_name(script_path: Path) -> str:
    for line in script_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("# default = "):
            return stripped.split('"')[1]
    raise AssertionError(f"{script_path}: missing tool.runspec.config default")


def _parse_recipe_config(config_dir: Path, config_name: str) -> dict:
    config = parse_config(GlobalContext(config=config_name), config_dir, config_name)
    return OmegaConf.to_container(config, resolve=False)


def _vllm_cfg(config_path: Path) -> dict:
    policy = _policy_block(config_path)
    generation = policy.get("generation")
    assert isinstance(generation, dict), (
        f"{config_path}: missing policy.generation block"
    )
    vllm_cfg = generation.get("vllm_cfg")
    assert isinstance(vllm_cfg, dict), (
        f"{config_path}: missing policy.generation.vllm_cfg block"
    )
    return vllm_cfg


def _http_chat_template_kwargs(config_path: Path) -> dict:
    """Return vLLM serving chat_template_kwargs from an RL config."""
    http_chat = _http_chat_serving_kwargs(config_path)
    kwargs = http_chat.get("chat_template_kwargs")
    assert isinstance(kwargs, dict), (
        f"{config_path}: chat_template_kwargs must be a mapping inside "
        "http_server_serving_chat_kwargs so RL serving does not silently "
        "inherit Qwen-chat defaults)"
    )
    return kwargs


def _http_chat_serving_kwargs(config_path: Path) -> dict:
    """Return vLLM HTTP chat serving kwargs from an RL config."""
    vllm_cfg = _vllm_cfg(config_path)
    http_chat = vllm_cfg.get("http_server_serving_chat_kwargs")
    assert isinstance(http_chat, dict), (
        f"{config_path}: missing policy.generation.vllm_cfg."
        "http_server_serving_chat_kwargs block"
    )
    return http_chat


def _tokenizer_chat_template_kwargs(config_path: Path) -> dict:
    """Return tokenizer chat_template_kwargs from a stage RL config."""
    policy = _policy_block(config_path)
    tokenizer = policy.get("tokenizer")
    assert isinstance(tokenizer, dict), f"{config_path}: missing policy.tokenizer block"
    kwargs = tokenizer.get("chat_template_kwargs")
    assert isinstance(kwargs, dict), (
        f"{config_path}: policy.tokenizer.chat_template_kwargs must be a mapping; "
        "it must not be null when rollout serving pins Qwen chat kwargs"
    )
    return kwargs


@pytest.mark.parametrize(
    "config_path", RL_CONFIGS, ids=lambda p: p.parent.parent.name
)
def test_rl_stage_pins_unified_chat_template_kwargs(config_path: Path) -> None:
    kwargs = _http_chat_template_kwargs(config_path)
    for key, expected in EXPECTED_KWARGS.items():
        assert key in kwargs, f"{config_path}: missing chat_template_kwargs.{key}"
        assert kwargs[key] is expected, (
            f"{config_path}: chat_template_kwargs.{key}={kwargs[key]!r} "
            f"diverges from the unified Qwen RL contract ({key}={expected!r})"
        )


@pytest.mark.parametrize(
    "config_path", RL_CONFIGS, ids=lambda p: p.parent.parent.name
)
def test_tokenizer_kwargs_match_rollout_serving_kwargs(config_path: Path) -> None:
    tokenizer_kwargs = _tokenizer_chat_template_kwargs(config_path)
    serving_kwargs = _http_chat_template_kwargs(config_path)

    assert tokenizer_kwargs == serving_kwargs == EXPECTED_KWARGS, (
        f"{config_path}: tokenizer kwargs {tokenizer_kwargs!r} must exactly "
        f"match rollout serving kwargs {serving_kwargs!r}"
    )


@pytest.mark.parametrize(
    "config_path", RL_CONFIGS, ids=lambda p: p.parent.parent.name
)
def test_vllm_cfg_has_no_conflicting_enable_thinking_sibling(config_path: Path) -> None:
    vllm_cfg = _vllm_cfg(config_path)
    nested_enable_thinking = _http_chat_template_kwargs(config_path)["enable_thinking"]

    if "enable_thinking" in vllm_cfg:
        assert vllm_cfg["enable_thinking"] is nested_enable_thinking, (
            f"{config_path}: policy.generation.vllm_cfg.enable_thinking="
            f"{vllm_cfg['enable_thinking']!r} conflicts with nested "
            "http_server_serving_chat_kwargs.chat_template_kwargs.enable_thinking="
            f"{nested_enable_thinking!r}"
        )


@pytest.mark.parametrize(
    "config_path", RL_CONFIGS, ids=lambda p: p.parent.parent.name
)
def test_http_serving_uses_unified_qwen_parser_contract(config_path: Path) -> None:
    http_chat = _http_chat_serving_kwargs(config_path)
    for key, expected in EXPECTED_HTTP_CHAT_SERVING_FIELDS.items():
        assert http_chat.get(key) == expected, (
            f"{config_path}: http_server_serving_chat_kwargs.{key}="
            f"{http_chat.get(key)!r} diverges from the unified Qwen RL "
            f"serving contract ({key}={expected!r})"
        )


def test_all_rl_configs_agree_on_chat_template_kwargs() -> None:
    """Cross-config consistency: every runnable RL config uses the same kwargs.
    Drift here is the bug, not the values."""
    per_stage_kwargs = {
        config_path.parent.parent.name: tuple(
            sorted(_http_chat_template_kwargs(config_path).items())
        )
        for config_path in RL_CONFIGS
    }
    distinct = set(per_stage_kwargs.values())
    assert len(distinct) == 1, (
        "RL stages disagree on chat_template_kwargs: "
        + "; ".join(
            f"{name}={dict(items)}" for name, items in per_stage_kwargs.items()
        )
    )


def test_all_rl_configs_agree_on_http_serving_parser_contract() -> None:
    """Cross-config consistency: generic and stage-specific RL serving
    must use the same tool parser and Qwen reasoning parser plugin."""
    per_config_contract = {
        config_path.parent.parent.name: {
            key: _http_chat_serving_kwargs(config_path).get(key)
            for key in EXPECTED_HTTP_CHAT_SERVING_FIELDS
        }
        for config_path in RL_CONFIGS
    }
    distinct = {tuple(sorted(contract.items())) for contract in per_config_contract.values()}
    assert len(distinct) == 1, (
        "RL configs disagree on HTTP serving parser contract: "
        + "; ".join(
            f"{name}={contract}" for name, contract in per_config_contract.items()
        )
    )


def test_generic_runspec_default_tiny_inherits_qwen_rl_contract() -> None:
    """The generic `nemotron super3 rl` runspec default must not bypass
    the Qwen chat-template, parser, or stop-string contract."""
    default_name = _runspec_default_config_name(GENERIC_RL_RUNSPEC_SCRIPT)
    assert default_name == "tiny"

    tiny_config_path = GENERIC_RL_CONFIG_DIR / f"{default_name}.yaml"
    tiny_raw = yaml.safe_load(tiny_config_path.read_text(encoding="utf-8"))
    assert isinstance(tiny_raw, dict), f"{tiny_config_path}: top-level must be a mapping"
    assert tiny_raw.get("defaults") == "default.yaml"

    resolved = _parse_recipe_config(GENERIC_RL_CONFIG_DIR, default_name)
    policy = resolved.get("policy")
    assert isinstance(policy, dict), f"{tiny_config_path}: missing policy block"
    assert "defaults" not in resolved

    tokenizer = policy.get("tokenizer")
    assert isinstance(tokenizer, dict), f"{tiny_config_path}: missing policy.tokenizer"
    assert tokenizer.get("chat_template_kwargs") == EXPECTED_KWARGS

    generation = policy.get("generation")
    assert isinstance(generation, dict), f"{tiny_config_path}: missing policy.generation"
    assert generation.get("stop_strings") == ["<|im_end|>"]

    vllm_cfg = generation.get("vllm_cfg")
    assert isinstance(vllm_cfg, dict), f"{tiny_config_path}: missing vllm_cfg"
    http_chat = vllm_cfg.get("http_server_serving_chat_kwargs")
    assert isinstance(http_chat, dict), (
        f"{tiny_config_path}: missing http_server_serving_chat_kwargs"
    )
    for key, expected in EXPECTED_HTTP_CHAT_SERVING_FIELDS.items():
        assert http_chat.get(key) == expected
    assert http_chat.get("chat_template_kwargs") == EXPECTED_KWARGS

    assert resolved["grpo"]["max_num_steps"] == 10
    assert resolved["run"]["model"] == "super3-sft-model-tiny:latest"


@pytest.mark.parametrize(
    ("config_dir", "config_name"),
    RL_DEFAULT_OVERLAY_CONFIGS,
    ids=lambda value: value.name if isinstance(value, Path) else value,
)
def test_stage2_rl_default_overlays_resolve_qwen_contract_with_real_loader(
    config_dir: Path,
    config_name: str,
) -> None:
    resolved = _parse_recipe_config(config_dir, config_name)
    assert "defaults" not in resolved

    policy = resolved.get("policy")
    assert isinstance(policy, dict), f"{config_dir}/{config_name}: missing policy block"
    tokenizer = policy.get("tokenizer")
    assert isinstance(tokenizer, dict), (
        f"{config_dir}/{config_name}: missing policy.tokenizer"
    )
    assert tokenizer.get("chat_template_kwargs") == EXPECTED_KWARGS

    generation = policy.get("generation")
    assert isinstance(generation, dict), (
        f"{config_dir}/{config_name}: missing policy.generation"
    )
    assert generation.get("stop_strings") == ["<|im_end|>"]

    vllm_cfg = generation.get("vllm_cfg")
    assert isinstance(vllm_cfg, dict), f"{config_dir}/{config_name}: missing vllm_cfg"
    http_chat = vllm_cfg.get("http_server_serving_chat_kwargs")
    assert isinstance(http_chat, dict), (
        f"{config_dir}/{config_name}: missing http_server_serving_chat_kwargs"
    )
    assert http_chat.get("chat_template_kwargs") == EXPECTED_KWARGS
    for key, expected in EXPECTED_HTTP_CHAT_SERVING_FIELDS.items():
        assert http_chat.get(key) == expected
