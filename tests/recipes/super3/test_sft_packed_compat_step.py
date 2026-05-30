from __future__ import annotations

import inspect
import sys
import types
from collections.abc import Callable
from functools import partial
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


def _install_stub_gpt_step(forward_step: Callable[..., Any]) -> None:
    for parent in ("megatron", "megatron.bridge", "megatron.bridge.training"):
        sys.modules.setdefault(parent, types.ModuleType(parent))

    gpt_step = types.ModuleType("megatron.bridge.training.gpt_step")
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


def _two_arg_upstream(data_iterator: Any, model: Any) -> tuple[Any, Any]:
    del data_iterator
    output = model(tokens="batch", packed_seq_params={"packed": True})
    return output, lambda output_tensor: output_tensor


def test_packed_compat_step_signature_requests_bridge_state_injection() -> None:
    """Bridge injects GlobalState when the first parameter is named ``state``.

    This keeps the runtime schedule call ``partial(forward_step, state)(
    data_iterator, model)`` on the state-aware upstream gpt_step path.
    """
    signature = inspect.signature(packed_compat_step.forward_step)

    assert list(signature.parameters) == [
        "state",
        "data_iterator",
        "model",
        "return_schedule_plan",
    ]
    assert signature.parameters["model"].default is None
    assert signature.parameters["return_schedule_plan"].default is False


def test_packed_compat_step_keeps_existing_two_arg_stub_behavior() -> None:
    leaf = _MambaLikeLeaf()
    model = _ForwardingWrapper(_ForwardingWrapper(leaf))
    assert not packed_compat_step._model_forward_accepts_kwarg(model)

    _install_stub_gpt_step(_two_arg_upstream)
    try:
        output, _loss = packed_compat_step.forward_step(iter(()), model)
    finally:
        _remove_stub_gpt_step()

    assert output == ("batch", None)
    assert leaf.calls == [{"tokens": "batch", "position_ids": None}]


def test_packed_compat_step_bridge_partial_drops_packed_seq_params_for_mamba_like_leaf() -> None:
    upstream_calls: list[dict[str, Any]] = []

    def state_aware_upstream(
        state: Any,
        data_iterator: Any,
        model: Any,
        return_schedule_plan: bool = False,
    ) -> tuple[Any, Any]:
        upstream_calls.append(
            {
                "state": state,
                "data_iterator": data_iterator,
                "return_schedule_plan": return_schedule_plan,
            }
        )
        output = model(tokens="batch", packed_seq_params={"packed": True})
        return output, lambda output_tensor: output_tensor

    leaf = _MambaLikeLeaf()
    model = _ForwardingWrapper(_ForwardingWrapper(leaf))
    data_iterator = iter(())

    _install_stub_gpt_step(state_aware_upstream)
    try:
        bridge_injected_step = partial(packed_compat_step.forward_step, "state")
        output, _loss = bridge_injected_step(data_iterator, model)
    finally:
        _remove_stub_gpt_step()

    assert output == ("batch", None)
    assert leaf.calls == [{"tokens": "batch", "position_ids": None}]
    assert upstream_calls == [
        {"state": "state", "data_iterator": data_iterator, "return_schedule_plan": False}
    ]


def test_packed_compat_step_bridge_partial_preserves_packed_seq_params_for_supported_leaf() -> None:
    upstream_calls: list[dict[str, Any]] = []

    def state_aware_upstream(
        state: Any,
        data_iterator: Any,
        model: Any,
        return_schedule_plan: bool = False,
    ) -> tuple[Any, Any]:
        upstream_calls.append(
            {
                "state": state,
                "data_iterator": data_iterator,
                "return_schedule_plan": return_schedule_plan,
            }
        )
        output = model(tokens="batch", packed_seq_params={"packed": True})
        return output, lambda output_tensor: output_tensor

    leaf = _PackedAwareLeaf()
    model = _ForwardingWrapper(_ForwardingWrapper(leaf))
    assert packed_compat_step._model_forward_accepts_kwarg(model)
    data_iterator = iter(())

    _install_stub_gpt_step(state_aware_upstream)
    try:
        bridge_injected_step = partial(
            packed_compat_step.forward_step,
            "state",
            return_schedule_plan=True,
        )
        output, _loss = bridge_injected_step(data_iterator, model)
    finally:
        _remove_stub_gpt_step()

    assert output == ("batch", {"packed": True})
    assert leaf.calls == [{"tokens": "batch", "packed_seq_params": {"packed": True}}]
    assert upstream_calls == [
        {"state": "state", "data_iterator": data_iterator, "return_schedule_plan": True}
    ]
