# task028_m2_long_context_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

> Keep only durable cross-session facts that are not obvious from a quick diff.

---

## Knowledge Entries

1. Session 1 uses a 128K-character sandbox cap; this is not the production
   512K / 1M context path.
2. `long_context_qa` is span-aware only over provided synthetic evidence spans;
   source-specific benchmark parsing is deferred until source pins are approved.
3. Data-registry rows for RULER, AA-LCR, and long-doc QA remain deferred.

---
