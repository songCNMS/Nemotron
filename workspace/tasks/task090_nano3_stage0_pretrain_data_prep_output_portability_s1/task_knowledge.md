# task090_nano3_stage0_pretrain_data_prep_output_portability_s1 - Task Knowledge

<!-- METADATA:SESSION=14 -->

## Knowledge Entries

1. assignment: Nano3 stage0 pretrain data-prep default `output_dir` must not use a named-user `/lustre` path.
2. technical fact: `PreTrainDataPrepConfig.output_dir` defaults to `NEMO_RUN_DIR` if set and `.` otherwise, with `output/nano3/stage0_pretrain` appended.
3. file change: `default.yaml` now uses `${oc.env:NEMO_RUN_DIR,.}/output/nano3/stage0_pretrain`; `tiny.yaml` was left unchanged.
4. test contract: Nano3 stage0 pretrain data-prep configs must preserve `blend_path`, `output_dir`, shard counts, tokenizer, text field, sample, force, config name, plan, download, tokenization, and observability fields.
5. test evidence: Focused pytest, py_compile, Ruff, static output_dir scan, and diff checks passed locally for task090.
