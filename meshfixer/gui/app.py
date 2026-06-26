import sys
from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QMainWindow,
    QMessageBox, QStatusBar, QVBoxLayout, QWidget,
)

from meshfixer.diagnostics import analyze_mesh
from meshfixer.formats import UnsupportedFormatError, load_mesh, save_mesh
from meshfixer.gui.panel_input import FileDropWidget
from meshfixer.gui.panel_repair import RepairPanel
from meshfixer.gui.panel_stats import StatsPanel
from meshfixer.repair import RepairConfig, repair_mesh


class _RepairWorker(QThread):
    finished = Signal(bool, list)

    def __init__(self, ms, config: RepairConfig):
        super().__init__()
        self._ms = ms
        self._config = config

    def run(self):
        from meshfixer.repair import repair_mesh as _repair
        result = _repair(self._ms, self._config, engine="meshlab")
        self.finished.emit(result.success, result.warnings)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MeshFixer")
        self.resize(700, 460)

        self._ms = None
        self._input_path: Path | None = None
        self._worker: _RepairWorker | None = None

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self._input_panel = FileDropWidget()
        self._stats_panel = StatsPanel()
        self._repair_panel = RepairPanel()

        layout.addWidget(self._input_panel)
        layout.addWidget(self._stats_panel)
        layout.addWidget(self._repair_panel)

        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage("Ready — drop a mesh file or click Browse.")

        self._input_panel.file_selected.connect(self._on_file_selected)
        self._repair_panel.repair_requested.connect(self._on_repair)
        self._repair_panel.save_requested.connect(self._on_save)

    def _on_file_selected(self, path: Path):
        self._input_path = path
        self._stats_panel.clear()
        self._status.showMessage(f"Loading {path.name}…")
        QApplication.processEvents()
        try:
            self._ms = load_mesh(path)
        except (FileNotFoundError, UnsupportedFormatError) as e:
            self._status.showMessage(f"Error: {e}")
            return
        stats = analyze_mesh(self._ms)
        self._stats_panel.update_before(stats)
        self._input_panel.set_filename(path)
        self._status.showMessage(f"Loaded {path.name} — {stats.triangle_count:,} triangles")

    def _on_repair(self):
        if self._ms is None:
            self._status.showMessage("Load a file first.")
            return
        config = self._repair_panel.get_config()
        self._status.showMessage("Repairing…")
        QApplication.processEvents()
        self._worker = _RepairWorker(self._ms, config)
        self._worker.finished.connect(self._on_repair_done)
        self._worker.start()

    def _on_repair_done(self, success: bool, warnings: list):
        if not success:
            self._status.showMessage("Repair failed. " + "; ".join(warnings))
            return
        stats = analyze_mesh(self._ms)
        self._stats_panel.update_after(stats)
        msg = "Repair complete."
        if warnings:
            msg += " Warnings: " + "; ".join(warnings)
        self._status.showMessage(msg)

    def _on_save(self):
        if self._ms is None:
            self._status.showMessage("Load and repair a file first.")
            return
        default = str(
            self._input_path.with_stem(self._input_path.stem + "_fixed")
        ) if self._input_path else "repaired.stl"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save repaired mesh", default,
            "Mesh Files (*.stl *.3mf);;All Files (*)",
        )
        if not path:
            return
        try:
            save_mesh(self._ms, Path(path))
            self._status.showMessage(f"Saved: {path}")
        except UnsupportedFormatError as e:
            QMessageBox.critical(self, "Save Error", str(e))


def run_app() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
