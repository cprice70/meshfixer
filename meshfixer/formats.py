from pathlib import Path
import pymeshlab

SUPPORTED_EXTENSIONS = {".stl", ".3mf"}


class UnsupportedFormatError(Exception):
    pass


def load_mesh(path: Path) -> pymeshlab.MeshSet:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFormatError(f"Unsupported format: {ext}")
    if ext == ".3mf":
        return _load_3mf(path)
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(str(path))
    return ms


def save_mesh(ms: pymeshlab.MeshSet, path: Path) -> None:
    path = Path(path)
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFormatError(f"Unsupported format: {ext}")
    if ext == ".3mf":
        _save_3mf(ms, path)
        return
    ms.save_current_mesh(str(path))


def _load_3mf(path: Path) -> pymeshlab.MeshSet:
    import trimesh
    import numpy as np

    scene = trimesh.load(str(path), force="mesh")
    if isinstance(scene, trimesh.Scene):
        combined = trimesh.util.concatenate(list(scene.geometry.values()))
    else:
        combined = scene

    vertices = np.array(combined.vertices, dtype=np.float64)
    faces = np.array(combined.faces, dtype=np.int32)
    ms = pymeshlab.MeshSet()
    m = pymeshlab.Mesh(vertex_matrix=vertices, face_matrix=faces)
    ms.add_mesh(m)
    return ms


def _save_3mf(ms: pymeshlab.MeshSet, path: Path) -> None:
    import trimesh
    import numpy as np

    mesh = ms.current_mesh()
    vertices = np.array(mesh.vertex_matrix(), dtype=np.float64)
    faces = np.array(mesh.face_matrix(), dtype=np.int32)
    tm = trimesh.Trimesh(vertices=vertices, faces=faces)
    tm.export(str(path))
