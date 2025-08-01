"""
TetGenIO - Input/Output data structure for TetGen

This module contains the TetGenIO class which handles input and output
data for tetrahedral mesh generation, similar to the tetgenio class in C++ TetGen.
"""

import numpy as np
from typing import Optional, List, Tuple
import os


class Polygon:
    """A simple polygon (no holes) with vertices forming a ring."""
    
    def __init__(self):
        self.vertex_list: Optional[np.ndarray] = None
        self.number_of_vertices: int = 0
        
    def set_vertices(self, vertices: np.ndarray):
        """Set the vertices of the polygon."""
        self.vertex_list = np.array(vertices, dtype=np.int32)
        self.number_of_vertices = len(vertices)


class Facet:
    """A polygonal region possibly with holes, edges, and points."""
    
    def __init__(self):
        self.polygon_list: List[Polygon] = []
        self.number_of_polygons: int = 0
        self.hole_list: Optional[np.ndarray] = None
        self.number_of_holes: int = 0
        
    def add_polygon(self, polygon: Polygon):
        """Add a polygon to this facet."""
        self.polygon_list.append(polygon)
        self.number_of_polygons += 1
        
    def set_holes(self, holes: np.ndarray):
        """Set the hole points for this facet."""
        self.hole_list = np.array(holes, dtype=np.float64)
        self.number_of_holes = len(holes)


class VoroEdge:
    """An edge of the Voronoi diagram."""
    
    def __init__(self, v1: int = -1, v2: int = -1, normal: Optional[np.ndarray] = None):
        self.v1 = v1
        self.v2 = v2
        self.vnormal = normal if normal is not None else np.zeros(3)


class VoroFacet:
    """A facet of the Voronoi diagram."""
    
    def __init__(self):
        self.c1: int = -1
        self.c2: int = -1
        self.edge_list: List[int] = []
        self.number_of_edges: int = 0


