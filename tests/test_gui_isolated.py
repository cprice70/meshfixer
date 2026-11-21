import subprocess
import sys
from pathlib import Path

GUI_TESTS = Path(__file__).parent / "gui"


def test_gui_suite_in_separate_process():
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(GUI_TESTS)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
