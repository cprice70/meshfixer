from dataclasses import dataclass
import pymeshlab


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


def analyze_mesh(ms: pymeshlab.MeshSet) -> MeshStats:
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

    return MeshStats(
        triangle_count=mesh.face_number(),
        vertex_count=mesh.vertex_number(),
        is_watertight=is_watertight,
        hole_count=int(topo.get("number_holes", 0)),
        non_manifold_edge_count=int(topo.get("non_two_manifold_edges", 0)),
        non_manifold_vertex_count=int(topo.get("non_two_manifold_vertices", 0)),
        degenerate_face_count=int(topo.get("number_zero_area_faces", 0)),
        bounding_box=bbox,
    )
