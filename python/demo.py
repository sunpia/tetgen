#!/usr/bin/env python3
"""
TetGen Python Demo Script

This script demonstrates the basic functionality of the TetGen Python implementation.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def demo_without_numpy():
    """Demo that works without numpy installed."""
    print("TetGen Python Implementation Demo")
    print("=" * 50)
    print()
    
    try:
        # Try to import TetGen modules
        print("Testing imports...")
        
        # Test behavior module (no numpy dependency)
        from tetgen.tetgen_behavior import TetGenBehavior
        print("✓ TetGenBehavior imported successfully")
        
        # Test behavior functionality
        behavior = TetGenBehavior()
        behavior.parse_commandline("pq1.414aV")
        print("✓ Command line parsing works")
        print(f"  Switches: {behavior.get_commandline_string()}")
        
        # Test individual settings
        behavior2 = TetGenBehavior()
        behavior2.plc = True
        behavior2.quality = True
        behavior2.minratio = 2.0
        behavior2.verbose = True
        print("✓ Direct property setting works")
        
        print()
        print("Basic functionality test completed successfully!")
        print("Note: Full mesh generation requires numpy to be installed.")
        print()
        print("To install numpy and run full tests:")
        print("  pip install numpy scipy matplotlib")
        print("  python examples/basic_examples.py")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Some dependencies may be missing.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def demo_with_numpy():
    """Demo that requires numpy."""
    try:
        import numpy as np
        print("NumPy is available - running full demo...")
        print()
        
        from tetgen import TetGenIO, TetGenBehavior, TetGen
        from tetgen.tetgen_io import Facet, Polygon
        
        # Create a simple tetrahedron
        print("Creating simple tetrahedron mesh...")
        input_data = TetGenIO()
        
        points = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.5, 0.866, 0.0],
            [0.5, 0.289, 0.816]
        ])
        
        input_data.set_points(points)
        print(f"✓ Created input with {input_data.number_of_points} points")
        
        # Set up behavior
        behavior = TetGenBehavior()
        behavior.convex = True
        behavior.quiet = True
        
        # Generate mesh
        tetgen = TetGen()
        output = tetgen.tetrahedralize(behavior, input_data)
        
        print(f"✓ Generated mesh with {output.number_of_points} points")
        print(f"✓ Generated {output.number_of_tetrahedra} tetrahedra")
        
        # Test file I/O
        print("\nTesting file I/O...")
        test_filename = "test_output.node"
        
        if output.save_nodes(test_filename):
            print(f"✓ Saved nodes to {test_filename}")
            
            # Try to load it back
            reload_data = TetGenIO()
            if reload_data.load_node(test_filename):
                print(f"✓ Loaded nodes from {test_filename}")
                print(f"  Points match: {reload_data.number_of_points == output.number_of_points}")
            
            # Clean up
            if os.path.exists(test_filename):
                os.unlink(test_filename)
                print("✓ Cleaned up test file")
        
        print()
        print("Full demo completed successfully!")
        
    except ImportError:
        print("NumPy not available - running basic demo only...")
        demo_without_numpy()
    except Exception as e:
        print(f"Error in full demo: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main demo function."""
    print("Starting TetGen Python demo...")
    print()
    
    # Check Python version
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print()
    
    # Try full demo first, fall back to basic if needed
    demo_with_numpy()
    
    print()
    print("Demo completed. For more examples, see:")
    print("  - examples/basic_examples.py")
    print("  - examples/example.poly")
    print("  - tests/test_tetgen.py")


if __name__ == "__main__":
    main()
