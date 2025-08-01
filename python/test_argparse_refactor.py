#!/usr/bin/env python3
"""
Test script for the refactored TetGenBehavior with argparse
"""

import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tetgen.tetgen_behavior import TetGenBehavior

def test_argparse_refactor():
    """Test the argparse-based command line parsing."""
    print("Testing TetGenBehavior with argparse refactor")
    print("=" * 50)
    
    test_cases = [
        ("pq1.414", "PLC with quality ratio 1.414"),
        ("pq1.414a0.1V", "PLC, quality, volume constraint, verbose"),
        ("rcfev", "Refine with convex hull, faces, edges, voronoi"),
        ("pq2.0A", "PLC, quality ratio 2.0, attributes"),
        ("pDiS100", "PLC, conforming Delaunay, insert points, 100 Steiner points"),
        ("pqzfT1e-6", "PLC, quality, zero-indexing, faces, tolerance"),
        ("po2", "PLC with second-order elements"),
        ("pY0", "PLC with Y0 option"),
        ("-pq1.2", "With leading dash"),
        ("", "Empty switches"),
    ]
    
    for switches, description in test_cases:
        print(f"\nTesting: '{switches}' ({description})")
        print("-" * 40)
        
        behavior = TetGenBehavior()
        success = behavior.parse_commandline(switches)
        
        if success:
            print("✓ Parsing successful")
            print(f"  Command line: {behavior.commandline}")
            print(f"  Reconstructed: {behavior.get_commandline_string()}")
            
            # Show some key settings
            settings = []
            if behavior.plc:
                settings.append("PLC")
            if behavior.quality:
                settings.append(f"Quality (ratio: {behavior.minratio})")
            if behavior.refine:
                settings.append("Refine")
            if behavior.varvolume:
                if behavior.fixedvolume:
                    settings.append(f"Volume constraint: {behavior.maxvolume}")
                else:
                    settings.append("Volume constraint")
            if behavior.convex:
                settings.append("Convex hull")
            if behavior.facesout:
                settings.append("Output faces")
            if behavior.edgesout:
                settings.append("Output edges")
            if behavior.voroout:
                settings.append("Output Voronoi")
            if behavior.verbose:
                settings.append("Verbose")
            if behavior.quiet:
                settings.append("Quiet")
            if behavior.zeroindex:
                settings.append("Zero-based indexing")
            if behavior.order == 2:
                settings.append("Second-order elements")
            if behavior.steiner > 0:
                settings.append(f"Steiner points: {behavior.steiner}")
            if behavior.epsilon != 1e-8:
                settings.append(f"Tolerance: {behavior.epsilon}")
                
            if settings:
                print(f"  Active settings: {', '.join(settings)}")
            else:
                print("  No special settings active")
        else:
            print("✗ Parsing failed")

def test_comparison_with_old_method():
    """Compare results with what the old method would produce."""
    print("\n\nComparison Test")
    print("=" * 50)
    
    # Test cases that should work the same way
    test_switches = [
        "pq1.414",
        "pq2.0a0.1",
        "rcfev",
        "pADi",
        "pzfQ",
        "po2V"
    ]
    
    for switches in test_switches:
        print(f"\nTesting switches: '{switches}'")
        
        behavior = TetGenBehavior()
        success = behavior.parse_commandline(switches)
        
        if success:
            reconstructed = behavior.get_commandline_string()
            print(f"  Original:      {switches}")
            print(f"  Reconstructed: {reconstructed}")
            
            # Check if key flags are set correctly
            checks = []
            if 'p' in switches and behavior.plc:
                checks.append("✓ PLC")
            elif 'p' in switches:
                checks.append("✗ PLC")
                
            if 'q' in switches and behavior.quality:
                checks.append("✓ Quality")
            elif 'q' in switches:
                checks.append("✗ Quality")
                
            if 'r' in switches and behavior.refine:
                checks.append("✓ Refine")
            elif 'r' in switches:
                checks.append("✗ Refine")
                
            if 'a' in switches and behavior.varvolume:
                checks.append("✓ Volume")
            elif 'a' in switches:
                checks.append("✗ Volume")
                
            if 'f' in switches and behavior.facesout:
                checks.append("✓ Faces")
            elif 'f' in switches:
                checks.append("✗ Faces")
                
            if 'V' in switches and behavior.verbose:
                checks.append("✓ Verbose")
            elif 'V' in switches:
                checks.append("✗ Verbose")
                
            print(f"  Checks: {' '.join(checks)}")
        else:
            print("  ✗ Parsing failed")

def main():
    """Run all tests."""
    try:
        test_argparse_refactor()
        test_comparison_with_old_method()
        print("\n" + "=" * 50)
        print("All tests completed!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
