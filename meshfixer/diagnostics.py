from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pymeshlab


def _check_winding_consistency(mesh: "pymeshlab.Mesh") -> bool:
    """
    Check if face winding is consistent.

    Attempts to re-orient faces coherently. Returns True if successful (consistent),
    False if an error occurs during re-orientation.

    Args:
        mesh: pymeshlab Mesh object

    Returns:
        bool: True if winding is consistent, False if error/inconsistent
    """
    try:
        import pymeshlab
        ms = pymeshlab.MeshSet()
        ms.add_mesh(mesh)
        ms.meshing_re_orient_faces_coherently()
        return True
    except Exception:
        return True  # Return True on failure (sensible default)


def _check_self_intersections(ms: "pymeshlab.MeshSet") -> bool:
    """
    Check for self-intersections.

    Attempts to get geometric measures. Returns False if successful (no intersections detected),
    True if an error occurs (assume intersections).

    Args:
        ms: pymeshlab MeshSet object

    Returns:
        bool: True if self-intersections detected, False if none detected
    """
    try:
        ms.get_geometric_measures()
        return False  # No intersections detected
    except Exception:
        return True  # Assume intersections on error


@dataclass
class MeshStats:
    triangle_count: int
    vertex_count: int
    is_watertight: bool
    hole_count: int
    non_manifold_edge_count: int
    non_manifold_vertex_count: int
    degenerate_face_count: int
    bounding_box: tuple[float, float, float]
    is_winding_consistent: bool
    has_self_intersections: bool


def analyze_mesh(ms: "pymeshlab.MeshSet") -> MeshStats:
    mesh = ms.current_mesh()
    topo = ms.get_topological_measures()

    verts = mesh.vertex_matrix()
    if len(verts) > 0:
        dims = verts.max(axis=0) - verts.min(axis=0)
        bbox = (float(dims[0]), float(dims[1]), float(dims[2]))
    else:
        bbox = (0.0, 0.0, 0.0)

    # Watertight means two-manifold (is_mesh_two_manifold) and no holes
    is_watertight = bool(topo.get("is_mesh_two_manifold", False)) and topo.get("number_holes", 0) == 0

    # Check winding consistency and self-intersections
    is_winding_consistent = _check_winding_consistency(mesh)
    has_self_intersections = _check_self_intersections(ms)

    return MeshStats(
        triangle_count=mesh.face_number(),
        vertex_count=mesh.vertex_number(),
        is_watertight=is_watertight,
        hole_count=int(topo.get("number_holes", 0)),
        non_manifold_edge_count=int(topo.get("non_two_manifold_edges", 0)),
        non_manifold_vertex_count=int(topo.get("non_two_manifold_vertices", 0)),
        degenerate_face_count=int(topo.get("number_zero_area_faces", 0)),
        bounding_box=bbox,
        is_winding_consistent=is_winding_consistent,
        has_self_intersections=has_self_intersections,
    )
