# Development Guide

This guide provides information for developers working on the Brokkoli Plant Manager integration.

## Project Structure

```
homeassistant-brokkoli/
├── custom_components/plant/     # Main integration code
├── docs/                        # Documentation
├── tests/                       # Test files
├── .github/workflows/          # GitHub Actions workflows
├── requirements.txt             # Runtime dependencies
├── requirements_test.txt       # Test dependencies
└── README.md                   # Main README
```

## Setting Up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/dingausmwald/homeassistant-brokkoli.git
   cd homeassistant-brokkoli
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements_test.txt
   ```

## Code Style

Follow the Home Assistant code style guidelines:
- Use type hints where possible
- Follow PEP 8 for code formatting
- Write docstrings for public functions and classes
- Keep functions focused and small

## Testing

### Running Tests

Run the simple verification script:
```bash
python tests/verify_integration.py
```

Run the full test suite:
```bash
pytest tests/
```

### Writing Tests

1. Place test files in the `tests/` directory
2. Use descriptive test function names
3. Follow the AAA pattern (Arrange, Act, Assert)
4. Mock external dependencies
5. Test both positive and negative cases

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run tests to ensure nothing is broken
6. Submit a pull request

## Release Process

1. Update version in `manifest.json`
2. Update changelog
3. Create a GitHub release
4. Publish to HACS if applicable

## Architecture Overview

### Main Components

1. **PlantDevice** - Main device entity that represents a plant or cycle
2. **Sensor Entities** - Current sensor readings and calculated values
3. **Number Entities** - Configurable threshold min/max values
4. **Select Entities** - Plant options and configuration selections
5. **Text Entities** - Plant attributes and descriptive information

### Data Flow

1. External sensors provide raw data
2. PlantCurrent sensors track current values
3. Calculations are performed to derive additional metrics
4. Thresholds are checked to determine plant health
5. Results are exposed as Home Assistant entities

## Constants and Configuration

All constants are defined in `const.py`:
- Attribute names (`ATTR_*`)
- Reading names (`READING_*`)
- Default values
- Icons
- Units

## Best Practices

### Error Handling

- Handle `STATE_UNKNOWN` and `STATE_UNAVAILABLE` gracefully
- Log errors with appropriate context
- Implement retry mechanisms for transient failures
- Validate input data before processing

### Performance

- Use efficient data structures
- Minimize I/O operations
- Cache expensive calculations when appropriate
- Use async/await for I/O-bound operations

### Compatibility

- Maintain backward compatibility when possible
- Handle deprecated configuration options gracefully
- Test with multiple Home Assistant versions
- Follow Home Assistant integration guidelines

## Debugging

### Logging

Use the built-in logger:
```python
import logging
_LOGGER = logging.getLogger(__name__)
_LOGGER.debug("Debug message")
_LOGGER.info("Info message")
_LOGGER.warning("Warning message")
_LOGGER.error("Error message")
```

### Common Issues

1. **Import Errors** - Check that all dependencies are installed
2. **Entity Registration Issues** - Verify device_info is correctly set
3. **State Update Problems** - Check that async_write_ha_state() is called
4. **Configuration Flow Issues** - Validate data before processing

## API Documentation

### Services

The integration provides several services:
- `plant.create_plant`
- `plant.remove_plant`
- `plant.clone_plant`
- `plant.replace_sensor`
- `plant.move_to_area`
- `plant.change_position`
- `plant.add_image`
- `plant.create_cycle`
- `plant.remove_cycle`
- `plant.move_to_cycle`
- `plant.export_plants`
- `plant.import_plants`
- `plant.add_watering`
- `plant.add_conductivity`
- `plant.add_ph`

### WebSockets

The integration provides WebSocket endpoints for the frontend:
- `plant/get_info` - Get plant information
- `plant/upload_image` - Upload plant images
- `plant/delete_image` - Delete plant images
- `plant/set_main_image` - Set main plant image