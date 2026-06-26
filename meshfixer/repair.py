from dataclasses import dataclass, field
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


def repair_mesh(
    ms: "pymeshlab.MeshSet", config: RepairConfig, engine: str = "meshlab"
) -> RepairResult:
    """Repair a mesh using the specified backend engine.

    Args:
        ms: PyMeshLab MeshSet containing the mesh to repair
        config: Repair configuration specifying which operations to perform
        engine: Name of the repair backend to use (default: "meshlab")

    Returns:
        RepairResult with success status and any warnings
    """
    from meshfixer.backends import get_backend

    backend = get_backend(engine)
    return backend.repair(ms, config)
