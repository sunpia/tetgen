"""
Basic TetGen Python Examples

This script demonstrates basic usage of the TetGen Python implementation.
"""

import numpy as np
import os
import sys

# Add parent directory to path to import tetgen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tetgen import TetGenIO, TetGenBehavior, TetGen


def example_cube():
    """Generate a tetrahedral mesh of a cube."""
    print("Example 1: Cube tetrahedralization")
    print("-" * 40)
    
    # Create a simple cube
    input_data = TetGenIO()
    
    # Define 8 vertices of a unit cube
    points = np.array([
        [0.0, 0.0, 0.0],  # 0
        [1.0, 0.0, 0.0],  # 1
        [1.0, 1.0, 0.0],  # 2
        [0.0, 1.0, 0.0],  # 3
        [0.0, 0.0, 1.0],  # 4
        [1.0, 0.0, 1.0],  # 5
        [1.0, 1.0, 1.0],  # 6
        [0.0, 1.0, 1.0],  # 7
    ])
    
    input_data.set_points(points)
    
    # Define 6 faces of the cube (each face is split into 2 triangles)
    from tetgen.tetgen_io import Facet, Polygon
    
    # Bottom face (z=0)
    facet1 = Facet()
    poly1 = Polygon()
    poly1.set_vertices([0, 1, 2, 3])  # quad
    facet1.add_polygon(poly1)
    input_data.add_facet(facet1)
    
    # Top face (z=1)
    facet2 = Facet()
    poly2 = Polygon()
    poly2.set_vertices([4, 7, 6, 5])  # quad (reverse order for outward normal)
    facet2.add_polygon(poly2)
    input_data.add_facet(facet2)
    
    # Front face (y=0)
    facet3 = Facet()
    poly3 = Polygon()
    poly3.set_vertices([0, 4, 5, 1])
    facet3.add_polygon(poly3)
    input_data.add_facet(facet3)
    
    # Back face (y=1)
    facet4 = Facet()
    poly4 = Polygon()
    poly4.set_vertices([3, 2, 6, 7])
    facet4.add_polygon(poly4)
    input_data.add_facet(facet4)
    
    # Left face (x=0)
    facet5 = Facet()
    poly5 = Polygon()
    poly5.set_vertices([0, 3, 7, 4])
    facet5.add_polygon(poly5)
    input_data.add_facet(facet5)
    
    # Right face (x=1)
    facet6 = Facet()
    poly6 = Polygon()
    poly6.set_vertices([1, 5, 6, 2])
    facet6.add_polygon(poly6)
    input_data.add_facet(facet6)
    
    # Set up behavior for quality mesh generation
    behavior = TetGenBehavior()
    behavior.plc = True          # Tetrahedralize PLC
    behavior.quality = True      # Generate quality mesh
    behavior.minratio = 1.414    # Radius-edge ratio bound
    behavior.verbose = True      # Verbose output
    
    # Generate mesh
    tetgen = TetGen()
    output = tetgen.tetrahedralize(behavior, input_data)
    
    print(f"Generated mesh with {output.number_of_points} points and {output.number_of_tetrahedra} tetrahedra")
    print()
    
    return output


def example_sphere():
    """Generate a tetrahedral mesh of a sphere (simplified as icosahedron)."""
    print("Example 2: Sphere tetrahedralization")
    print("-" * 40)
    
    # Create a simplified sphere using icosahedron vertices
    input_data = TetGenIO()
    
    # Golden ratio
    phi = (1.0 + np.sqrt(5.0)) / 2.0
    
    # 12 vertices of icosahedron
    points = np.array([
        [-1,  phi,  0],
        [ 1,  phi,  0],
        [-1, -phi,  0],
        [ 1, -phi,  0],
        [ 0, -1,  phi],
        [ 0,  1,  phi],
        [ 0, -1, -phi],
        [ 0,  1, -phi],
        [ phi,  0, -1],
        [ phi,  0,  1],
        [-phi,  0, -1],
        [-phi,  0,  1]
    ])
    
    # Normalize to unit sphere
    for i in range(len(points)):
        points[i] = points[i] / np.linalg.norm(points[i])
    
    input_data.set_points(points)
    
    # Create some triangular faces (simplified - real icosahedron has 20 faces)
    from tetgen.tetgen_io import Facet, Polygon
    
    # Add a few sample triangular faces
    faces = [
        [0, 11, 5],
        [0, 5, 1],
        [0, 1, 7],
        [0, 7, 10],
        [0, 10, 11],
        [1, 5, 9],
        [5, 11, 4],
        [11, 10, 2],
        [10, 7, 6],
        [7, 1, 8]
    ]
    
    for face_verts in faces:
        facet = Facet()
        poly = Polygon()
        poly.set_vertices(face_verts)
        facet.add_polygon(poly)
        input_data.add_facet(facet)
    
    # Set up behavior
    behavior = TetGenBehavior()
    behavior.plc = True
    behavior.quality = True
    behavior.minratio = 2.0
    behavior.verbose = True
    
    # Generate mesh
    tetgen = TetGen()
    output = tetgen.tetrahedralize(behavior, input_data)
    
    print(f"Generated mesh with {output.number_of_points} points and {output.number_of_tetrahedra} tetrahedra")
    print()
    
    return output


