# task037_env_health_dashboard_s1

Session 1 scaffold for an offline environment-health dashboard over recorded
M0 health baseline reports.

Scope:
- Consume a local `health_baseline_report.json` artifact.
- Emit panel-ready JSON data and a compact Markdown report.
- Cover per-environment status, reward quality, latency telemetry, telemetry
  gaps, and deferred/runtime signals.
- Keep live Grafana/W&B publication, production telemetry streams, auth, and
  cluster deployment out of scope.

Entrypoint:
- `python -m nemotron.recipes.super3.milestones.m2_env_health_dashboard.dashboard --input-report health_baseline_report.json --output-json dashboard.json --output-markdown dashboard.md`
