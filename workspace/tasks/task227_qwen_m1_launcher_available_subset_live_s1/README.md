# task227_qwen_m1_launcher_available_subset_live_s1

Owner: intern_nem_dev_2
Status: In progress
Base/product commit: `1d037329f5a02cdc04f2a09a16e7342721be4c87`
Branch: `intern_nem_dev_2/task227_qwen_m1_launcher_available_subset_live_s1`

## Scope

Live validation for the PM-released Qwen M1 launcher-available subset only.

- Use task226 release checklist and command shapes as source of truth.
- Use task225-approved official evaluator runtime.
- Launch exactly one task227-owned SGLang endpoint if preflight passes.
- Run sanitized endpoint smoke, official corrected math smoke, and only the 14 M1 launcher-available targets.
- Do not run the five missing-mapping M1 targets or any M2/full 27-target benchmark.

Artifact root: `/mnt/cephfs/data/processing/nemotron-live-validation/task227`
