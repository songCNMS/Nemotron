# task322_qwen_all_sft_raw_materialize_count_decontam_s1 - Raw materialize/count/decontam report

<!-- METADATA:STATUS=Working,DISPOSITION=PARTIAL_PASS_WITH_EXCLUSIONS,SESSION=4 -->

## Disposition

`PARTIAL_PASS_WITH_EXCLUSIONS`.

Task322 resolved all 12 task319 raw all-SFT source candidates to exact HF files
and task308 sha256 references. Two task-owned standard JSONL sources were safely
materialized, counted, row-manifested, checksummed, and decontam-checked. Ten
sources were fail-closed excluded because each selected file is larger than the
bounded task322 materialization threshold of `1000000000` bytes.

This is not final packing evidence. It does not prove supervised-token counts,
Qwen chat-template packing, or full all-SFT source readiness.

## Branch and revision

- Branch: `intern_nemotron_worker_2/task322_qwen_all_sft_raw_materialize_count_decontam_s1`
- Base: `origin/main` at `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Lead docs imported from `origin/intern_nemotron_lead/session1-recovery-task-docs`
  at `7055dac63c772ac8a317454bffead4a469a0112f`
- Product code changes: none

## Output root

`/work-agents/intern_nemotron_worker_2/outputs/task322_qwen_all_sft_raw_materialize_count_decontam_s1/run_20260603T203100Z`

Output size: `1.6G`.

## Inputs

- Task319 source matrix:
  `/work-agents/intern_nemotron_worker_2/outputs/task319_qwen_all_sft_raw_blend_decontam_feasibility_s1/run_20260603T194128Z/matrices/source_matrix.tsv`
  - rows including header: `13`
  - sha256: `9bf2ff2bf0821330659f89c9f7d08854e9d76b30f12ca1c507325a3756964dc1`
- Task246 AIME2025/HMMT/MATH heldout corpus:
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl`
  - rows: `560`
  - sha256: `614b2b347d33c1ec00cfd2c33222c26ad1d99b8b837bd7e48ea11fd4fedae6f9`
- Task246 prompt hash list:
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/prompt_hashes.sha256`
  - rows: `560`
  - sha256: `a2a348ee12f962d5dd7ed7cf0e5d034ebea4a76a2287804e97ade331b552a78d`
- Task311 MMLU-Pro heldout input reference:
  `/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z/input/mmlu_pro/mmlu_pro_test.jsonl`
  - rows: `12032`
  - sha256: `1c23fc1dae4745edcab672973ef66516cde6ff94f26e59be845a97c072caef36`
- Task311 input manifest:
  `/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z/input/input_manifest.json`
  - sha256: `c645afcdbd88a43b447b6e3d1585df77d1c19b442a6256b1c0a2630a2f9cb053`
- Task314 MMLU-Pro row-transition reference:
  `/work-agents/intern_nemotron_worker_1/outputs/task314_qwen_all_sft_mmlu_pro_regression_forensics_s1/run_20260603T191500Z/mmlu_pro_row_transitions.jsonl`
  - sha256: `ab338411b96010b3408679f56d42185d69907bfd4a6272c85b8481d3ef077760`
- Task314 checksum manifest:
  `/work-agents/intern_nemotron_worker_1/outputs/task314_qwen_all_sft_mmlu_pro_regression_forensics_s1/run_20260603T191500Z/output_checksum_manifest.json`
  - sha256: `10bd7713eb6bc82a8fc5b7421115356f93ac95c72f4dc675908c9d941722ba50`

## Commands and environment

Environment:

- Host: local worker CPU environment under `/work-agents/intern_nemotron_worker_2/Nemotron`
- `HF_HOME=/work-agents/intern_nemotron_worker_2/outputs/task322_qwen_all_sft_raw_materialize_count_decontam_s1/run_20260603T203100Z/hf_home`
- `MAX_BYTES=1000000000`
- Output root:
  `/work-agents/intern_nemotron_worker_2/outputs/task322_qwen_all_sft_raw_materialize_count_decontam_s1/run_20260603T203100Z`

Commands executed:

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git checkout -B intern_nemotron_worker_2/task322_qwen_all_sft_raw_materialize_count_decontam_s1 origin/main
git checkout origin/intern_nemotron_lead/session1-recovery-task-docs -- workspace/tasks/task322_qwen_all_sft_raw_materialize_count_decontam_s1

# Inline Python metadata probe against the task319 source matrix and HF repo
# metadata, matching selected files to task308 sha256 values.
HF_HOME=<output_root>/hf_home python - <<'PY' > <output_root>/logs/hf_metadata_probe.log 2>&1
# wrote manifests/hf_metadata_resolution.json and matrices/source_resolution.tsv
PY

# Inline Python bounded materialize/count/decontam. It materialized only files
# <= MAX_BYTES, wrote row manifests, decontam reports, summary JSON, matrix TSV,
# raw files, and checksum manifest.
HF_HOME=<output_root>/hf_home MAX_BYTES=1000000000 python - <<'PY' > <output_root>/logs/materialize_count_decontam.log 2>&1
# wrote manifests/materialize_count_decontam_summary.json
PY

sha256sum -c <output_root>/manifests/artifact_checksums.sha256
git diff --check
```

