# task137_qwen_eval_task_audit_completeness_s1 knowledge

<!-- METADATA:SESSION=1 -->

## Working Notes

- `m1_full_basket_launcher_available.yaml` is the source of truth for the
  runnable 14-task audit set.
- `qwen_chat_contract.task_audit.bucket_semantics` is set to
  `exactly_one_bucket_per_runnable_task`; tests collect list-valued keys ending
  in `_tasks` as classification buckets.
- Long-context, tool/agentic, and multilingual runnable tasks are explicit risk
  buckets instead of being silently omitted from the Qwen eval audit.
