# task_knowledge

<!-- METADATA:SESSION=1 -->

## 编写规则

- 仅记录跨 session 仍然有用的、且无法通过读代码/git log 直接得出的事实。
- 临时进度放 history_log.md，不要写到这里。

## 知识条目

### `<tool_call>` 在模板里出现两次的 footgun

`nano3.jinja` (和现在的 `super3.jinja`) 在 system 块里把 `<tool_call>` 当 format example 字符串注入 ：

```
If you choose to call a function ONLY reply in the following format with NO suffix:

<tool_call>
<function=example_function_name>
...
</tool_call>
```

写 render-time test 时直接 `rendered.index("<tool_call>")` 会抓到这段 example，不是 assistant 真正发出的 tool call。要 anchor 真 tool call 必须从 `<|im_start|>assistant` 之后 search。`tests/data_prep/test_chat_template_super3.py::test_super3_template_renders_four_role_conversation` 就踩过这个；以后写新模板 render 测试也要注意。

### `_BUILTIN_TEMPLATES` 扩展点

`src/nemotron/data_prep/core/chat_sft_shard_core.py::_apply_chat_template` 用 `_BUILTIN_TEMPLATES = {"nano3", "super3"}`。

加新的 builtin 模板 (e.g. `omni3`、`super_v4`)：

1. 在 `templates/` 加 `.jinja` 文件
2. 把名字加进 `_BUILTIN_TEMPLATES`
3. 模板文件名约定是 `{name}.jinja`，resolver 直接拼名字而不需要 case 分支

外部模板 (路径或 inline string) 走原有的 `Path(chat_template).exists()` / `else inline` 分支，不动。

### Super3 vs Nano3 verbatim 假设

`task012_super3_chat_template` Session 1 落地 `super3.jinja` 是 `nano3.jinja` 的 byte-identical body copy (前置 2 行 jinja 注释)。`test_super3_body_is_currently_verbatim_copy_of_nano3` 测试通过 strip 头部 jinja 注释后比对 body 一致。

主动 diverge 时 (Session 2+)：

- 在 `super3.jinja` 编辑想改的部分。
- 把 `test_super3_body_is_currently_verbatim_copy_of_nano3` 改成 "assert specific differences" (e.g. assert tool_response 边界改成某个新 token)，或直接 `pytest.skip` 注明 "Super3 has diverged from Nano3 at `<commit>`"。
- 不要去碰 `nano3.jinja` — 那是 Nano3 recipe 的独立资产，Super3 改 nano3 等于跨 recipe 隐式耦合，破规则。
