# task273_qwen_aime_v11_eval_gate_continuity_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. Positive Bridge import proof is not an FT-vs-base AIME comparison.
2. The canonical base score remains `11/30`; future FT evidence must be judged
   under the same corrected harness and denominator.
3. The continuity review must distinguish runtime/import readiness from
   quality evidence: import proof can unblock later setup but cannot replace
   same-harness base-vs-FT AIME artifacts.
4. task273 continuity decision is `APPROVE/PASS` for the matrix itself: the
   accepted base comparator is still task247 Qwen3-4B `11/30`, and the future
   FT non-regression threshold is exact-normalized `>= 11/30` under the same
   harness.
5. Coordinator Session 40 evidence root contains the required runtime markers
   (`TASK270_RUNTIME_SYMBOL_PREFLIGHT=PASS`, `IMPORT_DONE`,
   `BRIDGE_IMPORT_RC=0`, and `TASK270_FAIL_CLOSED_PREFLIGHT=PASS`), but it is
   not AIME evidence and task271/lead acceptance remains the right dependency.
6. `sha256sum -c session40_evidence.sha256` validates the main Session 40 logs
   and checkpoint manifest but reports a stale/mismatched hash for
   `artifact_inventory.sha256`; this is a task271 proof-provenance risk, not a
   baseline/protocol ambiguity.
7. task255/V10 remains failed and non-reusable: task257 scored `0/30`, task260
   attributes the failure to generation degeneration/corruption, and task261
   identifies likely base-load/training defects.
8. PR #322 is closed unmerged and dirty; it is stale task243 metadata and must
   not be refreshed or reused as gate evidence.
