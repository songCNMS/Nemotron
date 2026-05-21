"""Recorded environment-health dashboard scaffold for Super3 M2."""

from .dashboard import (
    build_dashboard_model,
    load_health_report,
    render_dashboard_markdown,
)

__all__ = [
    "build_dashboard_model",
    "load_health_report",
    "render_dashboard_markdown",
]
