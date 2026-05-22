# task033_env_scheduler - Task Knowledge

<!-- METADATA:SESSION=2 -->

> Keep only durable cross-session facts that are not obvious from a quick diff.

---

## Knowledge Entries

1. Session 1 intentionally models scheduling over local Python records only;
   production Ray/NeMo/vLLM/NeMo-Gym/Kubernetes integration remains separate.
2. Queue classification defaults to routing env ids containing `swe`, `browser`,
   or `gui` to the slow queue unless a per-env quota explicitly overrides the
   queue.
3. Backpressure is evaluated from explicit flags, in-flight quota exhaustion,
   pending quota exhaustion, recent rollout failures, and optional latency
   thresholds.

---
