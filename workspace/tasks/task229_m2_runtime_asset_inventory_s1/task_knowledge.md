# task229_m2_runtime_asset_inventory_s1 knowledge

<!-- METADATA:SESSION=1 -->

## Durable Findings

- M2 still has 8 held targets: `hle`, `browsecomp`, `bird_real_execution`,
  `bfcl_full`, `mcp_mark`, `tool_decathlon`, `multilingual_ifeval`, and
  `multilingual_humaneval`.
- Local CPU can see several candidate asset roots:
  - HLE base parquet and metadata under
    `/mnt/cephfs/data/processing/xiaofan.gui/benchmark/data/search_web/hle_base`
  - BrowseComp base CSV and search scaffolds under
    `/mnt/cephfs/data/processing/xiaofan.gui/benchmark/data/search_web`
  - MCPMark official task tree under
    `/mnt/cephfs/data/processing/xiaofan.gui/benchmark/data/agent_tool_web/mcpmark`
  - Related MCP Atlas and Claw-Eval candidate tool-agent data under
    `/mnt/cephfs/data/processing/xiaofan.gui/benchmark/data/agent_tool_web`
  - MultiPL-E/HumanEval and IFEval-related local assets under
    `/mnt/cephfs/data/processing/posttrain/shared_eval_data`
- Sampled xiaofan.gui/shared-eval candidate paths were not visible from the
  read-only NemTron or vpn probes, so run visibility remains a blocker.
- BIRD real-execution database assets were not found under checked stable or
  shared processing candidates; task024 remains only a local SQLite scaffold.
- Frozen Qwen3.5-122B-A10B baselines are still absent for all 8 M2 rows.
- Task225 appears to provide a task-owned `nemo-evaluator-launcher` runtime
  candidate, but task229 did not run or validate it. M2 still needs
  target-specific assets, credentials, sandboxes, and baselines before any
  live run.
