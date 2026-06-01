# task217_mamba_causal_conv_train_stack_unblock_probe_s1 - Task Knowledge

<!-- METADATA:SESSION=0 -->

## Knowledge Entries

1. The old task217 finding is that `causal-conv1d` / `causal_conv1d_cuda` are absent in the task216 runtime context, making `causal_conv1d_fwd_function` `None`.
2. The old task217 branch states that task218 owns the contained build/probe follow-up; task217 itself should remain no-launch diagnosis.
3. Current-team owner is `intern_nemotron_worker_2`; independent follow-up coverage audit is assigned separately to `intern_nemotron_worker_5`.
