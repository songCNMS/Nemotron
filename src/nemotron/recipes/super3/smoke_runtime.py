"""Runtime compatibility helpers for single-GPU smoke tests."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def patch_dataset_helper_compile_if_prebuilt() -> None:
    """Skip Megatron's helper rebuild when a wheel already ships the extension.

    Some Megatron-Core wheels include ``helpers_cpp`` but not the Makefile used
    by the runtime rebuild path. Smoke tests can safely use the packaged
    extension and avoid failing before the first training step.
    """
    try:
        import megatron.core.datasets.helpers_cpp  # noqa: F401
        import megatron.core.datasets.utils as dataset_utils
        import megatron.bridge.training.initialize as bridge_initialize
    except Exception as exc:
        # P3 #18: surface the no-op so a missing helpers_cpp + missing Makefile
        # combo at least leaves a breadcrumb instead of crashing later with
        # "Makefile not found" during initialize().
        logger.warning(
            "Skipping dataset-helper compile patch: %s. If a later training "
            "step fails with a missing Makefile, the prebuilt helpers_cpp is "
            "also unavailable in this environment.",
            exc,
        )
        return

    def _compile_helpers_noop() -> None:
        logger.info("Using prebuilt Megatron dataset helper extension")

    dataset_utils.compile_helpers = _compile_helpers_noop
    bridge_initialize.compile_helpers = _compile_helpers_noop
