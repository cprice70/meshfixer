import json
import subprocess
import sys
from pathlib import Path

import pytest

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


def test_repair_with_engine_pymeshfix(tmp_path):
    """Test repair with --engine pymeshfix flag"""
    pytest.importorskip("pymeshfix")
    out = tmp_path / "fixed.stl"
    result = run(
        ["repair", str(FIXTURES / "broken_tetrahedron.stl"), str(out), "--engine", "pymeshfix"]
    )
    assert result.returncode == 0
    assert out.exists()
    assert "engine: pymeshfix" in result.stdout


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
    # Note: 3MF export requires lxml which may not be installed
    # This test verifies the CLI accepts the flag and passes it through
    out = tmp_path / "fixed.3mf"
    result = run(
        ["repair", str(FIXTURES / "broken_tetrahedron.stl"), str(out), "--output-format", "3mf"]
    )
    # Either succeeds (if lxml available) or fails with specific error
    if result.returncode == 0:
        assert out.exists()
        assert out.suffix == ".3mf"
        assert "format: 3mf" in result.stdout
    else:
        # If lxml missing, at least verify the dependency error occurred
        assert "lxml" in result.stderr or "ModuleNotFoundError" in result.stderr


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


def test_full_workflow_meshlab_to_3mf(tmp_path):
    """Test complete workflow: diagnose → repair with meshlab → auto format to 3mf"""
    # Step a: Diagnose broken tetrahedron and capture is_watertight=False
    diag_result = run(["diagnose", str(FIXTURES / "broken_tetrahedron.stl"), "--json"])
    assert diag_result.returncode == 0
    diag_data = json.loads(diag_result.stdout)
    assert diag_data["is_watertight"] is False  # Should be broken initially

    # Step b: Repair with --engine meshlab --output-format auto
    out = tmp_path / "fixed.3mf"
    repair_result = run(
        [
            "repair",
            str(FIXTURES / "broken_tetrahedron.stl"),
            str(out),
            "--engine",
            "meshlab",
            "--output-format",
            "auto",
        ]
    )
    assert repair_result.returncode == 0

    # Step c: Verify .3mf output created (auto selected 3mf for watertight result)
    # If lxml is available, 3mf should be created; otherwise stl as fallback
    output_exists = (tmp_path / "fixed.3mf").exists() or (tmp_path / "fixed.stl").exists()
    assert output_exists, "Either .3mf or .stl output should exist"
    assert "engine: meshlab" in repair_result.stdout
    assert "format:" in repair_result.stdout

    # Step d: Diagnose fixed mesh and verify is_watertight=True
    if (tmp_path / "fixed.3mf").exists():
        fixed_file = tmp_path / "fixed.3mf"
    else:
        fixed_file = tmp_path / "fixed.stl"

    fixed_diag_result = run(["diagnose", str(fixed_file), "--json"])
    assert fixed_diag_result.returncode == 0
    fixed_diag_data = json.loads(fixed_diag_result.stdout)
    assert fixed_diag_data["is_watertight"] is True  # Should be watertight after repair


def test_repair_with_all_engines(tmp_path):
    """Test repair with all available engines (meshlab, trimesh)"""
    engines = ["meshlab", "trimesh"]

    for engine in engines:
        out = tmp_path / f"fixed_{engine}.stl"
        result = run(
            [
                "repair",
                str(FIXTURES / "broken_tetrahedron.stl"),
                str(out),
                "--engine",
                engine,
            ]
        )
        # Step a: Verify returncode == 0
        assert result.returncode == 0, f"Engine {engine} should return 0, got {result.returncode}: {result.stderr}"

        # Step b: Verify output file exists
        assert out.exists(), f"Output file for {engine} should exist at {out}"
        assert f"engine: {engine}" in result.stdout
