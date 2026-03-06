from pathlib import Path
import runpy


ROOT = Path(__file__).parent
APP_FILE = ROOT / "app" / "streamlit_app.py"
runpy.run_path(str(APP_FILE), run_name="__main__")
