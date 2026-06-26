# MeshFixer

Cross-platform mesh repair tool for 3D printing workflows. Fixes broken STL and 3MF files (holes, non-manifold geometry, flipped normals, duplicates).

## Features

- **CLI**: Repair meshes from terminal
  ```bash
  meshfixer repair broken.stl fixed.stl
  meshfixer diagnose broken.stl
  ```
- **GUI**: Desktop application with before/after stats
- **Cross-platform**: Windows, macOS, Linux

## Installation

Download release binaries from [GitHub Releases](https://github.com/cprice70/meshfixer/releases):
- macOS: `.dmg`
- Windows: `.exe` installer
- Linux: `.AppImage`

Or build from source:
```bash
git clone https://github.com/cprice70/meshfixer
cd meshfixer
uv sync
uv run meshfixer gui  # or: uv run meshfixer repair file.stl
```

## Known Issues

### macOS: GUI unavailable (Qt framework conflict)
The GUI has a segmentation fault on macOS due to bundled Qt frameworks (pymeshlab Qt5 + PySide6 Qt6 collision).

**Workaround**: Use CLI mode on macOS
```bash
uv run meshfixer repair input.stl output.stl
```

GUI works on Windows and Linux.

## Repair Pipeline

Automated 8-step repair:
1. Remove duplicate vertices/faces/null faces
2. Remove unreferenced vertices
3. Repair non-manifold edges
4. Repair non-manifold vertices (if filter available)
5. Fix face normals
6. Close holes

All steps configurable via CLI flags.

## License

GPL-3.0
