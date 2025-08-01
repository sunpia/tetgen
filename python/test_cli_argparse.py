#!/usr/bin/env python3
"""
Test script to validate CLI argparse integration works correctly.
"""

import sys
import os

# Add the tetgen package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from tetgen.cli import parse_arguments, create_behavior_from_args
from tetgen.tetgen_behavior import TetGenBehavior

def test_cli_argparse():
    """Test CLI argparse integration."""
    print("Testing CLI argparse integration...")
    
    test_cases = [
        # Basic flags
        (['test.poly', '-p'], 'plc'),
        (['test.poly', '-r'], 'refine'),
        (['test.poly', '-q'], 'quality'),
        (['test.poly', '-a'], 'varvolume'),
        (['test.poly', '-A'], 'regionattrib'),
        (['test.poly', '-D'], 'conforming'),
        (['test.poly', '-i'], 'insertaddpoints'),
        (['test.poly', '-c'], 'convex'),
        (['test.poly', '-f'], 'facesout'),
        (['test.poly', '-e'], 'edgesout'),
        (['test.poly', '-v'], 'voroout'),
        (['test.poly', '-Q'], 'quiet'),
        (['test.poly', '-V'], 'verbose'),
        (['test.poly', '-z'], 'zeroindex'),
        
        # Quality with ratio
        (['test.poly', '-q', '1.414'], 'quality_ratio'),
        (['test.poly', '--quality', '1.2'], 'quality_ratio'),
        
        # Volume constraint
        (['test.poly', '-a', '0.1'], 'volume_constraint'),
        (['test.poly', '--volume', '0.05'], 'volume_constraint'),
        
        # Switches string
        (['test.poly', '--switches', 'pq1.414'], 'switches_string'),
        (['test.poly', '--switches', 'pq1.414a0.1V'], 'switches_complex'),
    ]
    
    passed = 0
    failed = 0
    
    for args, test_name in test_cases:
        try:
            parsed_args = parse_arguments(args)
            behavior = create_behavior_from_args(parsed_args)
            
            if test_name == 'plc':
                assert behavior.plc == True
            elif test_name == 'refine':
                assert behavior.refine == True
            elif test_name == 'quality':
                assert behavior.quality == True
            elif test_name == 'varvolume':
                assert behavior.varvolume == True
            elif test_name == 'regionattrib':
                assert behavior.regionattrib == True
            elif test_name == 'conforming':
                assert behavior.conforming == True
            elif test_name == 'insertaddpoints':
                assert behavior.insertaddpoints == True
            elif test_name == 'convex':
                assert behavior.convex == True
            elif test_name == 'facesout':
                assert behavior.facesout == True
            elif test_name == 'edgesout':
                assert behavior.edgesout == True
            elif test_name == 'voroout':
                assert behavior.voroout == True
            elif test_name == 'quiet':
                assert behavior.quiet == True
            elif test_name == 'verbose':
                assert behavior.verbose == True
            elif test_name == 'zeroindex':
                assert behavior.zeroindex == True
            elif test_name == 'quality_ratio':
                assert behavior.quality == True
                assert behavior.ratio == True
                assert behavior.minratio > 1.0
            elif test_name == 'volume_constraint':
                assert behavior.varvolume == True
                assert behavior.fixedvolume == True
                assert behavior.maxvolume > 0
            elif test_name == 'switches_string':
                assert behavior.plc == True
                assert behavior.quality == True
            elif test_name == 'switches_complex':
                assert behavior.plc == True
                assert behavior.quality == True
                assert behavior.varvolume == True
                assert behavior.verbose == True
            
            print(f"✓ {test_name}: {' '.join(args)}")
            passed += 1
            
        except Exception as e:
            print(f"✗ {test_name}: {' '.join(args)} - {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0

def test_switches_roundtrip():
    """Test that switches can be parsed and regenerated correctly."""
    print("\nTesting switches roundtrip...")
    
    test_switches = [
        "p",
        "pq",
        "pq1.414",
        "pq1.414a0.1",
        "pq1.414a0.1V",
        "pqafev",
        "rcfev",
        "pADi",
        "pqzf",
    ]
    
    passed = 0
    failed = 0
    
    for switches in test_switches:
        try:
            # Parse switches
            behavior = TetGenBehavior()
            behavior.parse_commandline(switches)
            
            # Generate switches string
            generated = behavior.get_commandline_string()
            
            # Parse generated switches
            behavior2 = TetGenBehavior()
            behavior2.parse_commandline(generated)
            
            # Check key properties match
            properties = ['plc', 'quality', 'varvolume', 'refine', 'facesout', 
                         'edgesout', 'voroout', 'verbose', 'quiet', 'zeroindex']
            
            for prop in properties:
                if getattr(behavior, prop) != getattr(behavior2, prop):
                    raise ValueError(f"Property {prop} mismatch")
            
            print(f"✓ {switches} -> {generated}")
            passed += 1
            
        except Exception as e:
            print(f"✗ {switches} - {e}")
            failed += 1
    
    print(f"\nRoundtrip results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    success1 = test_cli_argparse()
    success2 = test_switches_roundtrip()
    
    if success1 and success2:
        print("\n🎉 All CLI argparse tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
