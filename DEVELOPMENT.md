# Brokkoli Plant Integration Development Guide

This document provides technical documentation for developers working on the Brokkoli Plant Integration for Home Assistant, including testing strategies, architecture overview, and development best practices.

## 🧪 Testing Strategy

The Brokkoli integration includes a comprehensive test suite designed to ensure code quality and prevent regressions. Tests are organized in the [tests](file:///d:/Python/2/homeassistant-brokkoli/tests) directory and can be run in isolation without requiring a full Home Assistant installation.

### Test Organization

All tests are located in the [tests](file:///d:/Python/2/homeassistant-brokkoli/tests) directory with the following structure:

```
tests/
├── test_config_flow_decimals.py          # Configuration flow decimal handling
├── test_constant_validation.py           # Constant definition validation
├── test_consumption_tracking.py          # Consumption calculations and services
├── test_data_persistence.py              # Data storage and restoration
├── test_integration_scenarios.py         # End-to-end integration testing
├── test_plant_entity.py                  # Plant device entity behavior
├── test_rounding_applies_current_sensors.py  # Sensor rounding validation
├── test_sensor_compile_rounding.py       # Sensor compilation rounding tests
├── test_sensor_configuration.py          # Sensor configuration validation
├── test_sensor_rounding_integration.py   # Sensor rounding integration tests
├── test_sensor_value_processing.py       # Sensor value handling and conversion
├── test_service_functionality.py         # Service functionality tests
└── run_tests.py                          # Test runner script
```

### Running Tests

#### Using the Custom Test Runner

The simplest way to run all tests is using the custom test runner:

```bash
cd homeassistant-brokkoli
python tests/run_tests.py
```

This runner executes all tests in isolation and provides a summary of results.

#### Individual Test Execution

Each test file can be executed independently:

```bash
cd homeassistant-brokkoli
python -m pytest tests/test_constant_validation.py -v
python -m pytest tests/test_sensor_value_processing.py -v
# ... etc
```

### Test Categories

#### 1. Constant Validation Tests
File: [test_constant_validation.py](file:///d:/Python/2/homeassistant-brokkoli/tests/test_constant_validation.py)

Validates that all required constants are properly defined in [const.py](file:///d:/Python/2/homeassistant-brokkoli/custom_components/plant/const.py):
- Basic constants (DOMAIN, sensor attributes, readings, units, icons)
- Device types and service constants
- Aggregation methods
- Consumption-related constants

#### 2. Sensor Value Processing Tests
File: [test_sensor_value_processing.py](file:///d:/Python/2/homeassistant-brokkoli/tests/test_sensor_value_processing.py)

Tests sensor value processing logic:
- Numeric conversion (int/float)
- Edge cases (negative values, decimals, scientific notation)
- Invalid value handling

#### 3. Consumption Tracking Tests
File: [test_consumption_tracking.py](file:///d:/Python/2/homeassistant-brokkoli/tests/test_consumption_tracking.py)

Validates consumption tracking functionality:
- Water, fertilizer, and power consumption calculations
- Default consumption values
- Service parameter validation

#### 4. Service Functionality Tests
File: [test_service_functionality.py](file:///d:/Python/2/homeassistant-brokkoli/tests/test_service_functionality.py)

Tests service functionality:
- Service constants validation
- Service schema existence

#### 5. Plant Entity Tests
File: [test_plant_entity.py](file:///d:/Python/2/homeassistant-brokkoli/tests/test_plant_entity.py)

Tests plant entity functionality:
- Plant attributes
- Device types
- Growth phases
- Configuration attributes

#### 6. Integration Scenario Tests
File: [test_integration_scenarios.py](file:///d:/Python/2/homeassistant-brokkoli/tests/test_integration_scenarios.py)

Tests integration scenarios:
- Module imports
- Config flow integration
- Sensor integration
- Service integration
- Data persistence integration
- Consumption integration

#### 7. Data Persistence Tests
File: [test_data_persistence.py](file:///d:/Python/2/homeassistant-brokkoli/tests/test_data_persistence.py)

Tests data persistence:
- Export/import functionality
- Plant creation persistence
- Configuration persistence
- Sensor and consumption data persistence

## 🏗️ Architecture Overview

### Core Components

1. **Configuration Flow** ([config_flow.py](file:///d:/Python/2/homeassistant-brokkoli/custom_components/plant/config_flow.py))
   - UI-based plant setup and configuration
   - Validation of user inputs
   - Integration with Seedfinder for strain data

2. **Plant Device** ([sensor.py](file:///d:/Python/2/homeassistant-brokkoli/custom_components/plant/sensor.py))
   - Main plant entity that groups all sensors
   - Problem state management
   - Threshold validation

3. **Sensor Management** ([sensor.py](file:///d:/Python/2/homeassistant-brokkoli/custom_components/plant/sensor.py))
   - Individual sensor entities for each metric
   - External sensor integration
   - Value processing and validation

4. **Consumption Tracking** ([plant_meters.py](file:///d:/Python/2/homeassistant-brokkoli/custom_components/plant/plant_meters.py))
   - Water, fertilizer, and power consumption meters
   - Utility meter integration
   - Total consumption tracking

5. **Services** ([services.py](file:///d:/Python/2/homeassistant-brokkoli/custom_components/plant/services.py))
   - Plant creation, removal, and cloning
   - Sensor replacement
   - Data export/import
   - Cycle management

### Data Flow

```
External Sensors → Plant Sensors → Plant Device → Consumption Meters → Home Assistant
                              ↘ Services & Config Flow
```

## 🔧 Development Best Practices

### Code Structure

1. **Modular Design**: Each component should have a single responsibility
2. **Constants Management**: All constants should be defined in [const.py](file:///d:/Python/2/homeassistant-brokkoli/custom_components/plant/const.py)
3. **Configuration Centralization**: Sensor configuration should be managed through [sensor_configuration.py](file:///d:/Python/2/homeassistant-brokkoli/custom_components/plant/sensor_configuration.py)
4. **Service Isolation**: Each service should be independently testable

### Testing Guidelines

1. **Isolated Testing**: Tests should not require a full Home Assistant instance
2. **Module Loading**: Use `importlib` to load modules without importing full HA dependencies
3. **Mocking**: Create minimal mock objects for Home Assistant components
4. **Validation**: Use standard Python assertions to validate behavior

### Constant Validation

Ensure all constants required by the integration are properly defined:
- Check that [const.py](file:///d:/Python/2/homeassistant-brokkoli/custom_components/plant/const.py) contains all required constants
- Validate that constants are accessible to all modules that import them
- Verify that AGGREGATION_METHODS and AGGREGATION_METHODS_EXTENDED are properly defined

## 🛠️ Development Environment

### Prerequisites

- Python 3.8+
- Home Assistant development environment (optional for testing)
- pytest for running tests

### Setting Up for Development

1. Clone the repository
2. Install development dependencies
3. Run tests to verify setup

### Code Quality

1. **PEP 8 Compliance**: Follow Python style guidelines
2. **Type Hints**: Use type hints for function parameters and return values
3. **Documentation**: Document public functions and classes
4. **Testing**: Maintain test coverage for new features

## 📈 Quality Metrics

### Test Coverage Targets

- Unit tests: 80% coverage minimum
- Integration tests: 70% coverage minimum
- Functional tests: 90% of core workflows

### Performance Benchmarks

- Test execution time: < 10 minutes
- Memory usage: < 500MB during testing
- Test reliability: > 95% pass rate

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all constants are defined before importing modules
2. **Module Loading**: Use the custom test runner to avoid HA dependency issues
3. **Test Failures**: Check that constants match exactly between test files and implementation

### Debugging Tips

1. Run individual test files to isolate issues
2. Use print statements in tests for debugging
3. Verify constant definitions match test expectations

## 🤝 Contributing

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request with detailed description

### Code Review Guidelines

1. Tests must pass before review
2. New functionality must include tests
3. Code should follow established patterns
4. Documentation should be updated for changes

## 📚 Additional Resources

- [Home Assistant Developer Documentation](https://developers.home-assistant.io/)
- [Brokkoli Card Repository](https://github.com/dingausmwald/lovelace-brokkoli-card)
- [Seedfinder Integration](https://github.com/dingausmwald/homeassistant-seedfinder)