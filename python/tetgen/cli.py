"""
Command-line interface for TetGen Python implementation

This module provides a command-line interface similar to the original TetGen.
"""

import sys
import os
import argparse
from typing import List, Optional
from .tetgen_io import TetGenIO
from .tetgen_behavior import TetGenBehavior
from .tetgen_mesh import TetGen


def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="TetGen Python - Quality Tetrahedral Mesh Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tetgen-python input.poly          # Generate mesh from PLC
  tetgen-python -pq1.414 input.poly # Quality mesh with ratio bound
  tetgen-python -ra0.1 input.tet    # Refine mesh with volume constraint
  tetgen-python -pq input.node      # Generate quality mesh from points
  
Switch explanations:
  -p  Tetrahedralize a piecewise linear complex (PLC)
  -r  Refine a previously generated mesh
  -q  Quality mesh generation
  -a  Apply a volume constraint
  -A  Assign attributes to regions
  -D  Conforming Delaunay
  -i  Insert additional points
  -c  Generate convex hull
  -f  Output boundary faces
  -e  Output edges
  -v  Output Voronoi diagram
  -Q  Quiet mode
  -V  Verbose mode
  -z  Zero-based indexing
        """
    )
    
    parser.add_argument('input_file', 
                       help='Input file (.node, .poly, .ele, etc.)')
    
    parser.add_argument('-p', '--plc', action='store_true',
                       help='Tetrahedralize a piecewise linear complex')
    
    parser.add_argument('-r', '--refine', action='store_true',
                       help='Refine a previously generated mesh')
    
    parser.add_argument('-q', '--quality', nargs='?', const='2.0', type=str,
                       help='Quality mesh generation with optional ratio bound')
    
    parser.add_argument('-a', '--volume', nargs='?', const='', type=str,
                       help='Apply volume constraint')
    
    parser.add_argument('-A', '--attributes', action='store_true',
                       help='Assign attributes to regions')
    
    parser.add_argument('-D', '--conforming', action='store_true',
                       help='Conforming Delaunay')
    
    parser.add_argument('-i', '--insert', action='store_true',
                       help='Insert additional points')
    
    parser.add_argument('-c', '--convex', action='store_true',
                       help='Generate convex hull')
    
    parser.add_argument('-f', '--faces', action='store_true',
                       help='Output boundary faces')
    
    parser.add_argument('-e', '--edges', action='store_true',
                       help='Output edges')
    
    parser.add_argument('-v', '--voronoi', action='store_true',
                       help='Output Voronoi diagram')
    
    parser.add_argument('-Q', '--quiet', action='store_true',
                       help='Quiet mode')
    
    parser.add_argument('-V', '--verbose', action='store_true',
                       help='Verbose mode')
    
    parser.add_argument('-z', '--zero', action='store_true',
                       help='Zero-based indexing')
    
    parser.add_argument('-o', '--output', type=str,
                       help='Output filename prefix')
    
    parser.add_argument('--switches', type=str,
                       help='TetGen switches string (alternative to individual flags)')
    
    return parser.parse_args(args)


def create_behavior_from_args(args: argparse.Namespace) -> TetGenBehavior:
    """Create TetGenBehavior from parsed arguments."""
    behavior = TetGenBehavior()
    
    # Handle switches string if provided
    if args.switches:
        behavior.parse_commandline(args.switches)
        return behavior
    
    # Set individual flags
    behavior.plc = args.plc
    behavior.refine = args.refine
    behavior.regionattrib = args.attributes
    behavior.conforming = args.conforming
    behavior.insertaddpoints = args.insert
    behavior.convex = args.convex
    behavior.facesout = args.faces
    behavior.edgesout = args.edges
    behavior.voroout = args.voronoi
    behavior.quiet = args.quiet
    behavior.verbose = args.verbose
    behavior.zeroindex = args.zero
    
    # Handle quality flag
    if args.quality is not None:
        behavior.quality = True
        try:
            ratio = float(args.quality)
            behavior.minratio = ratio
            behavior.ratio = True
        except ValueError:
            behavior.minratio = 2.0
    
    # Handle volume constraint
    if args.volume is not None:
        behavior.varvolume = True
        if args.volume:
            try:
                max_vol = float(args.volume)
                behavior.maxvolume = max_vol
                behavior.fixedvolume = True
            except ValueError:
                pass
    
    return behavior


def determine_file_type(filename: str) -> str:
    """Determine file type from extension."""
    _, ext = os.path.splitext(filename.lower())
    
    if ext == '.node':
        return 'node'
    elif ext == '.poly':
        return 'poly'
    elif ext == '.ele':
        return 'ele'
    elif ext == '.tet':
        return 'tet'
    elif ext == '.off':
        return 'off'
    else:
        # Try to guess from file content or default to poly
        return 'poly'


def load_input_file(filename: str, file_type: str) -> TetGenIO:
    """Load input file based on type."""
    input_data = TetGenIO()
    
    if file_type == 'node':
        if not input_data.load_node(filename):
            raise FileNotFoundError(f"Could not load node file: {filename}")
    elif file_type == 'poly':
        if not input_data.load_poly(filename):
            raise FileNotFoundError(f"Could not load poly file: {filename}")
    elif file_type in ['ele', 'tet']:
        # Load tetrahedral mesh (simplified)
        # Real implementation would load .node and .ele files
        base_name = os.path.splitext(filename)[0]
        node_file = base_name + '.node'
        if os.path.exists(node_file):
            if not input_data.load_node(node_file):
                raise FileNotFoundError(f"Could not load node file: {node_file}")
        else:
            raise FileNotFoundError(f"Node file not found: {node_file}")
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
    
    return input_data


def save_output_files(output_data: TetGenIO, base_name: str, behavior: TetGenBehavior):
    """Save output files based on behavior settings."""
    success = True
    
    # Always save nodes and elements
    node_file = f"{base_name}.1.node"
    if not output_data.save_nodes(node_file):
        print(f"Warning: Could not save node file: {node_file}")
        success = False
    elif not behavior.quiet:
        print(f"Saved {output_data.number_of_points} points to {node_file}")
    
    if output_data.number_of_tetrahedra > 0:
        ele_file = f"{base_name}.1.ele"
        if not output_data.save_elements(ele_file):
            print(f"Warning: Could not save element file: {ele_file}")
            success = False
        elif not behavior.quiet:
            print(f"Saved {output_data.number_of_tetrahedra} tetrahedra to {ele_file}")
    
    # Save faces if requested
    if behavior.facesout and output_data.number_of_triangles > 0:
        face_file = f"{base_name}.1.face"
        try:
            with open(face_file, 'w') as f:
                f.write(f"{output_data.number_of_triangles} 1\n")
                for i, face in enumerate(output_data.triangle_list):
                    marker = 1 if face in getattr(output_data, 'boundary_faces', set()) else 0
                    f.write(f"{i+1} {face[0]+1} {face[1]+1} {face[2]+1} {marker}\n")
            if not behavior.quiet:
                print(f"Saved {output_data.number_of_triangles} faces to {face_file}")
        except Exception as e:
            print(f"Warning: Could not save face file: {e}")
            success = False
    
    # Save edges if requested
    if behavior.edgesout and output_data.number_of_edges > 0:
        edge_file = f"{base_name}.1.edge"
        try:
            with open(edge_file, 'w') as f:
                f.write(f"{output_data.number_of_edges} 1\n")
                for i, edge in enumerate(output_data.edge_list):
                    f.write(f"{i+1} {edge[0]+1} {edge[1]+1} 1\n")
            if not behavior.quiet:
                print(f"Saved {output_data.number_of_edges} edges to {edge_file}")
        except Exception as e:
            print(f"Warning: Could not save edge file: {e}")
            success = False
    
    # Save Voronoi diagram if requested
    if behavior.voroout and output_data.number_of_voronoi_points > 0:
        voro_file = f"{base_name}.1.v.node"
        try:
            with open(voro_file, 'w') as f:
                f.write(f"{output_data.number_of_voronoi_points} 3 0 0\n")
                for i, point in enumerate(output_data.voronoi_point_list):
                    f.write(f"{i+1} {point[0]:.16g} {point[1]:.16g} {point[2]:.16g}\n")
            if not behavior.quiet:
                print(f"Saved {output_data.number_of_voronoi_points} Voronoi points to {voro_file}")
        except Exception as e:
            print(f"Warning: Could not save Voronoi file: {e}")
            success = False
    
    return success


def main():
    """Main entry point for command-line interface."""
    try:
        args = parse_arguments()
        
        # Check if input file exists
        if not os.path.exists(args.input_file):
            print(f"Error: Input file not found: {args.input_file}")
            return 1
        
        # Determine file type
        file_type = determine_file_type(args.input_file)
        
        # Create behavior from arguments
        behavior = create_behavior_from_args(args)
        
        # Set input filename for behavior
        behavior.infilename = args.input_file
        
        # Determine output filename
        if args.output:
            output_base = args.output
        else:
            output_base = os.path.splitext(args.input_file)[0]
        behavior.outfilename = output_base
        
        # Load input file
        if not behavior.quiet:
            print(f"Loading {file_type} file: {args.input_file}")
        
        input_data = load_input_file(args.input_file, file_type)
        
        if not behavior.quiet:
            print(f"Loaded {input_data.number_of_points} points")
            if input_data.number_of_facets > 0:
                print(f"Loaded {input_data.number_of_facets} facets")
        
        # Generate mesh
        tetgen = TetGen()
        output_data = tetgen.tetrahedralize(behavior, input_data)
        
        # Save output files
        if not save_output_files(output_data, output_base, behavior):
            print("Warning: Some output files could not be saved")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
