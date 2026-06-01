# task263_qwen_aime_v11_base_load_planner_sanity_s1 - Task Knowledge

<!-- METADATA:SESSION=3 -->

## Knowledge Entries

1. task255 logged `checkpoint.load: null`, `load_main_params_from_ckpt: false`,
   no positive checkpoint-load line, train loss `1.238679E+01`, and valid PPL
   `1.151471E+05`.
2. V11 must prove Qwen3-4B base weight load or Bridge-approved HF import before
   any SFT/export artifact can be accepted.
3. V11 must not use `train_iters=1` with `lr_decay_iters=1`; the first logged
   training step must have nonzero LR.
4. This task cannot authorize AIME eval, promotion, task243 comparison, or
   30B/8-GPU.
5. task263 branch starts from `origin/main`
   `513fefa1f1ace94302b56413769c78fb7224624c`; lead docs were imported from
   `81253415dd3285ce0eb56e69733d210742edcb50`.
6. Local worker host has `torch`, `transformers`, `safetensors`, `pyarrow`, and
   `omegaconf`, but no `megatron`/`megatron.bridge`; Bridge import/load proof
   must be run in a NemTron/NeMo environment or reported as that exact blocker.
7. After refreshing onto `origin/main` `5e839d4`, the task-owned `/root` sync
   and generated Bridge import probe still block at
   `ModuleNotFoundError: No module named 'megatron'`; no Bridge-approved import
   proof or positive checkpoint-load line exists yet.
8. The fail-closed preflight must block before training unless the Bridge import
   command returns rc `0` and logs `IMPORT_DONE` or an equivalent positive
   checkpoint-load proof.
9. The current bounded smoke schedule is plan-only and nonzero-LR:
   `train_iters=2`, `global_batch_size=2`, `optimizer.lr=5e-6`,
   `scheduler.lr_warmup_iters=0`, `scheduler.lr_decay_iters=20`, first logged
   step expected LR `5e-6`; a launch must recompute train iterations from
   actual V11 packed train rows before any training.
