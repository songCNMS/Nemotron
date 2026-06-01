# task241 V10 sidecar data report

<!-- METADATA:STATUS=ReadyForPR,SESSION=2 -->

## Summary

- Added `hard_math_runlength_dp_v10` as a separate M1 math supervision strategy.
- V10 keeps the V8 clean-final contract and narrows the hard sidecar to constrained binary/chair/seat sequence counting rows with run-length constraints plus either DP/recurrence signals or case-split combinatorics signals.
- V10 is included in the decontamination-required strategy set. Without `--decontaminate-math-against-corpus`, it raises unless `--skip-math-decontamination-check` is explicitly set.

## V10 filter

Required hard-row base:

- `math_competition_numeric`
- V7 long hard-math shape
- single clean final boxed scalar matching `m0_expected_answer`

Additional V10 signal groups:

- counting prompt: `count`, `how many`, `determine the number`, `find the number`, `number of`, `ways`
- binary/chair/sequence object: binary strings/sequences, bit strings, chairs, occupied chairs, seats, strings of length, zeros/ones
- run-length constraint: adjacent/consecutive/no-three/no-111/run-length/substring patterns
- solution reasoning: DP/recurrence/state/transition/table/trailing-run or blocks/gaps/binomial/generating-function style combinatorics

## Synthetic validation counts

Focused tests create four clean-final rows:

- 2 V10 positives: one chair/binary DP recurrence row with answer `907`, one binary-seat gaps/binomial row with answer `171`
- 1 V9-positive but V10-negative recurrence/run-length algebraic row
- 1 broad V8 clean-final but V10-negative polynomial row

Expected V10 sidecar result:

- hard verified source rows: 2
- hard verified written rows: 2
- broad verified source rows: 2
- broad verified written rows: 0
- source signal counts: counting prompt 2, sequence object 2, run-length constraint 2, DP/recurrence 1, case-split combinatorics 1

## Decontamination status

Focused tests verify:

- V10 requires a decontamination corpus by default.
- A synthetic AIME25-like prompt is dropped from base train and the V10 hard sidecar when present in the heldout corpus.
- A distinct clean V10 row remains in both base train and the V10 hard sidecar.

No AIME25 prompts or labels were added as training data. The AIME25-like prompt appears only in tests as heldout/decontamination corpus content and as an input row intentionally removed by decontamination.

## Artifacts

- Code: `src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py`
- Tests: `tests/recipes/super3/test_m1_agentic_sft.py`
- Tests: `tests/recipes/super3/test_m1_agentic_sft_math_decontamination.py`

## Checks

- `python -m py_compile src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py` passed.
- `python -m ruff check src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py tests/recipes/super3/test_m1_agentic_sft.py tests/recipes/super3/test_m1_agentic_sft_math_decontamination.py` passed.
- `git diff --check` passed.
- `PYTHONPATH=src python -m pytest -q tests/recipes/super3/test_m1_agentic_sft.py tests/recipes/super3/test_m1_agentic_sft_math_decontamination.py -k 'v10 or v9 or decontaminate or decontamination or hard_math'` passed: 22 passed, 90 deselected.
- `PYTHONPATH=src python -m pytest -q tests/recipes/super3/test_m1_agentic_sft.py tests/recipes/super3/test_m1_agentic_sft_math_decontamination.py -k 'not data_prep and not sft_data_artifact_records_chat_template_contract'` passed: 105 passed, 3 skipped, 4 deselected.

Full two-file pytest without deselection was attempted but three pre-existing `nemotron.data_prep` import tests fail in this sandbox because `cosmos_xenna` is not installed. This is an environment dependency gap, not a V10 behavior failure.

## Residual risk

- I did not run full uncapped M0/sidecar data generation, so real corpus V10 row counts remain for worker_4 or a data-prep audit run.
- Keyword selection is intentionally conservative and may miss semantically equivalent run-length DP rows that avoid the configured signal words.
- Planner/training launch wiring is not changed in this task; worker_2 still needs to expose V10 for runnable training configs.
