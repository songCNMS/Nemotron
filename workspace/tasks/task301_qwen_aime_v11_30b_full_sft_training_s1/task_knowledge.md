# task301_qwen_aime_v11_30b_full_sft_training_s1 - task knowledge

<!-- METADATA:SESSION=1 -->

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
