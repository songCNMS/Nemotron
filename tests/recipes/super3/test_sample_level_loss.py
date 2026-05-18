"""Tests for the plan §5.1 sample-level SFT loss helpers (task013 Session 1).

Pure-torch math; runs in CPU sandbox. The Megatron-Bridge wiring lives
in ``sample_level_step.py`` and is cluster-verified in Session 2.
"""

from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from nemotron.recipes.super3.stage1_sft.sample_level_loss import (  # noqa: E402
    compute_sample_level_loss,
    compute_token_level_loss,
    loss_aggregations_diverge,
)


def test_equal_length_batch_token_and_sample_match() -> None:
    """When every sample has the same number of unmasked tokens, the
    two aggregations produce the same scalar — this is the boundary
    case where plan §5.1's reweighting is a no-op."""
    loss_per_token = torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    loss_mask = torch.ones_like(loss_per_token)

    token = compute_token_level_loss(loss_per_token, loss_mask)
    sample = compute_sample_level_loss(loss_per_token, loss_mask)

    assert torch.allclose(token, torch.tensor(3.5))
    assert torch.allclose(sample, torch.tensor(3.5))
    assert not loss_aggregations_diverge(loss_per_token, loss_mask)


def test_uneven_length_batch_diverges_in_expected_direction() -> None:
    """Uneven-length batches: token-level weights a long sample more,
    sample-level weights both samples equally. Pin a concrete numeric
    example so the math is obvious — sample 0 has 3 tokens (mean 2.0),
    sample 1 has 1 token (mean 10.0). Sample-level mean = 6.0;
    token-level mean = (1+2+3+10)/4 = 4.0."""
    loss_per_token = torch.tensor([[1.0, 2.0, 3.0], [10.0, 0.0, 0.0]])
    loss_mask = torch.tensor([[1.0, 1.0, 1.0], [1.0, 0.0, 0.0]])

    token = compute_token_level_loss(loss_per_token, loss_mask)
    sample = compute_sample_level_loss(loss_per_token, loss_mask)

    assert torch.allclose(token, torch.tensor(4.0))
    assert torch.allclose(sample, torch.tensor(6.0))
    assert loss_aggregations_diverge(loss_per_token, loss_mask)


def test_fully_masked_row_does_not_pull_sample_level_toward_zero() -> None:
    """A row that's entirely padded contributes nothing — sample-level
    averages over the *non-empty* samples. This is the property that
    matters when a packed batch's last slot is fully padding."""
    loss_per_token = torch.tensor([[2.0, 4.0], [0.0, 0.0]])
    loss_mask = torch.tensor([[1.0, 1.0], [0.0, 0.0]])

    sample = compute_sample_level_loss(loss_per_token, loss_mask)

    assert torch.allclose(sample, torch.tensor(3.0))


def test_all_masked_batch_returns_zero_not_nan() -> None:
    """Operational sentinel: a fully-padded batch must not yield NaN —
    nan loss propagates into the optimizer and kills the run. Both
    aggregations return zero here."""
    loss_per_token = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
    loss_mask = torch.zeros_like(loss_per_token)

    token = compute_token_level_loss(loss_per_token, loss_mask)
    sample = compute_sample_level_loss(loss_per_token, loss_mask)

    assert torch.allclose(token, torch.tensor(0.0))
    assert torch.allclose(sample, torch.tensor(0.0))
    assert not torch.isnan(token)
    assert not torch.isnan(sample)


def test_sample_level_rejects_non_2d_inputs() -> None:
    """Catches calls that flatten before reaching the helper — those
    must be reshaped by the adapter, not handed straight to the math."""
    flat_loss = torch.tensor([1.0, 2.0, 3.0])
    flat_mask = torch.tensor([1.0, 1.0, 1.0])
    with pytest.raises(ValueError, match="2D"):
        compute_sample_level_loss(flat_loss, flat_mask)


def test_sample_level_rejects_mismatched_shapes() -> None:
    bad_loss = torch.zeros(2, 3)
    bad_mask = torch.zeros(2, 4)
    with pytest.raises(ValueError, match="share shape"):
        compute_sample_level_loss(bad_loss, bad_mask)


def test_sample_level_preserves_dtype_to_float32() -> None:
    """Stage A often runs in bf16; loss aggregation must promote to
    float32 to avoid overflow on long sequences."""
    loss_per_token = torch.tensor([[1.0, 2.0], [3.0, 4.0]], dtype=torch.bfloat16)
    loss_mask = torch.tensor([[1, 1], [1, 1]], dtype=torch.int64)

    out = compute_sample_level_loss(loss_per_token, loss_mask)
    assert out.dtype == torch.float32
