from __future__ import annotations

import sys
import types
from typing import Any

from nemotron.recipes.super3.stage1_sft import packed_compat_step


class _ForwardingWrapper:
    def __init__(self, module: Any) -> None:
        self.module = module

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.forward(*args, **kwargs)

    def forward(self, *args: Any, **kwargs: Any) -> Any:
        return self.module(*args, **kwargs)


class _MambaLikeLeaf:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.forward(*args, **kwargs)

    def forward(self, *, tokens: Any, position_ids: Any | None = None) -> tuple[Any, Any | None]:
        self.calls.append({"tokens": tokens, "position_ids": position_ids})
        return tokens, position_ids


class _PackedAwareLeaf:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.forward(*args, **kwargs)

    def forward(
        self,
        *,
        tokens: Any,
        packed_seq_params: Any | None = None,
    ) -> tuple[Any, Any | None]:
        self.calls.append({"tokens": tokens, "packed_seq_params": packed_seq_params})
        return tokens, packed_seq_params


def _install_stub_gpt_step() -> None:
    for parent in ("megatron", "megatron.bridge", "megatron.bridge.training"):
        sys.modules.setdefault(parent, types.ModuleType(parent))

    gpt_step = types.ModuleType("megatron.bridge.training.gpt_step")

    def forward_step(data_iterator: Any, model: Any) -> tuple[Any, Any]:
        del data_iterator
        output = model(tokens="batch", packed_seq_params={"packed": True})
        return output, lambda output_tensor: output_tensor

    gpt_step.forward_step = forward_step
    sys.modules["megatron.bridge.training.gpt_step"] = gpt_step


def _remove_stub_gpt_step() -> None:
    for module_name in (
        "megatron.bridge.training.gpt_step",
        "megatron.bridge.training",
        "megatron.bridge",
        "megatron",
    ):
        sys.modules.pop(module_name, None)


def test_packed_compat_step_drops_packed_seq_params_for_mamba_like_leaf() -> None:
    leaf = _MambaLikeLeaf()
    model = _ForwardingWrapper(_ForwardingWrapper(leaf))
    assert not packed_compat_step._model_forward_accepts_kwarg(model)

    _install_stub_gpt_step()
    try:
        output, _loss = packed_compat_step.forward_step(iter(()), model)
    finally:
        _remove_stub_gpt_step()

    assert output == ("batch", None)
    assert leaf.calls == [{"tokens": "batch", "position_ids": None}]


def test_packed_compat_step_preserves_packed_seq_params_for_supported_leaf() -> None:
    leaf = _PackedAwareLeaf()
    model = _ForwardingWrapper(_ForwardingWrapper(leaf))
    assert packed_compat_step._model_forward_accepts_kwarg(model)

    _install_stub_gpt_step()
    try:
        output, _loss = packed_compat_step.forward_step(iter(()), model)
    finally:
        _remove_stub_gpt_step()

    assert output == ("batch", {"packed": True})
    assert leaf.calls == [{"tokens": "batch", "packed_seq_params": {"packed": True}}]
