"""
TetGen Python package main module

Allows running the package as a module with:
python -m tetgen
"""

import sys
import os

def main():
    """Main entry point when package is run as module."""
    print("TetGen Python Implementation")
    print("=" * 40)
    print()
    print("Usage:")
    print("  python -m tetgen.cli [options] input_file    # Run CLI")
    print("  python demo.py                               # Run demo")
    print("  python examples/basic_examples.py            # Run examples")
    print("  python -m pytest tests/                      # Run tests")
    print()
    print("For command-line interface:")
    print("  python -m tetgen.cli --help")
    print()
    print("For Python API usage, see examples/ directory")
    
    # If arguments provided, try to run CLI
    if len(sys.argv) > 1:
        try:
            from .cli import main as cli_main
            sys.exit(cli_main())
        except ImportError as e:
            print(f"Error importing CLI: {e}")
            sys.exit(1)
    
if __name__ == "__main__":
    main()
