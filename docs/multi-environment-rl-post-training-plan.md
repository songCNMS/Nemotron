# Multi-Environment RL Post-Training Plan

Last updated: 2026-05-15

## Context

This plan is based on the current Nemotron repository structure and the existing Super3/Omni3 post-training recipes.

The repo already provides a reusable post-training spine:

- Super3: SFT -> 3x RLVR -> 2x SWE-RL -> RLHF -> Eval.
- RLVR: multi-environment training with verifiable rewards across math, code, STEM, safety, instruction following, long-context, tool-use, terminal-use, and reasoning-gym style tasks.
- SWE-RL: sandboxed software engineering rollouts, including SWE-pivot and full SWE-bench style isolated execution.
- RLHF: GenRM-based alignment with KL control.
- Infra: NeMo-RL, Ray, vLLM, NeMo-Gym, Megatron backend, W&B/artifact lineage, and nemo-runspec orchestration.
- Omni3: multimodal RL direction with MPO, text GRPO, and vision GRPO data-prep paths; the public recipe currently exposes a subset of upstream multimodal environments.

Primary repo anchors:

- `README.md`: Super3 includes a multi-stage RL pipeline with RLVR, SWE-RL, RLHF, and async GRPO.
- `docs/nemotron/super3/rl/index.md`: Super3 RL is organized as 6 sub-stages.
- `docs/nemotron/super3/rl/rlvr.md`: RLVR covers 21 environments and 37 datasets.
- `docs/nemotron/super3/rl/swe.md`: SWE-RL uses isolated sandboxes and OpenHands-style agent loops.
- `docs/nemotron/super3/evaluate.md`: evaluation covers general, reasoning, agentic, chat/IF, long-context, and multilingual benchmarks.
- `src/nemotron/recipes/omni3/stage1_rl/README.md`: Omni3 RL covers multimodal preference/text/vision flows, with public recipes exposing a subset of upstream environments.

## Assumptions

- The starting checkpoint is at least Super-class after pretraining/SFT. If the base model is substantially weaker, post-training alone is unlikely to close the gap to Qwen3.5-397B-A17B by year end.
- Sufficient GPU capacity is available for Super3-scale RL: hundreds to roughly 1K GPUs for full async GRPO, with separate capacity for slow environments such as SWE/browser/GUI.
- The target quality bar is evaluated on a weighted basket covering reasoning, coding, agentic tool use, software engineering, chat/instruction following, long context, multilingual, and optionally multimodal capabilities.
- Qwen/Qwen3.5-122B-A10B and Qwen/Qwen3.5-397B-A17B are treated as external target baselines. Their exact benchmark basket should be frozen once the team chooses the official comparison protocol.

## Milestones

| Time | Goal | Core Work | Acceptance Criteria |
|---|---|---|---|
| 2026-05-14 to 2026-07-31 | M1: reach Nemotron 3 Super-level performance | Complete data inventory, license/quality tags, difficulty buckets, and deduplication. Reuse Super3 SFT and RL 6-stage flow. Bring up 21-env RLVR, SWE1/SWE2 sandbox, and GenRM RLHF. Build Agentic SFT v0 covering tool calls, terminal use, search, structured outputs, and SWE traces. Run small -> full RLVR -> SWE -> RLHF. | Match or approach Super3 on the repo Super3 eval basket: MMLU-Pro, AIME/HMMT/GPQA, LiveCodeBench, TerminalBench, SWE-Bench, TauBench, IFBench/MultiChallenge, RULER, MMLU-ProX/WMT. Target weighted average within 1-2% of Super3 with no major category regression. |
| 2026-08-01 to 2026-10-16 | M2: match Qwen/Qwen3.5-122B-A10B | Expand to 35-50 environments: browser/search, TauBench domains, BIRD/SQL, TerminalBench v2, SWE multi-harness, multilingual IF/code, long-context, safety, jailbreak, and over-refusal. Agentic SFT v1 adds multi-turn tool traces, self-correction, and failure-repair trajectories. RL uses curriculum, dynamic sampling, and separate fast/slow environment queues. Add reward calibration, judge ensembles, rollout store, and environment health dashboards. | Match Qwen3.5-122B-A10B on the chosen text/agentic/coding basket: MMLU-Pro, GPQA, HLE, LiveCodeBench, SWE-Bench Verified, IFBench, MultiChallenge, AA-LCR/LongBench, TerminalBench, TauBench. Target weighted parity with no single critical category more than 3-5% behind. |
| 2026-10-17 to 2026-12-31 | M3: match Qwen/Qwen3.5-397B-A17B by year end | Expand to 70-100+ environments and million-plus rollout scale. Add GUI/MCP/browser, deep SWE, code security, long-horizon workplace assistant, multilingual agent tasks, and harder long-context tasks. If multimodal is in scope, integrate Omni-style MPO/vision/text RL for OCR, document, chart, video, and ASR environments. Agentic SFT v2 uses M2 successful trajectories, negative repairs, teacher reranking, and GenRM reranking. Run final RL in three waves: high-signal RLVR, slow SWE/browser/GUI, then final GenRM/RLHF. Upgrade infra to 1K GPU-class async GRPO, environment quota scheduler, sandbox pool, shadow eval, and automatic rollback. | Freeze final checkpoint by 2026-12-31. Match Qwen3.5-397B-A17B on the agreed text/agent/coding target basket such as BFCL, TAU2, VITA, DeepPlanning, Tool Decathlon, MCP-Mark, SWE-Bench, and TerminalBench. If multimodal is a hard requirement, also include MMMU/MMMU-Pro, MathVision, OCR, chart, document, and video evaluations. |

