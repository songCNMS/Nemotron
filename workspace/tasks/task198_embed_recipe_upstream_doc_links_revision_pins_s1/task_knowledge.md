# Task Knowledge

<!-- METADATA:SESSION=2 -->

- Task198 is limited to two Embed recipe upstream links and one focused static
  test.
- Export-Deploy tutorial revision:
  `e025bcd888d92ae226cccd4556f0a790bf714ec7`.
- Automodel biencoder source revision:
  `7dc827ca9108b2e45eb3beaba8a3cd148bfc658f`.
- `export.py` had pre-existing Ruff issues; fixing them in the scoped touched
  file was required for the task's Ruff gate and did not alter runtime
  semantics.
- PR #305 merged at `ea252765464a50d3b2fc46a5ab7922bf8285a6aa`; closeout only
  records status/report updates and does not alter product source/tests.
