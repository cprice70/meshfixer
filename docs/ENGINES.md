# Repair Engines

MeshFixer offers three repair backends, each with distinct capabilities, performance characteristics, and licensing implications.

## Overview

| Engine | License | Default | Speed | Complexity | Non-Manifold | Self-Intersections | Configurable |
|--------|---------|---------|-------|------------|--------------|--------------------|----|
| **meshlab** | GPL-3.0 | ✓ | Medium | High | Excellent | Good | Yes (via filters) |
| **trimesh** | MIT | - | Fast | Medium | Good | Good | Limited |
| **pymeshfix** | GPL-3.0 | - | Slow | Very High | Excellent | Excellent | No |

## meshlab (Default)

**Engine Name:** `meshlab`

### Overview

PyMeshLab-based repair engine. This is the default engine and provides the most comprehensive set of repair operations through MeshLab's mature suite of topology and geometry filters.

### License

- **GPL-3.0** (same as MeshFixer)
- PyMeshLab wraps the MeshLab C++ library, licensed under GPL-3.0
- No additional licensing concerns beyond MeshFixer's GPL-3.0

### Performance

- **Speed:** Medium (0.5-2 seconds for typical models)
- **Memory:** Moderate (scales with mesh complexity)
- **Scalability:** Good up to 1M triangles

### Repair Capabilities

#### Excellent
- Duplicate vertex/face removal
- Non-manifold edge repair
- Non-manifold vertex repair (when MeshLab filter available)
- Face normal consistency and flipping
- Small to medium hole filling (default: up to 30 edges)

#### Good
- Self-intersection detection
- Bounding box calculation
- Watertightness verification

#### Known Limitations
- Complex structural damage may require manual intervention
- Some topologies may resist full watertightness

### Usage

```bash
# Default usage
meshfixer repair broken.stl fixed.stl

# Specify explicitly
meshfixer repair broken.stl fixed.stl --engine meshlab

# Adjust hole fill threshold
meshfixer repair broken.stl fixed.stl --max-hole-size 50

# Skip hole filling
meshfixer repair broken.stl fixed.stl --skip-hole-fill
```

### Configuration

The meshlab backend is highly configurable:
- `--max-hole-size`: Maximum hole perimeter (in edges) to attempt filling
- `--skip-hole-fill`: Disable hole filling step
- All other repair steps are applied by default

## trimesh

**Engine Name:** `trimesh`

### Overview

The trimesh library is a lightweight Python-only implementation. It provides fast, efficient repairs without external dependencies. Best for batch processing or when performance is critical.

### License

- **MIT License** - permissive open source
- No GPL restrictions when using this backend
- Safe for proprietary/commercial use

### Performance

- **Speed:** Fast (0.1-0.5 seconds for typical models)
- **Memory:** Low (minimal overhead)
- **Scalability:** Excellent up to 10M triangles

### Repair Capabilities

#### Excellent
- Duplicate vertex removal
- Duplicate face removal
- Primitive geometry validation

#### Good
- Non-manifold edge detection
- Basic face normal consistency
- Simple watertightness operations
- Self-intersection detection

#### Limited
- Non-manifold vertex repair (basic only)
- Hole filling (very simple holes only)
- Complex topology repair

### Usage

```bash
# Using trimesh backend
meshfixer repair broken.stl fixed.stl --engine trimesh

# Trimesh is best for quick validation
meshfixer diagnose broken.stl  # Uses trimesh for fast analysis
```

### Configuration

The trimesh backend has minimal configuration:
- No hole filling capability
- No bypass flags for repair steps
- All geometry operations run automatically

## pymeshfix

**Engine Name:** `pymeshfix`

### Overview

PyMeshFix is a specialized C++ library for comprehensive mesh repair. It uses advanced algorithms to handle complex topological issues. Recommended for production mesh repair when GPL compliance is acceptable.

**This backend requires separate installation.**

### License

- **Dual-licensed: GPL-3.0 and Commercial**
- When using pymeshfix, your application must comply with GPL-3.0
- This applies to the entire binary distribution
- Commercial licenses available directly from pymeshfix author

### Installation

