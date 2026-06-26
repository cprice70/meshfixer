"""Mesh repair worker process. Runs in subprocess to isolate pymeshlab from GUI."""
import sys
import json
from pathlib import Path
import pymeshlab
from meshfixer.repair import RepairConfig, RepairResult


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"success": False, "warnings": ["Invalid arguments"], "ms": None}))
        sys.exit(1)

    mesh_path = Path(sys.argv[1])
    config_dict = json.loads(sys.argv[2])
    config = RepairConfig(**config_dict)

    warnings = []
    try:
        ms = pymeshlab.MeshSet()
        ms.load_new_mesh(str(mesh_path))

        if config.remove_duplicates:
            ms.meshing_remove_duplicate_vertices()
            ms.meshing_remove_duplicate_faces()
            ms.meshing_remove_null_faces()
            ms.meshing_remove_unreferenced_vertices()

        ms.meshing_repair_non_manifold_edges()
        ms.meshing_repair_non_manifold_vertices()

        if config.close_holes:
            try:
                ms.meshing_close_holes(maxholesize=config.max_hole_size)
            except:
                pass

        if config.fix_normals:
            try:
                ms.meshing_re_orient_faces_coherently()
            except:
                pass

        # Save result to same path (overwrites original)
        ms.save_current_mesh(str(mesh_path))

        result = {"success": True, "warnings": warnings}
    except Exception as e:
        result = {"success": False, "warnings": [str(e)]}

    print(json.dumps(result))


if __name__ == "__main__":
    main()
