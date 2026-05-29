"""Qwen SFT chat-template contract checks.

Qwen M1 SFT must train on packed rows rendered with Qwen's own tokenizer
template and with thinking disabled. Training on rows packed with the Super3
template can silently change role delimiters and final-answer formatting, so
the Qwen entrypoints validate the packed artifact metadata before building the
Megatron recipe.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

NEMOTRON_SUPER_TOKENIZER_DEFAULT = "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16"
LEGACY_AGENTIC_PACKED_SFT_DIR = "../output/super3/stage1_sft_agentic_v0/splits"
QWEN_AGENTIC_PACKED_SFT_DIR = "../output/super3/stage1_sft_agentic_v0_qwen/splits"
QWEN_DATA_PREP_TARGET_FAMILY = "qwen"
QWEN_DATA_PREP_CONFIG_NAME = "qwen_agentic_v0"
QWEN_SFT_CHAT_TEMPLATE = "tokenizer"
QWEN_SFT_CHAT_TEMPLATE_KWARGS: dict[str, bool] = {
    "enable_thinking": False,
    "truncate_history_thinking": False,
}
QWEN_TRAINING_PROFILE = "qwen"
SUPER3_M1_AGENTIC_PACKED_DIR_ENV_VAR = "SUPER3_M1_AGENTIC_PACKED_DIR"


def qwen_local_packed_sft_dir_default(
    packed_sft_dir: object,
    *,
    packed_dir_env_is_set: bool,
) -> str | None:
    """Return the Qwen local-train packed-data default for inherited config.

    The Qwen local train entrypoints intentionally reuse ``m1_agentic_train`` for
    most training knobs, but that YAML's fallback packed dir is the Super3
    ``agentic_v0`` output. Rewrite only that inherited fallback; explicit env or
    CLI/config overrides remain operator-owned.
    """

    if packed_sft_dir is None:
        return None

    resolved = str(packed_sft_dir)
    if packed_dir_env_is_set:
        return resolved
    if resolved == LEGACY_AGENTIC_PACKED_SFT_DIR:
        return QWEN_AGENTIC_PACKED_SFT_DIR
    return resolved


def _metadata_candidates(packed_sft_dir: str | Path) -> list[Path]:
    path = Path(packed_sft_dir).expanduser()
    if path.is_file():
        path = path.parent
    return [
        path / "metadata.json",
        path.parent / "metadata.json",
        path.parent.parent / "metadata.json",
    ]


def find_packed_sft_metadata_path(packed_sft_dir: str | Path) -> Path | None:
    """Find the SFTDataArtifact metadata JSON for a packed splits directory."""

    seen: set[Path] = set()
    for candidate in _metadata_candidates(packed_sft_dir):
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate.is_file():
            return candidate
    return None


def load_packed_sft_metadata(packed_sft_dir: str | Path) -> tuple[Path, dict[str, Any]]:
    """Load packed SFT artifact metadata from *packed_sft_dir*."""

    metadata_path = find_packed_sft_metadata_path(packed_sft_dir)
    if metadata_path is None:
        searched = ", ".join(str(path) for path in _metadata_candidates(packed_sft_dir))
        raise FileNotFoundError(
            "Qwen SFT requires packed data metadata.json so the chat template "
            f"contract can be verified. Searched: {searched}"
        )

    with metadata_path.open(encoding="utf-8") as f:
        metadata = json.load(f)
    if not isinstance(metadata, dict):
        raise ValueError(f"{metadata_path} must contain a JSON object")
    return metadata_path, metadata


def _metadata_value(metadata: Mapping[str, Any], key: str) -> Any:
    for container_key in ("", "metadata", "packing", "qwen_chat_contract"):
        container: Mapping[str, Any]
        if container_key:
            value = metadata.get(container_key)
            if not isinstance(value, Mapping):
                continue
            container = value
        else:
            container = metadata
        if key in container:
            return container[key]
    return None


def _config_value(config: Mapping[str, Any], key: str) -> Any:
    value = config.get(key)
    if value is not None:
        return value
    if key == "tokenizer_model":
        tokenizer = config.get("tokenizer")
        if isinstance(tokenizer, Mapping):
            return tokenizer.get("model") or tokenizer.get("tokenizer_model")
    return None


def _metadata_container(metadata: Mapping[str, Any], key: str) -> Mapping[str, Any] | None:
    value = metadata.get(key)
    if isinstance(value, Mapping):
        return value
    return None


def _normalize_tokenizer_ref(value: str) -> str:
    normalized = value.removeprefix("file://")
    for prefix in ("https://huggingface.co/", "http://huggingface.co/"):
        if normalized.startswith(prefix):
            normalized = normalized.removeprefix(prefix).split("/tree/", 1)[0]
            break
    if normalized.startswith("hf://models/"):
        normalized = normalized.removeprefix("hf://models/")
    if normalized.startswith(("/", "~", ".")) or Path(normalized).expanduser().exists():
        return str(Path(normalized).expanduser().resolve(strict=False))
    return normalized


def validate_qwen_data_prep_config(
    config: Mapping[str, Any],
    *,
    config_path: str | Path | None = None,
) -> None:
    """Validate a data-prep config before packing Qwen-target SFT rows.

    Qwen data must never rely on the Super3 profile defaults because those
    defaults use the Nemotron tokenizer and the repo-pinned Super3 template.
    This check stays lightweight so planners and tests can run it as a static
    invariant without importing the full data-prep pipeline.
    """

    label = str(config_path) if config_path is not None else "Qwen data-prep config"

    target_family = _config_value(config, "target_model_family")
    if target_family != QWEN_DATA_PREP_TARGET_FAMILY:
        raise ValueError(
            f"{label} must set target_model_family={QWEN_DATA_PREP_TARGET_FAMILY!r}; "
            f"got {target_family!r}."
        )

    config_name = _config_value(config, "config_name")
    if config_name != QWEN_DATA_PREP_CONFIG_NAME:
        raise ValueError(
            f"{label} must set config_name={QWEN_DATA_PREP_CONFIG_NAME!r}; "
            f"got {config_name!r}."
        )

    tokenizer_model = _config_value(config, "tokenizer_model")
    if not isinstance(tokenizer_model, str) or not tokenizer_model.strip():
        raise ValueError(f"{label} must set tokenizer.model to the explicit Qwen tokenizer/model.")
    if tokenizer_model == NEMOTRON_SUPER_TOKENIZER_DEFAULT:
        raise ValueError(
            f"{label} still points tokenizer.model at the Nemotron/Super3 default. "
            "Set tokenizer.model to the target Qwen HF model or local tokenizer path."
        )
    if not _is_qwen_ref(tokenizer_model):
        raise ValueError(
            f"{label} must set tokenizer.model to a recognizably Qwen tokenizer/model; "
            f"got {tokenizer_model!r}."
        )

    chat_template = _config_value(config, "chat_template")
    if chat_template != QWEN_SFT_CHAT_TEMPLATE:
        raise ValueError(
            f"{label} must set chat_template={QWEN_SFT_CHAT_TEMPLATE!r}; "
            f"got {chat_template!r}."
        )

    chat_template_kwargs = _config_value(config, "chat_template_kwargs")
    if not isinstance(chat_template_kwargs, Mapping):
        raise ValueError(f"{label} must define chat_template_kwargs for Qwen packing.")
    for key, expected in QWEN_SFT_CHAT_TEMPLATE_KWARGS.items():
        if chat_template_kwargs.get(key) is not expected:
            raise ValueError(
                f"{label} must set chat_template_kwargs.{key}={expected!r}; "
                f"got {chat_template_kwargs.get(key)!r}."
            )


def _is_qwen_ref(value: str | None) -> bool:
    if not value:
        return False
    normalized = _normalize_tokenizer_ref(str(value)).lower()
    return "qwen" in normalized


def _is_nemotron_super_ref(value: str | None) -> bool:
    if not value:
        return False
    normalized = _normalize_tokenizer_ref(str(value)).lower()
    return (
        normalized == _normalize_tokenizer_ref(NEMOTRON_SUPER_TOKENIZER_DEFAULT).lower()
        or "nvidia-nemotron-3-super" in normalized
        or "nemotron-3-super" in normalized
    )


def _is_qwen_profile(value: str | None) -> bool:
    return bool(value) and str(value).strip().lower().startswith(QWEN_TRAINING_PROFILE)


def _metadata_declares_qwen(metadata: Mapping[str, Any]) -> bool:
    tokenizer_uri = _metadata_value(metadata, "tokenizer_uri")
    if isinstance(tokenizer_uri, str) and _is_qwen_ref(tokenizer_uri):
        return True

    profile = _metadata_value(metadata, "model_profile") or _metadata_value(metadata, "training_profile")
    if isinstance(profile, str) and _is_qwen_profile(profile):
        return True

    if _metadata_container(metadata, "qwen_chat_contract") is not None:
        return True

    chat_template = _metadata_value(metadata, "chat_template")
    chat_template_kwargs = _metadata_value(metadata, "chat_template_kwargs")
    if chat_template == QWEN_SFT_CHAT_TEMPLATE and isinstance(chat_template_kwargs, Mapping):
        return all(
            chat_template_kwargs.get(key) is expected
            for key, expected in QWEN_SFT_CHAT_TEMPLATE_KWARGS.items()
        )

    return False


def validate_qwen_packed_sft_chat_contract(
    packed_sft_dir: str | Path,
    *,
    tokenizer_model: str | None = None,
) -> Path:
    """Validate packed SFT metadata matches the Qwen training contract.

    Returns the metadata path on success. Raises ValueError/FileNotFoundError
    with operator-facing remediation text on mismatch.
    """

    metadata_path, metadata = load_packed_sft_metadata(packed_sft_dir)

    chat_template = _metadata_value(metadata, "chat_template")
    if chat_template != QWEN_SFT_CHAT_TEMPLATE:
        raise ValueError(
            "Qwen SFT packed data must be rendered with chat_template=tokenizer; "
            f"{metadata_path} has chat_template={chat_template!r}. Regenerate data prep with "
            "chat_template=tokenizer chat_template_kwargs.enable_thinking=false "
            "chat_template_kwargs.truncate_history_thinking=false."
        )

    chat_template_kwargs = _metadata_value(metadata, "chat_template_kwargs")
    if not isinstance(chat_template_kwargs, Mapping):
        raise ValueError(
            f"{metadata_path} is missing chat_template_kwargs. Regenerate Qwen SFT packed data with "
            "chat_template_kwargs.enable_thinking=false and "
            "chat_template_kwargs.truncate_history_thinking=false."
        )
    for key, expected in QWEN_SFT_CHAT_TEMPLATE_KWARGS.items():
        if chat_template_kwargs.get(key) is not expected:
            raise ValueError(
                "Qwen SFT packed data must disable thinking in the chat template; "
                f"{metadata_path} has chat_template_kwargs.{key}={chat_template_kwargs.get(key)!r}, "
                f"expected {expected!r}."
            )

    tokenizer_uri = _metadata_value(metadata, "tokenizer_uri")
    if tokenizer_model and (
        not isinstance(tokenizer_uri, str) or not tokenizer_uri.strip()
    ):
        raise ValueError(
            "Qwen SFT packed data must record tokenizer_uri when a training "
            f"tokenizer_model is supplied; {metadata_path} is missing tokenizer_uri."
        )
    if tokenizer_uri is not None:
        if not isinstance(tokenizer_uri, str) or not tokenizer_uri.strip():
            raise ValueError(
                "Qwen SFT packed data tokenizer_uri must be a non-empty Qwen "
                f"tokenizer/model; {metadata_path} has tokenizer_uri={tokenizer_uri!r}."
            )
        if not _is_qwen_ref(tokenizer_uri):
            raise ValueError(
                "Qwen SFT packed data tokenizer_uri must point at a Qwen "
                f"tokenizer/model; {metadata_path} has tokenizer_uri={tokenizer_uri!r}."
            )
        if tokenizer_model and _normalize_tokenizer_ref(
            tokenizer_uri
        ) != _normalize_tokenizer_ref(tokenizer_model):
            raise ValueError(
                "Qwen SFT tokenizer mismatch between packed data and training config: "
                f"{metadata_path} tokenizer_uri={tokenizer_uri!r}, "
                f"training tokenizer_model={tokenizer_model!r}."
            )

    return metadata_path


def validate_qwen_training_pipeline_contract(
    packed_sft_dir: str | Path,
    *,
    tokenizer_model: str | None,
    training_profile: str | None = None,
    model_ref: str | None = None,
    train_entrypoint: str | Path | None = None,
    recipe_target: str | None = None,
) -> Path | None:
    """Validate a resolved training launch cannot mix Qwen and Nemotron defaults.

    This is an offline preflight: it inspects packed-data metadata plus the
    resolved launch/profile fields and raises before Megatron starts if Qwen
    packed data would be trained with the generic Nemotron profile, tokenizer,
    or recipe defaults. Non-Qwen metadata returns ``None`` without gating the
    legacy Nemotron path.
    """

    entrypoint_text = str(train_entrypoint or "")
    recipe_text = str(recipe_target or "")
    profile_is_qwen = _is_qwen_profile(training_profile)
    entrypoint_is_qwen = _is_qwen_ref(entrypoint_text)
    recipe_is_qwen = _is_qwen_ref(recipe_text)
    tokenizer_is_qwen = _is_qwen_ref(tokenizer_model)
    model_is_qwen = _is_qwen_ref(model_ref)
    explicit_qwen_target = any(
        (
            profile_is_qwen,
            entrypoint_is_qwen,
            recipe_is_qwen,
            tokenizer_is_qwen,
            model_is_qwen,
        )
    )
    metadata_path = find_packed_sft_metadata_path(packed_sft_dir)
    if metadata_path is None:
        if explicit_qwen_target:
            load_packed_sft_metadata(packed_sft_dir)
        return None
    metadata_path, metadata = load_packed_sft_metadata(packed_sft_dir)

    packed_is_qwen = _metadata_declares_qwen(metadata)
    qwen_target = packed_is_qwen or explicit_qwen_target
    if not qwen_target:
        return None

    if not profile_is_qwen:
        raise ValueError(
            "Qwen target training requires training_contract.model_profile=qwen "
            "(or SUPER3_M1_TRAINING_PROFILE=qwen). "
            f"{metadata_path} looks Qwen-like but launch profile is {training_profile!r}."
        )

    if not (entrypoint_is_qwen or recipe_is_qwen):
        raise ValueError(
            "Qwen training profile requires a Qwen train entrypoint or Qwen recipe target. "
            f"Got train_entrypoint={entrypoint_text!r}, recipe._target_={recipe_text!r}. "
            "Use qwen_local_train.py / qwen3_30b_a3b_local_train.py or set an explicit Qwen recipe."
        )

    if not tokenizer_model:
        raise ValueError(
            "Qwen training profile requires tokenizer.tokenizer_model to resolve to the Qwen HF model. "
            "Set SUPER3_M1_TOKENIZER_MODEL to the same Qwen path used for data packing."
        )
    if _is_nemotron_super_ref(tokenizer_model) or not tokenizer_is_qwen:
        raise ValueError(
            "Qwen training profile cannot use the Nemotron tokenizer default. "
            f"Resolved tokenizer.tokenizer_model={tokenizer_model!r}; set it to the Qwen HF model."
        )

    if model_ref and not model_is_qwen:
        raise ValueError(
            "Qwen training profile model_ref must point at a Qwen HF model. "
            f"Got model_ref={model_ref!r}."
        )

    return validate_qwen_packed_sft_chat_contract(
        packed_sft_dir,
        tokenizer_model=tokenizer_model,
    )


__all__ = [
    "LEGACY_AGENTIC_PACKED_SFT_DIR",
    "NEMOTRON_SUPER_TOKENIZER_DEFAULT",
    "QWEN_AGENTIC_PACKED_SFT_DIR",
    "QWEN_DATA_PREP_CONFIG_NAME",
    "QWEN_DATA_PREP_TARGET_FAMILY",
    "QWEN_SFT_CHAT_TEMPLATE",
    "QWEN_SFT_CHAT_TEMPLATE_KWARGS",
    "QWEN_TRAINING_PROFILE",
    "SUPER3_M1_AGENTIC_PACKED_DIR_ENV_VAR",
    "find_packed_sft_metadata_path",
    "load_packed_sft_metadata",
    "qwen_local_packed_sft_dir_default",
    "validate_qwen_data_prep_config",
    "validate_qwen_packed_sft_chat_contract",
    "validate_qwen_training_pipeline_contract",
]
