# GUI tests create a PySide6 (Qt6) QApplication. Once pymeshlab, which bundles
# Qt5, is loaded in the same process this segfaults, so tests/gui runs in its
# own process via tests/test_gui_isolated.py.
collect_ignore = ["gui"]
