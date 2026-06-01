# task261 task255 data/training root-cause report

<!-- METADATA:STATUS=ReadyForReview,ASSIGNEE=intern_nemotron_worker_1,SESSION=2 -->

## Scope And Branch

- Task: `task261_qwen_aime_v10_task255_data_training_root_cause_s1`.
- Branch: `intern_nemotron_worker_1/task261_qwen_aime_v10_task255_data_training_root_cause_s1`.
- Report content commit: `bddd499ec43d0f5b299c8676723608f422455e87`.
- PR: #333.
- Scope executed: read-only audit of task253 packed Qwen data, task255 Qwen3-4B one-iteration training/export evidence, and task257 downstream same-harness AIME failure summary.
- Boundaries kept: no training, no export, no endpoint launch, no AIME/task243 eval, no code changes, no artifact modification, no AIME2025 train data, no promotion/go-no-go claim, no 30B/8-GPU, no shared deletion.
- Global disposition remains `NO-GO/HOLD`.

## Artifacts Inspected

### task253 packing

- `packed_qwen/blend.json`: `963ad31c2265eaf9f10fdd261eb73705e72b83fbc0fff2b00f49891bfcbb0520`
- `packed_qwen/splits/metadata.json`: `18a83f43bdecaed886bd115945e3b767c99479bf6dafae20be544e21b36afac3`
- `packed_qwen_shard_summary.json`: `03d1e72da96c6c10528f8a218cca3e20b461268daae35b4388d566249705f040`
- `qwen_packing_xenna_unblock_report.md`: `2878ebec6a488638b5c511a402d96ced0871a9ec7ca9b262b1bb901ad9d1ba6a`
- `packed_qwen/runs/3d78398cca4e9946_1780343193/config.json`: `e4d6edbb8fb9d10353c1abdd6162b4ddd4b1e68aae9aeac6569a0f3cd2a5f43f`
- task251 source `agentic_sft_v0_train.jsonl`: `994166eeb83ffb5ebd213db9cc0d6cdd90208251bd2aab9dbb70cec7bf96691a`
- task251 source `agentic_sft_v0_math_hard_verified_full_solution_train.jsonl`: `2039b67b2bcf5cf74b576a640f1f3a198d675e3fbd64a886da4be5753ad515d9`
- task251 `data_blend_agentic_sft_v0.json`: `fdd56cef9f944566a9cd4332ec348ab503258f39a03f94cccd93c70b84b9b338`
- task251 M1 manifest: `3f367930cd9ddbb568f6ff75bebe3aa2b339332b1e56bd2533ce315cfbbf53ba`

### task255 training/export

- `training_manifest.json`: `4437ee9b1a5cc9d8ffcee850da515d3ebb12e837682fea9439cbbf4a3b74e939`
- `run_m1_agentic_sft.sh`: `9b45d806210a7145500845177cc701ba9d039daa6cbec8b82e0b908c6cd99795`
- `training_plan/report.md`: `1a49d3e5c48efb1b505c18265f1e8f103072a2c603e8aad8d5b24183b66b796b`
- `task255_qwen4b_pilot_checkpoint_export_report.md`: `3893af84bfdb4d78c4f31074a8454b2fa2bab2d69cfec71c42a36b75c49e7686`
- failed initial train log: `e1f8f9bbf863aa89adc3a7e4a9a0b1752d3a2e7037ae97e74fec8b0fe8175861`
- successful retry train log: `348812fc87f11dee8a1f22edf5de6e2eafd82dd3c50e10e44e0a048e3063d2e9`
- export log: `7e7e035bd5276252b19423e9b0a2c1a7516f9406a75b046775704b9bee7209ad`
- remote input checksum log: `9fb9b08f4b5fc6d82203f658da92b7221cb7cb14753cc5ca4a2eb4a07776ca19`
- HF export inventory log: `135d1d77374c3c962ede257251a02aaec94c6597e245881c99636f52900daad3`

### task257 downstream eval evidence