class TetGenIO:
    """
    Input/Output data structure for TetGen.
    
    This class handles all input and output data for tetrahedral mesh generation,
    including points, facets, tetrahedra, and various mesh attributes.
    """
    
    def __init__(self):
        # Point list
        self.point_list: Optional[np.ndarray] = None
        self.point_attribute_list: Optional[np.ndarray] = None  
        self.point_marker_list: Optional[np.ndarray] = None
        self.number_of_points: int = 0
        self.number_of_point_attributes: int = 0
        
        # Facet list
        self.facet_list: List[Facet] = []
        self.facet_marker_list: Optional[np.ndarray] = None
        self.number_of_facets: int = 0
        
        # Hole list
        self.hole_list: Optional[np.ndarray] = None
        self.number_of_holes: int = 0
        
        # Region list
        self.region_list: Optional[np.ndarray] = None
        self.number_of_regions: int = 0
        
        # Tetrahedron list
        self.tetrahedron_list: Optional[np.ndarray] = None
        self.tetrahedron_attribute_list: Optional[np.ndarray] = None
        self.tetrahedron_volume_constraint_list: Optional[np.ndarray] = None
        self.neighbor_list: Optional[np.ndarray] = None
        self.number_of_tetrahedra: int = 0
        self.number_of_corners: int = 4
        self.number_of_tetrahedron_attributes: int = 0
        
        # Triangle face list
        self.triangle_list: Optional[np.ndarray] = None
        self.triangle_attribute_list: Optional[np.ndarray] = None
        self.triangle_marker_list: Optional[np.ndarray] = None
        self.number_of_triangles: int = 0
        
        # Edge list
        self.edge_list: Optional[np.ndarray] = None
        self.edge_marker_list: Optional[np.ndarray] = None
        self.number_of_edges: int = 0
        
        # Voronoi diagram
        self.voronoi_point_list: Optional[np.ndarray] = None
        self.voronoi_point_attribute_list: Optional[np.ndarray] = None
        self.number_of_voronoi_points: int = 0
        self.number_of_voronoi_point_attributes: int = 0
        
        self.voronoi_edge_list: List[VoroEdge] = []
        self.number_of_voronoi_edges: int = 0
        
        self.voronoi_facet_list: List[VoroFacet] = []
        self.number_of_voronoi_facets: int = 0
        
        # Mesh dimension
        self.mesh_dim: int = 3
        
        # File names
        self.firstnumber: int = 0
        self.object_type: int = 0
        
    def initialize(self):
        """Initialize the data structure by clearing all arrays."""
        self.point_list = None
        self.point_attribute_list = None
        self.point_marker_list = None
        self.number_of_points = 0
        self.number_of_point_attributes = 0
        
        self.facet_list.clear()
        self.facet_marker_list = None
        self.number_of_facets = 0
        
        self.hole_list = None
        self.number_of_holes = 0
        
        self.region_list = None
        self.number_of_regions = 0
        
        self.tetrahedron_list = None
        self.tetrahedron_attribute_list = None
        self.tetrahedron_volume_constraint_list = None
        self.neighbor_list = None
        self.number_of_tetrahedra = 0
        self.number_of_corners = 4
        self.number_of_tetrahedron_attributes = 0
        
        self.triangle_list = None
        self.triangle_attribute_list = None
        self.triangle_marker_list = None
        self.number_of_triangles = 0
        
        self.edge_list = None
        self.edge_marker_list = None
        self.number_of_edges = 0
        
        self.voronoi_point_list = None
        self.voronoi_point_attribute_list = None
        self.number_of_voronoi_points = 0
        self.number_of_voronoi_point_attributes = 0
        
        self.voronoi_edge_list.clear()
        self.number_of_voronoi_edges = 0
        
        self.voronoi_facet_list.clear()
        self.number_of_voronoi_facets = 0
        
    def set_points(self, points: np.ndarray, attributes: Optional[np.ndarray] = None, 
                   markers: Optional[np.ndarray] = None):
        """Set the point coordinates and optional attributes/markers."""
        self.point_list = np.array(points, dtype=np.float64)
        self.number_of_points = len(points)
        
        if attributes is not None:
            self.point_attribute_list = np.array(attributes, dtype=np.float64)
            self.number_of_point_attributes = attributes.shape[1] if len(attributes.shape) > 1 else 1
            
        if markers is not None:
            self.point_marker_list = np.array(markers, dtype=np.int32)
            
    def add_facet(self, facet: Facet):
        """Add a facet to the facet list."""
        self.facet_list.append(facet)
        self.number_of_facets += 1
        
    def set_tetrahedra(self, tetrahedra: np.ndarray, attributes: Optional[np.ndarray] = None):
        """Set the tetrahedron connectivity and optional attributes."""
        self.tetrahedron_list = np.array(tetrahedra, dtype=np.int32)
        self.number_of_tetrahedra = len(tetrahedra)
        self.number_of_corners = tetrahedra.shape[1] if len(tetrahedra.shape) > 1 else 4
        
        if attributes is not None:
            self.tetrahedron_attribute_list = np.array(attributes, dtype=np.float64)
            self.number_of_tetrahedron_attributes = attributes.shape[1] if len(attributes.shape) > 1 else 1
            
    def load_node(self, filename: str) -> bool:
        """Load points from a .node file."""
        try:
            if not os.path.exists(filename):
                return False
                
            with open(filename, 'r') as f:
                # Skip comments and empty lines
                lines = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        lines.append(line)
                        
                if not lines:
                    return False
                    
                # First line: <# of points> <dimension> <# of attributes> <# of boundary markers>
                header = lines[0].split()
                num_points = int(header[0])
                dimension = int(header[1]) if len(header) > 1 else 3
                num_attributes = int(header[2]) if len(header) > 2 else 0
                num_markers = int(header[3]) if len(header) > 3 else 0
                
                if num_points == 0:
                    return True
                    
                points = []
                attributes = [] if num_attributes > 0 else None
                markers = [] if num_markers > 0 else None
                
                for i in range(1, min(len(lines), num_points + 1)):
                    parts = lines[i].split()
                    if len(parts) < dimension + 1:
                        continue
                        
                    # Skip point index, read coordinates
                    coords = [float(parts[j]) for j in range(1, dimension + 1)]
                    points.append(coords)
                    
                    # Read attributes if present
                    if attributes is not None and len(parts) > dimension + 1:
                        attr = [float(parts[j]) for j in range(dimension + 1, dimension + 1 + num_attributes)]
                        attributes.append(attr)
                        
                    # Read markers if present
                    if markers is not None and len(parts) > dimension + 1 + num_attributes:
                        marker = int(parts[dimension + 1 + num_attributes])
                        markers.append(marker)
                        
                self.set_points(np.array(points), 
                              np.array(attributes) if attributes else None,
                              np.array(markers) if markers else None)
                return True
                
        except Exception as e:
            print(f"Error loading node file {filename}: {e}")
            return False
            
    def load_poly(self, filename: str) -> bool:
        """Load a piecewise linear complex from a .poly file."""
        try:
            if not os.path.exists(filename):
                return False
                
            with open(filename, 'r') as f:
                lines = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        lines.append(line)
                        
                if not lines:
                    return False
                    
                line_idx = 0
                
                # Read points section
                header = lines[line_idx].split()
                num_points = int(header[0])
                dimension = int(header[1]) if len(header) > 1 else 3
                num_attributes = int(header[2]) if len(header) > 2 else 0
                num_markers = int(header[3]) if len(header) > 3 else 0
                line_idx += 1
                
                if num_points > 0:
                    points = []
                    attributes = [] if num_attributes > 0 else None
                    markers = [] if num_markers > 0 else None
                    
                    for i in range(num_points):
                        if line_idx >= len(lines):
                            break
                        parts = lines[line_idx].split()
                        line_idx += 1
                        
                        if len(parts) < dimension + 1:
                            continue
                            
                        coords = [float(parts[j]) for j in range(1, dimension + 1)]
                        points.append(coords)
                        
                        if attributes is not None and len(parts) > dimension + 1:
                            attr = [float(parts[j]) for j in range(dimension + 1, dimension + 1 + num_attributes)]
                            attributes.append(attr)
                            
                        if markers is not None and len(parts) > dimension + 1 + num_attributes:
                            marker = int(parts[dimension + 1 + num_attributes])
                            markers.append(marker)
                            
                    self.set_points(np.array(points), 
                                  np.array(attributes) if attributes else None,
                                  np.array(markers) if markers else None)
                
                # Read facets section
                if line_idx < len(lines):
                    header = lines[line_idx].split()
                    num_facets = int(header[0])
                    num_boundary_markers = int(header[1]) if len(header) > 1 else 0
                    line_idx += 1
                    
                    facet_markers = []
                    
                    for i in range(num_facets):
                        if line_idx >= len(lines):
                            break
                            
                        parts = lines[line_idx].split()
                        line_idx += 1
                        
                        num_polygons = int(parts[0])
                        num_holes = int(parts[1]) if len(parts) > 1 else 0
                        boundary_marker = int(parts[2]) if len(parts) > 2 and num_boundary_markers > 0 else 0
                        
                        facet = Facet()
                        
                        # Read polygons
                        for j in range(num_polygons):
                            if line_idx >= len(lines):
                                break
                            poly_parts = lines[line_idx].split()
                            line_idx += 1
                            
                            num_vertices = int(poly_parts[0])
                            vertices = [int(poly_parts[k]) - 1 for k in range(1, num_vertices + 1)]  # Convert to 0-based
                            
                            polygon = Polygon()
                            polygon.set_vertices(vertices)
                            facet.add_polygon(polygon)
                            
                        # Read holes if present
                        if num_holes > 0:
                            holes = []
                            for j in range(num_holes):
                                if line_idx >= len(lines):
                                    break
                                hole_parts = lines[line_idx].split()
                                line_idx += 1
                                hole_coords = [float(hole_parts[k]) for k in range(dimension)]
                                holes.append(hole_coords)
                            facet.set_holes(np.array(holes))
                            
                        self.add_facet(facet)
                        if num_boundary_markers > 0:
                            facet_markers.append(boundary_marker)
                            
                    if facet_markers:
                        self.facet_marker_list = np.array(facet_markers, dtype=np.int32)
                
                # Read holes section
                if line_idx < len(lines):
                    header = lines[line_idx].split()
                    num_holes = int(header[0])
                    line_idx += 1
                    
                    if num_holes > 0:
                        holes = []
                        for i in range(num_holes):
                            if line_idx >= len(lines):
                                break
                            parts = lines[line_idx].split()
                            line_idx += 1
                            hole_coords = [float(parts[j]) for j in range(1, dimension + 1)]
                            holes.append(hole_coords)
                        self.hole_list = np.array(holes)
                        self.number_of_holes = len(holes)
                
                # Read regions section
                if line_idx < len(lines):
                    header = lines[line_idx].split()
                    num_regions = int(header[0])
                    line_idx += 1
                    
                    if num_regions > 0:
                        regions = []
                        for i in range(num_regions):
                            if line_idx >= len(lines):
                                break
                            parts = lines[line_idx].split()
                            line_idx += 1
                            # Region format: point_x point_y point_z region_attribute region_volume_constraint
                            region_data = [float(parts[j]) for j in range(1, len(parts))]
                            regions.append(region_data)
                        self.region_list = np.array(regions)
                        self.number_of_regions = len(regions)
                        
                return True
                
        except Exception as e:
            print(f"Error loading poly file {filename}: {e}")
            return False
            
    def save_nodes(self, filename: str) -> bool:
        """Save points to a .node file."""
        try:
            with open(filename, 'w') as f:
                # Write header
                f.write(f"{self.number_of_points} {self.mesh_dim} {self.number_of_point_attributes} ")
                f.write(f"{1 if self.point_marker_list is not None else 0}\n")
                
                # Write points
                for i in range(self.number_of_points):
                    f.write(f"{i + 1}")  # 1-based indexing
                    
                    # Write coordinates
                    for j in range(self.mesh_dim):
                        f.write(f" {self.point_list[i, j]:.16g}")
                        
                    # Write attributes
                    if self.point_attribute_list is not None:
                        for j in range(self.number_of_point_attributes):
                            f.write(f" {self.point_attribute_list[i, j]:.16g}")
                            
                    # Write marker
                    if self.point_marker_list is not None:
                        f.write(f" {self.point_marker_list[i]}")
                        
                    f.write("\n")
                    
            return True
            
        except Exception as e:
            print(f"Error saving node file {filename}: {e}")
            return False
            
    def save_elements(self, filename: str) -> bool:
        """Save tetrahedra to a .ele file."""
        try:
            with open(filename, 'w') as f:
                # Write header
                f.write(f"{self.number_of_tetrahedra} {self.number_of_corners} {self.number_of_tetrahedron_attributes}\n")
                
                # Write tetrahedra
                for i in range(self.number_of_tetrahedra):
                    f.write(f"{i + 1}")  # 1-based indexing
                    
                    # Write vertex indices (convert to 1-based)
                    for j in range(self.number_of_corners):
                        f.write(f" {self.tetrahedron_list[i, j] + 1}")
                        
                    # Write attributes
                    if self.tetrahedron_attribute_list is not None:
                        for j in range(self.number_of_tetrahedron_attributes):
                            f.write(f" {self.tetrahedron_attribute_list[i, j]:.16g}")
                            
                    f.write("\n")
                    
            return True
            
        except Exception as e:
            print(f"Error saving element file {filename}: {e}")
            return False
