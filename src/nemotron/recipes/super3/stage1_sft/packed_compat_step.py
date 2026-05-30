# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Megatron-Bridge GPT step adapter for packed-sequence API drift.

Some Bridge/Megatron-Core builds add ``packed_seq_params`` in the standard
``gpt_step`` path whenever the dataset uses packed sequences, while Mamba model
forward implementations in the same build do not accept that keyword.  This
adapter delegates batch handling and loss construction to upstream
``gpt_step`` but filters the keyword only when the unwrapped model forward
chain does not advertise support for it.
"""

from __future__ import annotations

import inspect
from collections.abc import Iterator
from contextlib import contextmanager
from functools import wraps
from typing import Any

PACKED_SEQ_PARAMS_KWARG = "packed_seq_params"


def _iter_module_chain(model: Any) -> Iterator[Any]:
    """Yield ``model`` followed by common ``.module`` wrappers."""
    current = model
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        yield current
        child = getattr(current, "module", None)
        if child is None or child is current:
            break
        current = child


def _signature_accepts_kwarg(callable_obj: Any, kwarg: str) -> tuple[bool, bool]:
    """Return ``(known, accepts)`` for a callable signature."""
    try:
        signature = inspect.signature(callable_obj)
    except (TypeError, ValueError):
        return False, True

    for parameter in signature.parameters.values():
        if parameter.name == kwarg or parameter.kind == inspect.Parameter.VAR_KEYWORD:
            return True, True
    return True, False


def _model_forward_accepts_kwarg(model: Any, kwarg: str = PACKED_SEQ_PARAMS_KWARG) -> bool:
    """Detect whether the leaf model forward can receive ``kwarg``.

    Megatron wrappers commonly expose ``forward(*inputs, **kwargs)`` and pass
    all keywords through to their wrapped ``.module``.  Treat an explicit
    ``kwarg`` on any wrapper as support, but only treat catch-all ``**kwargs``
    as support on the leaf module after unwrapping common ``.module`` chains.
    If the leaf signature cannot be inspected, preserve upstream behavior.
    """
    chain = list(_iter_module_chain(model))
    if not chain:
        known, accepts = _signature_accepts_kwarg(getattr(model, "__call__", model), kwarg)
        return accepts if known else True

    for module in chain:
        forward = getattr(module, "forward", None)
        if forward is None:
            continue
        try:
            signature = inspect.signature(forward)
        except (TypeError, ValueError):
            continue
        if kwarg in signature.parameters:
            return True

    leaf_forward = getattr(chain[-1], "forward", None)
    if leaf_forward is None:
        known, accepts = _signature_accepts_kwarg(getattr(chain[-1], "__call__", chain[-1]), kwarg)
        return accepts if known else True

    try:
        leaf_signature = inspect.signature(leaf_forward)
    except (TypeError, ValueError):
        return True
    return any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in leaf_signature.parameters.values())


@contextmanager
def _drop_unsupported_packed_seq_params(model: Any) -> Iterator[Any]:
    """Temporarily filter ``packed_seq_params`` when the model cannot accept it."""
    if _model_forward_accepts_kwarg(model):
        yield model
        return

    original_forward = getattr(model, "forward", None)
    if original_forward is None:
        yield _PackedSeqParamsFilteringCallable(model)
        return

    @wraps(original_forward)
    def filtered_forward(*args: Any, **kwargs: Any) -> Any:
        kwargs.pop(PACKED_SEQ_PARAMS_KWARG, None)
        return original_forward(*args, **kwargs)

    setattr(model, "forward", filtered_forward)
    try:
        yield model
    finally:
        setattr(model, "forward", original_forward)


class _PackedSeqParamsFilteringCallable:
    """Callable proxy fallback for non-module model objects."""

    def __init__(self, model: Any) -> None:
        self._model = model

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        kwargs.pop(PACKED_SEQ_PARAMS_KWARG, None)
        return self._model(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._model, name)


def forward_step(data_iterator: Any, model: Any):  # pragma: no cover - cluster path
    """GPT forward step with Mamba packed-sequence keyword compatibility."""
    try:
        from megatron.bridge.training.gpt_step import forward_step as upstream_forward_step
    except ImportError as exc:
        raise ImportError(
            "packed_compat_step.forward_step requires megatron-bridge; "
            "install the nvcr Megatron-Bridge container or choose a different "
            "SFT `step_function`."
        ) from exc

    with _drop_unsupported_packed_seq_params(model) as compat_model:
        return upstream_forward_step(data_iterator, compat_model)


__all__ = [
    "PACKED_SEQ_PARAMS_KWARG",
    "_drop_unsupported_packed_seq_params",
    "_model_forward_accepts_kwarg",
    "forward_step",
]