- `summary.json`: `ba3dd7b10af3fbafd678df434602b3bee0e829a357025e38e5109cbed7367e6e`
- `results.jsonl`: `e4d4ba6ece47e0dff6693066488ebba7461fd12fb8ad6dc26741bb931030f5e6`
- `command.txt`: `e82f9f50e2aaad46d7aa54334ab422022c2d45444aa13ec13114ad4968bb902d`
- `endpoint_model_manifest.json`: `710bb2db20296762ebb6951db566abfcab90bb406e10ef7b2b548fead06f35d9`
- endpoint log: `1011e6c3b373455ca9b7a9a3a87443139a87e581e7daf6d8c966b38551e949b7`

### Qwen base reference files

- `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507/config.json`: `5beea1a4a34c62782bfb2f911c606741a3bab8f92d80a118fa053c28af12e8ba`
- `tokenizer_config.json`: `a62ff0a2472a0fa1b8eaabcb57c59b58afa42a22831dc141400b6e0cf2b65ce3`
- `model.safetensors.index.json`: `d6c42883a895dfef5b0080ed2116a1bcd764f558406b98923d675978a1abf29c`

## Data And Packing Observations

- task253 metadata uses tokenizer-native Qwen chat template with `enable_thinking=false`, `truncate_history_thinking=false`, tokenizer `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`, `pack_size=8192`, `num_shards=8`, `total_sequences=1093`, and `total_tokens=951216`.
- The packed parquet schema is `input_ids: list<int32>`, `loss_mask: list<uint8>`, `seq_start_id: list<int32>`.
- Exposed `splits/train` has 8 symlink shards, 79 rows, 596944 input tokens, 110945 supervised tokens, and no zero-supervised rows. Loss-mask ratio is `0.185855`.
- Exposed `splits/valid` has 1 symlink shard, 15 rows, 115993 input tokens, 18998 supervised tokens, and no zero-supervised rows. Loss-mask ratio is `0.163786`.
- Actual exposed train composition:
  - M0/general: 76 rows, 593275 tokens, 107538 supervised tokens, 5 symlink shards.
  - hard-math sidecar: 3 rows, 3669 tokens, 3407 supervised tokens, 3 symlink shards.
- The blend train list contains 15 dataset-qualified shard entries: 7 M0/general shards and 8 hard-math sidecar shards. The exposed train split has only 8 basename symlinks:
  - present: M0/general `shard_000000` through `shard_000004`, hard-math `shard_000005` through `shard_000007`.
  - missing from the training path: M0/general `shard_000005` and `shard_000006`, hard-math `shard_000000` through `shard_000004`.
- The missing intended train entries contain 34 packed rows: 29 M0/general rows plus 5 hard-math rows. This is a real packing/split materialization bug or at least a hazardous representation mismatch. It skews training data and suppresses most hard-math sidecar rows.
- Source task251 counts:
  - `agentic_sft_v0_train.jsonl`: 1100 rows, with 100 rows in each of 11 environments.
  - `agentic_sft_v0_math_hard_verified_full_solution_train.jsonl`: 8 rows.
  - `agentic_sft_v0_math_final_answer_train.jsonl`: 200 rows, but it is not a separate dataset in task253 `blend.json`.
  - `agentic_sft_v0_math_heldout_eval.jsonl`: 0 rows.
- Raw source pattern counts:
  - base 1100-row train has 200 `boxed` rows and 400 final-answer-phrase rows.
  - hard-math sidecar has 8 `boxed` rows and 8 final-answer-phrase rows.
  - final-answer-only file has 200 rows, all boxed/final-answer, but was not separately blended.
- Packed supervised-token decode pattern counts for the actual exposed task255 train split:
  - M0/general: 678 supervised sequences, 107538 supervised tokens, 125 boxed cues, 217 final-answer phrase cues, 179 tool-like cues.
  - hard-math: 3 supervised sequences, 3407 supervised tokens, 3 boxed cues, 1 final-answer phrase cue.
  - valid M0/general: 136 supervised sequences, 18998 supervised tokens, 25 boxed cues, 43 final-answer phrase cues, 37 tool-like cues.
