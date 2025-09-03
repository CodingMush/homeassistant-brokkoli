#!/usr/bin/env python3
"""Run all tests and verifications for the Brokkoli Plant Integration."""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and return the result."""
    print(f"\n[TEST] {description}")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode == 0:
            print("   [PASS] Success")
            if result.stdout.strip():
                # Only show first 200 characters to avoid cluttering output
                output = result.stdout.strip()
                if len(output) > 200:
                    output = output[:200] + "..."
                print(f"   Output: {output}")
            return True
        else:
            print("   [FAIL] Failed")
            if result.stderr.strip():
                # Only show first 200 characters to avoid cluttering output
                error = result.stderr.strip()
                if len(error) > 200:
                    error = error[:200] + "..."
                print(f"   Error: {error}")
            return False
            
    except Exception as e:
        print(f"   [FAIL] Exception: {e}")
        return False

def main():
    """Run all tests."""
    print("Brokkoli Plant Integration - Test Runner")
    print("=" * 50)
    
    results = []
    
    # Run simple verification
    results.append(run_command(
        "python tests/verify_integration.py",
        "Running simple verification"
    ))
    
    # Try to import all modules
    results.append(run_command(
        "python -c \"import custom_components.plant; import custom_components.plant.const; import custom_components.plant.sensor; print('All modules imported successfully')\"",
        "Testing module imports"
    ))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    
    passed = sum(results)
    total = len(results)
    
    print(f"   Passed: {passed}/{total}")
    
    if passed == total:
        print("   [SUCCESS] All tests passed!")
        return 0
    else:
        print("   [WARNING] Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())