```bash
pip install pymeshfix
```

### Performance

- **Speed:** Slow (2-10 seconds for typical models)
- **Memory:** High (builds topology structure)
- **Scalability:** Good up to 500K triangles

### Repair Capabilities

#### Excellent
- Complex non-manifold edge repair
- Non-manifold vertex repair (comprehensive)
- Self-intersection removal (robust)
- Topology reconstruction
- Hole filling (advanced algorithms)
- Robust watertightness achievement

#### Good
- Duplicate removal
- Face normal consistency
- Bounding box calculation

#### Considerations
- Slower than other backends
- May modify geometry more aggressively
- Best for meshes with severe topology issues

### Usage

```bash
# Using pymeshfix backend (requires separate installation)
pip install pymeshfix
meshfixer repair broken.stl fixed.stl --engine pymeshfix

# For severely damaged meshes
meshfixer repair complex_damage.stl repaired.stl --engine pymeshfix
```

### Configuration

The pymeshfix backend has no configuration options:
- All repair steps applied automatically
- No hole filling threshold (built-in)
- No bypass flags available
- Uses internal optimization algorithms

## Comparison Table

### Feature Matrix

| Feature | meshlab | trimesh | pymeshfix |
|---------|---------|---------|-----------|
| Duplicate removal | ✓ | ✓ | ✓ |
| Non-manifold edges | ✓✓ | ✓ | ✓✓ |
| Non-manifold vertices | ✓✓ | ✗ | ✓✓ |
| Self-intersections | ✓ | ✓ | ✓✓ |
| Hole filling | ✓ | ✗ | ✓ |
| Normal consistency | ✓ | ✓ | ✓ |
| Configurable | ✓ | ✗ | ✗ |

### Use-Case Decision Tree

```
Does your mesh have complex non-manifold topology?
├─ YES, and GPL compliance is OK
│  └─ Use pymeshfix (most robust)
├─ YES, but need permissive license
│  └─ Use meshlab (good balance)
└─ NO, or need maximum speed
   └─ Use trimesh (fastest)

Is performance critical (batch processing)?
├─ YES
│  └─ Use trimesh
└─ NO
   └─ Use meshlab or pymeshfix based on complexity

Do you need GPL compliance?
├─ Must avoid GPL
│  └─ Use trimesh
└─ GPL is acceptable
   └─ Use meshlab or pymeshfix
```

## Performance Benchmarks

For a typical 3D printer model (50K triangles with holes):

```
meshlab:   0.8s  (full repair with hole filling)
trimesh:   0.2s  (cleanup only, no hole fill)
pymeshfix: 4.5s  (comprehensive topology repair)
```

Times are approximate and vary by model complexity.

## Troubleshooting

### Engine Not Available

If you receive "engine not found", verify installation:

```bash
# Check pymeshfix installation (if needed)
pip list | grep pymeshfix

# Reinstall if missing
pip install pymeshfix
```

### Mesh Still Broken After Repair

1. **Try a different engine:** pymeshfix handles more complex cases
2. **Check diagnostics:** `meshfixer diagnose broken.stl`
3. **Consider specialized tools:** For severe damage, use Netfabb Basic, Formware, or Blender

### Performance Issues

- **meshlab too slow:** Try trimesh for fast preprocessing
- **trimesh insufficient:** Use meshlab or pymeshfix for better topology handling
- **pymeshfix too slow:** Reduce mesh size or use meshlab as faster alternative

## License Compliance Notes

### Using meshlab or trimesh

- No additional licensing beyond MeshFixer's GPL-3.0
- Safe for all use cases where GPL-3.0 is acceptable

### Using pymeshfix

- Dual-licensed (GPL-3.0 and Commercial)
- **GPL-3.0 path:** Your application and distributions must include GPL-3.0 notice
- **Commercial path:** Contact pymeshfix for separate commercial licensing
- Choose based on your project's licensing model

## See Also

- [README.md](../README.md) - Usage examples and installation
- [MeshLab documentation](https://www.meshlab.net/)
- [trimesh documentation](https://trimesh.org/)
- [PyMeshFix on GitHub](https://github.com/pmp-library/pmp-library)