- Conclusion: chat template and loss masks look plausible. Data composition is weak and skewed, but it does not by itself explain total AIME parse collapse from base-like behavior to random-looking outputs.

## Training And Export Observations

- task255 training was configured with `train_iters=1`, `global_batch_size=2`, `micro_batch_size=1`, `seq_length=8192`, optimizer LR `5e-6`, `lr_warmup_iters=0`, `lr_decay_iters=1`, `save_interval=1`.
- The generated planner command included `training_contract.*` CLI overrides. The first launch failed before training with Hydra struct error: `Key 'training_contract' is not in struct`.
- The successful retry removed those CLI overrides while retaining env-level Qwen settings:
  - `SUPER3_M1_QWEN_HF_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`
  - `SUPER3_M1_TOKENIZER_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`
  - `SUPER3_M1_PRETRAINED_CHECKPOINT=/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`
  - `SUPER3_M1_TRAINING_PROFILE=qwen`
- Successful retry config log shows:
  - `checkpoint.pretrained_checkpoint: /mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`
  - `checkpoint.load: null`
  - `checkpoint.load_main_params_from_ckpt: false`
  - `checkpoint.exit_on_missing_checkpoint: false`
- The train log does not contain a positive `successfully loaded checkpoint` line. Prior Qwen run docs in this repo treat that line as expected evidence for valid Megatron checkpoint loading, and the previous invalid V9 case with no such line trained at random-init-scale loss.
- Iteration 1 metrics:
  - consumed samples: 2
  - learning rate: `0.000000E+00`
  - train lm loss: `1.238679E+01`
  - grad norm: `98.488`
  - skipped/nan: `0/0`
- Validation at iteration 1:
  - lm loss: `1.165397E+01`
  - PPL: `1.151471E+05`
- These loss/PPL values are random-init scale for this codebase. Valid Qwen SFT runs documented nearby typically report early losses below 1 after confirmed checkpoint load.
- The zero LR at the only logged training step means task255 likely performed no useful weight update even if the model had loaded correctly.
- Export completed mechanically. The export log loaded the task255 checkpoint and reported only `_extra_state` missing-key warnings with `unexpected_keys=[]`, followed by `Success: All tensors from the original checkpoint were written.` This supports that export faithfully wrote the bad checkpoint; it does not prove the checkpoint began from the Qwen base.

## Downstream task257 Evidence

- Same-harness accepted base: `11/30`, parsed `23/30`.
- task255 FT artifact: `0/30`, parsed `0/30`, requests `30/30`.
- FT finish reasons: `length=23`, `stop=7`.
- FT average completion tokens: `7202.433333333333`.
- Result-tail pattern counts over 30 rows: 0 boxed, 0 final-answer phrase, 0 predictions, 0 nonempty boxed-values, 0 contains-expected.
- Response chars were large: min 7427, max 43074, mean 36968.1.
- Endpoint evidence is not the likely root cause: SGLang served the HF export path with model type `Qwen3ForCausalLM`, loaded all 3 safetensor shards, and no serving traceback is visible in the copied endpoint log.
- The downstream symptom is more consistent with corrupted/random or wrong-starting weights than with only answer-format mismatch. A pure format mismatch would more plausibly leave coherent math text with parse failures, not 0 parsed rows plus long nonsensical completions.

## Ranked Likely Root Causes

