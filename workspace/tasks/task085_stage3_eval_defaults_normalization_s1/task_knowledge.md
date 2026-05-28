# task085_stage3_eval_defaults_normalization_s1 knowledge

<!-- METADATA:SESSION=7 -->

## Working Notes

- Source YAML may retain `defaults` and `qwen_chat_contract` for inheritance and
  static audits.
- `normalize_evaluator_launcher_config()` is the launcher-bound cleanup point:
  strip `defaults`, `qwen_chat_contract`, and `corrected_math` there.
- Compact top-level `tasks` overlays must still expand into `evaluation.tasks`
  before normalization.
- Session 6 added no new implementation knowledge; it only corrected the task085
  session metadata/history record required by the stop hook.
- Session 7 added no new task085-specific implementation knowledge; task089 now
  owns the stage0 pretrain data-prep output-portability follow-up.
