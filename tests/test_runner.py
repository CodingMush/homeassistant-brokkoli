"""Simple test runner to verify tests are working."""
import sys
import os

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'custom_components'))

def test_imports():
    """Test that we can import the modules."""
    try:
        import plant
        print("✓ Plant module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import plant module: {e}")
        return False
    
    try:
        import plant.const
        print("✓ Plant const module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import plant.const module: {e}")
        return False
    
    try:
        import plant.sensor
        print("✓ Plant sensor module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import plant.sensor module: {e}")
        return False
    
    try:
        import plant.services
        print("✓ Plant services module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import plant.services module: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Running import tests...")
    success = test_imports()
    if success:
        print("All import tests passed!")
        sys.exit(0)
    else:
        print("Some import tests failed!")
        sys.exit(1)