The one-off helpers were not committed as product code; all reproducible
evidence is retained in task-owned logs, matrices, manifests, raw files, row
manifests, and checksum outputs.

## Artifact inventory and checksums

- `logs/hf_metadata_probe.log`
  - sha256: `1a60e94fdf90c4df48b8be4f86a96dfcdcd91f1cafa6de3d939644ea3e31f8ba`
- `logs/materialize_count_decontam.log`
  - sha256: `6c9ba0d2f7d53c5ce48765d2facf092fda4a8039151cf45ad10488a68d28ac30`
- `manifests/hf_metadata_resolution.json`
- `manifests/materialize_count_decontam_summary.json`
  - sha256: `a725a6646346376e671bcd75ae4068dc129d397e44bcc61e758c64ce6056680e`
- `matrices/source_resolution.tsv`
  - sha256: `c6c46aa2ac84f22f19239e64160f2f9c3a4c306d1b482b1e2f524c1b9a9727b1`
- `matrices/materialize_count_decontam_matrix.tsv`
  - sha256: `2634b36c3fc97c7b04044a3de98b1b1025059d2e79e7f438730d31513de9336d`
- `decontam/instruction-following-structured.decontam.json`
  - sha256: `e53e5aaa44bc92c920368360e0627957962da9570125dced9fb47ea8672c5a8c`
- `decontam/agentic-interactive.decontam.json`
  - sha256: `f5a392e09c686c2251559b80d9df812a14842a3dec5825489b1ff8b973c7299c`
- `manifests/artifact_checksums.sha256`
  - sha256: `1ca62fe125ecd98f4948752ad1a07328fdfef3047ec3f77d9da45c945ba7ccc8`
  - verification: `sha256sum -c` passed for all listed files after updating the
    log checksum to the final log contents.

## Summary counts

- Source candidates: `12`
- Resolved to exact HF file metadata: `12`
- Total selected payload size: `243316402226` bytes
- Included/materialized sources: `2`
- Included/materialized bytes: `543322912`
- Included/materialized rows: `23997`
- Excluded sources: `10`
- Exclusion reason class: `EXCLUDED_SIZE_GT_1GB`

## Source-by-source matrix

