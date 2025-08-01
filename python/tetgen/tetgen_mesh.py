"""
TetGen - Main tetrahedral mesh generation class

This module contains the main TetGen class that performs tetrahedral mesh
generation and 3D Delaunay triangulation.
"""

import numpy as np
from typing import List, Tuple, Optional, Set
import time
from .tetgen_io import TetGenIO
from .tetgen_behavior import TetGenBehavior
from .predicates import Predicates


class TetGenMesh:
    """Internal mesh data structure for TetGen."""
    
    def __init__(self):
        self.points: List[np.ndarray] = []
        self.tetrahedra: List[Tuple[int, int, int, int]] = []
        self.triangles: List[Tuple[int, int, int]] = []
        self.edges: List[Tuple[int, int]] = []
        
        # Mesh quality measures
        self.aspect_ratios: List[float] = []
        self.volumes: List[float] = []
        self.dihedral_angles: List[List[float]] = []
        
        # Boundary information
        self.boundary_faces: Set[Tuple[int, int, int]] = set()
        self.boundary_edges: Set[Tuple[int, int]] = set()
        
    def add_point(self, point: np.ndarray) -> int:
        """Add a point to the mesh and return its index."""
        self.points.append(point.copy())
        return len(self.points) - 1
        
    def add_tetrahedron(self, vertices: Tuple[int, int, int, int]) -> int:
        """Add a tetrahedron to the mesh and return its index."""
        self.tetrahedra.append(vertices)
        return len(self.tetrahedra) - 1
        
    def get_tetrahedron_volume(self, tet_idx: int) -> float:
        """Calculate volume of a tetrahedron."""
        if tet_idx >= len(self.tetrahedra):
            return 0.0
            
        v0, v1, v2, v3 = self.tetrahedra[tet_idx]
        return Predicates.tetrahedron_volume(
            self.points[v0], self.points[v1], 
            self.points[v2], self.points[v3]
        )
        
    def get_tetrahedron_aspect_ratio(self, tet_idx: int) -> float:
        """Calculate aspect ratio of a tetrahedron."""
        if tet_idx >= len(self.tetrahedra):
            return float('inf')
            
        v0, v1, v2, v3 = self.tetrahedra[tet_idx]
        return Predicates.aspect_ratio(
            self.points[v0], self.points[v1],
            self.points[v2], self.points[v3]
        )


