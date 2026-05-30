# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Forward-step dispatch registry for super3 SFT (task013, plan §5.1).

Standalone helper so the dispatch surface can be unit-tested without
dragging in ``train.py``'s torch / megatron-bridge / omegaconf imports.
``train.py`` re-exports the registry + helpers for production use.

Pattern mirrors ``omni3/stage0_sft/train.py::_STEP_FUNCTIONS``: short
names map to ``module:attr`` import specs, ``_load_forward_step`` does
the lazy resolution. Adding plan §5.1's sample-level second pass just
required wiring a single new row.
"""

from __future__ import annotations

import importlib
from collections.abc import Callable
from typing import Any

# Short-name → ``module:attr`` import spec. New entries land here.
_STEP_FUNCTIONS: dict[str, str] = {
    "gpt_step": "megatron.bridge.training.gpt_step:forward_step",
    "super3_packed_seq_compat_gpt_step": (
        "nemotron.recipes.super3.stage1_sft.packed_compat_step:forward_step"
    ),
    "super3_sample_level_step": (
        "nemotron.recipes.super3.stage1_sft.sample_level_step:forward_step"
    ),
}


def _import_attr(spec: str) -> Any:
    """Import ``module:attr`` (or ``module.attr``) and return the attribute."""
    if ":" in spec:
        module_path, attr = spec.split(":", 1)
    else:
        module_path, _, attr = spec.rpartition(".")
        if not module_path:
            raise ImportError(f"Cannot parse import spec: {spec!r}")
    return getattr(importlib.import_module(module_path), attr)


def _load_forward_step(name: str) -> Callable[..., Any]:
    """Resolve a forward-step function by short name or fully-qualified spec.

    Short names look up ``_STEP_FUNCTIONS``; specs containing ``:`` or
    ``.`` are loaded directly so operators can plug in custom step
    functions without editing this file.
    """
    spec = _STEP_FUNCTIONS.get(name, name)
    try:
        return _import_attr(spec)
    except (ImportError, AttributeError) as e:
        choices = ", ".join(sorted(_STEP_FUNCTIONS))
        raise ValueError(
            f"Unknown step function: {name!r}. "
            f"Choose from {{{choices}}} or pass a 'module:attr' import spec. "
            f"Underlying error: {e}"
        ) from e


__all__ = ["_STEP_FUNCTIONS", "_import_attr", "_load_forward_step"]