| Source | Dataset | Revision | File | Status | Bytes | Rows | File sha256 | Row manifest sha256 | Decontam hits |
|---|---|---|---|---:|---:|---:|---|---|---:|
| instruction-following-chat | `nvidia/Nemotron-Instruction-Following-Chat-v1` | `83dcd3aded0d289b0bbc018d3f9af4c5dd4005df` | `data/chat_if.jsonl` | `EXCLUDED_SIZE_GT_1GB` | `7000317929` | | `37f9ecc3c41dc5e97cfd6fca962a94afbc8713349900ea6f413c040df549ddb8` | | |
| instruction-following-structured | `nvidia/Nemotron-Instruction-Following-Chat-v1` | `83dcd3aded0d289b0bbc018d3f9af4c5dd4005df` | `data/structured_outputs.jsonl` | `INCLUDED_PASS` | `94752457` | `4969` | `03e4cc9a657f9f193860d82fe49764acc6b298f6ce6811497412aa5a0181ec77` | `206e27cb006fce1321115dd68732531cf46f6d3eb7e2d385f0eb3a2e7bb4c7a7` | `0/0/0` |
| competitive-cpp-00 | `nvidia/Nemotron-Competitive-Programming-v1` | `d6e7c6b404ed5db6e1104b41d0f80a0c7dad7bf8` | `data/competitive_coding_cpp.part_00.jsonl` | `EXCLUDED_SIZE_GT_1GB` | `25608786180` | | `1081e0a650ecdc02df1b4b8b4fecf4b3d39828908874b4bf1a4015e638005c62` | | |
| competitive-cpp-01 | `nvidia/Nemotron-Competitive-Programming-v1` | `d6e7c6b404ed5db6e1104b41d0f80a0c7dad7bf8` | `data/competitive_coding_cpp.part_01.jsonl` | `EXCLUDED_SIZE_GT_1GB` | `25921457397` | | `4500b6db059765aa6146d3c3247fdde1ce8b5cc762a7687ff4355b45e1701afa` | | |
| competitive-python-00 | `nvidia/Nemotron-Competitive-Programming-v1` | `d6e7c6b404ed5db6e1104b41d0f80a0c7dad7bf8` | `data/competitive_coding_python.part_00.jsonl` | `EXCLUDED_SIZE_GT_1GB` | `44531003881` | | `8314b37b7d42b32fb658c3be1fb974eb0814f44a856ccf2d90ec2d38856a7f5d` | | |
| competitive-python-01 | `nvidia/Nemotron-Competitive-Programming-v1` | `d6e7c6b404ed5db6e1104b41d0f80a0c7dad7bf8` | `data/competitive_coding_python.part_01.jsonl` | `EXCLUDED_SIZE_GT_1GB` | `44260933400` | | `988cc7a00686d6212b3f8fbef95919c8e72bbda81c9f859dd556df789bf44b30` | | |
| swe | `nvidia/Nemotron-SWE-v1` | `0fe17a965b297a9c943a59050a14c42d5f0083ce` | `data/r2e_gym.jsonl` | `EXCLUDED_SIZE_GT_1GB` | `11141242062` | | `1e0fb6d9a8d955fb0f2160e44a4946e5f2c4eb3931e80dadb724ff823cdbc14c` | | |
| math-proofs-lean | `nvidia/Nemotron-Math-Proofs-v1` | `97229c590831adfe96202f5cd071d444d535bf91` | `data/lean.jsonl` | `EXCLUDED_SIZE_GT_1GB` | `29525155225` | | `b423525d35ad16c791863670cbad76b27d8463e2574770732e2cf5bf70661a2e` | | |
| agentic-interactive | `nvidia/Nemotron-Agentic-v1` | `650d590978ca35c8f1ecea2faf136e5fac421b62` | `data/interactive_agent.jsonl` | `INCLUDED_PASS` | `448570455` | `19028` | `dcfeda22372fa707c979cab29ddfe896b89a933f15ed4acbb4f16e7e3787d9dd` | `81f558b6cd08b9159402aab073283d9cee2898d0b83b23efd71a3a49e6160fbc` | `0/0/0` |
| agentic-tool-calling | `nvidia/Nemotron-Agentic-v1` | `650d590978ca35c8f1ecea2faf136e5fac421b62` | `data/tool_calling.jsonl` | `EXCLUDED_SIZE_GT_1GB` | `5338348607` | | `f537a901d38a999627b8fe59e77a1007af0d79d71a892ad9a4a3d80456e5601b` | | |
| infinibyte-00 | `nvidia/Nemotron-Competitive-Programming-v1` | `d6e7c6b404ed5db6e1104b41d0f80a0c7dad7bf8` | `data/infinibyte.part_00.jsonl` | `EXCLUDED_SIZE_GT_1GB` | `24706580148` | | `7d6cc0943a9264696ba177f152fd12c60cc2e1b042787a205221abcd4059c9e7` | | |
| infinibyte-01 | `nvidia/Nemotron-Competitive-Programming-v1` | `d6e7c6b404ed5db6e1104b41d0f80a0c7dad7bf8` | `data/infinibyte.part_01.jsonl` | `EXCLUDED_SIZE_GT_1GB` | `24739254485` | | `0124e374453dce8fa7a6e7ecd75356160f2bde525ba97b246d2b39e8479c4ef3` | | |

