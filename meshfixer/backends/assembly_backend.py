"""Assembly repair: repair each body separately, then boolean-union them.

Multi-body exports (CAD assemblies) often contain overlapping or touching
bodies plus zero-volume junk triangles. Whole-mesh repair treats the
contact regions as non-manifold defects and deletes faces there, opening
holes it then cannot close. Repairing per body and unioning the solids
resolves the overlaps geometrically instead.
"""
from typing import TYPE_CHECKING

import numpy as np
import trimesh
import trimesh.repair

from meshfixer.backends.base import Backend
from meshfixer.repair import RepairConfig, RepairResult

if TYPE_CHECKING:
    import pymeshlab

# Bodies whose |volume| is below this fraction of the whole mesh's bounding
# box volume are treated as zero-volume slivers and discarded.
_SLIVER_VOLUME_FRACTION = 1e-9


def _repair_part(part: trimesh.Trimesh, config: RepairConfig) -> trimesh.Trimesh:
    import pymeshlab

    ms = pymeshlab.MeshSet()
    ms.add_mesh(pymeshlab.Mesh(vertex_matrix=part.vertices, face_matrix=part.faces))
    if config.remove_duplicates:
        ms.meshing_remove_duplicate_vertices()
        ms.meshing_remove_duplicate_faces()
        ms.meshing_remove_null_faces()
        ms.meshing_remove_unreferenced_vertices()
    for _ in range(10):
        ms.meshing_repair_non_manifold_edges()
        ms.meshing_repair_non_manifold_vertices()
        topo = ms.get_topological_measures()
        if topo["non_two_manifold_edges"] + topo["non_two_manifold_vertices"] == 0:
            break
    if config.close_holes:
        try:
            ms.meshing_close_holes(maxholesize=config.max_hole_size)
        except pymeshlab.PyMeshLabException:
            pass

    cm = ms.current_mesh()
    repaired = trimesh.Trimesh(cm.vertex_matrix(), cm.face_matrix(), process=True)
    if config.close_holes:
        # PyMeshLab's filler skips some small or non-simple holes; trimesh
        # handles the triangle/quad-sized ones it leaves behind.
        trimesh.repair.fill_holes(repaired)
    if config.fix_normals:
        trimesh.repair.fix_normals(repaired)
    return repaired


def _to_manifold(part: trimesh.Trimesh):
    import manifold3d

    return manifold3d.Manifold(
        manifold3d.Mesh(
            vert_properties=np.asarray(part.vertices, dtype=np.float32),
            tri_verts=np.asarray(part.faces, dtype=np.uint32),
        )
    )


class AssemblyBackend(Backend):
    """Per-body repair followed by a manifold3d boolean union."""

    name = "assembly"

    def repair(self, ms: "pymeshlab.MeshSet", config: RepairConfig) -> RepairResult:
        import manifold3d
        import pymeshlab

        mesh = ms.current_mesh()
        whole = trimesh.Trimesh(mesh.vertex_matrix(), mesh.face_matrix(), process=True)
        sliver_volume = _SLIVER_VOLUME_FRACTION * float(np.prod(whole.extents))
        parts = whole.split(only_watertight=False)

        solids = []
        slivers = 0
        repaired = 0
        unrepairable = 0
        unrepairable_bbox_volume = 0.0
        for part in parts:
            if len(part.faces) < 4 or abs(part.volume) <= sliver_volume:
                slivers += 1
                continue

            candidate = part
            if not candidate.is_watertight:
                candidate = _repair_part(part, config)
                repaired += 1

            if candidate.is_watertight:
                if candidate.volume < 0:
                    candidate.invert()
                manifold = _to_manifold(candidate)
            else:
                # manifold3d tolerates some defects (e.g. CAD sliver edges)
                # that PyMeshLab and trimesh cannot clean up.
                manifold = _to_manifold(part)

            if manifold.status() != manifold3d.Error.NoError:
                unrepairable += 1
                unrepairable_bbox_volume += float(np.prod(part.extents))
                continue
            solids.append(manifold)

        warnings = [f"Found {len(parts)} bodies"]
        if slivers:
            warnings.append(f"Dropped {slivers} zero-volume sliver bodies")
        if repaired:
            warnings.append(f"Repaired {repaired} open bodies before union")
        if unrepairable:
            warnings.append(
                f"Dropped {unrepairable} bodies that could not be made solid "
                f"(bounding-box volume {unrepairable_bbox_volume:.1f}); they are "
                f"missing from the output. Their holes may exceed the fill limit: "
                f"retry with a larger --max-hole-size (currently {config.max_hole_size})"
            )

        if not solids:
            return RepairResult(
                success=False, warnings=warnings + ["No solid bodies to union"]
            )

        union = manifold3d.Manifold.batch_boolean(solids, manifold3d.OpType.Add)
        if union.status() != manifold3d.Error.NoError:
            return RepairResult(
                success=False, warnings=warnings + [f"Union failed: {union.status()}"]
            )
        out = union.to_mesh()
        warnings.append(f"Unioned {len(solids)} solid bodies")

        # Keep manifold3d's vertex indexing as-is: bodies that touch along an
        # edge rely on duplicated coincident vertices to stay manifold.
        ms.clear()
        ms.add_mesh(
            pymeshlab.Mesh(
                vertex_matrix=np.asarray(out.vert_properties[:, :3], dtype=np.float64),
                face_matrix=np.asarray(out.tri_verts, dtype=np.int32),
            )
        )
        return RepairResult(success=True, warnings=warnings)
