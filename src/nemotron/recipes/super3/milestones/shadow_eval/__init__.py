"""Sandbox shadow-eval pipeline scaffold for Super3 M2."""

from .pipeline import (
    CanaryPolicy,
    DEFAULT_SHADOW_EVAL_BLOCKERS,
    ShadowEvalExample,
    ShadowEvalPlan,
    ShadowEvalReport,
    ShadowTaskResult,
    build_synthetic_shadow_plan,
    evaluate_shadow_plan,
    format_shadow_eval_report,
    tune_canary_policy,
)

__all__ = [
    "CanaryPolicy",
    "DEFAULT_SHADOW_EVAL_BLOCKERS",
    "ShadowEvalExample",
    "ShadowEvalPlan",
    "ShadowEvalReport",
    "ShadowTaskResult",
    "build_synthetic_shadow_plan",
    "evaluate_shadow_plan",
    "format_shadow_eval_report",
    "tune_canary_policy",
]
