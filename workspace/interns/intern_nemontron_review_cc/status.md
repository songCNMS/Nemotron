# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle,TASK= -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | - |
| PR | - |
| Session | 70 |

刚做完：task018 Session 2 sandbox part — M0 HelpSteer-2 → genrm_compare
converter (PR #84 / cfbb002, merged 2026-05-19)。3 大件:

1. **新 M0 env + data row** (`helpsteer2_pref_compare`)：family
   `rlhf_preference`，verifier `genrm_compare`；`nvidia/HelpSteer2`
   (cc-by-4.0, contamination_against [MT-Bench, HelpSteer1])
2. **新 converter** `transform_helpsteer2_pref`：两种 HelpSteer-2 flavor
   都支持 (explicit-pair + attribute-derived)；tie → "A"；explicit 优先
3. **RLHF registries 更新**：pref_data helpsteer2 行加 `m0_landed: true`；
   env_registry `genrm_compare` **故意保持** `blocked_external` (judge
   service 仍是 blocker)

20 个新 + 2 个修改 pytest case；sandbox 测试基线 474 → 494 passed +
7 skipped。三个 data-registry audit 全 clean。

## M1 converter layer (sandbox) 全部落地 🎉

本 session 完成最后一块 sandbox-runnable converter 工作：

- ✓ task014 (RLVR1 bridge + smoke wiring + combined.jsonl)
- ✓ task015 (21-env registry)
- ✓ task016 (SWE1 bridge + SWE-Gym first-tool-call pivot converter)
- ✓ task017 (SWE2 bridge + OpenHands trace converter + sandbox watchdog)
- ✓ task018 (RLHF bridge + HelpSteer-2 preference converter)

剩下全都是 cluster-side 工作:
- task014 真 launch (Ray + vLLM + NeMo-Gym services)
- task016/017/018 真 HF download + revision pin
- task017 OpenHands wrapper (等真 library 集成)
- task017 Session 3 (cluster smoke + Docker fallback)
- task018 Session 3 (GenRM judge service deployment)
- task018 Session 4 (端到端 RLHF smoke from SWE2 checkpoint)
- task018 tool-call pairing harness (follow-up)
- task013 Session 2 (两阶段 SFT driver — 需 CUDA)
- task019 Sessions 2-3 / task020 Session 3 (M1 eval cluster verify)
- task021 Session 4 (cluster verify)

下一候选 (sandbox-runnable):
- task021 Session 1 review 或 task013 Session 1 review (没单独 sandbox session)
- 找其他 plan/roadmap-listed sandbox gap
- 等用户接到 cluster 后启动 cluster sessions
