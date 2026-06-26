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
- **Multi-engine support**: Choose from PyMeshLab, trimesh, or pymeshfix repair backends
- **Format support**: STL and 3MF (auto or explicit format selection)

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

## Usage Examples

### Repair with Default Engine (PyMeshLab)

```bash
meshfixer repair broken.stl fixed.stl
```

### Repair with Specific Engine

```bash
# Using trimesh backend
meshfixer repair broken.stl fixed.stl --engine trimesh

# Using pymeshfix backend (requires separate installation)
meshfixer repair broken.stl fixed.stl --engine pymeshfix
```

### Repair with Format Selection

```bash
# Force output to STL
meshfixer repair broken.stl fixed.stl --output-format stl

# Force output to 3MF
meshfixer repair broken.stl fixed.stl --output-format 3mf

# Auto-select (3MF if watertight, STL otherwise)
meshfixer repair broken.stl fixed.stl --output-format auto
```

### Diagnose Issues

```bash
# Print detailed analysis
meshfixer diagnose broken.stl

# Output as JSON
meshfixer diagnose broken.stl --json
```

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

MeshFixer supports three repair backends, each with different capabilities:

- **meshlab** (default): PyMeshLab-based repairs — best general-purpose engine
- **trimesh**: Python trimesh library — fast, lightweight option
- **pymeshfix** (optional): GPL-licensed mesh repair — specialized for complex repairs

For detailed comparison and when to use each, see [docs/ENGINES.md](docs/ENGINES.md).

### Using pymeshfix

The pymeshfix backend requires separate installation:

```bash
pip install pymeshfix
```

**Important:** pymeshfix is dual-licensed under GPL-3.0 and commercial licenses. When using pymeshfix, your project and distributions must comply with the GPL-3.0 license. This does not apply to the meshlab or trimesh backends.

## License

GPL-3.0
