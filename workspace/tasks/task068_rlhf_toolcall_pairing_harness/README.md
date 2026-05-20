# task068_rlhf_toolcall_pairing_harness

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->
<!-- SESSION 1 LANDED: PR pending on 2026-05-19 (task068_design.md captures filter / gold-call / sampling / decontamination decisions) -->

## 背景

Lifted out of `task018_m1_rlhf_genrm_service` Session 2.

task018 Session 2 originally bundled two RLHF data deliverables: the
HelpSteer-2 preference converter (✓ landed) and a **tool-call pairing
harness** that wires HelpSteer-2 prompts to the parallel
`single_step_tool_use_with_argument_comparison` env per plan §5.6.

The harness was deferred during task018 Session 2 because the design
needs more thought — naïve cross-product of HelpSteer-2 prompts × M0
Hermes tool-call rows is a combinatorial blow-up (the M0 split has ~7k
HelpSteer-2 rows × ~30k Hermes rows = 200M+ candidate pairs). The right
shape needs:

1. **Relevance filter** — only pair HelpSteer-2 prompts whose semantic
   shape supports a tool-call follow-up (instruction-following, factual
   lookup, computational tasks; NOT poetry / opinion / chitchat).
2. **Per-prompt single tool target** — like SWE1 first-tool-call, the
   gold is *one* tool call per prompt; not a list of possible calls.
3. **Sampling cap** — at most K pairs per HelpSteer-2 prompt to keep
   the corpus tractable.

## Plan reference

Plan §5.6 RLHF acceptance:

> tool-call-validity check still passes per plan §5.6 note

`stage3_rlhf/config/default.yaml` loads two NeMo-Gym envs:
- `genrm_compare` — preference judge (task018 Session 2 data ✓)
- `single_step_tool_use_with_argument_comparison` — **parallel tool-call
  validity check** (this task)

The harness produces M0 rows for the second env so the RLHF stage can
verify the policy still emits well-formed tool calls during preference
optimization (otherwise the policy learns to please the GenRM judge by
talking eloquently but loses tool-call competence).

## 整 task 拆 Sessions

| Session | 子条目 | sandbox-runnable? | Status |
|---|---|---|---|
| 1 | Pairing strategy design doc + reference paired dataset shape — what fields, what relevance heuristic, what sampling cap | yes | ✓ Done (this PR — see `task068_design.md`) |
| 2 | M0 converter `transform_rlhf_toolcall_pairing` consuming HelpSteer-2 prompts + Hermes tool-call rows; emits paired rows for `single_step_tool_use_with_argument_comparison` env | yes | Todo |
| 3 | Flip the RLHF env registry's tool-call row to active; bridge picks it up; M0 prep generates the paired data | yes | Todo |
| 4 | Cluster smoke: end-to-end RLHF with both `genrm_compare` AND tool-call validity envs lit up | no — needs cluster + GenRM judge service (task018 Session 3) | Todo |

## Session 1 目标

Design doc — no code yet. Decide:

1. **Relevance filter** — what makes a HelpSteer-2 prompt "tool-call
   eligible"?
   - Keyword heuristic (mention of "look up", "compute", "search", "find")?
   - Embedding similarity vs Hermes prompt distribution?
   - Manual classifier trained on a small labeled set?
2. **Per-prompt gold call**
   - Sampling random Hermes call as ground truth (cheap but noisy)?
   - Picking the Hermes call whose function name appears in the prompt
     (better signal but lower coverage)?
   - LLM-generated tool call given the prompt (highest quality but
     expensive + requires inference)?
3. **Sampling cap** — what's K?
   - K=1: each HelpSteer-2 prompt maps to one tool-call pair → smallest
     corpus but high diversity per row
   - K=5: balanced
   - K=20: largest but risks corpus dominated by hub prompts
4. **Decontamination** — exclude HelpSteer-2 prompts that overlap with
   eval baskets (BFCL / TauBench airline / MCP-Mark)

Output: `task068_design.md` capturing the decisions + the converter
interface contract Session 2 will implement.

## Session 1 验收

- [x] Design doc `task068_design.md` covering filter / gold-call /
  sampling / decontamination
- [x] Reference paired-row shape with 4 worked examples (clear match /
  eligible-but-no-match / found-but-contaminated / kept-after-all-filters)
- [x] Sample corpus size estimate: 7K HelpSteer-2 train → ~1,200
  paired rows after relevance + match + decontam (83% drop)
- [x] Contamination plan vs M1 eval basket: BFCL / TauBench airline /
  MCP-Mark / HelpSteer1 (latter via task018 Session 2)
- [x] Converter interface contract documented (Session 2 implements)
- [x] Open questions section for product/lead alignment

## Decisions (Session 1)

- **Relevance filter**: keyword heuristic + Hermes template match (cheap,
  deterministic; ~30% pass rate expected)
- **Gold-call sourcing**: function-name match heuristic (Hermes
  `function.name` appears in HelpSteer-2 prompt) with required-arg
  tiebreak; rejects random-sample and LLM-zero-shot for v0
- **Sampling cap K=1**: one paired row per HelpSteer-2 prompt, picking
  the best Hermes match
- **Decontamination**: exclude prompts overlapping with BFCL /
  TauBench airline / MCP-Mark / HelpSteer1 eval baskets via task030
  Session 7's contamination_audit loader

## 依赖

- task018 Session 2 (HelpSteer-2 converter ✓) — already landed
- M0 Hermes function-calling rows (`m0_tool_calling_hermes` ✓) — already in M0
- Session 4 依赖 task018 Session 3 (judge service) AND cluster

## 不在本 task

- The GenRM judge service deployment (task018 Session 3)
- Multi-turn tool-call evaluation (M2 task033 / task038)
- Per-tool reward calibration (M2 task034 judge pool)

## 参考文件

- `src/nemotron/recipes/super3/milestones/m1_rlhf/rlhf_env_registry.yaml` —
  `single_step_tool_use_with_argument_comparison` row currently `m0_missing`
- `src/nemotron/recipes/super3/milestones/m0_data_env/prepare_m0_assets.py` —
  `transform_hermes_function_calling` for reference of how to emit
  argument_match-shaped rows
- `src/nemotron/recipes/super3/stage2_rl/stage3_rlhf/config/default.yaml` — RLHF stage config
- plan §5.6 + roadmap §1.6
