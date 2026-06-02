# task301_qwen_aime_v11_30b_full_sft_training_s1 - task knowledge

<!-- METADATA:SESSION=3 -->

## Knowledge Entries

1. launch-gate: 30B training must not start until runtime/resource, data/packing,
   and 30B base-score gates are available.
2. output: The checkpoint handoff must be sufficient for task300 canary and
   same-harness corrected AIME2025 testing.
3. boundary: Training success is not promotion and does not authorize endpoint
   or 30B release.
4. Session 1 gate state: task298, task299, and task300 have no visible branch,
   PR, or merged task dir, so task301 must remain fail-closed before launch.
5. Never start task301 30B SFT until task298 PASS, task299 PASS, and task300
   30B base-score artifact are all recorded with exact heads/artifact paths.
6. PR #362 is the task301 acceptance/blocker report PR. Current disposition is
   `BLOCKED_UPSTREAM_GATES_MISSING`; this is expected until upstream gates are
   visible and lead clears the sequence.
7. Session 3 branch visibility: task298 is visible at
   `7d24b9295740ef5c21fd443d6399ec9641f8f5c5`, task299 is visible at
   `ff30fad8e6899b9a98d9530006ef49c52c7d72fb`, and task300 is visible at
   `85a5ba134c486ac36f30b63e9bcae97f51fdc1f6`; their docs are still
   `InProgress` and do not satisfy the task301 launch gates.
