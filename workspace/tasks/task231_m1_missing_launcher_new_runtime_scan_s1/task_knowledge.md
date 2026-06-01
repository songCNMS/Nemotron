# Task Knowledge

<!-- METADATA:SESSION=5 -->

- Bounded task231 artifact search found only the task225 launcher runtime and
  wheelhouse under `/mnt/cephfs/data/processing/nemotron-live-validation`:
  no newer `nemo_evaluator_launcher` package was present.
- The local project venv `/work-agents/.venv` has no
  `nemo_evaluator_launcher` module or package metadata.
- Task225 local runtime, VPN copied freeze, and task227 official-runtime probe
  all point to `nemo-evaluator-launcher==0.2.5`.
- In that runtime, `terminalbench` resolves through the `codec` harness and is
  described as contamination detection; it is not an exact TerminalBench eval.
- Exact safe mappings for the five M1 missing targets require a newer
  approved launcher package or benchmark-owner supplied task names/contracts.
- Stop-hook validation for this workspace expects the active task history file
  to include an explicit heading for the current session number.
- Session 5 did not change mapping evidence; it only refreshed status for the
  PM ping. The decisive blocker remains absence of exact launcher tasks in the
  inspected local/task225/VPN/task227 runtime surfaces.
