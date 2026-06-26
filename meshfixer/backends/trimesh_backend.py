from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pymeshlab

import numpy as np
import trimesh
import trimesh.repair

from meshfixer.backends.base import Backend
from meshfixer.repair import RepairConfig, RepairResult


class TrimeshBackend(Backend):
    """Mesh repair backend using trimesh library."""

    name = "trimesh"

    def repair(
        self, ms: "pymeshlab.MeshSet", config: RepairConfig
    ) -> RepairResult:
        """Repair a mesh using trimesh operations.

        Args:
            ms: PyMeshLab MeshSet containing the mesh to repair
            config: Repair configuration specifying which operations to perform

        Returns:
            RepairResult with success status and any warnings
        """
        warnings = []

        try:
            # Extract mesh data from pymeshlab.MeshSet
            mesh = ms.current_mesh()
            vertices = np.array(mesh.vertex_matrix(), dtype=np.float64)
            faces = np.array(mesh.face_matrix(), dtype=np.int32)

            # Create trimesh.Trimesh
            tm = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)

            # Apply repair operations based on config
            try:
                if config.remove_duplicates:
                    # Merge duplicate vertices
                    tm.merge_vertices()
                    # Remove degenerate faces (zero-area faces)
                    tm.remove_degenerate_faces()
                    # Remove duplicate faces
                    tm.remove_duplicate_faces()
                    warnings.append("Removed duplicate vertices and faces")
            except Exception as e:
                warnings.append(f"Error removing duplicates: {str(e)}")

            try:
                if config.fix_normals:
                    # Fix normals: ensure consistent winding
                    trimesh.repair.fix_normals(tm)
                    # Fix winding order
                    tm.fix_normals()
                    warnings.append("Fixed normals and winding order")
            except Exception as e:
                warnings.append(f"Error fixing normals: {str(e)}")

            try:
                if config.close_holes:
                    # Fill holes in the mesh
                    trimesh.repair.fill_holes(tm)
                    warnings.append("Filled holes in mesh")
            except Exception as e:
                warnings.append(f"Error filling holes: {str(e)}")

            # Reload repaired mesh back into pymeshlab.MeshSet
            repaired_vertices = np.array(tm.vertices, dtype=np.float64)
            repaired_faces = np.array(tm.faces, dtype=np.int32)

            # Clear and reload into pymeshlab
            import pymeshlab

            repaired_mesh = pymeshlab.Mesh(
                vertex_matrix=repaired_vertices, face_matrix=repaired_faces
            )
            ms.clear()
            ms.add_mesh(repaired_mesh)

            return RepairResult(success=True, warnings=warnings)

        except Exception as e:
            return RepairResult(success=False, warnings=[f"Repair failed: {str(e)}"])
