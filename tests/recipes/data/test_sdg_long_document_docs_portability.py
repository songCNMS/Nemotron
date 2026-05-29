from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
LONG_DOCUMENT_DIR = REPO_ROOT / "src/nemotron/recipes/data/sdg/long-document"
README = LONG_DOCUMENT_DIR / "README.md"
OCR_CONFIG = LONG_DOCUMENT_DIR / "config/02-ocr.yaml"
PORTABLE_ROOT = "${NEMO_RUN_DIR:-.}/output/data/sdg/long-document"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_long_document_docs_do_not_use_developer_lustre_paths() -> None:
    for path in (README, OCR_CONFIG):
        text = _read(path)
        assert "/lustre/" not in text, f"{path} still contains a concrete /lustre/ example"


def test_long_document_docs_use_portable_output_examples() -> None:
    readme_text = _read(README)
    ocr_config_text = _read(OCR_CONFIG)

    for suffix in (
        "seeds",
        "seeds/seed_per_page.parquet",
        "ocr",
        "single_page_qa",
        "judged_single_page_qa",
        "chat_template.jinja",
        "internal/long-document-understanding-sdg/v1",
    ):
        assert f"{PORTABLE_ROOT}/{suffix}" in readme_text

    assert f"{PORTABLE_ROOT}/seeds/seed_per_page.parquet" in ocr_config_text


def test_long_document_docs_preserve_cli_commands_and_options() -> None:
    readme_text = _read(README)
    ocr_config_text = _read(OCR_CONFIG)

    for snippet in (
        "nemotron data sdg long-document seed",
        "nemotron data sdg long-document ocr",
        "nemotron data sdg long-document single-page-qa",
        "nemotron data sdg long-document judge",
        "--batch prep",
        "--serve",
        "--serve-config",
        "--config config/02-ocr.yaml",
        "vllm_endpoint=",
        "seed_path=",
        "artifact_path=",
        "output_dir=",
    ):
        assert snippet in readme_text

    for snippet in (
        "nemotron data sdg long-document ocr --run dlw -c 02-ocr",
        "vllm_endpoint=http://node:8000/v1",
        "seed_path=",
        "num_records=100",
    ):
        assert snippet in ocr_config_text
