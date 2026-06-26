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

## Repair Capabilities

**Handles well:**
- Simple holes (up to 30 edges by default)
- Basic non-manifold edges
- Duplicate vertices/faces
- Flipped/inconsistent face normals

**Limitations:**
- Complex structural damage (Bambu-slicer detectable issues may persist)
- Severely non-manifold meshes may not become fully watertight
- Very large holes or self-intersecting geometry require manual repair

For meshes with persistent topological errors, use specialized tools:
- [Netfabb Basic](https://www.autodesk.com/products/fusion-360/free-trial) (free online)
- [Formware](https://www.formware.co/) 
- [Blender](https://www.blender.org/) (manual with modeling tools)

## Repair Pipeline

Automated 8-step repair:
1. Remove duplicate vertices/faces/null faces
2. Remove unreferenced vertices
3. Repair non-manifold edges
4. Repair non-manifold vertices (if filter available)
5. Fix face normals
6. Close holes

All steps configurable via CLI flags.

## Repair Backends

MeshFixer supports multiple repair backends:
- **meshlab** (default): PyMeshLab-based repairs
- **trimesh**: Python trimesh library
- **pymeshfix** (optional): GPL-licensed mesh repair library

To use pymeshfix, install it separately:
```bash
pip install pymeshfix
```
Note: pymeshfix is GPL-licensed and requires separate installation.

## License

GPL-3.0
