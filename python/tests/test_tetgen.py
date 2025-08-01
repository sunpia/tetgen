"""
Unit tests for TetGen Python implementation

Run with: python -m pytest tests/
"""

import unittest
import numpy as np
import tempfile
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tetgen import TetGenIO, TetGenBehavior, TetGen, Predicates


class TestTetGenIO(unittest.TestCase):
    """Test TetGenIO class functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tetgen_io = TetGenIO()
        
    def test_initialization(self):
        """Test TetGenIO initialization."""
        self.assertEqual(self.tetgen_io.number_of_points, 0)
        self.assertEqual(self.tetgen_io.number_of_facets, 0)
        self.assertEqual(self.tetgen_io.number_of_tetrahedra, 0)
        self.assertIsNone(self.tetgen_io.point_list)
        
    def test_set_points(self):
        """Test setting points."""
        points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.tetgen_io.set_points(points)
        
        self.assertEqual(self.tetgen_io.number_of_points, 4)
        np.testing.assert_array_equal(self.tetgen_io.point_list, points)
        
    def test_set_tetrahedra(self):
        """Test setting tetrahedra."""
        tetrahedra = np.array([[0, 1, 2, 3]])
        self.tetgen_io.set_tetrahedra(tetrahedra)
        
        self.assertEqual(self.tetgen_io.number_of_tetrahedra, 1)
        self.assertEqual(self.tetgen_io.number_of_corners, 4)
        np.testing.assert_array_equal(self.tetgen_io.tetrahedron_list, tetrahedra)
        
    def test_save_load_nodes(self):
        """Test saving and loading node files."""
        points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.tetgen_io.set_points(points)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.node', delete=False) as f:
            filename = f.name
            
        try:
            # Save
            success = self.tetgen_io.save_nodes(filename)
            self.assertTrue(success)
            
            # Load
            new_io = TetGenIO()
            success = new_io.load_node(filename)
            self.assertTrue(success)
            
            self.assertEqual(new_io.number_of_points, 4)
            np.testing.assert_array_almost_equal(new_io.point_list, points)
            
        finally:
            if os.path.exists(filename):
                os.unlink(filename)


class TestTetGenBehavior(unittest.TestCase):
    """Test TetGenBehavior class functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.behavior = TetGenBehavior()
        
    def test_initialization(self):
        """Test TetGenBehavior initialization."""
        self.assertFalse(self.behavior.plc)
        self.assertFalse(self.behavior.quality)
        self.assertFalse(self.behavior.refine)
        self.assertEqual(self.behavior.minratio, 2.0)
        
    def test_parse_commandline_simple(self):
        """Test parsing simple command line switches."""
        success = self.behavior.parse_commandline("pq")
        self.assertTrue(success)
        self.assertTrue(self.behavior.plc)
        self.assertTrue(self.behavior.quality)
        
    def test_parse_commandline_with_ratio(self):
        """Test parsing quality switch with ratio."""
        success = self.behavior.parse_commandline("pq1.414")
        self.assertTrue(success)
        self.assertTrue(self.behavior.plc)
        self.assertTrue(self.behavior.quality)
        self.assertTrue(self.behavior.ratio)
        self.assertAlmostEqual(self.behavior.minratio, 1.414)
        
    def test_parse_commandline_with_volume(self):
        """Test parsing volume constraint switch."""
        success = self.behavior.parse_commandline("pa0.1")
        self.assertTrue(success)
        self.assertTrue(self.behavior.plc)
        self.assertTrue(self.behavior.varvolume)
        self.assertTrue(self.behavior.fixedvolume)
        self.assertAlmostEqual(self.behavior.maxvolume, 0.1)
        
    def test_get_commandline_string(self):
        """Test generating command line string."""
        self.behavior.plc = True
        self.behavior.quality = True
        self.behavior.minratio = 1.5
        self.behavior.ratio = True
        
        switches = self.behavior.get_commandline_string()
        self.assertIn('p', switches)
        self.assertIn('q', switches)
        self.assertIn('1.5', switches)


