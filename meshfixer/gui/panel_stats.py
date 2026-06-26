from PySide6.QtWidgets import QWidget, QHBoxLayout, QGridLayout, QLabel, QGroupBox
from meshfixer.diagnostics import MeshStats

_ROWS = [
    ("triangles", "Triangles"),
    ("vertices", "Vertices"),
    ("watertight", "Watertight"),
    ("holes", "Holes"),
    ("non_manifold", "Non-manifold"),
    ("degenerate", "Degenerate"),
]


def _make_grid(title: str) -> tuple[QGroupBox, dict[str, QLabel]]:
    box = QGroupBox(title)
    grid = QGridLayout(box)
    labels: dict[str, QLabel] = {}
    for i, (key, display) in enumerate(_ROWS):
        grid.addWidget(QLabel(display + ":"), i, 0)
        val = QLabel("—")
        grid.addWidget(val, i, 1)
        labels[key] = val
    return box, labels


class StatsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self._before_box, self._before = _make_grid("Before")
        self._after_box, self._after = _make_grid("After")
        layout.addWidget(self._before_box)
        layout.addWidget(self._after_box)

    def _fill(self, labels: dict[str, QLabel], stats: MeshStats):
        labels["triangles"].setText(f"{stats.triangle_count:,}")
        labels["vertices"].setText(f"{stats.vertex_count:,}")
        labels["watertight"].setText("✓ Yes" if stats.is_watertight else "✗ No")
        labels["holes"].setText(str(stats.hole_count))
        labels["non_manifold"].setText(
            str(stats.non_manifold_edge_count + stats.non_manifold_vertex_count)
        )
        labels["degenerate"].setText(str(stats.degenerate_face_count))

    def update_before(self, stats: MeshStats):
        self._fill(self._before, stats)

    def update_after(self, stats: MeshStats):
        self._fill(self._after, stats)

    def clear(self):
        for labels in (self._before, self._after):
            for lbl in labels.values():
                lbl.setText("—")
