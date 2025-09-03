# Brokkoli Plant Integration Tests

This directory contains tests for the Brokkoli Plant Manager integration for Home Assistant.

## Running Tests

### Simple Verification

To run a basic verification of the integration:

```bash
python tests/verify_integration.py
```

This script checks that all modules can be imported and that critical constants are properly defined.

### Full Test Suite

To run the full test suite (requires pytest and pytest-homeassistant-custom-component):

```bash
pytest tests/
```

## Test Structure

- `test_const.py` - Tests for constants defined in const.py
- `test_init.py` - Tests for the main integration module
- `test_sensor.py` - Tests for sensor entities
- `test_config_flow.py` - Tests for the configuration flow
- `test_integration.py` - Integration tests
- `verify_integration.py` - Simple verification script that doesn't require pytest
- `conftest.py` - pytest configuration and fixtures

## Requirements

To run the full test suite, you need:

```bash
pip install -r requirements_test.txt
```

This will install:
- pytest
- pytest-asyncio
- pytest-homeassistant-custom-component

## Test Categories

### Unit Tests
- Test individual functions and classes
- Mock external dependencies
- Focus on specific functionality

### Integration Tests
- Test the interaction between components
- Verify proper entity creation and registration
- Test service functionality

### Compatibility Tests
- Ensure backward compatibility
- Test with different Home Assistant versions
- Verify proper error handling