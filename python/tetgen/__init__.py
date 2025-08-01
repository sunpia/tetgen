"""
TetGen Python Implementation

A Python implementation of TetGen - Quality Tetrahedral Mesh Generator and 3D Delaunay Triangulator.

This package provides:
- TetGenIO: Input/output data structure
- TetGenBehavior: Configuration and behavior settings
- TetGen: Main mesh generation class
"""

try:
    from .tetgen_io import TetGenIO
    from .tetgen_behavior import TetGenBehavior
    from .tetgen_mesh import TetGen
    from .predicates import Predicates
    
    __all__ = [
        "TetGenIO",
        "TetGenBehavior", 
        "TetGen",
        "Predicates"
    ]
except ImportError as e:
    # Handle missing dependencies gracefully
    import warnings
    warnings.warn(f"TetGen Python: Missing dependencies - {e}", UserWarning)
    __all__ = []

__version__ = "1.0.0"
__author__ = "Python TetGen Implementation"
