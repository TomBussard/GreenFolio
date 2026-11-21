"""Start the dashboard beside this launcher."""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    directory = Path(__file__).resolve().parent
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(directory / "app.py")],
        cwd=directory,
        check=True,
    )
