# MeshFixer — Design Spec
_Date: 2026-06-25_

## Context

Users working with 3D printing workflows routinely encounter broken mesh files — STL and 3MF files with non-manifold edges, holes, flipped normals, and degenerate geometry. Existing tools (MeshLab, Meshmixer) require manual intervention and don't have a simple "load → fix → save" experience. MeshFixer is a focused, cross-platform desktop app with a clean GUI and CLI that automates mesh repair for the most common problems.

---

## Goals

- Load STL and 3MF files
- Run an automated repair pipeline (holes, non-manifold, normals, duplicates)
- Show before/after diagnostic stats
- Save repaired file (STL or 3MF)
- Work identically via GUI or CLI
- Distribute as self-contained binaries on Windows, Linux, macOS (no Python install required)

## Non-Goals (v1)

- 3D viewport preview (planned for v2)
- Mesh editing / sculpting
- Format conversion beyond STL ↔ 3MF
- Cloud or networked processing

---

## License

GPL-3.0 (matches PyMeshLab/VCGlib dependency requirements).

---

## Tech Stack

| Layer | Choice | Reason |
|-------|--------|--------|
| Language | Python 3.12+ | Fast iteration, excellent lib ecosystem |
| Repair engine | PyMeshLab | Full MeshLab filter set (VCGlib underneath), best automated repair available |
| GUI framework | PySide6 (Qt 6) | LGPL, cross-platform native, integrates with PyMeshLab |
| 3MF I/O | `lib3mf` Python bindings | Official reference implementation (BSD-2-Clause) |
| STL I/O | PyMeshLab native | Built-in, no extra dep |
| Packaging | PyInstaller + GHA | Per-platform builds, attached to GitHub Releases |
| Project tooling | uv + pyproject.toml | Fast dep management |

---

## Project Structure

```
meshfixer/
├── meshfixer/
│   ├── __main__.py        # Entry point — CLI args or launch GUI
│   ├── repair.py          # Core repair pipeline (no GUI imports)
│   ├── diagnostics.py     # Mesh health analysis (no GUI imports)
│   ├── formats.py         # STL/3MF I/O adapter
│   └── gui/
│       ├── app.py         # QApplication + MainWindow
│       ├── panel_input.py # File drop zone + browse button
│       ├── panel_stats.py # Before/after diagnostics display
│       └── panel_repair.py# Repair options checkboxes + run/save buttons
├── tests/
│   ├── fixtures/          # Sample broken STL/3MF files
│   ├── test_repair.py
│   ├── test_diagnostics.py
│   └── test_formats.py
├── pyproject.toml
├── .github/
│   └── workflows/
│       └── release.yml    # Build + package on tag push
└── docs/
    └── superpowers/specs/
        └── 2026-06-25-meshfixer-design.md
```

**Key invariant:** `repair.py`, `diagnostics.py`, and `formats.py` have zero GUI imports. The CLI calls them directly; the GUI wraps them in a `QThread` worker. Same logic, both modes.

---

## Repair Pipeline

`repair.py` runs an ordered sequence of PyMeshLab filter calls. Each step is independently toggleable. Default pipeline:

| Step | PyMeshLab Filter | Toggle |
|------|-----------------|--------|
| 1 | Remove duplicate vertices | `meshing_remove_duplicate_vertices` | ☑ on |
| 2 | Remove duplicate faces | `meshing_remove_duplicate_faces` | ☑ on |
| 3 | Remove zero-area faces | `meshing_remove_null_faces` | ☑ on |
| 4 | Remove unreferenced vertices | `meshing_remove_unreferenced_vertices` | ☑ on |
| 5 | Repair non-manifold edges | `meshing_repair_non_manifold_edges` | ☑ on |
| 6 | Repair non-manifold vertices | `meshing_repair_non_manifold_vertices` | ☑ on |
| 7 | Re-orient faces coherently | `meshing_re_orient_faces_coherently` | ☑ on |
| 8 | Close holes | `meshing_close_holes(maxholesize=N)` | ☑ on, configurable N |

The pipeline accepts a `RepairConfig` dataclass (step toggles + max hole size) and returns a `RepairResult` (success, warnings, output mesh path).