## Execution Schedule

| Phase | Dates | Deliverables |
|---|---:|---|
| Foundation | 2026-05-14 to 2026-05-31 | Data catalog, environment catalog, frozen eval basket, artifact/W&B lineage setup, sandbox/SIF preparation, Super3 dry-run and small-run. |
| Agentic SFT v0 | 2026-06-01 to 2026-06-21 | Tool, terminal, search, and SWE trajectory SFT. Unified OpenAI responses/tool schema. Loss masking and reasoning-mode conventions finalized. |
| M1 RL | 2026-06-22 to 2026-07-31 | RLVR1-3, SWE1-2, RLHF, Super3-parity checkpoint, and regression report. |
| M2 Environment Expansion | 2026-08-01 to 2026-08-31 | New environment integrations, failure sample mining, reward/judge calibration, rollout store, and env health dashboard. |
| M2 Training Sprint | 2026-09-01 to 2026-10-16 | Large-scale Agentic RL v1, Qwen3.5-122B-A10B parity checkpoint, and gap analysis. |
| M3 Expansion | 2026-10-17 to 2026-11-15 | GUI/browser/MCP/SWE/multimodal environment expansion and Agentic SFT v2. |
| M3 Convergence | 2026-11-16 to 2026-12-31 | Final RLVR/SWE/browser/GUI/RLHF runs, full eval, quantization/serving validation, and checkpoint freeze. |

## Workstreams

### 1. Data Collection, Curation, and Creation

- Build a unified data registry with source, license, domain, difficulty, format, tool requirements, reward type, contamination risk, and eval overlap tags.
- Normalize SFT data into OpenAI chat/responses format with explicit tool schemas, tool outputs, and role-based loss masking.
- Normalize RL data into NeMo-Gym-compatible JSONL with `responses_create_params`, expected answer or verifier metadata, environment name, and reward config.
- Create difficulty curricula by filtering samples the current SFT model already solves consistently, then sorting the remaining samples by pass rate, judge confidence, and rollout length.
- Maintain separate train/dev/shadow-eval splits for every environment to avoid reward overfitting.
- Mine failed rollouts from M1 and M2 into SFT repair data and RL replay candidates.

### 2. Interactive RL Environment Construction

Initial environment families:

- Math and formal reasoning: answer verification, Python tool execution, Lean/formal proof verification.
- Code generation: competitive programming, unit-test execution, code critique, repair.
- SWE: SWE-pivot, SWE-bench-style repo repair, multi-harness OpenHands/OpenCode/Codex formats.
- Tool use: single-step and multi-step function calling, argument comparison, schema adherence, structured output.
- Search/browser: web retrieval, BrowseComp-style browsing, grounded answer verification.
- Terminal/workplace assistant: shell tasks, calendar/workplace APIs, multi-turn transactional tasks.
- SQL/data: BIRD/text-to-SQL with execution reward, data science tasks with notebook or script execution.
- Safety and robustness: jailbreak detection, over-refusal reduction, safe tool use.
- Long context: retrieval, long-document reasoning, memory-heavy agent workflows.
- Multilingual: multilingual IF, code, translation, and localized tool-use tasks.
- Multimodal if in scope: OCR, document QA, charts, diagrams, video, ASR, and multimodal tool routing.

Environment requirements:

- Every environment must define reward range, pass/fail semantics, timeout, max turns, required tools, sandbox type, expected runtime, and failure modes.
- Fast environments can be mixed in RLVR; slow environments such as SWE/browser/GUI should run in separate queues or stages.
- Every environment needs a local small-run mode, health checks, telemetry, and a held-out shadow eval split.

### 3. Agentic SFT

Agentic SFT v0:

- Train tool-call syntax, terminal basics, search patterns, structured outputs, and short SWE traces.
- Preserve existing reasoning modes and chat templates.
- Include negative examples for malformed tool calls and hallucinated tool outputs.

Agentic SFT v1:

- Add multi-turn tool traces, self-correction, environment observation handling, and failed-then-fixed trajectories.
- Add cross-harness SWE traces so the model is not overfit to one agent loop.
- Add compact reasoning/low-effort variants for latency-sensitive tasks.

