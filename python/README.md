# TetGen Python Implementation

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Python implementation of TetGen - A Quality Tetrahedral Mesh Generator and 3D Delaunay Triangulator.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Examples](#examples)
- [API Reference](#api-reference)
- [File Formats](#file-formats)
- [Performance](#performance)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Overview

TetGen is originally a C++ library created by Hang Si for generating quality tetrahedral meshes and 3D Delaunay triangulations. This Python implementation aims to provide similar functionality in a more accessible format while maintaining the core algorithms and capabilities.

### Key Capabilities

- **Quality Tetrahedral Mesh Generation**: Generate meshes with controllable element quality
- **3D Delaunay Triangulation**: Robust Delaunay triangulation of point sets
- **Piecewise Linear Complex (PLC) Support**: Handle complex geometries with holes and regions
- **Mesh Refinement**: Improve existing meshes through various algorithms
- **Multiple Output Formats**: Support for various mesh file formats

## Features

- ✅ 3D Delaunay triangulation
- ✅ Quality mesh generation with radius-edge ratio bounds
- ✅ Piecewise Linear Complex (PLC) input
- ✅ Volume constraints
- ✅ Boundary face and edge extraction
- ✅ Voronoi diagram generation
- ✅ Multiple file format support (.node, .poly, .ele, .face, .edge)
- ✅ Command-line interface compatible with original TetGen
- ✅ Python API for programmatic use
- ✅ Comprehensive test suite

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/your-username/tetgen-python.git
cd tetgen-python/python

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Using pip (when available)

```bash
pip install tetgen-python
```

## Quick Start

### Python API

```python
import numpy as np
from tetgen import TetGenIO, TetGenBehavior, TetGen

# Create input geometry (a simple tetrahedron)
input_data = TetGenIO()
points = np.array([
    [0.0, 0.0, 0.0],
    [1.0, 0.0, 0.0],
    [0.5, 0.866, 0.0],
    [0.5, 0.289, 0.816]
])
input_data.set_points(points)

# Configure mesh generation
behavior = TetGenBehavior()
behavior.quality = True      # Generate quality mesh
behavior.minratio = 1.414    # Minimum radius-edge ratio
behavior.verbose = True      # Verbose output

# Generate mesh
tetgen = TetGen()
output = tetgen.tetrahedralize(behavior, input_data)

# Access results
print(f"Generated {output.number_of_points} points")
print(f"Generated {output.number_of_tetrahedra} tetrahedra")

# Get mesh data
vertices = output.point_list
tetrahedra = output.tetrahedron_list
```

### Command Line Interface

```bash
# Generate quality mesh from PLC
tetgen-python -pq1.414 input.poly

# Refine existing mesh with volume constraint
tetgen-python -ra0.1 mesh.1.node mesh.1.ele

# Generate convex hull with face output
tetgen-python -cf points.node

# Quality mesh with verbose output
tetgen-python -pq1.2V geometry.poly
```

## Examples

### Example 1: Cube Mesh Generation

```python
from tetgen import TetGenIO, TetGenBehavior, TetGen
from tetgen.tetgen_io import Facet, Polygon
import numpy as np

# Create cube vertices
input_data = TetGenIO()
points = np.array([
    [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],  # bottom
    [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]   # top
])
input_data.set_points(points)

# Define cube faces
faces = [
    [0, 1, 2, 3],  # bottom
    [4, 7, 6, 5],  # top
    [0, 4, 5, 1],  # front
    [3, 2, 6, 7],  # back
    [0, 3, 7, 4],  # left
    [1, 5, 6, 2]   # right
]

for face_vertices in faces:
    facet = Facet()
    polygon = Polygon()
    polygon.set_vertices(face_vertices)
    facet.add_polygon(polygon)
    input_data.add_facet(facet)

# Generate quality mesh
behavior = TetGenBehavior()
behavior.plc = True
behavior.quality = True
behavior.minratio = 1.414

tetgen = TetGen()
output = tetgen.tetrahedralize(behavior, input_data)
```

### Example 2: Random Points Convex Hull

```python
import numpy as np
from tetgen import TetGenIO, TetGenBehavior, TetGen

# Generate random points
np.random.seed(42)
points = np.random.rand(20, 3) * 2.0 - 1.0  # Points in [-1,1]^3

# Create input
input_data = TetGenIO()
input_data.set_points(points)

# Generate convex hull
behavior = TetGenBehavior()
behavior.convex = True

tetgen = TetGen()
output = tetgen.tetrahedralize(behavior, input_data)

print(f"Convex hull: {output.number_of_tetrahedra} tetrahedra")
```

## API Reference

### TetGenIO

Main input/output data structure:

```python
class TetGenIO:
    def set_points(points, attributes=None, markers=None)
    def set_tetrahedra(tetrahedra, attributes=None)
    def add_facet(facet)
    def load_node(filename)
    def load_poly(filename)
    def save_nodes(filename)
    def save_elements(filename)
```

### TetGenBehavior

Configuration and behavior settings:

```python
class TetGenBehavior:
    def parse_commandline(switches)
    def print_switches()
    def get_commandline_string()
    
    # Key properties:
    plc: bool              # Tetrahedralize PLC
    quality: bool          # Quality mesh generation
    minratio: float        # Minimum radius-edge ratio
    varvolume: bool        # Apply volume constraints
    maxvolume: float       # Maximum tetrahedron volume
    refine: bool           # Refine existing mesh
    facesout: bool         # Output boundary faces
    edgesout: bool         # Output edges
    voroout: bool          # Output Voronoi diagram
```

### TetGen

Main mesh generation class:

```python
class TetGen:
    def tetrahedralize(behavior, input_data, output_data=None, 
                      additional_points=None, background_mesh=None)
```

## File Formats

The Python implementation supports the same file formats as the original TetGen:

- **`.node`** - Point coordinates and attributes
- **`.poly`** - Piecewise Linear Complex description
- **`.ele`** - Tetrahedron connectivity
- **`.face`** - Boundary face connectivity
- **`.edge`** - Edge connectivity
- **`.v.node`** - Voronoi diagram vertices

## Performance

This Python implementation prioritizes clarity and correctness over raw performance. For production use with large meshes, consider using the original C++ TetGen for maximum performance.

## License

This project follows the same licensing terms as the original TetGen. Please see LICENSE for details.

## Acknowledgments

- **Hang Si** - Creator of the original TetGen library
- **Jonathan Shewchuk** - Robust geometric predicates algorithms
- **The TetGen community** - Continued development and support

## References

- Si, H. (2015). TetGen, a Delaunay-based quality tetrahedral mesh generator. *ACM Transactions on Mathematical Software*, 41(2), 1-36.
- Original TetGen website: http://www.tetgen.org