---

## Diagnostics

`diagnostics.py` runs before and after repair. Returns a `MeshStats` dataclass:

```python
@dataclass
class MeshStats:
    triangle_count: int
    vertex_count: int
    is_watertight: bool
    hole_count: int
    non_manifold_edge_count: int
    non_manifold_vertex_count: int
    degenerate_face_count: int
    bounding_box: tuple[float, float, float]  # x, y, z dimensions
```

---

## Format I/O

`formats.py` provides `load_mesh(path) -> MeshSet` and `save_mesh(ms, path)`.

- **STL:** PyMeshLab native load/save.
- **3MF:** Load via `lib3mf` → extract geometry → pass to PyMeshLab. Save: reverse. Fall back to `trimesh` if `lib3mf` bindings unavailable.

Supported input: `.stl`, `.3mf`
Supported output: `.stl`, `.3mf` (same format as input by default)

---

## CLI Interface

```
meshfixer                              # Launch GUI (no args)
meshfixer gui                          # Launch GUI explicitly
meshfixer repair input.stl             # Repair, save as input_fixed.stl
meshfixer repair input.stl output.stl  # Repair to explicit path
meshfixer repair input.3mf             # 3MF input/output
meshfixer diagnose input.stl           # Print stats, no repair
meshfixer diagnose input.stl --json    # Machine-readable output
meshfixer repair input.stl --skip-hole-fill
meshfixer repair input.stl --max-hole-size 100
```

Exit codes: 0 success, 1 input error, 2 repair failed, 3 file not found.

---

## GUI Layout

Single window (~700×500 px), three sections:

```
┌─────────────────────────────────────────────────────┐
│  [  Drop STL or 3MF file here, or Browse...  ]     │
├────────────────────┬────────────────────────────────┤
│  BEFORE            │  AFTER                         │
│  Triangles: 12,450 │  Triangles: 12,448             │
│  Watertight: ✗ No  │  Watertight: ✓ Yes             │
│  Holes: 3          │  Holes: 0                      │
│  Non-manifold: 14  │  Non-manifold: 0               │
│  Degenerate: 2     │  Degenerate: 0                 │
├────────────────────┴────────────────────────────────┤
│  ☑ Remove duplicates  ☑ Fix normals  ☑ Close holes │
│  Max hole size: [50] triangles                      │
│  [    Repair    ]    [  Save As...  ]               │
│  Status: Ready                                      │
└─────────────────────────────────────────────────────┘
```

Repair runs in a `QThread` worker — UI stays responsive. Status bar shows progress. Save defaults to `<input_dir>/<name>_fixed.<ext>`.

---

## Distribution / Packaging

GitHub Actions `release.yml` triggers on `v*` tag push. Three parallel jobs:

| Platform | Runner | PyInstaller mode | Output artifact |
|----------|--------|-----------------|-----------------|
| macOS | `macos-latest` | `--windowed` | `.app` → `.dmg` |
| Windows | `windows-latest` | `--onefile` | `.exe` → NSIS `.exe` installer |
| Linux | `ubuntu-22.04` | `--onefile` | ELF → `.AppImage` |

All three artifacts attached to the GitHub Release automatically.

---

## Testing

- Unit tests for `repair.py` and `diagnostics.py` using fixture meshes (intentionally broken STL files checked into `tests/fixtures/`)
- Integration test: load broken STL → repair → assert `is_watertight == True`
- CLI tests: subprocess calls checking exit codes and output
- No GUI unit tests in v1 (manual testing only for GUI)

Run: `uv run pytest`

---

## Verification

End-to-end test before shipping:
1. `uv sync && uv run meshfixer diagnose tests/fixtures/broken.stl` — confirms stats output
2. `uv run meshfixer repair tests/fixtures/broken.stl /tmp/fixed.stl` — confirms repair runs
3. `uv run meshfixer diagnose /tmp/fixed.stl` — confirms `Watertight: Yes`
4. Launch GUI: `uv run meshfixer` — drag in a broken file, click Repair, verify stats update
5. Run PyInstaller build locally, launch the `.app`/`.exe` with no Python installed
