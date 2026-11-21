from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QCheckBox, QComboBox, QLabel, QSpinBox, QPushButton
)
from meshfixer.backends import BACKENDS
from meshfixer.repair import RepairConfig

_ENGINE_TOOLTIPS = {
    "meshlab": "PyMeshLab whole-mesh repair (general purpose)",
    "trimesh": "Fast, lightweight trimesh repair",
    "pymeshfix": "pymeshfix repair (GPL)",
    "assembly": "Repair each body separately, then union them. "
                "Use for multi-part exports; save as 3MF",
}


class RepairPanel(QWidget):
    repair_requested = Signal()
    save_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)

        self._engine = QComboBox()
        for name in BACKENDS:
            self._engine.addItem(name)
            self._engine.setItemData(
                self._engine.count() - 1, _ENGINE_TOOLTIPS.get(name, ""), Qt.ToolTipRole
            )
        self.set_engine("meshlab")

        self._remove_dups = QCheckBox("Remove duplicates")
        self._remove_dups.setChecked(True)
        self._fix_normals = QCheckBox("Fix normals")
        self._fix_normals.setChecked(True)
        self._close_holes = QCheckBox("Close holes")
        self._close_holes.setChecked(True)

        self._hole_size = QSpinBox()
        self._hole_size.setRange(1, 10000)
        self._hole_size.setValue(30)

        repair_btn = QPushButton("Repair")
        repair_btn.clicked.connect(self.repair_requested)
        save_btn = QPushButton("Save As...")
        save_btn.clicked.connect(self.save_requested)

        layout.addWidget(QLabel("Engine:"))
        layout.addWidget(self._engine)
        layout.addWidget(self._remove_dups)
        layout.addWidget(self._fix_normals)
        layout.addWidget(self._close_holes)
        layout.addWidget(QLabel("Max hole size:"))
        layout.addWidget(self._hole_size)
        layout.addStretch()
        layout.addWidget(repair_btn)
        layout.addWidget(save_btn)

    def get_config(self) -> RepairConfig:
        return RepairConfig(
            remove_duplicates=self._remove_dups.isChecked(),
            fix_normals=self._fix_normals.isChecked(),
            close_holes=self._close_holes.isChecked(),
            max_hole_size=self._hole_size.value(),
        )

    def available_engines(self) -> list[str]:
        return [self._engine.itemText(i) for i in range(self._engine.count())]

    def get_engine(self) -> str:
        return self._engine.currentText()

    def set_engine(self, name: str) -> None:
        index = self._engine.findText(name)
        if index < 0:
            raise ValueError(f"Unknown engine: {name}")
        self._engine.setCurrentIndex(index)
