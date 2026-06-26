from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pymeshlab

from meshfixer.repair import RepairConfig, RepairResult


class Backend(ABC):
    """Abstract base class for mesh repair backends."""

    name: str

    @abstractmethod
    def repair(
        self, ms: "pymeshlab.MeshSet", config: RepairConfig
    ) -> RepairResult:
        """Repair a mesh according to the provided configuration.

        Args:
            ms: PyMeshLab MeshSet containing the mesh to repair
            config: Repair configuration specifying which operations to perform

        Returns:
            RepairResult with success status and any warnings
        """
        pass
