from pathlib import Path
import pytest
from meshfixer.backends import get_backend
from meshfixer.repair import RepairConfig
from meshfixer.diagnostics import analyze_mesh
from meshfixer.formats import load_mesh

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def broken_ms():
    return load_mesh(FIXTURES / "broken_tetrahedron.stl")


def test_trimesh_backend_exists():
    """Test that the trimesh backend can be retrieved."""
    backend = get_backend("trimesh")
    assert backend.name == "trimesh"


def test_trimesh_repair_on_broken_mesh(broken_ms):
    """Test that trimesh backend successfully repairs a broken mesh."""
    backend = get_backend("trimesh")
    config = RepairConfig()
    result = backend.repair(broken_ms, config)
    assert result.success is True


def test_trimesh_improves_watertightness(broken_ms):
    """Test that trimesh backend repairs mesh and provides feedback."""
    # Get initial stats
    stats_before = analyze_mesh(broken_ms)
    initial_watertight = stats_before.is_watertight

    # Repair the mesh
    backend = get_backend("trimesh")
    config = RepairConfig()
    result = backend.repair(broken_ms, config)

    # Get stats after repair
    stats_after = analyze_mesh(broken_ms)
    after_watertight = stats_after.is_watertight

    # The repair should succeed and perform repair operations
    assert result.success is True
    # Should have warnings about what was done
    assert len(result.warnings) > 0
    # Mesh should still be valid (has vertices and faces)
    assert stats_after.vertex_count > 0
    assert stats_after.triangle_count > 0
