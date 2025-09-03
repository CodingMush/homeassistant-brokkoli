#!/usr/bin/env python3
"""
Test script to verify the sensor module can be imported without syntax errors.
"""

import sys
import os

# Add the current directory to the path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Try to import the sensor module
    import sensor
    print("Sensor module imported successfully!")
    
except SyntaxError as e:
    print(f"Syntax error in sensor module: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error importing sensor module: {e}")
    sys.exit(1)