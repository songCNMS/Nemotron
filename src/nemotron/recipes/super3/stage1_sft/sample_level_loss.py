# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Sample-level SFT loss aggregation (plan §5.1, task013 Session 1).

Plan §5.1 calls for a two-stage SFT loss schedule: ``先 token-level，再
sample-level``. Today the SFT path (``stage1_sft/train.py``) calls
``megatron.bridge.training.gpt_step.forward_step`` directly, which
aggregates cross-entropy over *all* unmasked tokens — long assistant
turns dominate the gradient. The sample-level helper here averages
cross-entropy within each sequence first, then averages across the
batch, so every sample contributes equally regardless of length.

Pure CPU torch implementation: integration with Megatron-Bridge's
``forward_step`` protocol lives in ``sample_level_step.py`` and is
gated on the upstream import landing on a real cluster. The math here
is what the unit tests pin down; Session 2 wires it into the training
loop.
"""

from __future__ import annotations

import torch


def compute_token_level_loss(
    loss_per_token: torch.Tensor,
    loss_mask: torch.Tensor,
) -> torch.Tensor:
    """Standard token-level SFT loss aggregation.

    Equivalent to ``megatron.bridge.training.gpt_step``'s default loss
    aggregation: sum of unmasked token losses divided by total unmasked
    token count. Long sequences dominate proportionally. Included here
    so the tests can compare token-level vs sample-level on the same
    synthetic inputs.

    Args:
        loss_per_token: per-token loss values, shape ``(batch, seq_len)``
            (or broadcastable to it).
        loss_mask: 0/1 (or float) mask of which tokens count toward the
            loss, same shape as ``loss_per_token``.

    Returns:
        Scalar tensor. Returns ``0.0`` (and not NaN) when no token is
        unmasked across the entire batch — matches the operational
        sentinel callers expect when a batch is fully padded.
    """
    loss_per_token = loss_per_token.to(torch.float32)
    loss_mask = loss_mask.to(torch.float32)
    masked_sum = (loss_per_token * loss_mask).sum()
    mask_total = loss_mask.sum()
    if mask_total.item() == 0:
        return torch.zeros((), dtype=torch.float32, device=loss_per_token.device)
    return masked_sum / mask_total


def compute_sample_level_loss(
    loss_per_token: torch.Tensor,
    loss_mask: torch.Tensor,
) -> torch.Tensor:
    """Plan §5.1 sample-level SFT loss aggregation.

    Per-sample mean of unmasked token losses, then batch-mean over
    samples that have at least one unmasked token. Samples that are
    fully masked drop out of the average (they contribute 0 and aren't
    counted in the denominator), so a batch with one fully-padded row
    doesn't get a spurious zero pull on the mean.

    Args:
        loss_per_token: per-token loss values, shape ``(batch, seq_len)``.
        loss_mask: 0/1 (or float) mask, same shape.

    Returns:
        Scalar tensor. Returns ``0.0`` when every sample in the batch is
        fully masked (no signal at all). Otherwise the average of the
        per-sample means over the *non-empty* samples.
    """
    if loss_per_token.dim() != 2 or loss_mask.dim() != 2:
        raise ValueError(
            "sample-level loss expects 2D (batch, seq_len) tensors; "
            f"got loss_per_token.shape={tuple(loss_per_token.shape)}, "
            f"loss_mask.shape={tuple(loss_mask.shape)}"
        )
    if loss_per_token.shape != loss_mask.shape:
        raise ValueError(
            "loss_per_token and loss_mask must share shape; "
            f"got {tuple(loss_per_token.shape)} vs {tuple(loss_mask.shape)}"
        )
    loss_per_token = loss_per_token.to(torch.float32)
    loss_mask = loss_mask.to(torch.float32)
    per_sample_sum = (loss_per_token * loss_mask).sum(dim=-1)
    per_sample_mask_count = loss_mask.sum(dim=-1)
    has_signal = per_sample_mask_count > 0
    # Avoid divide-by-zero for fully-masked rows; their contribution is
    # masked out below anyway.
    safe_count = per_sample_mask_count.clamp(min=1.0)
    per_sample_loss = per_sample_sum / safe_count
    nonempty_count = has_signal.to(torch.float32).sum()
    if nonempty_count.item() == 0:
        return torch.zeros((), dtype=torch.float32, device=loss_per_token.device)
    return (per_sample_loss * has_signal.to(torch.float32)).sum() / nonempty_count


def loss_aggregations_diverge(
    loss_per_token: torch.Tensor,
    loss_mask: torch.Tensor,
    *,
    rtol: float = 1e-4,
    atol: float = 1e-6,
) -> bool:
    """Return True when token-level vs sample-level give different scalars
    on the same inputs.

    Useful as a sanity check: equal-length batches with identical mask
    counts per row produce the same scalar under both aggregations;
    uneven-length batches diverge. Tests use this to characterise the
    boundary; production callers do not normally need it.
    """
    a = compute_token_level_loss(loss_per_token, loss_mask)
    b = compute_sample_level_loss(loss_per_token, loss_mask)
    return not torch.allclose(a, b, rtol=rtol, atol=atol)


__all__ = [
    "compute_token_level_loss",
    "compute_sample_level_loss",
    "loss_aggregations_diverge",
]
