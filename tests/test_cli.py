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


def test_repair_with_engine_meshlab(tmp_path):
    """Test repair with --engine meshlab flag"""
    out = tmp_path / "fixed.stl"
    result = run(
        ["repair", str(FIXTURES / "broken_tetrahedron.stl"), str(out), "--engine", "meshlab"]
    )
    assert result.returncode == 0
    assert out.exists()
    assert "engine: meshlab" in result.stdout


def test_repair_with_engine_trimesh(tmp_path):
    """Test repair with --engine trimesh flag"""
    out = tmp_path / "fixed.stl"
    result = run(
        ["repair", str(FIXTURES / "broken_tetrahedron.stl"), str(out), "--engine", "trimesh"]
    )
    assert result.returncode == 0
    assert out.exists()
    assert "engine: trimesh" in result.stdout


def test_repair_output_format_auto(tmp_path):
    """Test repair with --output-format auto (chooses format based on watertightness)"""
    # For broken mesh, auto should choose stl
    out = tmp_path / "fixed.stl"
    result = run(
        ["repair", str(FIXTURES / "broken_tetrahedron.stl"), str(out), "--output-format", "auto"]
    )
    assert result.returncode == 0
    assert out.exists()
    # The format reported depends on whether the repair resulted in watertight mesh
    assert "format:" in result.stdout


def test_repair_output_format_stl(tmp_path):
    """Test repair with explicit --output-format stl"""
    out = tmp_path / "fixed.stl"
    result = run(
        ["repair", str(FIXTURES / "broken_tetrahedron.stl"), str(out), "--output-format", "stl"]
    )
    assert result.returncode == 0
    assert out.exists()
    assert out.suffix == ".stl"
    assert "format: stl" in result.stdout


def test_repair_output_format_3mf(tmp_path):
    """Test repair with explicit --output-format 3mf (CLI parsing only)"""
    # Note: 3MF export requires networkx which may not be installed
    # This test verifies the CLI accepts the flag and passes it through
    out = tmp_path / "fixed.3mf"
    result = run(
        ["repair", str(FIXTURES / "broken_tetrahedron.stl"), str(out), "--output-format", "3mf"]
    )
    # Either succeeds (if networkx available) or fails with specific error
    if result.returncode == 0:
        assert out.exists()
        assert out.suffix == ".3mf"
        assert "format: 3mf" in result.stdout
    else:
        # If networkx missing, at least verify the flag was parsed
        assert "format: 3mf" in result.stdout or "networkx" in result.stderr


def test_repair_defaults_to_meshlab(tmp_path):
    """Test that repair defaults to meshlab engine with auto format"""
    out = tmp_path / "fixed.stl"
    result = run(["repair", str(FIXTURES / "broken_tetrahedron.stl"), str(out)])
    assert result.returncode == 0
    assert out.exists()
    assert "engine: meshlab" in result.stdout
    assert "format: stl" in result.stdout or "format: 3mf" in result.stdout


def test_full_workflow_meshlab_to_stl(tmp_path):
    """Test complete workflow: diagnose → repair with meshlab engine"""
    # First diagnose the broken mesh
    diag_result = run(["diagnose", str(FIXTURES / "broken_tetrahedron.stl"), "--json"])
    assert diag_result.returncode == 0
    diag_data = json.loads(diag_result.stdout)
    assert diag_data["is_watertight"] is False  # Should be broken initially

    # Then repair with meshlab engine (STL output)
    out = tmp_path / "fixed.stl"
    repair_result = run(
        [
            "repair",
            str(FIXTURES / "broken_tetrahedron.stl"),
            str(out),
            "--engine",
            "meshlab",
            "--output-format",
            "stl",
        ]
    )
    assert repair_result.returncode == 0
    assert out.exists()
    assert "engine: meshlab" in repair_result.stdout
    assert "format: stl" in repair_result.stdout
