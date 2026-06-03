# task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1 - 30B corrected AIME FT-vs-base gate

<!-- METADATA:STATUS=Idle,ASSIGNEE=intern_nemotron_worker_3,SESSION=7 -->

## Background

The user authorized attempting the Qwen AIME V11 30B data -> training -> testing
workflow, subject to fail-closed gates. The upstream 30B path has reached the
first corrected AIME2025 FT-vs-base gate:

- task298/#364 accepted runtime/resource/base-load proof for
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- task299/#365 accepted 30B V11 data/packing contract evidence.
- task300/#363 accepted same-harness Qwen3-30B-A3B base AIME2025 score
  `15/30 = 0.5`.
- task301/#362 produced a salvage candidate checkpoint at `iter_0000035` after
  reaching `35/35` train steps with skipped `0`, NaN `0`, and a saved
  checkpoint, but built-in validation hung and the run ended with `train_rc=1`.
- task303/#366 approved the task301 checkpoint only for later non-AIME canary
  consideration.
- task304/#367 passed a bounded synthetic non-AIME checkpoint-load/completion-
  retention canary for `iter_0000035`.
- task305/#368 independently reviewed and accepted task304 as
  `APPROVE_TASK304_NON_AIME_CANARY_PASS_WITH_RESIDUALS`.

task304/task305 are not benchmark evidence. The next gate is a corrected
AIME2025 held-out evaluation comparing the task301 fine-tuned checkpoint against
the accepted 30B base score under the same harness.

## Goal

Run or precisely block the corrected AIME2025 same-harness comparison for the
task301 Qwen3-30B-A3B salvage checkpoint `iter_0000035`.

The comparison passes only if the fine-tuned checkpoint scores at least the
accepted base `15/30 = 0.5` under the same corrected evaluator/protocol.

## Inputs

- Current main after #367:
  `7a93a6cea16e45284a58287b91c0069b7416fa99`.
- Base model/tokenizer:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Accepted 30B base score:
  `15/30 = 0.5`.
- task300 base artifact root:
  `/work-agents/intern_nemotron_worker_3/outputs/task300_qwen_aime_v11_30b_same_harness_testing_s1/run_20260602T152008Z`.
- task301 remote run root:
  `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z`.
- task301 local output root:
  `/work-agents/intern_nemotron_worker_5/outputs/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z`.
- Candidate checkpoint:
  `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/checkpoints/iter_0000035`.
- task304 canary local artifact root:
  `/work-agents/intern_nemotron_worker_3/outputs/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/run_20260602T175458Z`.
- task304 canary remote root:
  `/root/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/run_20260602T175458Z`.
- task304 merged head:
  `1f23d8339c123702eaa9336c1fe2b25afcd6122a`.
- task305 merged head:
  `e0809da85900d9ed96cd8d053d34911fb7bd3080`.

## Scope

- Start from current `origin/main` after #367.
- Create worker branch:
  `intern_nemotron_worker_3/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1`.
- Sync code to `/root` before NemTron execution, per project rule.
- Use Qwen3-30B-A3B-Instruct-2507 and the task301 `iter_0000035` checkpoint
  only.
- Use AIME2025 prompts/labels only as held-out eval/decontam input. Do not
  include any AIME2025 prompt or label in trainable data.
- Prefer the accepted task304 no-export/no-endpoint checkpoint-load route,
  adapted only as needed for corrected AIME generation. If same-harness AIME
  testing cannot proceed without export or endpoint, stop and report the exact
  blocker for lead authorization. Any future export/endpoint would be eval-only
  and never promotion.
- Prove protocol equivalence to task300 before judging the FT checkpoint:
  prompt source/cache, generation settings, parser, answer normalizer,
  denominator, score normalization, and corrected AIME2025 protocol.
