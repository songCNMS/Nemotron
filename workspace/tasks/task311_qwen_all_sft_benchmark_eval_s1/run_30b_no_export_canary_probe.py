#!/usr/bin/env python3
"""Task311 no-export/no-endpoint 30B non-AIME canary wrapper.

This reuses the accepted task304 in-process MCore canary runner while stamping
artifacts with the task311 task id. The route remains bounded to checkpoint-load
and synthetic non-AIME completion retention.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


TASK_ID = "task311_qwen_all_sft_benchmark_eval_s1"
SOURCE_RUNNER = (
    Path(__file__).resolve().parents[1]
    / "task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1"
    / "run_30b_no_export_canary_probe.py"
)


def load_runner():
    spec = importlib.util.spec_from_file_location("task304_canary_runner", SOURCE_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load source runner: {SOURCE_RUNNER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.TASK_ID = TASK_ID
    return module


if __name__ == "__main__":
    raise SystemExit(load_runner().main())
