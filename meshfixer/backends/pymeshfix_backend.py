from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pymeshlab

import numpy as np

from meshfixer.backends.base import Backend
from meshfixer.repair import RepairConfig, RepairResult

# Try to import pymeshfix (optional dependency)
try:
    import pymeshfix
except ImportError:
    pymeshfix = None


class PymeshfixBackend(Backend):
    """Mesh repair backend using pymeshfix library (GPL-licensed)."""

    name = "pymeshfix"

    def __init__(self):
        """Initialize the pymeshfix backend.

        Raises:
            ImportError: If pymeshfix is not installed
        """
        if pymeshfix is None:
            raise ImportError(
                "pymeshfix is not installed. Install with: pip install pymeshfix"
            )

    def repair(
        self, ms: "pymeshlab.MeshSet", config: RepairConfig
    ) -> RepairResult:
        """Repair a mesh using pymeshfix operations.

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

            # Create pymeshfix.MeshFix
            pf = pymeshfix.MeshFix(vertices, faces)

            # Apply repair operations based on config
            try:
                if config.remove_duplicates:
                    # Clean the mesh (removes duplicate vertices, etc.)
                    pf.clean()
                    warnings.append("Removed duplicate vertices")
            except Exception as e:
                warnings.append(f"Error removing duplicates: {str(e)}")

            try:
                # Main repair operation (fixes holes, non-manifold edges, etc.)
                pf.repair()
                warnings.append("Performed mesh repair")
            except Exception as e:
                warnings.append(f"Error during repair: {str(e)}")

            # Reload repaired mesh back into pymeshlab.MeshSet
            repaired_vertices = np.array(pf.points, dtype=np.float64)
            repaired_faces = np.array(pf.faces, dtype=np.int32)

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
