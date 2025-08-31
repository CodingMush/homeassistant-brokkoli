#!/usr/bin/env python3
"""
Simple verification script to check that the syntax error is fixed.
"""

def verify_syntax_fix():
    """Verify that the syntax error in sensor.py is fixed."""
    try:
        # Try to compile the file
        with open('custom_components/plant/sensor.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to compile the content
        compile(content, 'sensor.py', 'exec')
        print("✓ PASS: sensor.py compiles without syntax errors")
        return True
    except SyntaxError as e:
        print(f"✗ FAIL: Syntax error still present: {e}")
        return False
    except Exception as e:
        print(f"✗ FAIL: Other error: {e}")
        return False

if __name__ == "__main__":
    print("Verifying syntax fix...")
    result = verify_syntax_fix()
    if result:
        print("\n✓ Syntax fix verification passed!")
    else:
        print("\n✗ Syntax fix verification failed!")
        exit(1)