class TetGen:
    """
    Main TetGen class for tetrahedral mesh generation.
    
    This class provides the main interface for generating quality tetrahedral
    meshes from piecewise linear complexes (PLCs).
    """
    
    def __init__(self):
        self.predicates = Predicates()
        self.mesh = TetGenMesh()
        self.behavior = TetGenBehavior()
        
        # Statistics
        self.statistics = {
            'input_points': 0,
            'input_facets': 0,
            'output_points': 0,
            'output_tetrahedra': 0,
            'output_faces': 0,
            'output_edges': 0,
            'min_dihedral': 0.0,
            'max_dihedral': 0.0,
            'min_aspect_ratio': 0.0,
            'max_aspect_ratio': 0.0,
            'total_volume': 0.0,
            'cpu_time': 0.0
        }
        
    def tetrahedralize(self, behavior: TetGenBehavior, input_data: TetGenIO, 
                      output_data: Optional[TetGenIO] = None,
                      additional_points: Optional[TetGenIO] = None,
                      background_mesh: Optional[TetGenIO] = None) -> TetGenIO:
        """
        Main tetrahedralization function.
        
        Args:
            behavior: TetGen behavior settings
            input_data: Input geometry (points, facets, etc.)
            output_data: Optional output container
            additional_points: Optional additional points to insert
            background_mesh: Optional background mesh for sizing
            
        Returns:
            TetGenIO object containing the generated mesh
        """
        start_time = time.time()
        
        # Copy behavior settings
        self.behavior.copy_from(behavior)
        
        if output_data is None:
            output_data = TetGenIO()
        else:
            output_data.initialize()
            
        # Print startup message
        if not self.behavior.quiet:
            self._print_startup_message()
            
        # Validate input
        if not self._validate_input(input_data):
            raise ValueError("Invalid input data")
            
        # Copy input statistics
        self.statistics['input_points'] = input_data.number_of_points
        self.statistics['input_facets'] = input_data.number_of_facets
        
        try:
            # Main mesh generation pipeline
            if self.behavior.refine:
                self._refine_mesh(input_data, output_data)
            else:
                self._generate_mesh(input_data, output_data, additional_points, background_mesh)
                
            # Post-processing
            if self.behavior.quality and not self.behavior.refine:
                self._improve_mesh_quality(output_data)
                
            # Generate additional output
            if self.behavior.facesout:
                self._extract_boundary_faces(output_data)
                
            if self.behavior.edgesout:
                self._extract_edges(output_data)
                
            if self.behavior.voroout:
                self._generate_voronoi_diagram(output_data)
                
            # Calculate statistics
            self._calculate_statistics(output_data)
            
        except Exception as e:
            if not self.behavior.quiet:
                print(f"Error during mesh generation: {e}")
            raise
            
        # Record timing
        self.statistics['cpu_time'] = time.time() - start_time
        
        # Print statistics
        if not self.behavior.quiet:
            self._print_statistics()
            
        return output_data
        
    def _print_startup_message(self):
        """Print TetGen startup message."""
        print("TetGen")
        print("A Quality Tetrahedral Mesh Generator and 3D Delaunay Triangulator")
        print("Version 1.0.0 (Python Implementation)")
        print("")
        
        if self.behavior.verbose:
            print("Switches:")
            self.behavior.print_switches()
            print("")
            
    def _validate_input(self, input_data: TetGenIO) -> bool:
        """Validate input data."""
        if input_data.number_of_points < 4:
            if not self.behavior.quiet:
                print("Error: Need at least 4 points for tetrahedralization")
            return False
            
        if input_data.point_list is None:
            if not self.behavior.quiet:
                print("Error: No point data provided")
            return False
            
        # Check for degenerate points
        points = input_data.point_list
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                if np.allclose(points[i], points[j], atol=1e-14):
                    if not self.behavior.quiet:
                        print(f"Warning: Duplicate points found at indices {i} and {j}")
                        
        return True
        
    def _generate_mesh(self, input_data: TetGenIO, output_data: TetGenIO,
                      additional_points: Optional[TetGenIO] = None,
                      background_mesh: Optional[TetGenIO] = None):
        """Generate tetrahedral mesh from PLC."""
        if not self.behavior.quiet and self.behavior.verbose:
            print("Generating tetrahedral mesh...")
            
        # Initialize mesh with input points
        self.mesh = TetGenMesh()
        point_map = {}
        
        for i, point in enumerate(input_data.point_list):
            point_idx = self.mesh.add_point(point)
            point_map[i] = point_idx
            
        # Add additional points if provided
        if additional_points and additional_points.number_of_points > 0:
            for point in additional_points.point_list:
                self.mesh.add_point(point)
                
        # Generate initial Delaunay triangulation
        self._delaunay_triangulation()
        
        # Handle PLC constraints if provided
        if input_data.number_of_facets > 0:
            self._recover_boundary_facets(input_data, point_map)
            
        # Remove tetrahedra in holes
        if input_data.number_of_holes > 0:
            self._remove_holes(input_data)
            
        # Apply volume constraints
        if self.behavior.varvolume:
            self._apply_volume_constraints(input_data)
            
        # Copy results to output
        self._copy_mesh_to_output(output_data)
        
    def _delaunay_triangulation(self):
        """Generate 3D Delaunay triangulation of points."""
        if len(self.mesh.points) < 4:
            return
            
        # Simple incremental construction (not optimized)
        # In a real implementation, this would use more sophisticated algorithms
        
        # Start with first 4 points if they're not coplanar
        initial_points = self.mesh.points[:4]
        
        # Check if points are coplanar
        if self._points_coplanar(initial_points):
            # Find a non-coplanar point
            for i in range(4, len(self.mesh.points)):
                if not self._points_coplanar(initial_points[:3] + [self.mesh.points[i]]):
                    initial_points[3] = self.mesh.points[i]
                    # Swap in point list
                    self.mesh.points[3], self.mesh.points[i] = self.mesh.points[i], self.mesh.points[3]
                    break
                    
        # Create initial tetrahedron
        if not self._points_coplanar(initial_points):
            # Ensure positive orientation
            orient = self.predicates.orient3d(initial_points[0], initial_points[1], 
                                            initial_points[2], initial_points[3])
            if orient < 0:
                # Swap two vertices to fix orientation
                self.mesh.points[1], self.mesh.points[2] = self.mesh.points[2], self.mesh.points[1]
                
            self.mesh.add_tetrahedron((0, 1, 2, 3))
            
        # Add remaining points incrementally
        for i in range(4, len(self.mesh.points)):
            self._insert_point_delaunay(i)
            
    def _points_coplanar(self, points: List[np.ndarray]) -> bool:
        """Check if 4 points are coplanar."""
        if len(points) < 4:
            return True
            
        return abs(self.predicates.orient3d(points[0], points[1], points[2], points[3])) < 1e-12
        
    def _insert_point_delaunay(self, point_idx: int):
        """Insert a point into existing Delaunay triangulation."""
        point = self.mesh.points[point_idx]
        
        # Find tetrahedron containing the point
        containing_tet = -1
        for i, tet in enumerate(self.mesh.tetrahedra):
            v0, v1, v2, v3 = tet
            if self.predicates.point_in_tetrahedron(point, self.mesh.points[v0],
                                                   self.mesh.points[v1], self.mesh.points[v2],
                                                   self.mesh.points[v3]):
                containing_tet = i
                break
                
        if containing_tet == -1:
            # Point is outside convex hull - simplified handling
            # In a real implementation, this would be more sophisticated
            return
            
        # Split the containing tetrahedron
        old_tet = self.mesh.tetrahedra[containing_tet]
        
        # Remove old tetrahedron
        del self.mesh.tetrahedra[containing_tet]
        
        # Add 4 new tetrahedra
        v0, v1, v2, v3 = old_tet
        self.mesh.add_tetrahedron((point_idx, v0, v1, v2))
        self.mesh.add_tetrahedron((point_idx, v0, v1, v3))
        self.mesh.add_tetrahedron((point_idx, v0, v2, v3))
        self.mesh.add_tetrahedron((point_idx, v1, v2, v3))
        
        # Restore Delaunay property (simplified - should use flipping)
        
    def _recover_boundary_facets(self, input_data: TetGenIO, point_map: dict):
        """Recover boundary facets in the mesh."""
        if not self.behavior.quiet and self.behavior.verbose:
            print(f"Recovering {input_data.number_of_facets} boundary facets...")
            
        # This is a simplified implementation
        # Real TetGen uses sophisticated constrained Delaunay algorithms
        for facet in input_data.facet_list:
            for polygon in facet.polygon_list:
                if polygon.number_of_vertices >= 3:
                    # For each triangle in the polygon (simple triangulation)
                    for i in range(1, polygon.number_of_vertices - 1):
                        v0 = point_map.get(polygon.vertex_list[0], polygon.vertex_list[0])
                        v1 = point_map.get(polygon.vertex_list[i], polygon.vertex_list[i])
                        v2 = point_map.get(polygon.vertex_list[i + 1], polygon.vertex_list[i + 1])
                        
                        # Mark as boundary triangle
                        self.mesh.boundary_faces.add(tuple(sorted([v0, v1, v2])))
                        
    def _remove_holes(self, input_data: TetGenIO):
        """Remove tetrahedra that lie inside holes."""
        if not self.behavior.quiet and self.behavior.verbose:
            print(f"Removing tetrahedra in {input_data.number_of_holes} holes...")
            
        # Mark tetrahedra for removal
        to_remove = []
        
        for i, tet in enumerate(self.mesh.tetrahedra):
            # Calculate tetrahedron centroid
            v0, v1, v2, v3 = tet
            centroid = (self.mesh.points[v0] + self.mesh.points[v1] + 
                       self.mesh.points[v2] + self.mesh.points[v3]) / 4.0
                       
            # Check if centroid is in any hole
            for hole in input_data.hole_list:
                if np.linalg.norm(centroid - hole) < 1e-6:  # Simplified hole test
                    to_remove.append(i)
                    break
                    
        # Remove marked tetrahedra
        for i in reversed(to_remove):
            del self.mesh.tetrahedra[i]
            
    def _apply_volume_constraints(self, input_data: TetGenIO):
        """Apply volume constraints to tetrahedra."""
        if self.behavior.fixedvolume and self.behavior.maxvolume > 0:
            if not self.behavior.quiet and self.behavior.verbose:
                print(f"Applying volume constraint: {self.behavior.maxvolume}")
                
            # Split tetrahedra that are too large
            i = 0
            while i < len(self.mesh.tetrahedra):
                volume = self.mesh.get_tetrahedron_volume(i)
                if volume > self.behavior.maxvolume:
                    # Split tetrahedron (simplified)
                    self._split_tetrahedron(i)
                else:
                    i += 1
                    
    def _split_tetrahedron(self, tet_idx: int):
        """Split a tetrahedron to reduce its volume."""
        # Simplified tetrahedron splitting
        # Real implementation would be much more sophisticated
        tet = self.mesh.tetrahedra[tet_idx]
        v0, v1, v2, v3 = tet
        
        # Add centroid point
        centroid = (self.mesh.points[v0] + self.mesh.points[v1] + 
                   self.mesh.points[v2] + self.mesh.points[v3]) / 4.0
        centroid_idx = self.mesh.add_point(centroid)
        
        # Remove original tetrahedron
        del self.mesh.tetrahedra[tet_idx]
        
        # Add 4 new smaller tetrahedra
        self.mesh.add_tetrahedron((centroid_idx, v0, v1, v2))
        self.mesh.add_tetrahedron((centroid_idx, v0, v1, v3))
        self.mesh.add_tetrahedron((centroid_idx, v0, v2, v3))
        self.mesh.add_tetrahedron((centroid_idx, v1, v2, v3))
        
    def _improve_mesh_quality(self, output_data: TetGenIO):
        """Improve mesh quality through various operations."""
        if not self.behavior.quiet and self.behavior.verbose:
            print("Improving mesh quality...")
            
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            improved = False
            
            # Check and improve poor quality tetrahedra
            for i in range(len(self.mesh.tetrahedra)):
                aspect_ratio = self.mesh.get_tetrahedron_aspect_ratio(i)
                
                if aspect_ratio > self.behavior.minratio:
                    # Try to improve this tetrahedron
                    if self._improve_tetrahedron_quality(i):
                        improved = True
                        break
                        
            if not improved:
                break
                
            iteration += 1
            
        if not self.behavior.quiet and self.behavior.verbose:
            print(f"Quality improvement completed after {iteration} iterations")
            
    def _improve_tetrahedron_quality(self, tet_idx: int) -> bool:
        """Try to improve quality of a specific tetrahedron."""
        # Simplified quality improvement
        # Real TetGen uses edge/face flipping, vertex smoothing, etc.
        return False
        
    def _extract_boundary_faces(self, output_data: TetGenIO):
        """Extract boundary faces from the mesh."""
        face_count = {}
        
        # Count face occurrences
        for tet in self.mesh.tetrahedra:
            v0, v1, v2, v3 = tet
            faces = [
                tuple(sorted([v0, v1, v2])),
                tuple(sorted([v0, v1, v3])),
                tuple(sorted([v0, v2, v3])),
                tuple(sorted([v1, v2, v3]))
            ]
            
            for face in faces:
                face_count[face] = face_count.get(face, 0) + 1
                
        # Boundary faces appear exactly once
        boundary_faces = [face for face, count in face_count.items() if count == 1]
        
        # Convert to output format
        output_data.triangle_list = np.array(boundary_faces, dtype=np.int32)
        output_data.number_of_triangles = len(boundary_faces)
        
    def _extract_edges(self, output_data: TetGenIO):
        """Extract edges from the mesh."""
        edges = set()
        
        for tet in self.mesh.tetrahedra:
            v0, v1, v2, v3 = tet
            tet_edges = [
                tuple(sorted([v0, v1])),
                tuple(sorted([v0, v2])),
                tuple(sorted([v0, v3])),
                tuple(sorted([v1, v2])),
                tuple(sorted([v1, v3])),
                tuple(sorted([v2, v3]))
            ]
            
            edges.update(tet_edges)
            
        # Convert to output format
        output_data.edge_list = np.array(list(edges), dtype=np.int32)
        output_data.number_of_edges = len(edges)
        
    def _generate_voronoi_diagram(self, output_data: TetGenIO):
        """Generate Voronoi diagram dual to Delaunay triangulation."""
        # Simplified Voronoi generation
        voronoi_points = []
        
        for tet in self.mesh.tetrahedra:
            v0, v1, v2, v3 = tet
            center, _ = self.predicates.circumcenter_3d(
                self.mesh.points[v0], self.mesh.points[v1],
                self.mesh.points[v2], self.mesh.points[v3]
            )
            voronoi_points.append(center)
            
        output_data.voronoi_point_list = np.array(voronoi_points)
        output_data.number_of_voronoi_points = len(voronoi_points)
        
    def _copy_mesh_to_output(self, output_data: TetGenIO):
        """Copy mesh data to output structure."""
        # Copy points
        output_data.point_list = np.array(self.mesh.points)
        output_data.number_of_points = len(self.mesh.points)
        
        # Copy tetrahedra
        if self.mesh.tetrahedra:
            output_data.tetrahedron_list = np.array(self.mesh.tetrahedra, dtype=np.int32)
            output_data.number_of_tetrahedra = len(self.mesh.tetrahedra)
            output_data.number_of_corners = 4
            
        # Set indexing
        if self.behavior.zeroindex:
            output_data.firstnumber = 0
        else:
            output_data.firstnumber = 1
            
    def _refine_mesh(self, input_data: TetGenIO, output_data: TetGenIO):
        """Refine an existing tetrahedral mesh."""
        if not self.behavior.quiet:
            print("Refining existing mesh...")
            
        # Copy input mesh
        output_data.point_list = input_data.point_list.copy()
        output_data.number_of_points = input_data.number_of_points
        output_data.tetrahedron_list = input_data.tetrahedron_list.copy()
        output_data.number_of_tetrahedra = input_data.number_of_tetrahedra
        output_data.number_of_corners = input_data.number_of_corners
        
        # Apply refinement operations
        # This is a simplified implementation
        
    def _calculate_statistics(self, output_data: TetGenIO):
        """Calculate mesh statistics."""
        self.statistics['output_points'] = output_data.number_of_points
        self.statistics['output_tetrahedra'] = output_data.number_of_tetrahedra
        self.statistics['output_faces'] = output_data.number_of_triangles
        self.statistics['output_edges'] = output_data.number_of_edges
        
        if output_data.number_of_tetrahedra > 0:
            volumes = []
            aspect_ratios = []
            all_angles = []
            
            for tet in output_data.tetrahedron_list:
                v0, v1, v2, v3 = tet
                points = [output_data.point_list[v0], output_data.point_list[v1],
                         output_data.point_list[v2], output_data.point_list[v3]]
                
                # Volume
                volume = self.predicates.tetrahedron_volume(*points)
                volumes.append(volume)
                
                # Aspect ratio
                aspect_ratio = self.predicates.aspect_ratio(*points)
                aspect_ratios.append(aspect_ratio)
                
                # Dihedral angles
                edges = [(0,1,2,3), (0,1,3,2), (0,2,3,1), (1,2,3,0), (1,2,0,3), (2,3,0,1)]
                for a, b, c, d in edges:
                    angle = self.predicates.dihedral_angle(points[a], points[b], points[c], points[d])
                    all_angles.append(angle)
                    
            self.statistics['total_volume'] = sum(volumes)
            
            if aspect_ratios:
                self.statistics['min_aspect_ratio'] = min(aspect_ratios)
                self.statistics['max_aspect_ratio'] = max(aspect_ratios)
                
            if all_angles:
                self.statistics['min_dihedral'] = min(all_angles)
                self.statistics['max_dihedral'] = max(all_angles)
                
    def _print_statistics(self):
        """Print mesh generation statistics."""
        print("\nMesh generation completed.")
        print("Statistics:")
        print(f"  Input points: {self.statistics['input_points']}")
        print(f"  Input facets: {self.statistics['input_facets']}")
        print(f"  Output points: {self.statistics['output_points']}")
        print(f"  Output tetrahedra: {self.statistics['output_tetrahedra']}")
        
        if self.statistics['output_faces'] > 0:
            print(f"  Output faces: {self.statistics['output_faces']}")
        if self.statistics['output_edges'] > 0:
            print(f"  Output edges: {self.statistics['output_edges']}")
            
        if self.statistics['max_aspect_ratio'] > 0:
            print(f"  Aspect ratio range: {self.statistics['min_aspect_ratio']:.3f} - {self.statistics['max_aspect_ratio']:.3f}")
            
        if self.statistics['max_dihedral'] > 0:
            print(f"  Dihedral angle range: {self.statistics['min_dihedral']:.1f}° - {self.statistics['max_dihedral']:.1f}°")
            
        print(f"  Total volume: {self.statistics['total_volume']:.6e}")
        print(f"  CPU time: {self.statistics['cpu_time']:.3f} seconds")
        print("")
