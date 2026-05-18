# task_knowledge

<!-- METADATA:SESSION=1 -->

## 编写规则

- 仅记录跨 session 仍然有用的、且无法通过读代码/git log 直接得出的事实。
- 临时进度放 history_log.md，不要写到这里。

## 知识条目

### M0 wiring 六点 checklist 的最小集

每加一个新 env，必须同时改 6 个文件。漏掉哪个会怎样：

1. 漏 `data_registry.yaml` → `prepare_m0_assets.py` 加载时 `selected_specs` 拿不到，整个 env 跳过。
2. 漏 `environment_registry.yaml` → `validate_registries` 把它判成 unknown environment 直接 raise。
3. 漏 `prepare_m0_assets.CONVERTERS` 注册 → `validate_registries` 报 "unknown converter"。
4. 漏 `SYSTEM_PROMPTS[env_id]` → converter 里 `SYSTEM_PROMPTS[spec["environment"]]` KeyError。converter 也可以直接传 literal，但分离常量更便于审计；新 env 一定要加。
5. 漏 `run_m0_health_baseline.py` verifier dispatch → oracle baseline 走 fallback `{"error": f"unsupported verifier: ..."}`，整张 health gate 判 fail。
6. 漏 `prepare_m1_agentic_sft.ASSISTANT_BUILDERS` 或 `M1_USE_BY_ENV` → M1 SFT prep 把整列 row 计成 `unsupported M0 environment` 失败，manifest.errors 鼓起来，但 ASCII 报错没有指明是 #6 漏了。

修复顺序: 6 → 5 → 4 → 3 → 2 → 1 (从下游回到上游)，因为下游 raise 比较温柔，先稳住 M1 端再加 M0 数据更稳。

### NuminaMath-CoT 答案抽取

`AI-MO/NuminaMath-CoT` 每行 `solution` 字段是完整 CoT，答案通常在最后一个 `\boxed{…}` 里。提取逻辑：

```python
matches = re.findall(r'\\boxed\{([^}]*)\}', solution)
if matches:
    return matches[-1].strip()
```

注意嵌套大括号: 一些解很少地包含嵌套 `\boxed{\frac{a}{b}}` — 简单 `[^}]*` 抓不到嵌套右括号，会截断。M0 阶段先用简版，遇到 boxed 解析失败的行落到 `manifest.errors` 即可，task057 可以升级到平衡括号解析。

### MuSiQue paragraphs 字段

`dgslibisey/MuSiQue` (Ans config) 的 `paragraphs` 是 list of dict，每个 dict 字段:
- `idx`: int
- `title`: str
- `paragraph_text`: str
- `is_supporting`: bool

注意是 `paragraph_text`，不是 `text` (HotpotQA 用 `sentences` 列表)。也不是 list-of-sentences — 它是单一文本块，直接 join 即可。

### Hermes `func_calling` vs `func_calling_singleturn`

`NousResearch/hermes-function-calling-v1` 的 `func_calling` config 是多轮的；`func_calling_singleturn` 是单轮的。`transform_hermes_function_calling` 已经在 task002 修过支持多轮 trajectory，无需再改 converter — 只需要新 spec 指 `hf_config: func_calling` 和新 env `multi_turn_tool_use` (max_turns 调高)。
