from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QCheckBox, QLabel, QSpinBox, QPushButton
)
from meshfixer.repair import RepairConfig


class RepairPanel(QWidget):
    repair_requested = Signal()
    save_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)

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
