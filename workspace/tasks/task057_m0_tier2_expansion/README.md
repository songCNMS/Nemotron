# task057_m0_tier2_expansion

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->
<!-- SESSION 1 LANDED: PR #108 / d5d215c on 2026-05-19 (multilingual_instruct env via CohereLabs/aya_dataset) -->
<!-- SESSION 2 LANDED: PR #118 / 3ca0b32 on 2026-05-20 (long_context_qa_smoke env via THUDM/LongAlpaca-12k; 17 tests) -->
<!-- SESSION 3 LANDED: PR #120 / 8e1e7fe on 2026-05-20 (sql_text_to_query env via BIRD-SQL; 29 tests) -->
<!-- SESSION 4 LANDED: PR #122 / 7730b8f on 2026-05-20 (terminal-tier2 via intercode-nl2bash; reuses existing env; quote normalization enhancement; 26 tests) -->
<!-- SESSION 5 LANDED: PR pending on 2026-05-20 (safety_reasoning_smoke env via Nemotron-Content-Safety-Reasoning; 37 tests) -->

## 背景

`docs/m0-dataset-expansion-plan.md` §3 Tier-2 列出 6 个 M0 environment，每个都对应 plan §7 一类 family，但比 Tier-1 多一层污染 / 许可证审计成本。Tier-1 (task056) 必须先合入主干，才有公平的 contamination baseline 可比对。

## Session 切分 (2026-05-19 添加)

整个 task 原 README 把 6 个 envs 当作一个原子工作。实际每个 env 自带独立的：
- HF source 形态 (verify offline 的话需要 mock schema)
- License/contamination 考量
- Verifier 写法
- Test 工作

所以拆成 6 个 sessions，一 session 落地一个 env。Session 1 选 `multilingual_instruct`
作为 baseline pattern (源 Aya 干净 / 无 contamination overlap with M0 + M1 eval / verifier
只是 `normalized_exact_or_contains` 的多语言变种)，后续 5 个 env 按这个 pattern
adapt。

| Session | Env | HF source | Status |
|---|---|---|---|
| 1 | `multilingual_instruct` | `CohereLabs/aya_dataset` | ✓ Done (this PR) |
| 2 | `long_context_qa_smoke` | `THUDM/LongAlpaca-12k` | ✓ Done (this PR) |
| 3 | `sql_text_to_query` | `birdsql/bird_mini_dev` + `bird-bench/bird` | ✓ Done (this PR) |
| 4 | `terminal_basic_shell` (tier-2 extension) | `epinnock/intercode-nl2bash-curated` | ✓ Done (this PR) |
| 5 | `safety_reasoning_smoke` | `nvidia/Nemotron-Content-Safety-Reasoning-Dataset` | ✓ Done (this PR; data_registry row deferred for schema verification) |
| 6 | `math_with_tools` | `MathLLMs/MathCodeInstruct` | Todo (NuminaMath dedup) |

## 目标 (整 task)

落地 Tier-2 6 个环境，每个走完同样的六点 wiring checklist (见 `docs/m0-dataset-expansion-plan.md` §5)。

| Env id (M0) | HF source | License | 注意事项 |
|---|---|---|---|
| `sql_text_to_query` | `birdsql/bird_mini_dev` + `bird-bench/bird` train | CC-BY-SA-4.0 ⚠ | mini_dev 必须 held out，绝不能进 train。新 verifier `sql_execution_match`，oracle baseline 用 reference SQL string match (而非真执行) |
| `terminal_basic_shell` | `epinnock/intercode-nl2bash-curated` (优先) 或 community `CLI-1M` | CC-BY-4.0 / Apache-2.0 | CLI-1M 是 forum-announced，HF 路径需要确认；intercode-nl2bash 9 K 行已足以做 smoke |
| `safety_reasoning_smoke` | `nvidia/Nemotron-Content-Safety-Reasoning-Dataset` | CC-BY-4.0 | 数据 viewer schema 有报错，loader 需先验证；新 verifier `safety_judge_stub` |
| `multilingual_instruct` | `CohereLabs/aya_dataset` (人工写) | Apache-2.0 | 不要用 `aya_collection` (含翻译 FLAN，可能污染 XNLI/XQuAD)；新 verifier `multilingual_exact_or_contains` |
| `long_context_qa_smoke` | `THUDM/LongAlpaca-12k` train | Apache-2.0 | 把 `zai-org/LongBench-v2` 留给 task019/task020 eval；不要混进 M0 train |
| `math_with_tools` | `MathLLMs/MathCodeInstruct` (优先) 或 `nvidia/OpenMathInstruct-2` | Apache-2.0 / CC-BY-4.0 | 两个都基于 GSM8K/MATH seed — heavy contamination，必须先跟 MATH/AIME 做去重 |

