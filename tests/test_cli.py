import json
import subprocess
import sys
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"
PYTHON = sys.executable


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, "-m", "meshfixer"] + args,
        capture_output=True,
        text=True,
    )


def test_diagnose_exits_zero():
    result = run(["diagnose", str(FIXTURES / "broken_tetrahedron.stl")])
    assert result.returncode == 0


def test_diagnose_output_contains_triangle():
    result = run(["diagnose", str(FIXTURES / "broken_tetrahedron.stl")])
    assert "triangle" in result.stdout.lower()


def test_diagnose_json_flag():
    result = run(["diagnose", str(FIXTURES / "broken_tetrahedron.stl"), "--json"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "triangle_count" in data
    assert "is_watertight" in data


def test_repair_creates_output(tmp_path):
    out = tmp_path / "fixed.stl"
    result = run(["repair", str(FIXTURES / "broken_tetrahedron.stl"), str(out)])
    assert result.returncode == 0
    assert out.exists()


def test_repair_missing_file_exits_3():
    result = run(["repair", "nonexistent.stl"])
    assert result.returncode == 3


def test_diagnose_missing_file_exits_3():
    result = run(["diagnose", "nonexistent.stl"])
    assert result.returncode == 3
