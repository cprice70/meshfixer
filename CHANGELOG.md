# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-06-25

### Features

- **Multi-backend mesh repair**: Support for meshlab (primary), trimesh, and pymeshfix (optional) backends with pluggable architecture
- **Smart export format selection**: Auto-detect optimal output format (STL vs 3MF) based on repair result watertightness
- **Enhanced diagnostic output**: Detailed mesh analysis with watertightness detection, triangle/vertex counts, and JSON export support
- **Comprehensive CLI**: Full repair and diagnostic workflows with configurable engines and output formats

### Changed

- Refactored repair logic into pluggable backend abstraction with common interface
- Extracted format detection and export logic into dedicated formats module
- Improved error handling with specific exit codes (file_not_found=3)
- Standardized output format reporting in CLI responses

### Dependencies

- Added `trimesh>=4.0` for mesh analysis and repair
- Added `pymeshfix>=0.18` (optional) for alternative repair backend
- Added `networkx>=3.0` for mesh graph operations
- Added `lxml>=4.9` for 3MF file format support

### Fixed

- Corrected pymeshlab filter name in meshlab backend implementation

### Breaking Changes

- None. v0.2.0 is fully backward compatible with v0.1.0.

## [0.1.0] - 2026-06-20

### Features

- Initial release with basic STL mesh repair using pymeshlab
- CLI interface for diagnose and repair commands
- Single backend (meshlab) implementation
- Basic output format support (STL)
