# Brokkoli Plant Manager Tests

This directory contains tests for the Brokkoli Plant Manager Home Assistant integration.

## Test Structure

- `conftest.py` - Test fixtures and configuration
- `test_init.py` - Tests for the main integration initialization
- `test_config_flow.py` - Tests for the configuration flow
- `test_services.py` - Tests for plant services
- `test_sensors.py` - Tests for sensor entities
- `test_plant_meters.py` - Tests for plant meter entities
- `test_plant_helpers.py` - Tests for helper functions
- `test_number.py` - Tests for number entities

## Running Tests

To run the tests, execute:

```bash
pytest
```

To run tests with coverage:

```bash
pytest --cov=custom_components.plant
```

## Test Coverage

The tests cover:

1. **Service functionality** - Testing all custom services like replace_sensor, create_plant, remove_plant
2. **Sensor processing** - Testing how sensors process valid, invalid, and boundary condition values
3. **Entity initialization** - Testing proper initialization of all entity types
4. **Configuration flow** - Testing the user configuration process
5. **Helper functions** - Testing utility functions like PPFD to DLI conversion
6. **Integration setup** - Testing the main integration entry points

## Writing New Tests

When adding new tests:

1. Use the existing fixtures in `conftest.py` when possible
2. Follow the naming convention `test_descriptive_test_name`
3. Include both positive and negative test cases
4. Test boundary conditions and error cases
5. Use mocks to isolate the unit under test