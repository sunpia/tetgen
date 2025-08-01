#!/usr/bin/env python3
"""
Test complex command parsing to ensure full argparse compatibility.
"""

import sys
import os

# Add the tetgen package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from tetgen.tetgen_behavior import TetGenBehavior

def test_complex_parsing():
    """Test complex parsing scenarios."""
    print("Testing complex command parsing scenarios...")
    
    test_cases = [
        # Original format complex commands
        ("pq1.414a0.1YS0T1e-10V", {
            'plc': True,
            'quality': True, 
            'ratio': True,
            'minratio': 1.414,
            'varvolume': True,
            'fixedvolume': True,
            'maxvolume': 0.1,
            'nobisect': True,
            'steiner': 0,
            'epsilon': 1e-10,
            'verbose': True
        }),
        
        # Quality with different ratios
        ("q2.0", {
            'quality': True,
            'ratio': True,
            'minratio': 2.0
        }),
        
        ("q1.1", {
            'quality': True,
            'ratio': True,
            'minratio': 1.1
        }),
        
        # Volume constraints
        ("a5.5", {
            'varvolume': True,
            'fixedvolume': True,
            'maxvolume': 5.5
        }),
        
        # Steiner points
        ("S10", {
            'steiner': 10
        }),
        
        # Tolerance
        ("T1e-12", {
            'epsilon': 1e-12
        }),
        
        # All output flags
        ("fevg", {
            'facesout': True,
            'edgesout': True,
            'voroout': True,
            'meditview': True
        }),
    ]
    
    passed = 0
    failed = 0
    
    for switches, expected in test_cases:
        try:
            behavior = TetGenBehavior()
            behavior.parse_commandline(switches)
            
            # Check all expected properties
            for prop, expected_value in expected.items():
                actual_value = getattr(behavior, prop)
                if isinstance(expected_value, float):
                    if abs(actual_value - expected_value) > 1e-10:
                        raise ValueError(f"Property {prop}: expected {expected_value}, got {actual_value}")
                else:
                    if actual_value != expected_value:
                        raise ValueError(f"Property {prop}: expected {expected_value}, got {actual_value}")
            
            # Test roundtrip
            generated = behavior.get_commandline_string()
            behavior2 = TetGenBehavior()
            behavior2.parse_commandline(generated)
            
            # Check key properties still match
            for prop in expected.keys():
                if isinstance(expected[prop], float):
                    if abs(getattr(behavior2, prop) - expected[prop]) > 1e-10:
                        raise ValueError(f"Roundtrip failed for {prop}")
                else:
                    if getattr(behavior2, prop) != expected[prop]:
                        raise ValueError(f"Roundtrip failed for {prop}")
            
            print(f"✓ {switches} -> {generated}")
            passed += 1
            
        except Exception as e:
            print(f"✗ {switches} - {e}")
            failed += 1
    
    print(f"\nComplex parsing results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    success = test_complex_parsing()
    
    if success:
        print("\n🎉 All complex parsing tests passed!")
        print("The argparse refactor maintains full backward compatibility!")
        sys.exit(0)
    else:
        print("\n❌ Some complex parsing tests failed")
        sys.exit(1)
