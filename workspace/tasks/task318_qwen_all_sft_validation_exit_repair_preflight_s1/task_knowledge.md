# task318_qwen_all_sft_validation_exit_repair_preflight_s1 - Task Knowledge

<!-- METADATA:SESSION=78 -->

## Knowledge Entries

1. Task310 train loop reached iter 35/35, but validation hung and `train_rc=1`.
2. Task313 approved task310 checkpoint only for load/canary handoff, not clean
   training success.
3. A future 30B run must have explicit validation/exit/rc/checkpoint teardown
   behavior before optimizer launch.
4. This task does not authorize training or eval.