## 子任务

每个 env 单独成 sub-issue，下面给最常被忽视的几条 watch-out:

### sql_text_to_query
- BIRD 数据集分 7 个 schemas，每个 schema 多个 question。把整张数据集按 schema 切，每个 schema 在 train/val 都出现 (cross-schema generalization 是 BIRD 的核心评测项)。
- 不需要 DB sandbox — M0 阶段只检查 candidate SQL 与 reference 的归一化 string match；真正的执行检查留给 M1 RLVR/eval。

### terminal_basic_shell
- 命令长度 cap = 200 字符 (避免噩梦行)，dataset 大部分行符合。
- 即使是 smoke，verifier 也要做 `re.sub(r'\\s+', ' ', cmd).strip()` + 引号归一化，否则 oracle 都过不了。

### safety_reasoning_smoke
- 注意 dataset card 的 viewer 报错 — 可能字段 schema 跟其他 NVIDIA dataset 不一样。第一步用 `datasets.load_dataset(... , streaming=True)` 抽 5 行 dump schema 出来看再写 converter。
- Verifier oracle = reference safety verdict (allow/block + reasoning text)；M0 阶段不接 judge model。

### multilingual_instruct
- Aya 每行有 `language` 字段，按需 filter 到 plan 6 语言: de / es / fr / it / ja / zh。
- M0 smoke 每语种 ~17 行 (100 / 6 取整)。

### long_context_qa_smoke
- LongAlpaca 文档长度跨 16K - 100K tokens，M0 smoke 取最短的 100 个。
- 真长 context (256K-1M) 是 M2 task028 / task037 的范围。

### math_with_tools
- 每行 solution 包含 `<python>...</python>` 或 ` ```python ... ``` ` 代码块。converter 必须保留代码块原样，verifier oracle 用最后一个 `\boxed{}` 答案。
- 注意跟 task056 NuminaMath 去重：用 `metadata.source_id` 比对，重的全部移到 math_with_tools (因为它的代码块更有信息)。

## Session 1 验收

- [x] 新 env `multilingual_instruct` in `environment_registry.yaml`
  (family `multilingual`, verifier `multilingual_exact_or_contains`,
  required field `extra_env_info.language`)
- [x] 新 converter `transform_aya_multilingual` in
  `prepare_m0_assets.py` — handles `inputs/targets` + alias
  `instruction/response`; language-scope filter (`de/es/fr/it/ja/zh`);
  accepts both `language` (full name) and `language_code` (ISO)
- [x] 新 verifier `multilingual_exact_or_contains` in
  `run_m0_health_baseline.py` — Unicode NFC + `casefold()`; preserves
  CJK punctuation; does NOT strip English articles (German "die"
  survives)
- [x] `m0_multilingual_aya` data_registry row **deferred** to Session
  1.5 — requires pinning a real Aya commit SHA which needs HF access.
  Schema documented in YAML comment + locked-in test verifying the
  row is NOT in the registry yet (catches accidental re-add without
  real pin)
- [x] 28 个 pytest case (vs ≥ 12 acceptance for 1 of 6 envs)
- [x] 三个 data-registry audit 全 clean

## 整 task 验收 (across 6 sessions)

- [ ] 6 个 env 全部走完 6-point wiring。
- [ ] 新加 5 个 verifier stub (`sql_execution_match`、`safety_judge_stub`、`multilingual_exact_or_contains`、`long_context_qa_stub`、`math_with_tools_match`)。
- [ ] `tests/recipes/super3/test_m0_*.py` 新增 ≥ 12 个 case (每 env 2 个：converter + health gate)。
- [ ] `tests/recipes/super3/test_m1_agentic_sft.py` 新增 ≥ 6 个 case。
- [ ] `docs/m0-dataset-expansion-plan.md` §3 Tier-2 表的 6 行全部能勾上。
- [ ] 至少 1 个 contamination audit (建议：BIRD vs Spider，因为很多人混用)，结果落到 `data_registry.yaml` 新的 `contamination_against` 字段 (字段 schema 由 task058 引入)。

## 依赖

- **task056** 必须先合入主干 (Tier-1 把 NuminaMath / MuSiQue / multi-turn Hermes 落地后，task057 才能用同样的 wiring pattern)。
- **task058** 引入 `contamination_against` schema 字段；task057 的 contamination audit 需要这个字段。

## 参考文件

- 同 task056 的参考文件清单
- `docs/m0-dataset-expansion-plan.md` §3 Tier-2 + §6 open questions
