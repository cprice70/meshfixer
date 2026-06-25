from pathlib import Path
import pytest
from meshfixer.repair import RepairConfig, RepairResult, repair_mesh
from meshfixer.diagnostics import analyze_mesh
from meshfixer.formats import load_mesh

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def broken_ms():
    return load_mesh(FIXTURES / "broken_tetrahedron.stl")


@pytest.fixture
def watertight_ms():
    return load_mesh(FIXTURES / "watertight_tetrahedron.stl")


def test_repair_returns_result(broken_ms):
    result = repair_mesh(broken_ms, RepairConfig())
    assert isinstance(result, RepairResult)


def test_repair_result_has_success_flag(broken_ms):
    result = repair_mesh(broken_ms, RepairConfig())
    assert isinstance(result.success, bool)


def test_watertight_stays_watertight(watertight_ms):
    result = repair_mesh(watertight_ms, RepairConfig())
    assert result.success is True
    stats = analyze_mesh(watertight_ms)
    assert stats.is_watertight is True


def test_repair_config_defaults():
    config = RepairConfig()
    assert config.remove_duplicates is True
    assert config.fix_normals is True
    assert config.close_holes is True
    assert config.max_hole_size == 30


def test_repair_with_hole_fill_disabled(broken_ms):
    config = RepairConfig(close_holes=False)
    result = repair_mesh(broken_ms, config)
    assert isinstance(result, RepairResult)