The full machine-readable matrix is:

`/work-agents/intern_nemotron_worker_2/outputs/task322_qwen_all_sft_raw_materialize_count_decontam_s1/run_20260603T203100Z/matrices/materialize_count_decontam_matrix.tsv`

## Included source details

### instruction-following-structured

- Local path:
  `/work-agents/intern_nemotron_worker_2/outputs/task322_qwen_all_sft_raw_materialize_count_decontam_s1/run_20260603T203100Z/raw/instruction-following-structured/structured_outputs.jsonl`
- File bytes: `94752457`
- File sha256: `03e4cc9a657f9f193860d82fe49764acc6b298f6ce6811497412aa5a0181ec77`
- Row count: `4969`
- Parse errors: `0`
- Row manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task322_qwen_all_sft_raw_materialize_count_decontam_s1/run_20260603T203100Z/row_manifests/instruction-following-structured.rows.tsv.gz`
- Row manifest sha256:
  `206e27cb006fce1321115dd68732531cf46f6d3eb7e2d385f0eb3a2e7bb4c7a7`
- Decontam: prompt-hash hits `0`, normalized-prompt hits `0`, 13-word ngram
  hits `0`

### agentic-interactive

- Local path:
  `/work-agents/intern_nemotron_worker_2/outputs/task322_qwen_all_sft_raw_materialize_count_decontam_s1/run_20260603T203100Z/raw/agentic-interactive/interactive_agent.jsonl`
- File bytes: `448570455`
- File sha256: `dcfeda22372fa707c979cab29ddfe896b89a933f15ed4acbb4f16e7e3787d9dd`
- Row count: `19028`
- Parse errors: `0`
- Row manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task322_qwen_all_sft_raw_materialize_count_decontam_s1/run_20260603T203100Z/row_manifests/agentic-interactive.rows.tsv.gz`
- Row manifest sha256:
  `81f558b6cd08b9159402aab073283d9cee2898d0b83b23efd71a3a49e6160fbc`
- Decontam: prompt-hash hits `0`, normalized-prompt hits `0`, 13-word ngram
  hits `0`

## Decontam method

For the two included sources, the task-owned materializer:

- Parsed each JSONL row and recorded row-level manifest hashes.
- Collected string fields for decontam scanning.
- Checked exact sha256 hits against task246 prompt hashes.
- Checked normalized heldout prompt substring hits.
- Checked 13-word heldout ngram overlap hits.

The MMLU-Pro task311 input and task314 row-transition artifacts are recorded
above as heldout references with hashes. They were not used as train rows and
were not copied into the task322 raw materialized source root.

## Excluded source blockers

The 10 excluded sources are exact blockers for a full all-SFT contract:

- `instruction-following-chat`: `7000317929` bytes
- `competitive-cpp-00`: `25608786180` bytes
- `competitive-cpp-01`: `25921457397` bytes
- `competitive-python-00`: `44531003881` bytes
- `competitive-python-01`: `44260933400` bytes
- `swe`: `11141242062` bytes
- `math-proofs-lean`: `29525155225` bytes
- `agentic-tool-calling`: `5338348607` bytes
- `infinibyte-00`: `24706580148` bytes
- `infinibyte-01`: `24739254485` bytes

Each selected file exceeded the task322 bounded materialization threshold of
`1000000000` bytes. Total selected payload size across all 12 candidates is
`243316402226` bytes, so full materialization should be handled only by a
separate resource-approved task.

## Recommendation

- Do not treat this as full all-eligible SFT packing readiness.
- A later packing task may use only the two `INCLUDED_PASS` sources if lead
  explicitly scopes a small repair seed.
- A full all-SFT packed-data contract still needs a resource-approved raw
  materialization/count/decontam pass for the 10 excluded large files, plus
  supervised-token counts, split exposure parity, and Qwen tokenizer-native
  chat-template packing proof.

## Boundary confirmation

No final packing, training, optimizer steps, benchmark eval, export, endpoint,
promotion, task255 reuse, AIME2025 train data use, shared deletion/mutation,
main push, merge, or self-merge was performed. No product code was edited.
