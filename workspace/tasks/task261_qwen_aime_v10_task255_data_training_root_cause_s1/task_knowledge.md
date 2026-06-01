# task261_qwen_aime_v10_task255_data_training_root_cause_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. task261 is a read-only data/training root-cause audit after task255 failed
   AIME with FT `0/30` versus base `11/30`.
2. The audit should inspect task253 packed shards, task255 logs/configs, and
   downstream task257 failure evidence.
3. It must not train, rerun eval, alter artifacts, or authorize promotion or
   30B/8-GPU.
4. Any V11 pilot recommendation must preserve AIME2025 as held-out eval and
   require same-harness base-vs-FT comparison.
5. Task261 branch base is current `origin/main`
   `9c6cdb6974e4b2c27378d95e228d0536fb5ada41`, and task docs were imported
   from lead docs branch `c866509`.
6. task253 Qwen packed metadata uses tokenizer-native Qwen chat template with
   `enable_thinking=false`, `truncate_history_thinking=false`, `pack_size=8192`,
   and Qwen3-4B tokenizer path
   `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
7. task253 exposed `splits/train` has 79 rows, 596944 input tokens, 110945
   supervised tokens, and no zero-supervised rows; `splits/valid` has 15 rows,
   115993 input tokens, and 18998 supervised tokens.
8. task253 `blend.json` intended 15 dataset-qualified train shard entries, but
   `splits/train` exposes only 8 basename symlinks, omitting M0/general shards
   5-6 and hard-math shards 0-4 from the actual training path.
9. task255 successful retry used the raw Qwen HF directory as
   `SUPER3_M1_PRETRAINED_CHECKPOINT`, logged `checkpoint.load: null`,
   `load_main_params_from_ckpt: false`, no positive checkpoint-load line, and
   random-init-scale train/valid loss.
10. task255 ran one iteration with `lr_decay_iters=1`; the only logged step had
    `learning rate: 0.000000E+00`, consumed samples `2`, train loss
    `1.238679E+01`, and validation PPL `1.151471E+05`.
11. task257 downstream FT eval produced `0/30`, parsed `0/30`, finish reasons
    `length=23, stop=7`, with no boxed/final-answer/prediction rows in the
    result tails; serving loaded the HF export as Qwen3 without visible
    endpoint error.
12. Safest V11 recommendation: discard task255 as invalid evidence, require
    explicit Qwen base-load proof before SFT/export, fix the one-step zero-LR
    schedule, fix split basename collisions, and keep AIME2025 held out with
    same-harness Qwen3-4B base-vs-FT comparison before any claim.
