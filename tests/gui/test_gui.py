"""GUI tests for repair-engine selection. Run headless via Qt's offscreen platform."""
import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from meshfixer.backends import BACKENDS  # noqa: E402
from meshfixer.gui.app import default_save_path  # noqa: E402
from meshfixer.gui.panel_repair import RepairPanel  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def test_engine_picker_lists_available_backends(qapp):
    panel = RepairPanel()
    assert panel.available_engines() == list(BACKENDS)


def test_engine_picker_defaults_to_meshlab(qapp):
    assert RepairPanel().get_engine() == "meshlab"


def test_engine_picker_returns_selected_engine(qapp):
    panel = RepairPanel()
    panel.set_engine("assembly")
    assert panel.get_engine() == "assembly"


def test_default_save_path_uses_3mf_after_assembly_repair():
    # STL re-merges the duplicated vertices that keep touching bodies manifold
    assert default_save_path(Path("/x/Part.stl"), engine="assembly") == Path("/x/Part_fixed.3mf")


def test_default_save_path_keeps_input_extension_otherwise():
    assert default_save_path(Path("/x/Part.stl"), engine="meshlab") == Path("/x/Part_fixed.stl")
