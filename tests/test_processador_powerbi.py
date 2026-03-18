from pathlib import Path


def test_processador_powerbi_uses_official_batch_pipeline():
    script_file = Path(__file__).resolve().parents[1] / "scripts" / "processador_powerbi.py"
    content = script_file.read_text(encoding="utf-8")
    assert "run_batch_pipeline" in content
    assert "SystemExit(main())" in content
