from dataclasses import dataclass, field, asdict
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pymeshlab


@dataclass
class RepairConfig:
    remove_duplicates: bool = True
    fix_normals: bool = True
    close_holes: bool = True
    max_hole_size: int = 30


@dataclass
class RepairResult:
    success: bool
    warnings: list[str] = field(default_factory=list)


def repair_mesh(ms: "pymeshlab.MeshSet", config: RepairConfig) -> RepairResult:
    import pymeshlab

    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as f:
        temp_path = Path(f.name)

    try:
        ms.save_current_mesh(str(temp_path))

        result_json = subprocess.run(
            [sys.executable, "-m", "meshfixer._repair_worker",
             str(temp_path),
             json.dumps(asdict(config))],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result_json.returncode != 0:
            return RepairResult(success=False, warnings=[result_json.stderr])

        result_data = json.loads(result_json.stdout)

        ms_new = pymeshlab.MeshSet()
        ms_new.load_new_mesh(str(temp_path))
        mesh = ms_new.current_mesh()

        ms.clear()
        ms.add_mesh(mesh)

        return RepairResult(
            success=result_data["success"],
            warnings=result_data.get("warnings", [])
        )

    finally:
        temp_path.unlink(missing_ok=True)
