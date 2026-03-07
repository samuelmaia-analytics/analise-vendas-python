from pathlib import Path


def test_app_entrypoint_points_to_streamlit_app():
    app_file = Path(__file__).resolve().parents[1] / "app.py"
    content = app_file.read_text(encoding="utf-8")
    assert 'APP_FILE = ROOT / "app" / "streamlit_app.py"' in content
    assert "runpy.run_path" in content
