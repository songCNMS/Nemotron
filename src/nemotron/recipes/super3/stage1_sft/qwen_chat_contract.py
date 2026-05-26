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

QWEN_SFT_CHAT_TEMPLATE = "tokenizer"
QWEN_SFT_CHAT_TEMPLATE_KWARGS: dict[str, bool] = {
    "enable_thinking": False,
    "truncate_history_thinking": False,
}


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
    if tokenizer_model and isinstance(tokenizer_uri, str) and tokenizer_uri:
        if _normalize_tokenizer_ref(tokenizer_uri) != _normalize_tokenizer_ref(tokenizer_model):
            raise ValueError(
                "Qwen SFT tokenizer mismatch between packed data and training config: "
                f"{metadata_path} tokenizer_uri={tokenizer_uri!r}, "
                f"training tokenizer_model={tokenizer_model!r}."
            )

    return metadata_path
