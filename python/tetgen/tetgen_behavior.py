"""
TetGenBehavior - Configuration and behavior settings for TetGen

This module contains the TetGenBehavior class which handles all configuration
options and behavioral parameters for tetrahedral mesh generation.
"""

import argparse
import re
from typing import Optional, Dict, Any, List


class TetGenBehavior:
    """
    Configuration and behavior settings for TetGen.
    
    This class maintains all switches and parameters used by TetGen's
    mesh generation algorithms, similar to the tetgenbehavior class in C++ TetGen.
    """
    
    def __init__(self):
        # Mesh generation switches
        self.plc = False                    # -p: Tetrahedralize a piecewise linear complex (PLC)
        self.refine = False                 # -r: Refine a previously generated mesh
        self.quality = False                # -q: Quality mesh generation
        self.ratio = False                  # -q: Quality mesh generation with ratio bound
        self.minratio = 2.0                # Minimum radius-edge ratio
        self.mindihedral = 0.0             # Minimum dihedral angle bound
        self.maxdihedral = 180.0           # Maximum dihedral angle bound
        self.varvolume = False             # -a: Apply a volume constraint
        self.fixedvolume = False           # Apply a fixed volume constraint
        self.maxvolume = -1.0              # Maximum volume constraint
        self.regionattrib = False          # -A: Assign attributes to regions
        self.conforming = False            # -D: Conforming Delaunay
        self.insertaddpoints = False       # -i: Insert additional points
        self.diagnose = False              # -d: Diagnose intersections
        self.checkclosure = 0              # Check PLC closure level
        self.convex = False                # -c: Generate a convex hull
        self.weighted = False              # -w: Weighted Delaunay triangulation
        self.brio_hilbert = True           # Use BRIO+Hilbert point ordering
        self.incrflip = False              # Use incremental flip algorithm
        self.flipinsert = False            # Use flip insertion algorithm
        self.metric = False                # -m: Use a metric
        self.coarsen = False               # -R: Coarsen the mesh
        
        # Output format switches
        self.zeroindex = False             # -z: Number items starting from zero
        self.order = 1                     # -o2: Generate second-order elements
        self.facesout = False              # -f: Output faces
        self.edgesout = False              # -e: Output edges
        self.voroout = False               # -v: Output Voronoi diagram
        self.meditview = False             # -g: Output mesh for Medit
        self.gidview = False               # -G: Output mesh for GiD
        self.geomview = False              # -O: Output mesh for Geomview
        self.optlevel = 1                  # Mesh optimization level
        self.optscheme = 7                 # Optimization scheme
        self.dofull = False                # Do full optimization
        
        # Algorithmic switches
        self.fliprepair = True             # Use flip operations for repair
        self.docheck = False               # -C: Check the consistency of mesh
        self.quiet = False                 # -Q: Quiet mode
        self.verbose = False               # -V: Verbose mode
        self.useshelles = False            # Use shell elements
        
        # Mesh sizing
        self.nobisect = False              # Suppress boundary segment splitting
        self.steiner = -1                  # Maximum number of Steiner points
        self.coarsenratio = 0.0           # Coarsening ratio
        self.steinerleft = -1              # Number of Steiner points left
        
        # Input/output file control
        self.object = 0                    # Object type (0=nodes, 1=poly, 2=off)
        self.nofacewritten = False         # Don't write faces
        self.noelewritten = False          # Don't write elements
        self.nojettison = False            # Don't jettison unused vertices
        
        # Command line strings
        self.commandline = ""              # Original command line
        self.switches = ""                 # Switch string
        
        # File names
        self.infilename = ""               # Input filename
        self.outfilename = ""              # Output filename
        self.addinfilename = ""            # Additional points filename
        self.bgmeshfilename = ""           # Background mesh filename
        
        # Internal parameters
        self.epsilon = 1e-8                # A relative tolerance for collinearity test
        self.minedgelength = 0.0          # Minimum edge length
        self.maxedgelength = 0.0          # Maximum edge length
        self.alpha1 = 0.0                 # Alpha parameter 1
        self.alpha2 = 0.0                 # Alpha parameter 2
        self.alpha3 = 0.0                 # Alpha parameter 3
        
        # Quality mesh parameters
        self.offcenter = 0.0              # Off-center parameter
        self.conformdel = False           # Conforming Delaunay
        self.optmaxdihedral = 165.0       # Maximum dihedral angle for optimization
        self.optminsmtdihed = 179.0       # Minimum smoothing dihedral angle
        self.optminslidihed = 179.0       # Minimum sliding dihedral angle
        
        # Coarsening parameters
        self.coarsenthres = 0.0           # Coarsening threshold
        
        # Element numbering
        self.firstnumber = 0              # First vertex/element number
        
    def parse_commandline(self, switches: str) -> bool:
        """
        Parse command line switches string using argparse.
        
        Args:
            switches: Command line switches string (e.g., "pq1.414a0.1")
            
        Returns:
            True if parsing successful, False otherwise
        """
        if not switches:
            return True
            
        self.switches = switches
        self.commandline = f"tetgen {switches}"
        
        # Convert TetGen-style switches to argparse format
        # Handle switches that may be concatenated (e.g., "pq1.414a0.1")
        args = self._convert_tetgen_switches_to_args(switches)
        
        # Create argument parser
        parser = argparse.ArgumentParser(prog='tetgen', add_help=False, exit_on_error=False)
        
        # Add all TetGen switches
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
        parser.add_argument('-d', '--diagnose', action='store_true',
                           help='Diagnose intersections')
        parser.add_argument('-c', '--convex', action='store_true',
                           help='Generate convex hull')
        parser.add_argument('-w', '--weighted', action='store_true',
                           help='Weighted Delaunay triangulation')
        parser.add_argument('-m', '--metric', action='store_true',
                           help='Use metric')
        parser.add_argument('-R', '--coarsen', action='store_true',
                           help='Coarsen mesh')
        parser.add_argument('-z', '--zero', action='store_true',
                           help='Zero-based indexing')
        parser.add_argument('-o', '--order', type=str, default='1',
                           help='Element order (1 or 2)')
        parser.add_argument('-f', '--faces', action='store_true',
                           help='Output faces')
        parser.add_argument('-e', '--edges', action='store_true',
                           help='Output edges')
        parser.add_argument('-v', '--voronoi', action='store_true',
                           help='Output Voronoi diagram')
        parser.add_argument('-g', '--medit', action='store_true',
                           help='Output for Medit')
        parser.add_argument('-G', '--gid', action='store_true',
                           help='Output for GiD')
        parser.add_argument('-O', '--geomview', action='store_true',
                           help='Output for Geomview')
        parser.add_argument('-C', '--check', action='store_true',
                           help='Check mesh consistency')
        parser.add_argument('-Q', '--quiet', action='store_true',
                           help='Quiet mode')
        parser.add_argument('-V', '--verbose', action='store_true',
                           help='Verbose mode')
        parser.add_argument('-Y', '--yoptions', type=str,
                           help='Y options')
        parser.add_argument('-S', '--steiner', type=int,
                           help='Maximum Steiner points')
        parser.add_argument('-T', '--tolerance', type=float,
                           help='Tolerance value')
        
        try:
            # Parse the arguments
            parsed_args = parser.parse_args(args)
            
            # Apply parsed arguments to behavior settings
            self._apply_parsed_args(parsed_args)
            
            return True
            
        except (argparse.ArgumentError, SystemExit, ValueError) as e:
            # Handle parsing errors gracefully
            if not self.quiet:
                print(f"Error parsing switches '{switches}': {e}")
            return False
            
    def _convert_tetgen_switches_to_args(self, switches: str) -> List[str]:
        """
        Convert TetGen-style concatenated switches to separate arguments.
        
        For example: "pq1.414a0.1V" -> ["-p", "-q", "1.414", "-a", "0.1", "-V"]
        """
        args = []
        i = 0
        
        while i < len(switches):
            char = switches[i]
            
            # Skip leading dashes
            if char == '-':
                i += 1
                continue
                
            # Add the switch with dash prefix
            switch_arg = f"-{char}"
            args.append(switch_arg)
            i += 1
            
            # Handle switches that take numeric arguments
            if char in ['q', 'a', 'S', 'T']:
                # Look for following digits/decimal
                value = ""
                while i < len(switches) and (switches[i].isdigit() or switches[i] in '.eE+-'):
                    value += switches[i]
                    i += 1
                    
                if value:
                    args.append(value)
                    
            # Handle special cases
            elif char == 'o' and i < len(switches) and switches[i] == '2':
                args.append('2')
                i += 1
            elif char == 'Y' and i < len(switches):
                # Y takes a single character option (Y0, Y1, etc.)
                if i < len(switches) and switches[i].isdigit():
                    args.append(switches[i])
                    i += 1
                else:
                    # Default Y option
                    args.append('0')
                
        return args
        
    def _apply_parsed_args(self, args: argparse.Namespace):
        """Apply parsed arguments to behavior settings."""
        self.plc = args.plc
        self.refine = args.refine
        self.regionattrib = args.attributes
        self.conforming = args.conforming
        self.insertaddpoints = args.insert
        self.diagnose = args.diagnose
        self.convex = args.convex
        self.weighted = args.weighted
        self.metric = args.metric
        self.coarsen = args.coarsen
        self.zeroindex = args.zero
        self.facesout = args.faces
        self.edgesout = args.edges
        self.voroout = args.voronoi
        self.meditview = args.medit
        self.gidview = args.gid
        self.geomview = args.geomview
        self.docheck = args.check
        self.quiet = args.quiet
        self.verbose = args.verbose
        
        # Handle quality flag with optional ratio
        if args.quality is not None:
            self.quality = True
            if args.quality and args.quality != '2.0':  # Has a value and not default
                try:
                    self.minratio = float(args.quality)
                    self.ratio = True
                except ValueError:
                    self.minratio = 2.0
                    self.ratio = False
            else:
                # q was specified but no ratio given, use default ratio
                self.minratio = 2.0
                self.ratio = True
            
        # Handle volume constraint
        if args.volume is not None:
            self.varvolume = True
            if args.volume:  # Has a value
                try:
                    self.maxvolume = float(args.volume)
                    self.fixedvolume = True
                except ValueError:
                    pass
                    
        # Handle element order
        if args.order == '2':
            self.order = 2
        else:
            self.order = 1
            
        # Handle zero indexing
        if self.zeroindex:
            self.firstnumber = 0
            
        # Handle Y options
        if args.yoptions:
            if args.yoptions == '0':
                self.nobisect = True
            # Add other Y options as needed
            
        # Handle Steiner points
        if args.steiner is not None:
            self.steiner = args.steiner
            self.steinerleft = self.steiner
            
        # Handle tolerance
        if args.tolerance is not None:
            self.epsilon = args.tolerance
        
    def print_switches(self):
        """Print all active switches."""
        print("TetGen switches:")
        if self.plc:
            print("  -p: Tetrahedralize a piecewise linear complex")
        if self.refine:
            print("  -r: Refine a previously generated mesh")
        if self.quality:
            print(f"  -q: Quality mesh generation (min ratio: {self.minratio})")
        if self.varvolume:
            if self.fixedvolume:
                print(f"  -a: Apply volume constraint (max: {self.maxvolume})")
            else:
                print("  -a: Apply volume constraint")
        if self.regionattrib:
            print("  -A: Assign attributes to regions")
        if self.conforming:
            print("  -D: Conforming Delaunay")
        if self.insertaddpoints:
            print("  -i: Insert additional points")
        if self.diagnose:
            print("  -d: Diagnose intersections")
        if self.convex:
            print("  -c: Generate convex hull")
        if self.weighted:
            print("  -w: Weighted Delaunay triangulation")
        if self.metric:
            print("  -m: Use metric")
        if self.coarsen:
            print("  -R: Coarsen mesh")
        if self.zeroindex:
            print("  -z: Zero-based indexing")
        if self.order == 2:
            print("  -o2: Second-order elements")
        if self.facesout:
            print("  -f: Output faces")
        if self.edgesout:
            print("  -e: Output edges")
        if self.voroout:
            print("  -v: Output Voronoi diagram")
        if self.docheck:
            print("  -C: Check mesh consistency")
        if self.quiet:
            print("  -Q: Quiet mode")
        if self.verbose:
            print("  -V: Verbose mode")
            
    def get_commandline_string(self) -> str:
        """Get the equivalent command line string for current settings."""
        switches = ""
        
        if self.plc:
            switches += "p"
        if self.refine:
            switches += "r"
        if self.quality:
            switches += "q"
            if self.ratio and self.minratio != 2.0:
                switches += str(self.minratio)
        if self.varvolume:
            switches += "a"
            if self.fixedvolume and self.maxvolume > 0:
                switches += str(self.maxvolume)
        if self.regionattrib:
            switches += "A"
        if self.conforming:
            switches += "D"
        if self.insertaddpoints:
            switches += "i"
        if self.diagnose:
            switches += "d"
        if self.convex:
            switches += "c"
        if self.weighted:
            switches += "w"
        if self.metric:
            switches += "m"
        if self.coarsen:
            switches += "R"
        if self.zeroindex:
            switches += "z"
        if self.order == 2:
            switches += "o2"
        if self.facesout:
            switches += "f"
        if self.edgesout:
            switches += "e"
        if self.voroout:
            switches += "v"
        if self.meditview:
            switches += "g"
        if self.gidview:
            switches += "G"
        if self.geomview:
            switches += "O"
        if self.docheck:
            switches += "C"
        if self.quiet:
            switches += "Q"
        if self.verbose:
            switches += "V"
        if self.nobisect:
            switches += "Y0"
        if self.steiner >= 0:
            switches += f"S{self.steiner}"
        if self.epsilon != 1e-8:
            switches += f"T{self.epsilon}"
            
        return switches
        
    def copy_from(self, other: 'TetGenBehavior'):
        """Copy settings from another TetGenBehavior instance."""
        # Copy all boolean flags
        self.plc = other.plc
        self.refine = other.refine
        self.quality = other.quality
        self.ratio = other.ratio
        self.varvolume = other.varvolume
        self.fixedvolume = other.fixedvolume
        self.regionattrib = other.regionattrib
        self.conforming = other.conforming
        self.insertaddpoints = other.insertaddpoints
        self.diagnose = other.diagnose
        self.convex = other.convex
        self.weighted = other.weighted
        self.brio_hilbert = other.brio_hilbert
        self.incrflip = other.incrflip
        self.flipinsert = other.flipinsert
        self.metric = other.metric
        self.coarsen = other.coarsen
        self.zeroindex = other.zeroindex
        self.facesout = other.facesout
        self.edgesout = other.edgesout
        self.voroout = other.voroout
        self.meditview = other.meditview
        self.gidview = other.gidview
        self.geomview = other.geomview
        self.fliprepair = other.fliprepair
        self.docheck = other.docheck
        self.quiet = other.quiet
        self.verbose = other.verbose
        self.useshelles = other.useshelles
        self.nobisect = other.nobisect
        self.nofacewritten = other.nofacewritten
        self.noelewritten = other.noelewritten
        self.nojettison = other.nojettison
        
        # Copy numeric parameters
        self.minratio = other.minratio
        self.mindihedral = other.mindihedral
        self.maxdihedral = other.maxdihedral
        self.maxvolume = other.maxvolume
        self.order = other.order
        self.optlevel = other.optlevel
        self.optscheme = other.optscheme
        self.steiner = other.steiner
        self.coarsenratio = other.coarsenratio
        self.steinerleft = other.steinerleft
        self.object = other.object
        self.epsilon = other.epsilon
        self.minedgelength = other.minedgelength
        self.maxedgelength = other.maxedgelength
        self.alpha1 = other.alpha1
        self.alpha2 = other.alpha2
        self.alpha3 = other.alpha3
        self.offcenter = other.offcenter
        self.optmaxdihedral = other.optmaxdihedral
        self.optminsmtdihed = other.optminsmtdihed
        self.optminslidihed = other.optminslidihed
        self.coarsenthres = other.coarsenthres
        self.firstnumber = other.firstnumber
        
        # Copy strings
        self.commandline = other.commandline
        self.switches = other.switches
        self.infilename = other.infilename
        self.outfilename = other.outfilename
        self.addinfilename = other.addinfilename
        self.bgmeshfilename = other.bgmeshfilename
