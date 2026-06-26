from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QFileDialog
)


class FileDropWidget(QWidget):
    file_selected = Signal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(60)

        layout = QHBoxLayout(self)
        self._label = QLabel("Drop STL or 3MF file here")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse)
        layout.addWidget(self._label, stretch=1)
        layout.addWidget(browse_btn)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open mesh file", "",
            "Mesh Files (*.stl *.3mf);;All Files (*)",
        )
        if path:
            self.file_selected.emit(Path(path))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0].toLocalFile().lower()
            if url.endswith((".stl", ".3mf")):
                event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            self.file_selected.emit(Path(urls[0].toLocalFile()))

    def set_filename(self, path: Path):
        self._label.setText(str(path.name))
