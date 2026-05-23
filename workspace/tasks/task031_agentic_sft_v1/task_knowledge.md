# task031_agentic_sft_v1 - Task Knowledge

<!-- METADATA:SESSION=3 -->

> Keep only durable cross-session facts that are not obvious from a quick diff.

---

## Knowledge Entries

1. Session 1 treats Agentic SFT v1 as a local builder/schema contract over
   task032-style rollout records; production trace mining and packed SFT
   generation are later sessions.
2. Failure-repair rows preserve assistant tool-call turns and tool observation
   turns so downstream chat-template masking can keep tool outputs out of the
   assistant loss.
3. Compact reasoning is represented as explicit metadata plus a concise system
   prompt variant, not as a cluster training mode.
4. Session 2 routing prefers explicit local metadata hints such as `harness`,
   `trace_harness`, or `trace_source`; env/tool heuristics are fallbacks for
   synthetic rows only.
5. Session 3 added no new Agentic SFT implementation knowledge; it only
   recorded PR #156 merge closeout before the PM-assigned task039 work.

---
