"""Tests for task035 contamination pipeline Session 2 prompt scanner."""

from __future__ import annotations

import json
from pathlib import Path

from nemotron.recipes.super3.milestones.data_registries.contamination_scanner import (
    format_prompt_contamination_markdown,
    scan_prompt_corpus,
    scan_prompt_corpus_files,
    text_ngrams,
    token_ngrams,
    tokenize,
)


def test_tokenizer_and_ngram_extraction_are_deterministic() -> None:
    assert tokenize("HotpotQA: Who wrote the book?") == [
        "hotpotqa",
        "who",
        "wrote",
        "the",
        "book",
    ]
    assert token_ngrams(["a", "b", "c", "d"], 3) == {"a b c", "b c d"}
    assert text_ngrams("short prompt", 8) == {"short prompt"}


def test_scan_prompt_corpus_flags_exact_eval_prompt_as_blocker() -> None:
    prompts = [
        {
            "id": "train_hotpot_copy",
            "prompt": "Which author wrote the novel that inspired the film Blade Runner?",
        }
    ]
    eval_sets = {
        "hle": [
            {
                "id": "hle_001",
                "prompt": "Which author wrote the novel that inspired the film Blade Runner?",
            }
        ]
    }

    report = scan_prompt_corpus(
        prompts,
        eval_sets,
        ngram_size=5,
        informational_threshold=0.25,
        blocker_threshold=0.75,
    )

    assert report["counts"]["blocker"] == 1
    assert report["counts"]["informational"] == 0
    finding = report["blockers"][0]
    assert finding["prompt_id"] == "train_hotpot_copy"
    assert finding["eval_set"] == "hle"
    assert finding["eval_id"] == "hle_001"
    assert finding["score"] == 1.0
    assert finding["posture"] == "blocker"


def test_scan_prompt_corpus_flags_partial_overlap_as_informational() -> None:
    prompts = [
        {
            "id": "train_partial",
            "prompt": (
                "Solve the browser search task using citations. "
                "The final answer must mention the museum opening year."
            ),
        }
    ]
    eval_sets = {
        "browsecomp": [
            {
                "id": "browse_eval",
                "prompt": (
                    "Before solving, inspect all pages. The final answer "
                    "must mention the museum opening year and cite source URLs."
                ),
            }
        ]
    }

    report = scan_prompt_corpus(
        prompts,
        eval_sets,
        ngram_size=4,
        informational_threshold=0.3,
        blocker_threshold=0.9,
    )

    assert report["counts"]["blocker"] == 0
    assert report["counts"]["informational"] == 1
    finding = report["informational"][0]
    assert finding["posture"] == "informational"
    assert finding["score"] < 0.9
    assert "final answer must mention" in finding["matched_ngrams"]


def test_scan_prompt_corpus_reports_clean_when_below_threshold() -> None:
    report = scan_prompt_corpus(
        [{"id": "train_clean", "prompt": "Write a shell command that lists files."}],
        {"bfcl": [{"id": "bfcl_eval", "prompt": "Call the weather API function."}]},
        ngram_size=4,
        informational_threshold=0.25,
        blocker_threshold=0.75,
    )

    assert report["findings"] == []
    assert report["blockers"] == []
    assert report["informational"] == []
    assert report["counts"] == {"clean": 1, "informational": 0, "blocker": 0}


def test_scan_prompt_corpus_files_supports_local_jsonl_and_json(tmp_path: Path) -> None:
    prompts = tmp_path / "prompts.jsonl"
    prompts.write_text(
        json.dumps(
            {
                "id": "train_eval_leak",
                "prompt": (
                    "Return the exact JSON object with key final_answer "
                    "and value blue."
                ),
            }
        )
        + "\n",
        encoding="utf-8",
    )
    eval_file = tmp_path / "eval.json"
    eval_file.write_text(
        json.dumps(
            {
                "examples": [
                    {
                        "id": "json_eval",
                        "prompt": (
                            "Return the exact JSON object with key final_answer "
                            "and value blue."
                        ),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = scan_prompt_corpus_files(
        prompts,
        {"structured_outputs": eval_file},
        ngram_size=6,
    )

    assert report["counts"]["blocker"] == 1
    assert report["blockers"][0]["eval_set"] == "structured_outputs"


def test_scan_prompt_corpus_counts_are_per_prompt_not_per_pair() -> None:
    """Regression: `counts` used to mix per-pair (blocker/informational)
    and per-prompt (clean) units, so 1 prompt × N matching eval rows
    inflated blocker/informational counts by N. Fix: `counts` is now
    consistently per-prompt (worst posture wins); per-pair detail is
    available under the new `finding_counts` field.
    """
    prompts = [
        {
            "id": "train_repeated_match",
            "prompt": "Answer with the exact phrase alpha beta gamma delta",
        }
    ]
    # Three eval rows all carry the same overlapping phrase.
    eval_sets = {
        "if_eval": [
            {
                "id": "if_a",
                "prompt": "Answer with the exact phrase alpha beta gamma delta",
            },
            {
                "id": "if_b",
                "prompt": "Answer with the exact phrase alpha beta gamma delta",
            },
            {
                "id": "if_c",
                "prompt": "Answer with the exact phrase alpha beta gamma delta",
            },
        ]
    }

    report = scan_prompt_corpus(prompts, eval_sets, ngram_size=4)

    # 3 (prompt, eval) findings — finding_counts captures per-pair.
    assert len(report["findings"]) == 3
    assert report["finding_counts"]["blocker"] == 3
    assert report["finding_counts"]["informational"] == 0
    assert report["finding_counts"]["clean"] == 0

    # But only 1 prompt is contaminated — counts is per-prompt.
    assert report["counts"]["blocker"] == 1
    assert report["counts"]["informational"] == 0
    assert report["counts"]["clean"] == 0


def test_markdown_report_is_review_friendly() -> None:
    report = scan_prompt_corpus(
        [
            {
                "id": "train_copy",
                "prompt": "Answer with the exact phrase alpha beta gamma delta",
            }
        ],
        {
            "if_eval": [
                {
                    "id": "if_1",
                    "prompt": "Answer with the exact phrase alpha beta gamma delta",
                }
            ]
        },
        ngram_size=4,
    )

    text = format_prompt_contamination_markdown(report)

    assert "# Prompt Corpus Contamination Scan" in text
    assert "| blocker | train_copy | if_eval | if_1 |" in text
    assert "ngram_size" in text
