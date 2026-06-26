import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pymeshlab

from meshfixer.backends.base import Backend
from meshfixer.repair import RepairConfig, RepairResult
from dataclasses import asdict


class MeshlabBackend(Backend):
    """Mesh repair backend using PyMeshLab library via subprocess worker."""

    name = "meshlab"

    def repair(
        self, ms: "pymeshlab.MeshSet", config: RepairConfig
    ) -> RepairResult:
        """Repair a mesh using PyMeshLab operations in a subprocess.

        Args:
            ms: PyMeshLab MeshSet containing the mesh to repair
            config: Repair configuration specifying which operations to perform

        Returns:
            RepairResult with success status and any warnings
        """
        import pymeshlab

        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as f:
            temp_path = Path(f.name)

        try:
            # Save the mesh to a temporary file
            ms.save_current_mesh(str(temp_path))

            # Call the repair worker subprocess
            result_json = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "meshfixer._repair_worker",
                    str(temp_path),
                    json.dumps(asdict(config)),
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result_json.returncode != 0:
                return RepairResult(success=False, warnings=[result_json.stderr])

            result_data = json.loads(result_json.stdout)

            # Load the repaired mesh back into a MeshSet
            ms_new = pymeshlab.MeshSet()
            ms_new.load_new_mesh(str(temp_path))
            mesh = ms_new.current_mesh()

            # Replace the original mesh with the repaired one
            ms.clear()
            ms.add_mesh(mesh)

            return RepairResult(
                success=result_data["success"],
                warnings=result_data.get("warnings", []),
            )

        finally:
            temp_path.unlink(missing_ok=True)
