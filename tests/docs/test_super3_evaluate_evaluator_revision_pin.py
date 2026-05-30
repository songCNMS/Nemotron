"""Static checks for Super3 evaluate NeMo Evaluator doc link pins."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

EVALUATE_DOC = REPO_ROOT / "docs/nemotron/super3/evaluate.md"
EVALUATOR_SHA = "eb3ddf2acc7f2e1fa03aeba168afea636562779c"
REPRO_GUIDE_PATH = (
    "packages/nemo-evaluator-launcher/examples/nemotron/"
    "nemotron-3-super/reproducibility.md"
)
MUTABLE_REPRO_GUIDE_URL = (
    "https://github.com/NVIDIA-NeMo/Evaluator/blob/main/" f"{REPRO_GUIDE_PATH}"
)
PINNED_REPRO_GUIDE_URL = (
    "https://github.com/NVIDIA-NeMo/Evaluator/blob/"
    f"{EVALUATOR_SHA}/{REPRO_GUIDE_PATH}"
)
REPRO_GUIDE_URL_RE = re.compile(
    r"https://github\.com/NVIDIA-NeMo/Evaluator/blob/([^/\s)]+)/"
    + re.escape(REPRO_GUIDE_PATH)
)


def test_super3_evaluate_pins_evaluator_reproducibility_links() -> None:
    text = EVALUATE_DOC.read_text(encoding="utf-8")

    assert MUTABLE_REPRO_GUIDE_URL not in text
    revisions = REPRO_GUIDE_URL_RE.findall(text)
    assert revisions == [EVALUATOR_SHA, EVALUATOR_SHA, EVALUATOR_SHA]
    assert text.count(PINNED_REPRO_GUIDE_URL) == 3

    assert "# Stage 4: Evaluation" in text
    assert "Nemotron 3 Super" in text
    assert "NeMo Evaluator" in text
    assert "nemo-evaluator-launcher" in text
