"""Tests for the assembly (per-part repair + boolean union) engine."""
import numpy as np
import pymeshlab
import pytest
import trimesh

from meshfixer.backends import get_backend
from meshfixer.diagnostics import analyze_mesh
from meshfixer.formats import load_mesh, save_mesh
from meshfixer.repair import RepairConfig, repair_mesh


def _meshset(*meshes: trimesh.Trimesh) -> pymeshlab.MeshSet:
    combined = trimesh.util.concatenate(meshes)
    ms = pymeshlab.MeshSet()
    ms.add_mesh(
        pymeshlab.Mesh(
            vertex_matrix=np.asarray(combined.vertices, dtype=np.float64),
            face_matrix=np.asarray(combined.faces, dtype=np.int32),
        )
    )
    return ms


def _volume(ms: pymeshlab.MeshSet) -> float:
    m = ms.current_mesh()
    return trimesh.Trimesh(m.vertex_matrix(), m.face_matrix(), process=False).volume


@pytest.fixture
def overlapping_boxes():
    a = trimesh.creation.box(extents=(2, 2, 2))
    b = trimesh.creation.box(extents=(2, 2, 2))
    b.apply_translation((1, 0, 0))
    return a, b


def test_assembly_backend_registered():
    assert get_backend("assembly").name == "assembly"


def test_assembly_unions_overlapping_bodies(overlapping_boxes):
    ms = _meshset(*overlapping_boxes)

    result = repair_mesh(ms, RepairConfig(), engine="assembly")

    assert result.success
    stats = analyze_mesh(ms)
    assert stats.is_watertight
    assert stats.non_manifold_edge_count == 0
    # union of two 8-unit cubes overlapping by 4 units
    assert _volume(ms) == pytest.approx(12.0, rel=1e-4)


def test_assembly_drops_zero_volume_slivers(overlapping_boxes):
    # back-to-back triangle pair touching a box edge: zero volume junk
    tri = np.array([[1, 1, 1], [1, -1, 1], [1, 0, 3]], dtype=float)
    sliver = trimesh.Trimesh(
        vertices=np.vstack([tri, tri]), faces=[[0, 1, 2], [5, 4, 3]], process=False
    )
    ms = _meshset(*overlapping_boxes, sliver)

    result = repair_mesh(ms, RepairConfig(), engine="assembly")

    assert result.success
    assert analyze_mesh(ms).is_watertight
    assert any("sliver" in w for w in result.warnings)


def test_assembly_repairs_open_part_before_union(overlapping_boxes):
    a, b = overlapping_boxes
    open_b = b.copy()
    open_b.update_faces(np.arange(len(open_b.faces)) != 0)  # punch a 3-edge hole

    ms = _meshset(a, open_b)

    result = repair_mesh(ms, RepairConfig(), engine="assembly")

    assert result.success
    assert analyze_mesh(ms).is_watertight
    assert _volume(ms) == pytest.approx(12.0, rel=1e-4)


def test_assembly_fails_cleanly_when_nothing_solid():
    tri = trimesh.Trimesh(vertices=[[0, 0, 0], [1, 0, 0], [0, 1, 0]], faces=[[0, 1, 2]])
    ms = _meshset(tri)

    result = repair_mesh(ms, RepairConfig(), engine="assembly")

    assert not result.success


def test_3mf_roundtrip_keeps_coincident_vertices_separate(tmp_path):
    # Two cubes sharing one edge: manifold only if the edge's vertices stay
    # duplicated per body. Welding them on save/load makes that edge
    # non-manifold (4 faces on one edge).
    a = trimesh.creation.box(extents=(1, 1, 1))
    b = trimesh.creation.box(extents=(1, 1, 1))
    b.apply_translation((1, 1, 0))
    ms = _meshset(a, b)
    assert analyze_mesh(ms).non_manifold_edge_count == 0

    out = tmp_path / "edge_touch.3mf"
    save_mesh(ms, out)
    reloaded = load_mesh(out)

    assert analyze_mesh(reloaded).non_manifold_edge_count == 0


def test_assembly_warns_with_hint_when_body_hole_exceeds_limit(overlapping_boxes):
    a, _ = overlapping_boxes
    sphere = trimesh.creation.icosphere(subdivisions=3, radius=1.0)
    sphere.apply_translation((5, 0, 0))
    # carve a cap off the sphere: hole boundary far larger than the limit below
    keep = sphere.triangles_center[:, 2] < 0.7
    sphere.update_faces(keep)
    sphere.remove_unreferenced_vertices()
    ms = _meshset(a, sphere)

    result = repair_mesh(ms, RepairConfig(max_hole_size=5), engine="assembly")

    assert result.success
    dropped = [w for w in result.warnings if "could not be made solid" in w]
    assert dropped, result.warnings
    assert "--max-hole-size" in dropped[0]
    assert "volume" in dropped[0]
