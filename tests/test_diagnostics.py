from pathlib import Path
import pymeshlab
import pytest
from meshfixer.diagnostics import MeshStats, analyze_mesh

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def broken_ms():
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(str(FIXTURES / "broken_tetrahedron.stl"))
    return ms


def test_meshstats_is_dataclass(broken_ms):
    stats = analyze_mesh(broken_ms)
    assert isinstance(stats, MeshStats)


def test_broken_tetrahedron_triangle_count(broken_ms):
    stats = analyze_mesh(broken_ms)
    assert stats.triangle_count == 3


def test_broken_tetrahedron_vertex_count(broken_ms):
    stats = analyze_mesh(broken_ms)
    assert stats.vertex_count == 4


def test_broken_tetrahedron_not_watertight(broken_ms):
    stats = analyze_mesh(broken_ms)
    assert stats.is_watertight is False


def test_broken_tetrahedron_has_hole(broken_ms):
    stats = analyze_mesh(broken_ms)
    assert stats.hole_count >= 1


def test_bounding_box_is_tuple_of_three_floats(broken_ms):
    stats = analyze_mesh(broken_ms)
    assert len(stats.bounding_box) == 3
    assert all(isinstance(v, float) for v in stats.bounding_box)
