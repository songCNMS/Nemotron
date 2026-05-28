# task097_rlhf_toolcall_contamination_skip_contract_s1 knowledge

<!-- METADATA:SESSION=10 -->

## Working Notes

- `prepare()` is used directly by tests with `argparse.Namespace`; use
  `getattr(args, "skip_contamination_check", False)` so older constructed
  namespaces fail closed instead of implicitly skipping contamination checks.
- The manifest fields added for explicit skips are
  `contamination_check_skipped` and `contamination_check_skip_warning`.
- A skipped contamination check is for sandbox/smoke use only and must not be
  interpreted by lineage consumers as clean decontaminated output.
