# task037_env_health_dashboard_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

> Keep only durable cross-session facts that are not obvious from a quick diff.

---

## Knowledge Entries

1. The dashboard scaffold treats `health_baseline_report.json` as the recorded
   contract: `health.environments` supplies split health, and
   `baselines.environments[*].aggregate[*]` supplies reward metrics,
   telemetry summaries, declared telemetry, and `telemetry_gap`.
2. `*_ms` numeric telemetry is surfaced in the latency panel; the default slow
   signal threshold is 1000 ms and is configurable in the local CLI.
3. Runtime/deferred signals are inferred from declared or emitted telemetry
   names containing runtime-related terms, telemetry gaps for those names,
   slow latency rows, and skipped baseline rows.

---
