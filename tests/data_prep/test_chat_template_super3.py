"""Render-time + resolver tests for the Super3 chat template (task012).

`super3.jinja` ships as a verbatim copy of `nano3.jinja` with a 2-line
header comment for lineage. These tests pin the contract:

- `_apply_chat_template("super3", ...)` loads the new file (resolver
  knows the name).
- The four-role conversation (system / user / assistant w/ tool_calls /
  tool) renders into the expected `<|im_start|>` / `<tool_call>` /
  `<tool_response>` boundary tokens in order.
- The `tool_call_repair_negative` round-trip is preserved: a user message
  carrying an escaped invalid artifact (per
  `escape_tool_markup_for_prompt`) survives Jinja rendering as quoted
  text, not as a real tool call.
- The body of `super3.jinja` (header stripped) is currently equal to
  `nano3.jinja`; the test will fail loudly the first time someone
  deliberately diverges, which is the signal to remove this byte-identity
  assertion.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from jinja2.sandbox import ImmutableSandboxedEnvironment

REPO_ROOT = Path(__file__).resolve().parents[2]
NANO3_PATH = REPO_ROOT / "src/nemotron/data_prep/templates/nano3.jinja"
SUPER3_PATH = REPO_ROOT / "src/nemotron/data_prep/templates/super3.jinja"

# Strips a contiguous block of leading whitespace + `{# ... #}` comments;
# anchors to start of file so it only touches the header.
_LEADING_JINJA_COMMENT_RE = re.compile(r"^(?:\s*\{\#[^#]*\#\}\s*)+", re.DOTALL)


def _strip_jinja_header_comments(text: str) -> str:
    return _LEADING_JINJA_COMMENT_RE.sub("", text, count=1)


def _render(template_text: str, **kwargs: object) -> str:
    env = ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True)
    return env.from_string(template_text).render(**kwargs)


def test_apply_chat_template_resolves_super3_name() -> None:
    """task012 resolver: `chat_template: super3` loads the new file.

    `chat_sft_shard_core` transitively imports `nemotron.data_prep.blend`
    which requires pydantic; skip cleanly when the full data-prep stack
    isn't installed in the test env. NemTron has it.
    """
    import pytest

    pytest.importorskip("pydantic")
    from nemotron.data_prep.core.chat_sft_shard_core import _apply_chat_template

    class _StubTokenizer:
        chat_template: str | None = None

    stub = _StubTokenizer()
    _apply_chat_template(stub, "super3")

    assert stub.chat_template == SUPER3_PATH.read_text(encoding="utf-8")
    # And nano3 still resolves correctly — no regression.
    nano = _StubTokenizer()
    _apply_chat_template(nano, "nano3")
    assert nano.chat_template == NANO3_PATH.read_text(encoding="utf-8")


def test_chat_template_kwargs_are_expanded_for_tokenizer_native_templates() -> None:
    """Tokenizer-native Qwen templates receive top-level kwargs.

    Super3/Nano3 read the nested ``chat_template_kwargs`` object, but
    HuggingFace tokenizer-native templates commonly read variables such as
    ``enable_thinking`` directly. The data-prep helper must provide both
    shapes when it renders messages.
    """
    from nemotron.data_prep.core.chat_template import split_template_into_messages

    class _RecordingTokenizer:
        def __init__(self) -> None:
            self.calls: list[dict[str, Any]] = []

        def apply_chat_template(
            self,
            messages: Sequence[Mapping[str, Any]],
            *,
            tokenize: bool = False,
            add_generation_prompt: bool = False,
            tools: Sequence[Mapping[str, Any]] | None = None,
            **kwargs: Any,
        ) -> str | list[int]:
            assert tokenize is False
            assert tools is None
            self.calls.append(dict(kwargs))
            rendered = ""
            for message in messages:
                rendered += (
                    f"<|im_start|>{message['role']}\n"
                    f"{message.get('content', '')}<|im_end|>\n"
                )
            if add_generation_prompt:
                rendered += "<|im_start|>assistant\n"
            return rendered

    template_kwargs = {
        "enable_thinking": False,
        "truncate_history_thinking": False,
    }
    tokenizer = _RecordingTokenizer()
    chunks = split_template_into_messages(
        [
            {"role": "user", "content": "Solve 1+1."},
            {"role": "assistant", "content": "2"},
        ],
        tokenizer,
        start_from_last_user=False,
        chat_template_kwargs=template_kwargs,
    )

    assert [chunk["role"] for chunk in chunks] == ["user", "assistant"]
    assert tokenizer.calls
    for call in tokenizer.calls:
        assert call["enable_thinking"] is False
        assert call["truncate_history_thinking"] is False
        assert call["chat_template_kwargs"] == template_kwargs


def test_super3_template_renders_four_role_conversation() -> None:
    """plan §5.1 + task012 acceptance: the four supervision shapes
    (system / user / assistant w/ tool_calls / tool turn) render into
    `<|im_start|>`, `<tool_call>`, and `<tool_response>` boundary tokens
    in the right order."""
    template_text = SUPER3_PATH.read_text(encoding="utf-8")
    messages = [
        {"role": "system", "content": "You are a helpful tool-using assistant."},
        {"role": "user", "content": "What is the weather in Paris?"},
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "call_0",
                    "type": "function",
                    "function": {"name": "lookup", "arguments": {"city": "Paris"}},
                }
            ],
        },
        {"role": "tool", "content": '{"city":"Paris","weather":"sunny"}'},
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "lookup",
                "description": "Look up weather by city.",
                "parameters": {
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"],
                },
            },
        }
    ]

    rendered = _render(
        template_text,
        messages=messages,
        tools=tools,
        add_generation_prompt=False,
        chat_template_kwargs={"enable_thinking": False, "truncate_history_thinking": False},
    )

    # Role boundaries appear in conversation order. Note: the template
    # injects a literal `<tool_call>` block in the system message as a
    # format example, so we anchor the *real* assistant tool call by
    # searching only after `<|im_start|>assistant`.
    p_system = rendered.index("<|im_start|>system")
    p_user = rendered.index("<|im_start|>user")
    p_assistant = rendered.index("<|im_start|>assistant")
    p_real_tool_call_open = rendered.index("<tool_call>", p_assistant)
    p_real_tool_call_close = rendered.index("</tool_call>", p_real_tool_call_open)
    p_tool_response_open = rendered.index("<tool_response>", p_real_tool_call_close)
    p_tool_response_close = rendered.index("</tool_response>", p_tool_response_open)
    positions = [
        p_system,
        p_user,
        p_assistant,
        p_real_tool_call_open,
        p_real_tool_call_close,
        p_tool_response_open,
        p_tool_response_close,
    ]
    assert positions == sorted(positions), (
        "expected boundary tokens to appear in conversation order, got positions: " + str(positions)
    )
    # The tool schema is injected into the system block (Nano3/Super3 convention)
    assert "<tools>" in rendered
    assert "<function>" in rendered and "</function>" in rendered
    # The assistant tool call carries the call name + argument value
    assert "<function=lookup>" in rendered
    assert "<parameter=city>" in rendered
    assert "Paris" in rendered  # appears in both the user prompt and the tool response


def test_super3_template_keeps_escaped_tool_markup_as_quoted_text() -> None:
    """task005 (`905de2d`) fix: when `tool_call_repair_negative` puts an
    escaped invalid artifact in the user message, the chat template must
    keep it as quoted text — NOT interpret it as a real `<tool_call>` that
    Jinja would emit verbatim. The escape is HTML-entity style
    (`&lt;tool_call&gt;`), so the rendered output should contain the
    entity but NOT a bare opening `<tool_call>` block in the user turn.
    """
    template_text = SUPER3_PATH.read_text(encoding="utf-8")
    escaped_artifact = (
        "&lt;tool_call&gt;\n<function=lookup>\n"
        "<parameter=city>\nPari\n</parameter>\n"
        "</function>\n&lt;/tool_call&gt;"
    )
    messages = [
        {"role": "system", "content": "You repair tool calls."},
        {
            "role": "user",
            "content": (
                "A previous assistant produced the invalid tool-use artifact below. "
                "Identify that it is invalid and repair it.\n\n"
                f"Invalid artifact:\n{escaped_artifact}"
            ),
        },
    ]
    rendered = _render(
        template_text,
        messages=messages,
        tools=[],
        add_generation_prompt=False,
        chat_template_kwargs={"enable_thinking": False},
    )

    # The escaped entities should survive — they are what the model
    # actually sees as the invalid artifact to repair.
    assert "&lt;tool_call&gt;" in rendered
    assert "&lt;/tool_call&gt;" in rendered
    # And there must be no raw `<tool_call>` block emitted in the user
    # turn (the only real ones come from assistant tool_calls; this test
    # has none, so there should be zero `<tool_call>` open tags).
    assert rendered.count("<tool_call>") == 0


def test_super3_body_is_currently_verbatim_copy_of_nano3() -> None:
    """task012 ships `super3.jinja` as a verbatim copy of `nano3.jinja`
    (plus a 2-line header comment). Strip the jinja header comments from
    super3 and confirm the body matches nano3 byte-for-byte.

    When Super3 deliberately diverges from Nano3, the diverging PR should
    update this test (assert specific differences) or remove it. Until
    then, accidental drift between the two templates is a regression.
    """
    nano = NANO3_PATH.read_text(encoding="utf-8")
    super3_body = _strip_jinja_header_comments(SUPER3_PATH.read_text(encoding="utf-8"))
    assert super3_body == nano, (
        "super3.jinja body diverged from nano3.jinja unexpectedly; if intentional, "
        "update or remove `test_super3_body_is_currently_verbatim_copy_of_nano3`."
    )
