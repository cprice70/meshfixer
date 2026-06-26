from meshfixer.backends.base import Backend
from meshfixer.backends.trimesh_backend import TrimeshBackend
from meshfixer.backends.meshlab_backend import MeshlabBackend

BACKENDS = {
    "trimesh": TrimeshBackend,
    "meshlab": MeshlabBackend,
}


def get_backend(name: str) -> Backend:
    """Get a backend by name.

    Args:
        name: Name of the backend to retrieve

    Returns:
        Backend instance for the specified backend

    Raises:
        ValueError: If the backend name is not found
    """
    if name not in BACKENDS:
        raise ValueError(
            f"Unknown backend: {name}. Available backends: {', '.join(BACKENDS.keys())}"
        )
    return BACKENDS[name]()
