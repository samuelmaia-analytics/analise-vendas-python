from __future__ import annotations

from pathlib import Path

from src.sales_analytics.data_dictionary import build_data_dictionary_markdown, export_data_dictionary


def test_build_data_dictionary_markdown_includes_raw_and_curated_sections():
    markdown = build_data_dictionary_markdown()

    assert "# Data Dictionary" in markdown
    assert "## Raw Dataset" in markdown
    assert "### `fato_vendas.csv`" in markdown
    assert "ORDERDATE" in markdown


def test_export_data_dictionary_writes_markdown(tmp_path: Path):
    output_path = export_data_dictionary(tmp_path / "data_dictionary.md")

    assert output_path.exists()
    assert "Curated Artifacts" in output_path.read_text(encoding="utf-8")
