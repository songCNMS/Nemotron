# task221 History Log

## 2026-05-30

- Created evidence-only branch `intern_nem_dev_3/task221_qwen_eval_full_benchmark_prepare_s1` from `origin/main` at `1d037329f5a02cdc04f2a09a16e7342721be4c87`.
- Reused task210 Session 4 evidence showing staged model copy PASS, SGLang smoke PASS with required Qwen chat template kwargs, direct corrected math smoke 2/2 PASS, cleanup PASS, and full benchmark held.
- Ran focused CPU/static validator shard: 136 passed, 8 warnings.
- Verified local stable model visibility and NemTron staged model visibility without starting endpoint or querying/using GPU compute.
- Prepared held SGLang, sanitized smoke, corrected math smoke, M1 launcher-available, and M1 full-basket command artifacts under `/mnt/cephfs/data/processing/nemotron-live-validation/task221/commands`.
- Generated static M1/M2 target inventory and full 27-target run plan under `/mnt/cephfs/data/processing/nemotron-live-validation/task221`.
- Recorded readiness as PASS/HOLD pending PM release after task220.
