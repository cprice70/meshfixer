from dataclasses import dataclass, field
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


def repair_mesh(ms: pymeshlab.MeshSet, config: RepairConfig) -> RepairResult:
    warnings: list[str] = []
    try:
        if config.remove_duplicates:
            ms.meshing_remove_duplicate_vertices()
            ms.meshing_remove_duplicate_faces()
            ms.meshing_remove_null_faces()
            ms.meshing_remove_unreferenced_vertices()

        ms.meshing_repair_non_manifold_edges()

        # Split non-manifold vertices — filter name varies by PyMeshLab version.
        # If this raises, check available filters with: ms.print_filter_list()
        try:
            ms.meshing_repair_non_manifold_by_splitting()
        except AttributeError:
            warnings.append("Non-manifold vertex repair skipped (filter unavailable in this PyMeshLab version)")

        if config.fix_normals:
            ms.meshing_re_orient_faces_coherently()

        if config.close_holes:
            ms.meshing_close_holes(maxholesize=config.max_hole_size)

    except Exception as e:
        warnings.append(str(e))
        return RepairResult(success=False, warnings=warnings)

    return RepairResult(success=True, warnings=warnings)