def example_points_only():
    """Generate convex hull of random points."""
    print("Example 3: Convex hull of random points")
    print("-" * 40)
    
    # Generate random points
    np.random.seed(42)  # For reproducible results
    n_points = 20
    points = np.random.rand(n_points, 3) * 2.0 - 1.0  # Points in [-1, 1]^3
    
    input_data = TetGenIO()
    input_data.set_points(points)
    
    # Set up behavior for convex hull
    behavior = TetGenBehavior()
    behavior.convex = True       # Generate convex hull
    behavior.verbose = True
    
    # Generate mesh
    tetgen = TetGen()
    output = tetgen.tetrahedralize(behavior, input_data)
    
    print(f"Generated convex hull with {output.number_of_points} points and {output.number_of_tetrahedra} tetrahedra")
    print()
    
    return output


def example_quality_refinement():
    """Demonstrate quality mesh refinement."""
    print("Example 4: Quality mesh refinement")
    print("-" * 40)
    
    # Start with a simple tetrahedron
    input_data = TetGenIO()
    
    points = np.array([
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.5, 0.866, 0.0],
        [0.5, 0.289, 0.816]
    ])
    
    input_data.set_points(points)
    
    # Set up behavior for aggressive quality improvement
    behavior = TetGenBehavior()
    behavior.quality = True
    behavior.minratio = 1.2      # Strict quality bound
    behavior.varvolume = True    # Enable volume constraint
    behavior.maxvolume = 0.01    # Small volume constraint
    behavior.fixedvolume = True
    behavior.verbose = True
    
    # Generate mesh
    tetgen = TetGen()
    output = tetgen.tetrahedralize(behavior, input_data)
    
    print(f"Generated refined mesh with {output.number_of_points} points and {output.number_of_tetrahedra} tetrahedra")
    print()
    
    return output


def save_example_files():
    """Save example input files for testing."""
    print("Saving example input files...")
    
    # Create examples directory if it doesn't exist
    examples_dir = os.path.dirname(__file__)
    
    # Save cube.poly file
    cube_poly = os.path.join(examples_dir, "cube.poly")
    with open(cube_poly, 'w') as f:
        f.write("# Unit cube\n")
        f.write("8 3 0 1\n")  # 8 points, 3D, 0 attributes, 1 boundary marker
        f.write("1  0.0 0.0 0.0  1\n")
        f.write("2  1.0 0.0 0.0  1\n")
        f.write("3  1.0 1.0 0.0  1\n")
        f.write("4  0.0 1.0 0.0  1\n")
        f.write("5  0.0 0.0 1.0  1\n")
        f.write("6  1.0 0.0 1.0  1\n")
        f.write("7  1.0 1.0 1.0  1\n")
        f.write("8  0.0 1.0 1.0  1\n")
        f.write("6 1\n")  # 6 facets, 1 boundary marker
        f.write("1 0 1\n")  # facet 1, 0 holes, marker 1
        f.write("4  1 2 3 4\n")  # bottom face
        f.write("1 0 1\n")
        f.write("4  5 8 7 6\n")  # top face
        f.write("1 0 1\n")
        f.write("4  1 5 6 2\n")  # front face
        f.write("1 0 1\n")
        f.write("4  4 3 7 8\n")  # back face
        f.write("1 0 1\n")
        f.write("4  1 4 8 5\n")  # left face
        f.write("1 0 1\n")
        f.write("4  2 6 7 3\n")  # right face
        f.write("0\n")  # 0 holes
        f.write("0\n")  # 0 regions
        
    print(f"Saved {cube_poly}")
    
    # Save simple.node file
    simple_node = os.path.join(examples_dir, "simple.node")
    with open(simple_node, 'w') as f:
        f.write("# Simple tetrahedron\n")
        f.write("4 3 0 0\n")
        f.write("1  0.0 0.0 0.0\n")
        f.write("2  1.0 0.0 0.0\n")
        f.write("3  0.5 0.866 0.0\n")
        f.write("4  0.5 0.289 0.816\n")
    
    print(f"Saved {simple_node}")
    
    print()


def main():
    """Run all examples."""
    print("TetGen Python Examples")
    print("=" * 50)
    print()
    
    # Save example files first
    save_example_files()
    
    # Run examples
    try:
        example_cube()
        example_sphere()
        example_points_only()
        example_quality_refinement()
        
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