Agentic SFT v2:

- Distill successful M2 trajectories.
- Convert high-reward rollouts into supervised traces after filtering for correctness and style.
- Include hard negative repairs from SWE/browser/tool failures.
- Use teacher or GenRM reranking to select concise, robust traces.

### 4. Agentic RL

M1 RL:

- Reproduce Super3-style RL flow: RLVR1 -> RLVR2 -> RLVR3 -> SWE1 -> SWE2 -> RLHF.
- Keep the first target simple: stabilize the full stack and avoid category regressions.
- Track reward distribution, pass@1, best@k, rollout length, tool-call validity, overlong rate, and KL/drift.

M2 RL:

- Introduce dynamic sampling by environment performance gap.
- Separate fast verifiable RLVR from slow SWE/browser queues.
- Add judge ensembles and calibration for non-binary rewards.
- Add per-environment quotas so high-throughput tasks do not dominate the gradient.

M3 RL:

- Run curriculum waves from high-confidence verifiable rewards to slower agentic tasks and final GenRM/RLHF.
- Add shadow-eval gating before promoting a checkpoint to the next stage.
- Use rollback rules for regressions in SWE, tool validity, safety, long context, or multilingual tasks.

### 5. Agentic RL Infrastructure

Required infra by M1:

- NeMo-RL/Ray/vLLM/NeMo-Gym launch path validated at small and full scale.
- Sandbox container for code execution, Lean/formal tasks, terminal tasks, and SWE.
- SWE container with prefetched venvs and SIF/Docker/Podman image support.
- W&B/artifact lineage for raw data, prepared data, model checkpoints, and eval reports.
- Basic environment telemetry: reward, latency, timeout, crash, invalid tool call, malformed reasoning, and overlong stats.

Required infra by M2:

- Central rollout store with prompt, response, environment observation, reward, verifier logs, and model version.
- Environment scheduler with quotas, backpressure, and fast/slow queue separation.
- Judge service pool with model versioning and calibration sets.
- Automated contamination checks and eval-overlap reports.
- Canary and shadow-eval pipeline for every promoted checkpoint.

Required infra by M3:

- 1K GPU-class async GRPO with decoupled training/inference, policy-lag monitoring, and automatic recovery.
- Sandbox pool manager for SWE/browser/GUI with resource limits, timeout handling, filesystem isolation, and artifact capture.
- Environment replay/debug UI for failed rollouts.
- Automatic checkpoint promotion/rollback gates.
- Serving validation for BF16 plus quantized candidates if deployment parity matters.

## Evaluation Gates

Each milestone should produce:

- A frozen checkpoint.
- A full eval report against the milestone target basket.
- A regression report versus the previous checkpoint.
- Per-environment training metrics and reward health.
- A data lineage report listing all datasets, filters, and generated samples.
- A known-gap list with owners and next actions.

Suggested benchmark families:

- General knowledge: MMLU-Pro.
- Reasoning: AIME25, HMMT, GPQA, HLE.
- Coding: LiveCodeBench, SciCode, competitive programming pass@k.
- Agentic: TerminalBench, TauBench, BrowseComp, BIRD, BFCL, MCP-Mark, Tool Decathlon.
- SWE: SWE-Bench Verified, SWE-Bench multi-harness, multilingual SWE if available.
- Chat/IF: IFBench, MultiChallenge, Arena-Hard-style prompts.
- Long context: AA-LCR, RULER at 256K/512K/1M, long-document QA.
- Multilingual: MMLU-ProX, WMT24++, multilingual IF/code/tool tasks.
- Multimodal if in scope: MMMU/MMMU-Pro, MathVision, OCRBench, chart/document/video/ASR tasks.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Base checkpoint is below target capacity | RL cannot close the gap to 397B-class targets | Add distillation from stronger teachers, extend SFT, or adjust target scope before M2. |
| Reward hacking in non-verifiable environments | Apparent gains do not transfer to real evals | Use held-out shadow evals, judge ensembles, adversarial checks, and reward audit sets. |
| Slow environments dominate wall clock | RL throughput collapses | Separate slow queues/stages, use replay buffers, cap per-env quota, and optimize sandbox pools. |
| SWE/browser sandbox instability | Training interruptions and noisy rewards | Add health checks, memory watchdogs, command blocklists, retry policy, and per-env failure accounting. |
| Tool-call format drift | Agentic benchmarks regress | Keep tool syntax SFT replay, invalid-tool penalties, and schema-specific eval gates. |
| Category regressions after RL | Gains in one domain degrade others | Multi-environment mixing, per-category eval gates, rollback rules, and final GenRM/RLHF with KL control. |
| Contamination or eval leakage | Invalid benchmark claims | Maintain data provenance, dedup against evals, and freeze eval holdouts early. |

