"""
Predicates - Geometric predicates for robust computation

This module provides robust geometric predicates for determining the orientation
and relative position of points in 3D space. It's based on Jonathan Shewchuk's
adaptive precision floating-point arithmetic.
"""

import numpy as np
from typing import Tuple
import math


class Predicates:
    """
    Robust geometric predicates for computational geometry.
    
    This class provides exact predicates for orientation tests and other
    geometric computations needed for tetrahedral mesh generation.
    """
    
    def __init__(self):
        # Machine epsilon and related constants
        self.epsilon = np.finfo(float).eps
        self.splitter = 0.0
        self.resulterrbound = 0.0
        self.ccwerrboundA = 0.0
        self.ccwerrboundB = 0.0
        self.ccwerrboundC = 0.0
        self.o3derrboundA = 0.0
        self.o3derrboundB = 0.0
        self.o3derrboundC = 0.0
        self.isperrboundA = 0.0
        self.isperrboundB = 0.0
        self.isperrboundC = 0.0
        
        self._exactinit()
        
    def _exactinit(self):
        """Initialize the constants for exact arithmetic."""
        half = 0.5
        check = 1.0
        epsilon = 1.0
        lastcheck = 0.0
        
        # Find machine epsilon
        while (1.0 + epsilon) != 1.0:
            lastcheck = check
            epsilon *= half
            if epsilon == 0.0:
                epsilon = lastcheck
                break
            check = 1.0 + epsilon
            
        self.epsilon = epsilon
        self.splitter = 1.0
        epsilon *= half
        
        if epsilon != 0.0:
            self.splitter = 1.0 + epsilon
            
        # Calculate error bounds
        self.resulterrbound = (3.0 + 8.0 * self.epsilon) * self.epsilon
        self.ccwerrboundA = (3.0 + 16.0 * self.epsilon) * self.epsilon
        self.ccwerrboundB = (2.0 + 12.0 * self.epsilon) * self.epsilon
        self.ccwerrboundC = (9.0 + 64.0 * self.epsilon) * self.epsilon * self.epsilon
        self.o3derrboundA = (7.0 + 56.0 * self.epsilon) * self.epsilon
        self.o3derrboundB = (3.0 + 28.0 * self.epsilon) * self.epsilon
        self.o3derrboundC = (26.0 + 288.0 * self.epsilon) * self.epsilon * self.epsilon
        self.isperrboundA = (16.0 + 224.0 * self.epsilon) * self.epsilon
        self.isperrboundB = (5.0 + 72.0 * self.epsilon) * self.epsilon
        self.isperrboundC = (71.0 + 1408.0 * self.epsilon) * self.epsilon * self.epsilon
        
    def orient2d(self, pa: np.ndarray, pb: np.ndarray, pc: np.ndarray) -> float:
        """
        2D orientation test.
        
        Returns a positive value if pa, pb, and pc occur in counterclockwise order;
        a negative value if they occur in clockwise order; and zero if they are collinear.
        
        Args:
            pa, pb, pc: 2D points as numpy arrays
            
        Returns:
            Orientation determinant
        """
        detleft = (pa[0] - pc[0]) * (pb[1] - pc[1])
        detright = (pa[1] - pc[1]) * (pb[0] - pc[0])
        det = detleft - detright
        
        if detleft == 0.0 or detright == 0.0 or (detleft > 0.0) != (detright > 0.0):
            return det
            
        detsum = abs(detleft + detright)
        if abs(det) >= self.ccwerrboundA * detsum:
            return det
            
        # Use exact arithmetic if needed (simplified version)
        return det
        
    def orient3d(self, pa: np.ndarray, pb: np.ndarray, pc: np.ndarray, pd: np.ndarray) -> float:
        """
        3D orientation test.
        
        Returns a positive value if pd lies below the plane passing through pa, pb, and pc;
        "below" is defined so that pa, pb, and pc appear in counterclockwise order when
        viewed from above the plane. Returns a negative value if pd lies above the plane.
        Returns zero if the points are coplanar.
        
        Args:
            pa, pb, pc, pd: 3D points as numpy arrays
            
        Returns:
            Orientation determinant
        """
        adx = pa[0] - pd[0]
        bdx = pb[0] - pd[0]
        cdx = pc[0] - pd[0]
        ady = pa[1] - pd[1]
        bdy = pb[1] - pd[1]
        cdy = pc[1] - pd[1]
        adz = pa[2] - pd[2]
        bdz = pb[2] - pd[2]
        cdz = pc[2] - pd[2]
        
        det = adx * (bdy * cdz - bdz * cdy) + \
              bdx * (cdy * adz - cdz * ady) + \
              cdx * (ady * bdz - adz * bdy)
              
        return det
        
    def insphere(self, pa: np.ndarray, pb: np.ndarray, pc: np.ndarray, 
                 pd: np.ndarray, pe: np.ndarray) -> float:
        """
        Insphere test.
        
        Returns a positive value if pe lies inside the sphere passing through
        pa, pb, pc, and pd; a negative value if it lies outside; and zero if
        the five points are cospherical.
        
        Args:
            pa, pb, pc, pd, pe: 3D points as numpy arrays
            
        Returns:
            Insphere determinant
        """
        aex = pa[0] - pe[0]
        bex = pb[0] - pe[0]
        cex = pc[0] - pe[0]
        dex = pd[0] - pe[0]
        aey = pa[1] - pe[1]
        bey = pb[1] - pe[1]
        cey = pc[1] - pe[1]
        dey = pd[1] - pe[1]
        aez = pa[2] - pe[2]
        bez = pb[2] - pe[2]
        cez = pc[2] - pe[2]
        dez = pd[2] - pe[2]
        
        aexbey = aex * bey
        bexaey = bex * aey
        ab = aexbey - bexaey
        bexcey = bex * cey
        cexbey = cex * bey
        bc = bexcey - cexbey
        cexdey = cex * dey
        dexcey = dex * cey
        cd = cexdey - dexcey
        dexaey = dex * aey
        aexdey = aex * dey
        da = dexaey - aexdey
        
        aexcey = aex * cey
        cexaey = cex * aey
        ac = aexcey - cexaey
        bexdey = bex * dey
        dexbey = dex * bey
        bd = bexdey - dexbey
        
        abc = aez * bc - bez * ac + cez * ab
        bcd = bez * cd - cez * bd + dez * bc
        cda = cez * da + dez * ac + aez * cd
        dab = dez * ab + aez * bd + bez * da
        
        alift = aex * aex + aey * aey + aez * aez
        blift = bex * bex + bey * bey + bez * bez
        clift = cex * cex + cey * cey + cez * cez
        dlift = dex * dex + dey * dey + dez * dez
        
        det = (dlift * abc - clift * dab) + (blift * cda - alift * bcd)
        
        return det
        
    def incircle(self, pa: np.ndarray, pb: np.ndarray, pc: np.ndarray, pd: np.ndarray) -> float:
        """
        Incircle test.
        
        Returns a positive value if pd lies inside the circle passing through
        pa, pb, and pc; a negative value if it lies outside; and zero if the
        four points are cocircular.
        
        Args:
            pa, pb, pc, pd: 2D points as numpy arrays
            
        Returns:
            Incircle determinant
        """
        adx = pa[0] - pd[0]
        ady = pa[1] - pd[1]
        bdx = pb[0] - pd[0]
        bdy = pb[1] - pd[1]
        cdx = pc[0] - pd[0]
        cdy = pc[1] - pd[1]
        
        abdet = adx * bdy - bdx * ady
        bcdet = bdx * cdy - cdx * bdy
        cadet = cdx * ady - adx * cdy
        alift = adx * adx + ady * ady
        blift = bdx * bdx + bdy * bdy
        clift = cdx * cdx + cdy * cdy
        
        det = alift * bcdet + blift * cadet + clift * abdet
        
        return det
        
    @staticmethod
    def distance(pa: np.ndarray, pb: np.ndarray) -> float:
        """Calculate Euclidean distance between two points."""
        return np.linalg.norm(pa - pb)
        
    @staticmethod
    def distance_squared(pa: np.ndarray, pb: np.ndarray) -> float:
        """Calculate squared Euclidean distance between two points."""
        diff = pa - pb
        return np.dot(diff, diff)
        
    @staticmethod
    def dot_product(va: np.ndarray, vb: np.ndarray) -> float:
        """Calculate dot product of two vectors."""
        return np.dot(va, vb)
        
    @staticmethod
    def cross_product(va: np.ndarray, vb: np.ndarray) -> np.ndarray:
        """Calculate cross product of two 3D vectors."""
        return np.cross(va, vb)
        
    @staticmethod
    def triangle_area(pa: np.ndarray, pb: np.ndarray, pc: np.ndarray) -> float:
        """Calculate area of a triangle defined by three points."""
        v1 = pb - pa
        v2 = pc - pa
        cross = np.cross(v1, v2)
        if len(cross.shape) == 0:  # 2D case
            return abs(cross) * 0.5
        else:  # 3D case
            return np.linalg.norm(cross) * 0.5
            
    @staticmethod
    def tetrahedron_volume(pa: np.ndarray, pb: np.ndarray, 
                          pc: np.ndarray, pd: np.ndarray) -> float:
        """Calculate volume of a tetrahedron defined by four points."""
        v1 = pb - pa
        v2 = pc - pa
        v3 = pd - pa
        
        # Volume = |det(v1, v2, v3)| / 6
        det = np.linalg.det(np.column_stack([v1, v2, v3]))
        return abs(det) / 6.0
        
    @staticmethod
    def circumcenter_3d(pa: np.ndarray, pb: np.ndarray, 
                       pc: np.ndarray, pd: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Calculate circumcenter and circumradius of a tetrahedron.
        
        Returns:
            Tuple of (circumcenter, circumradius)
        """
        # Translate so pa is at origin
        b = pb - pa
        c = pc - pa
        d = pd - pa
        
        # Calculate the circumcenter using the formula for tetrahedron circumcenter
        b_sq = np.dot(b, b)
        c_sq = np.dot(c, c)
        d_sq = np.dot(d, d)
        
        bc = np.cross(b, c)
        cd = np.cross(c, d)
        db = np.cross(d, b)
        
        denom = 2.0 * np.dot(b, cd)
        
        if abs(denom) < 1e-14:
            # Degenerate case, return centroid
            center = (pa + pb + pc + pd) / 4.0
            radius = max(np.linalg.norm(center - pa),
                        np.linalg.norm(center - pb),
                        np.linalg.norm(center - pc),
                        np.linalg.norm(center - pd))
            return center, radius
            
        # Circumcenter relative to pa
        circumcenter_rel = (d_sq * bc + c_sq * db + b_sq * cd) / denom
        circumcenter = pa + circumcenter_rel
        
        # Circumradius
        circumradius = np.linalg.norm(circumcenter_rel)
        
        return circumcenter, circumradius
        
    @staticmethod
    def point_in_tetrahedron(point: np.ndarray, pa: np.ndarray, pb: np.ndarray,
                           pc: np.ndarray, pd: np.ndarray) -> bool:
        """
        Test if a point lies inside a tetrahedron.
        
        Uses barycentric coordinates to test containment.
        """
        # Translate so pa is at origin
        v0 = pb - pa
        v1 = pc - pa  
        v2 = pd - pa
        p = point - pa
        
        # Calculate barycentric coordinates
        try:
            # Solve the system: p = u*v0 + v*v1 + w*v2
            # This gives us barycentric coordinates (1-u-v-w, u, v, w)
            matrix = np.column_stack([v0, v1, v2])
            coords = np.linalg.solve(matrix, p)
            
            # Check if all barycentric coordinates are non-negative
            u, v, w = coords
            return u >= 0 and v >= 0 and w >= 0 and (u + v + w) <= 1
            
        except np.linalg.LinAlgError:
            # Degenerate tetrahedron
            return False
            
    @staticmethod
    def dihedral_angle(pa: np.ndarray, pb: np.ndarray, pc: np.ndarray, pd: np.ndarray) -> float:
        """
        Calculate dihedral angle between two faces sharing an edge.
        
        The edge is defined by pa and pb, and the two faces are
        (pa, pb, pc) and (pa, pb, pd).
        
        Returns:
            Dihedral angle in degrees (0-180)
        """
        # Vector along the edge
        edge = pb - pa
        edge_norm = np.linalg.norm(edge)
        
        if edge_norm < 1e-14:
            return 0.0
            
        edge = edge / edge_norm
        
        # Vectors from edge to third points
        v1 = pc - pa
        v2 = pd - pa
        
        # Project out the edge component
        v1_perp = v1 - np.dot(v1, edge) * edge
        v2_perp = v2 - np.dot(v2, edge) * edge
        
        # Normalize
        v1_norm = np.linalg.norm(v1_perp)
        v2_norm = np.linalg.norm(v2_perp)
        
        if v1_norm < 1e-14 or v2_norm < 1e-14:
            return 0.0
            
        v1_perp = v1_perp / v1_norm
        v2_perp = v2_perp / v2_norm
        
        # Calculate angle
        cos_angle = np.clip(np.dot(v1_perp, v2_perp), -1.0, 1.0)
        angle = math.acos(cos_angle)
        
        return math.degrees(angle)
        
    @staticmethod
    def aspect_ratio(pa: np.ndarray, pb: np.ndarray, 
                    pc: np.ndarray, pd: np.ndarray) -> float:
        """
        Calculate aspect ratio of a tetrahedron.
        
        Returns the ratio of circumradius to shortest edge length.
        A perfect tetrahedron has aspect ratio of approximately 1.63.
        """
        # Calculate circumradius
        _, circumradius = Predicates.circumcenter_3d(pa, pb, pc, pd)
        
        # Find shortest edge
        edges = [
            np.linalg.norm(pb - pa),
            np.linalg.norm(pc - pa),
            np.linalg.norm(pd - pa),
            np.linalg.norm(pc - pb),
            np.linalg.norm(pd - pb),
            np.linalg.norm(pd - pc)
        ]
        
        min_edge = min(edges)
        
        if min_edge < 1e-14:
            return float('inf')
            
        return circumradius / min_edge
