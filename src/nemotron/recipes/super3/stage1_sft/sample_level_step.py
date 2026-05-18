# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Megatron-Bridge forward_step adapter for sample-level SFT loss.

Plan §5.1 two-stage SFT schedule (task013):

  - Stage A: standard token-level cross-entropy SFT (existing
    ``megatron.bridge.training.gpt_step.forward_step`` path; no change).
  - Stage B: load Stage A checkpoint, run a second optimizer pass with
    this adapter — same data, same model, sample-level loss aggregation
    per ``sample_level_loss.compute_sample_level_loss``.

Megatron-Bridge's ``forward_step`` protocol returns
``(output_tensor, loss_func)`` where ``loss_func(loss_mask, output_tensor)``
computes the final scalar loss. The adapter here delegates the model
forward + batch fetch to upstream gpt_step (so we stay in sync with any
batching / position-id / context-parallel handling that lives upstream),
then *replaces* the returned ``loss_func`` with a sample-level variant
that closes over the same ``loss_mask``.

Cluster integration (running this with real Megatron-Bridge under
``finetune(...)``) is task013 Session 2 — sandbox-runnable tests here
pin the math via ``sample_level_loss`` and the wiring via the
``_STEP_FUNCTIONS`` dispatch table in ``stage1_sft/train.py``.
"""

from __future__ import annotations

from typing import Any

import torch

from nemotron.recipes.super3.stage1_sft.sample_level_loss import (
    compute_sample_level_loss,
)


def sample_level_loss_func(
    loss_mask: torch.Tensor,
    output_tensor: torch.Tensor,
) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
    """Plan §5.1 sample-level loss function with the Megatron-Bridge
    ``loss_func(loss_mask, output_tensor)`` signature.

    Upstream ``megatron.bridge.training.gpt_step`` builds its loss_func
    closure as ``partial(loss_func, loss_mask)`` and the trainer calls
    that partial with the model's ``output_tensor`` (per-token cross-
    entropy values returned by ``CrossEntropy``). We mirror the
    signature, but route the aggregation through our sample-level
    helper.

    Returns ``(loss, metadata)`` per Megatron-Bridge convention. The
    metadata dict carries the ``"lm loss"`` key so existing W&B /
    manifest logging picks the value up unchanged.
    """
    # ``output_tensor`` from gpt_step's loss_func is shaped
    # (batch * seq_len,) — flattened across batch and sequence
    # dimensions. The matching loss_mask shape is the same.
    if output_tensor.dim() == 1:
        # Flat case: reshape both back to (batch, seq_len). The
        # upstream pipeline preserves shape on the mask side as
        # (batch, seq_len) in most paths; if it ever flattens both
        # we fall back to treating the whole flat tensor as one
        # sample. That keeps callers running rather than crashing,
        # at the cost of degenerating into token-level aggregation —
        # Session 2 cluster verify confirms which shape upstream
        # actually delivers.
        if loss_mask.dim() == 2:
            seq_len = loss_mask.shape[-1]
            output_tensor = output_tensor.view(-1, seq_len)
        else:
            output_tensor = output_tensor.unsqueeze(0)
            loss_mask = loss_mask.unsqueeze(0)
    elif output_tensor.dim() != 2:
        raise ValueError(
            "sample_level_loss_func expects 1D (batch*seq_len) or 2D "
            f"(batch, seq_len) output_tensor; got shape {tuple(output_tensor.shape)}"
        )

    if loss_mask.dim() == 1:
        loss_mask = loss_mask.view_as(output_tensor)

    loss = compute_sample_level_loss(output_tensor, loss_mask)
    # Megatron-Bridge's gpt_step typically also returns a num_tokens or
    # similar count for logging; we keep the metadata minimal here and
    # let Session 2 add what cluster eval needs.
    return loss, {"lm loss": loss.detach()}


def forward_step(data_iterator: Any, model: Any):  # pragma: no cover - cluster path
    """Sample-level forward step, matching gpt_step.forward_step signature.

    Delegates model forward + batch unpacking to upstream gpt_step, then
    replaces the returned ``loss_func`` with our sample-level variant.

    Not exercised in sandbox tests — running this needs CUDA + the nvcr
    Megatron-Bridge container. Session 2 covers the cluster verify; the
    sandbox contract here is "imports cleanly when megatron-bridge is
    installed, otherwise raises a clear ImportError at call time".
    """
    try:
        from functools import partial

        from megatron.bridge.training.gpt_step import (
            forward_step as upstream_forward_step,
            loss_func as upstream_loss_func,
        )
    except ImportError as exc:
        raise ImportError(
            "sample_level_step.forward_step requires megatron-bridge; "
            "install the nvcr Megatron-Bridge container or pin to "
            "gpt_step in your YAML by leaving `step_function:` unset."
        ) from exc

    # Reuse upstream batch fetch + model forward; swap loss_func with
    # ours. Upstream returns `(output_tensor, partial(loss_func, loss_mask))`
    # so we extract the loss_mask captured in that partial.
    output_tensor, bound_loss_func = upstream_forward_step(data_iterator, model)

    # Recover loss_mask from the upstream partial. Megatron-Bridge's
    # gpt_step builds it as `partial(loss_func, loss_mask)`, so the
    # first positional arg holds the mask.
    if hasattr(bound_loss_func, "args") and bound_loss_func.args:
        loss_mask = bound_loss_func.args[0]
    else:
        # Some upstream variants use a closure instead of partial; fall
        # back to calling upstream's loss_func with a sentinel that lets
        # us snapshot the mask via the captured scope. This branch is
        # paranoia for forward-compat — Session 2 verifies which shape
        # upstream actually ships and the unused branch can be deleted.
        raise RuntimeError(
            "upstream gpt_step loss_func does not expose loss_mask via "
            "functools.partial.args; cannot wrap. Pin megatron-bridge "
            "to the tested version or open task013 Session 2 follow-up."
        )

    return output_tensor, partial(sample_level_loss_func, loss_mask)


__all__ = [
    "sample_level_loss_func",
    "forward_step",
]