1. Highest confidence: task255 likely did not initialize from real Qwen3-4B base weights, or the loader accepted the raw HF directory as metadata while training from randomly initialized Megatron weights. Evidence: raw HF directory used as `SUPER3_M1_PRETRAINED_CHECKPOINT`, `checkpoint.load: null`, `load_main_params_from_ckpt: false`, `exit_on_missing_checkpoint: false`, no `successfully loaded checkpoint` line, random-init-scale train/valid loss, and task257 random-looking long outputs. Exact remaining gap: this host cannot inspect the remote runtime venv or remote `/root/task255...` checkpoint tensors, so a tensor-level base-vs-task255 comparison was not performed.
2. High confidence: the one-iteration schedule had zero effective LR at the only step. Evidence: `train_iters=1`, `lr_decay_iters=1`, `lr_warmup_iters=0`, logged LR `0.000000E+00`. This alone would produce a no-op base-like artifact if base load had succeeded, so it is secondary to root cause 1 for the severe degradation.
3. Medium confidence: split materialization basename collisions or equivalent split export bug caused the actual `splits/train` directory to omit 34 intended packed train rows, including 5 of 8 hard-math sidecar rows. This weakens and skews the pilot, but does not explain random-generation collapse by itself.
4. Medium confidence: the data and training volume were far too small for a quality signal. The run consumed only 2 packed train rows. The actual hard-math exposure was 3 rows, and final-answer supervision was incidental inside the general train shard rather than intentionally weighted. This explains no expected improvement, not a base-to-0/30 regression if base weights were preserved.
5. Lower confidence: chat-template mismatch. The available metadata and validation point to the correct Qwen tokenizer-native template with `enable_thinking=false` and `truncate_history_thinking=false`.
6. Lower confidence: loss-mask bug. Loss masks are nonzero, binary, and plausible at aggregate and decoded-supervised-token levels. No zero-supervised rows were found.
7. Lower confidence: serving-side issue. Endpoint loaded the exported HF model as Qwen3 and task257 used the same parser/route shape as accepted base evidence.

## Safest V11 Pilot Recommendation

Do not reuse the task255 checkpoint or HF export for any further decision. Treat it as invalid evidence except as a failure artifact.

Recommended V11 sequence:

1. First produce a Qwen3-4B base-load/export sanity artifact before any SFT. The run must prove base weight load with an explicit `successfully loaded checkpoint ... at iteration 0` line or an equivalent Bridge-approved HF-import proof. If Megatron-Bridge expects a Megatron checkpoint root with `latest_checkpointed_iteration.txt`, do not pass the raw HF directory as `SUPER3_M1_PRETRAINED_CHECKPOINT`.
2. Add an early abort gate: if the first train/valid loss is random-init scale, or no positive checkpoint-load line is present, stop and do not export/evaluate.
3. Fix the LR schedule before training. Do not use `train_iters=1` with `lr_decay_iters=1`. Use enough iterations to consume the intended split at least once and verify the first logged training step has nonzero LR.
4. Fix packed split materialization before training. The exposed split directory must preserve dataset-qualified shard identity or train directly from a blend representation that cannot collide on shard basenames. Add a manifest assertion that exposed train rows/tokens/shards match the intended blend.
5. Rebuild data with intentional math/final-answer weighting. Include all reviewed hard-math sidecar rows, and only include final-answer supervision from decontaminated non-heldout sources. Keep AIME2025 prompts/labels held out.
6. Keep the known-good chat contract fixed: Qwen tokenizer, tokenizer-native chat template, `enable_thinking=false`, `truncate_history_thinking=false`, same model/tokenizer path.
7. After a valid 4B SFT pilot, require same-harness Qwen3-4B base-vs-FT comparison before any promotion claim. No AIME2025 train data, no 30B/8-GPU, and no go/no-go claim should be made from task261.

## Contamination And Boundary Status

- No AIME2025 prompts or labels were found in the inspected task253 trainable data paths. task253 metadata points to task251 M1 train and hard-math sidecar JSONLs, and task251 `agentic_sft_v0_math_heldout_eval.jsonl` has 0 rows.
- AIME2025 appears only in task257 downstream eval evidence, not trainable outputs.
- No train/export/eval/endpoint was launched by task261.
- No shared artifacts were modified by task261.
- Residual risk: direct remote checkpoint tensor inspection and remote Bridge package source inspection were unavailable from this host, so the exact loader mechanism remains an evidence gap. The log/metric/downstream evidence is still sufficient to recommend invalidating task255 and restarting with explicit base-load proof.