- Reuse the accepted task300 base score only if equivalence is proven. If
  equivalence cannot be proven, report `BASE_PROTOCOL_MISMATCH_HOLD` or rerun
  the base within this task's no-training/no-promotion boundaries and explain
  why rerun was necessary.
- Preserve full completions and parser diagnostics for every AIME2025 prompt.

## Boundaries

- Do not train or run optimizer steps.
- Do not use AIME2025 prompts or labels as trainable data.
- Do not reuse task255 artifacts.
- Do not delete existing files under `/mnt/cephfs/data/processing/lei.song`.
- Do not promote, claim production readiness, push main, merge, or self-merge.
- Do not launch a production endpoint.
- Do not export or convert the checkpoint unless the no-export same-harness
  route is impossible; if export/endpoint appears required, stop and report a
  blocker for lead authorization.
- Do not start additional training, a second 30B training run, 30B/8-GPU scale
  beyond this evaluation route, or any task not explicitly assigned here.

## Expected Output

- Worker branch and PR if repo docs/status/report files change.
- Task-owned local output root:
  `/work-agents/intern_nemotron_worker_3/outputs/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/`.
- Remote task-owned run root under `/root`.
- Report:
  `workspace/tasks/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/30b_task301_same_harness_aime_eval_report.md`.
- Official mailbox report with:
  - branch/head/PR or exact blocker;
  - commands/env, source commit, local paths, NemTron paths, GPUs, and
    parallelism;
  - proof of task300 protocol equivalence or exact reason for base rerun/HOLD;
  - prompt/cache/parser/normalizer/denominator evidence;
  - FT full completions, raw results, parser diagnostics, and checksum
    manifests;
  - prompt count, parsed count, correct count, exact-normalized score, stop/
    length distribution, empty/null/final-marker diagnostics, mixed-script and
    degeneration flags;
  - PASS/FAIL/HOLD/BLOCK disposition against accepted base `15/30`;
  - explicit confirmation that no training, AIME train data, task255 reuse,
    shared deletion, promotion, production endpoint, main push, or merge
    occurred.

## Worker Result

- Report:
  `workspace/tasks/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/30b_task301_same_harness_aime_eval_report.md`.
- Local artifacts:
  `/work-agents/intern_nemotron_worker_3/outputs/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/run_20260602T190432Z`.
- Remote artifacts:
  `/root/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/run_20260602T190432Z`.
- Disposition: `FAIL`.
- FT score: `14/30 = 0.4666666666666667`.
- Accepted base comparator: task300 `15/30 = 0.5`.
- Delta: `-1/30`, `-0.033333333333333326`.
- Evidence is complete for the no-export/no-endpoint same-harness route:
  `30/30` results, full completions, and parser diagnostics retained; `17/30`
  parsed; finish reasons `stop=17`, `length=13`.
- Residual: `sampling_exact_parameter_match=false` because task306 used the
  accepted no-export MCore greedy substitute while task300 base used SGLang
  `/v1/chat/completions`.

## Acceptance Criteria

- PASS: task301 `iter_0000035` FT exact-normalized corrected AIME2025 score is
  `>= 15/30` under the same accepted corrected protocol, with complete artifacts
  and no boundary violation. This still does not authorize promotion, endpoint,
  export, or additional 30B training.
- FAIL: FT exact-normalized corrected AIME2025 score is below `15/30` under the
  same accepted corrected protocol.
- HOLD: protocol equivalence, base reuse/rerun, artifacts, parser/normalizer,
  denominator, or completion evidence is incomplete.
- BLOCK: the comparison cannot proceed within boundaries or would require
  forbidden training, task255 reuse, AIME2025 train data, shared deletion,
  unapproved export/endpoint, promotion, direct main push, or merge.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_3`
- Related tasks: task298, task299, task300, task301, task303, task304, task305
- Related PRs: #362, #363, #364, #365, #366, #367, #368
- Next gate: independent review/runbook update will be assigned only after
  task306 returns complete artifacts or a precise blocker.
