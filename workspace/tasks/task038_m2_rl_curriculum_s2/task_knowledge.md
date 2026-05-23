# task038_m2_rl_curriculum_s2 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

- Session 2 landed `RewardCalibrationSummary` and `CalibratedReward` for per-env/per-checkpoint reward calibration over local rollout traces.
- Zero-variance summaries return z-score `0.0` and normalized reward `0.5`; missing summaries return z-score `0.0` and normalized reward `0.0`.
- Session 3 starts from the merged Session 2 API and preserves S1/S2 regression tests while adding judge ensemble dispatch.