class TestPredicates(unittest.TestCase):
    """Test Predicates class functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.predicates = Predicates()
        
    def test_orient2d(self):
        """Test 2D orientation predicate."""
        # Counterclockwise points
        pa = np.array([0, 0])
        pb = np.array([1, 0])
        pc = np.array([0, 1])
        
        result = self.predicates.orient2d(pa, pb, pc)
        self.assertGreater(result, 0)  # Should be positive
        
        # Clockwise points
        result = self.predicates.orient2d(pa, pc, pb)
        self.assertLess(result, 0)  # Should be negative
        
        # Collinear points
        pc_collinear = np.array([2, 0])
        result = self.predicates.orient2d(pa, pb, pc_collinear)
        self.assertAlmostEqual(result, 0, places=10)
        
    def test_orient3d(self):
        """Test 3D orientation predicate."""
        # Points with positive orientation
        pa = np.array([0, 0, 0])
        pb = np.array([1, 0, 0])
        pc = np.array([0, 1, 0])
        pd = np.array([0, 0, -1])  # Below the plane
        
        result = self.predicates.orient3d(pa, pb, pc, pd)
        self.assertGreater(result, 0)
        
        # Points with negative orientation
        pd_above = np.array([0, 0, 1])  # Above the plane
        result = self.predicates.orient3d(pa, pb, pc, pd_above)
        self.assertLess(result, 0)
        
    def test_distance(self):
        """Test distance calculation."""
        pa = np.array([0, 0, 0])
        pb = np.array([3, 4, 0])
        
        distance = self.predicates.distance(pa, pb)
        self.assertAlmostEqual(distance, 5.0)
        
    def test_tetrahedron_volume(self):
        """Test tetrahedron volume calculation."""
        # Unit tetrahedron
        pa = np.array([0, 0, 0])
        pb = np.array([1, 0, 0])
        pc = np.array([0, 1, 0])
        pd = np.array([0, 0, 1])
        
        volume = self.predicates.tetrahedron_volume(pa, pb, pc, pd)
        expected_volume = 1.0 / 6.0  # Volume of unit tetrahedron
        self.assertAlmostEqual(volume, expected_volume, places=10)
        
    def test_circumcenter_3d(self):
        """Test circumcenter calculation."""
        # Regular tetrahedron centered at origin
        h = np.sqrt(2.0/3.0)  # Height from center to face
        r = np.sqrt(3.0)/3.0  # Radius of base circle
        
        pa = np.array([0, 0, h])
        pb = np.array([r, 0, -h/3])
        pc = np.array([-r/2, r*np.sqrt(3)/2, -h/3])
        pd = np.array([-r/2, -r*np.sqrt(3)/2, -h/3])
        
        center, radius = self.predicates.circumcenter_3d(pa, pb, pc, pd)
        
        # Center should be close to origin
        np.testing.assert_array_almost_equal(center, [0, 0, 0], decimal=10)
        
        # All vertices should be equidistant from center
        distances = [np.linalg.norm(center - p) for p in [pa, pb, pc, pd]]
        for d in distances:
            self.assertAlmostEqual(d, radius, places=10)


class TestTetGenMesh(unittest.TestCase):
    """Test TetGen main mesh generation class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tetgen = TetGen()
        
    def test_tetrahedralize_simple(self):
        """Test basic tetrahedralization."""
        # Create input with 4 points
        input_data = TetGenIO()
        points = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])
        input_data.set_points(points)
        
        # Set up behavior
        behavior = TetGenBehavior()
        behavior.convex = True  # Generate convex hull
        behavior.quiet = True   # Suppress output
        
        # Generate mesh
        output = self.tetgen.tetrahedralize(behavior, input_data)
        
        # Check results
        self.assertGreater(output.number_of_points, 0)
        self.assertGreater(output.number_of_tetrahedra, 0)
        
    def test_tetrahedralize_with_quality(self):
        """Test tetrahedralization with quality constraints."""
        # Create input with more points
        input_data = TetGenIO()
        np.random.seed(42)
        points = np.random.rand(10, 3)
        input_data.set_points(points)
        
        # Set up behavior for quality mesh
        behavior = TetGenBehavior()
        behavior.convex = True
        behavior.quality = True
        behavior.minratio = 1.5
        behavior.quiet = True
        
        # Generate mesh
        output = self.tetgen.tetrahedralize(behavior, input_data)
        
        # Check results
        self.assertGreater(output.number_of_points, 0)
        self.assertGreater(output.number_of_tetrahedra, 0)
        
    def test_validate_input(self):
        """Test input validation."""
        # Empty input should fail
        empty_input = TetGenIO()
        self.assertFalse(self.tetgen._validate_input(empty_input))
        
        # Too few points should fail
        input_data = TetGenIO()
        points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])  # Only 3 points
        input_data.set_points(points)
        self.assertFalse(self.tetgen._validate_input(input_data))
        
        # Valid input should pass
        points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]])
        input_data.set_points(points)
        self.assertTrue(self.tetgen._validate_input(input_data))


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple components."""
    
    def test_full_pipeline_cube(self):
        """Test full pipeline with cube geometry."""
        # Create cube geometry
        input_data = TetGenIO()
        
        # Cube vertices
        points = np.array([
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],  # bottom
            [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]   # top
        ])
        input_data.set_points(points)
        
        # Add cube faces as facets
        from tetgen.tetgen_io import Facet, Polygon
        
        faces = [
            [0, 1, 2, 3],  # bottom
            [4, 7, 6, 5],  # top
            [0, 4, 5, 1],  # front
            [3, 2, 6, 7],  # back
            [0, 3, 7, 4],  # left
            [1, 5, 6, 2]   # right
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
        behavior.facesout = True
        behavior.edgesout = True
        behavior.quiet = True
        
        # Generate mesh
        tetgen = TetGen()
        output = tetgen.tetrahedralize(behavior, input_data)
        
        # Verify results
        self.assertGreaterEqual(output.number_of_points, 8)  # At least original vertices
        self.assertGreater(output.number_of_tetrahedra, 0)
        
        # Check that output has faces if requested
        if behavior.facesout:
            self.assertGreater(output.number_of_triangles, 0)
            
        # Check that output has edges if requested
        if behavior.edgesout:
            self.assertGreater(output.number_of_edges, 0)
            
    def test_file_io_round_trip(self):
        """Test saving and loading files."""
        # Create simple mesh
        input_data = TetGenIO()
        points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]])
        tetrahedra = np.array([[0, 1, 2, 3]])
        
        input_data.set_points(points)
        input_data.set_tetrahedra(tetrahedra)
        
        # Save to temporary files
        with tempfile.TemporaryDirectory() as tmpdir:
            node_file = os.path.join(tmpdir, "test.node")
            ele_file = os.path.join(tmpdir, "test.ele")
            
            # Save
            self.assertTrue(input_data.save_nodes(node_file))
            self.assertTrue(input_data.save_elements(ele_file))
            
            # Load
            loaded_data = TetGenIO()
            self.assertTrue(loaded_data.load_node(node_file))
            
            # Verify
            self.assertEqual(loaded_data.number_of_points, 4)
            np.testing.assert_array_almost_equal(loaded_data.point_list, points)


def run_tests():
    """Run all tests."""
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.dirname(__file__), pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Run tests
    success = run_tests()
    sys.exit(0 if success else 1)
