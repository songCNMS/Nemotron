# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""M2 eval basket registry and adapter-config scaffold."""

from nemotron.recipes.super3.milestones.m2_eval_basket.registry import (
    ADAPTER_CONFIG_PATH,
    EXPECTED_M2_BENCHMARK_IDS,
    REGISTRY_PATH,
    adapter_config_by_id,
    benchmarks_by_category,
    format_runtime_blocker_report,
    load_m2_adapter_config,
    load_m2_eval_basket,
    runtime_blockers,
    validate_m2_adapter_config,
    validate_m2_eval_basket,
)

__all__ = [
    "ADAPTER_CONFIG_PATH",
    "EXPECTED_M2_BENCHMARK_IDS",
    "REGISTRY_PATH",
    "adapter_config_by_id",
    "benchmarks_by_category",
    "format_runtime_blocker_report",
    "load_m2_adapter_config",
    "load_m2_eval_basket",
    "runtime_blockers",
    "validate_m2_adapter_config",
    "validate_m2_eval_basket",
]
