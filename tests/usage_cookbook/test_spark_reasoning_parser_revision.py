from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SPARK_GUIDE = REPO_ROOT / "usage-cookbook/Nemotron-3-Super/SparkDeploymentGuide/README.md"

EXPECTED_REPO = "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4"
EXPECTED_REVISION = "4f0cf9daaeb7a4d5e23f80a00e7ed15f0e03caf6"
EXPECTED_FILE = "super_v3_reasoning_parser.py"
EXPECTED_URL = (
    f"https://huggingface.co/{EXPECTED_REPO}/resolve/{EXPECTED_REVISION}/{EXPECTED_FILE}"
)


def _spark_guide_text() -> str:
    return SPARK_GUIDE.read_text(encoding="utf-8")


def _reasoning_parser_wget_urls(text: str) -> list[str]:
    return re.findall(r"wget\s+(https://huggingface\.co/\S+/super_v3_reasoning_parser\.py)", text)


def test_spark_reasoning_parser_downloads_are_commit_pinned() -> None:
    urls = _reasoning_parser_wget_urls(_spark_guide_text())

    assert urls == [EXPECTED_URL, EXPECTED_URL]
    for url in urls:
        assert EXPECTED_REPO in url
        assert EXPECTED_REVISION in url
        assert re.search(r"/resolve/[0-9a-f]{40}/super_v3_reasoning_parser\.py$", url)


def test_spark_reasoning_parser_downloads_have_no_floating_main_ref() -> None:
    text = _spark_guide_text()

    assert "/raw/main/super_v3_reasoning_parser.py" not in text
    assert "/resolve/main/super_v3_reasoning_parser.py" not in text
    assert "/main/super_v3_reasoning_parser.py" not in text


def test_spark_guide_keeps_vllm_and_trt_llm_sections() -> None:
    text = _spark_guide_text()

    assert "## vLLM" in text
    assert "## TensorRT-LLM" in text
