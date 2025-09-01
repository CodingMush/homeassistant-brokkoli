# Brokkoli Plant Manager - Developer Guide

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Component Structure](#component-structure)
4. [Development Setup](#development-setup)
5. [Code Standards](#code-standards)
6. [Testing](#testing)
7. [Services](#services)
8. [Entities](#entities)
9. [Configuration Flow](#configuration-flow)

11. [Data Models](#data-models)
12. [API Reference](#api-reference)
13. [Contributing](#contributing)

## Overview

The Brokkoli Plant Manager is a Home Assistant custom integration designed for monitoring cannabis plants with sensors and configurable thresholds. It provides comprehensive plant management features including:

- Device-based plant modeling with grouped sensor entities
- Configurable min/max thresholds for environmental sensors
- Problem state detection when thresholds are exceeded
- Plant lifecycle tracking (growth, flowering phases)
- Support for cloning, moving, and grouping plants into cycles
- Integration with strain database via Seedfinder

## Architecture

The integration follows Home Assistant's custom integration patterns with a modular architecture:

```
plant/
├── __init__.py              # Main integration setup and entry point
├── config_flow.py           # Configuration flow implementation
├── const.py                 # Constants and configuration
├── sensor.py                # Sensor entities
├── plant_thresholds.py      # Threshold entities (min/max values)
├── number.py                # Number entities (threshold configuration)
├── select.py                # Select entities (growth phase, treatment)
├── text.py                  # Text entities (notes, descriptions)
├── services.py              # Custom services
├── services.yaml            # Service definitions
├── plant_helpers.py         # Helper functions and utilities
├── plant_meters.py          # Meter entities for consumption tracking
├── sensor_definitions.py    # Centralized sensor definitions
├── precision_utils.py       # Precision handling utilities
├── performance_utils.py     # Performance optimization utilities
├── security_utils.py        # Security utilities
├── ha_compliance.py         # Home Assistant compliance utilities
├── translations/            # Multi-language support
└── manifest.json            # Integration metadata
```

## Component Structure

### Main Integration (`__init__.py`)
- Entry point for the integration
- Device registration and management
- Entity lifecycle management
- WebSocket API handlers
- Data storage and retrieval

### Configuration Flow (`config_flow.py`)
- Guided UI-based setup for plants, cycles, and tents
- Validation of user input
- Integration with Seedfinder for strain data
- Dynamic form generation based on device type

### Sensors (`sensor.py`)
- Current sensor entities (temperature, moisture, etc.)
- Calculated sensors (PPFD, DLI)
- Consumption sensors (water, fertilizer, power)
- Virtual sensor implementation
- Median sensors for cycles

### Thresholds (`plant_thresholds.py`)
- Min/max threshold entities
- Threshold validation logic
- Problem state detection

### Numbers (`number.py`)
- Configurable threshold values
- UI controls for adjusting limits

### Selects (`select.py`)
- Growth phase selection
- Treatment selection
- Cycle assignment

### Text (`text.py`)
- Notes and description fields
- Custom attributes

### Services (`services.py`)
- Plant management services
- Sensor replacement services
- Data export/import services
- Tent and cycle management services

## Development Setup

### Prerequisites
- Python 3.9+
- Home Assistant development environment
- HACS (for testing installation)

### Installation for Development
1. Clone the repository:
```bash
git clone https://github.com/dingausmwald/homeassistant-brokkoli.git
```

2. Set up Home Assistant development environment:
```bash
# Follow Home Assistant development setup guide
# https://developers.home-assistant.io/docs/development_environment
```

3. Link the integration to your Home Assistant config:
```bash
ln -s /path/to/homeassistant-brokkoli/custom_components/plant ~/.homeassistant/custom_components/plant
```

### Directory Structure
```
homeassistant-brokkoli/
├── custom_components/
│   └── plant/               # Integration code
├── tests/                   # Unit and integration tests
├── README.md                # User documentation
├── DEVELOPER_GUIDE.md       # This document
└── ...
```

## Code Standards

### PEP 8 Compliance
- Follow PEP 8 style guide for Python code
- Use 4 spaces for indentation
- Limit lines to 88 characters (Black standard)
- Use meaningful variable and function names

### Type Hints
- Use type hints for all function parameters and return values
- Use `typing` module for complex types

```python
from typing import Optional, Dict, Any

def example_function(param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """Example function with type hints."""
    return {"result": param1, "count": param2}
```

### Error Handling
- Use try/except blocks for error-prone operations
- Log errors with appropriate severity levels
- Raise `HomeAssistantError` for user-facing errors

```python
try:
    result = some_operation()
except Exception as e:
    _LOGGER.error("Error in some_operation: %s", str(e))
    raise HomeAssistantError(f"Operation failed: {str(e)}")
```

### Documentation
- Add docstrings to all public methods and classes
- Use Google-style docstrings
- Include parameter descriptions and return values

```python
def example_method(param1: str, param2: int = 0) -> bool:
    """Example method documentation.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        ValueError: If param1 is invalid
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    return True
```

## Testing

### Unit Tests
- Located in `tests/` directory
- Use `pytest` for test framework
- Mock external dependencies
- Test edge cases and error conditions

### Running Tests
``bash
# Run all tests
pytest tests/

# Run tests with coverage
pytest --cov=custom_components.plant tests/
```

### Test Structure
```python
import pytest
from unittest.mock import Mock, AsyncMock

class TestExampleClass:
    """Test example class functionality."""
    
    @pytest.fixture
    def mock_hass(self):
        """Create mock Home Assistant instance."""
        return Mock()
        
    def test_example_method(self, mock_hass):
        """Test example method."""
        # Arrange
        instance = ExampleClass(mock_hass)
        
        # Act
        result = instance.example_method()
        
        # Assert
        assert result is True
```

### Integration Tests
- Test complete workflows
- Verify service interactions
- Test configuration flow steps

## Services

### Service Registration
Services are registered in `async_setup_services` in `services.py`:

```python
async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for plant integration."""
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_CREATE_PLANT,
        create_plant,
        schema=CREATE_PLANT_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL
    )
```

### Service Implementation
``python
async def create_plant(call: ServiceCall) -> ServiceResponse:
    """Create a new plant.
    
    Args:
        call: ServiceCall containing plant configuration
        
    Returns:
        ServiceResponse with created plant information
    """
    try:
        # Validate input
        # Create plant entity
        # Return response
        pass
    except Exception as e:
        _LOGGER.error("Error creating plant: %s", str(e))
        raise HomeAssistantError(f"Failed to create plant: {str(e)}")
```

### Available Services
- `plant.create_plant` - Create a new plant
- `plant.remove_plant` - Remove a plant
- `plant.clone_plant` - Clone an existing plant
- `plant.replace_sensor` - Replace sensor for a plant
- `plant.create_cycle` - Create a new cycle
- `plant.remove_cycle` - Remove a cycle
- `plant.move_to_cycle` - Move plant to cycle
- `plant.create_tent` - Create a new tent
- `plant.assign_to_tent` - Assign plant to tent
- `plant.unassign_from_tent` - Unassign plant from tent
- `plant.move_to_area` - Move plant to area
- `plant.add_image` - Add image to plant
- `plant.change_position` - Change plant position
- `plant.export_plants` - Export plant configurations
- `plant.import_plants` - Import plant configurations

## Entities

### Entity Types
1. **Sensor Entities** - Current sensor readings
2. **Number Entities** - Configurable threshold values
3. **Select Entities** - Selection options (growth phase, treatment)
4. **Text Entities** - Notes and descriptions

### Entity Registration
Entities are registered through Home Assistant's entity platform:

```python
async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Plant Sensors from a config entry."""
    plant = hass.data[DOMAIN][entry.entry_id][ATTR_PLANT]
    
    # Create sensor entities
    sensors = [
        PlantCurrentTemperature(hass, entry, plant),
        PlantCurrentMoisture(hass, entry, plant),
        # ... other sensors
    ]
    
    async_add_entities(sensors)
```

### Entity Lifecycle
1. `__init__` - Initialize entity
2. `async_added_to_hass` - Entity added to Home Assistant
3. `async_will_remove_from_hass` - Entity will be removed
4. State updates through `async_write_ha_state()`

## Configuration Flow

### Flow Handler
```python
@config_entries.HANDLERS.register(DOMAIN)
class PlantConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Plant."""
    
    VERSION = 1
    
    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # Implementation
```

### Flow Steps
1. `async_step_user` - Initial step
2. `async_step_plant` - Plant configuration
3. `async_step_cycle` - Cycle configuration
4. `async_step_tent` - Tent configuration
5. `async_step_sensor` - Sensor assignment
6. `async_step_thresholds` - Threshold configuration

## Data Models

### Plant Device
```python
class PlantDevice:
    """Representation of a plant device."""
    
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self._hass = hass
        self._entry = entry
        self._plant_id = None
        self._plant_info = {}
        # ... other attributes
```

### Config Entry Data Structure
```python
{
    "plant_info": {
        "device_type": "plant",
        "name": "Example Plant",
        "strain": "Example Strain",
        "breeder": "Example Breeder",
        "plant_id": "0001",
        "sensors": {
            "temperature_sensor": "sensor.temperature_1",
            "moisture_sensor": "sensor.moisture_1"
        },
        "limits": {
            "min_temperature": 10,
            "max_temperature": 30,
            "min_moisture": 20,
            "max_moisture": 60
        }
    }
}
```

## API Reference

### Constants (`const.py`)
- Domain definitions
- Service names
- Attribute names
- Default values
- Device types

### Sensor Definitions (`sensor_definitions.py`)
- Centralized sensor configuration
- Precision settings
- Device classes
- Units of measurement

### Helper Functions (`plant_helpers.py`)
- Plant data management
- Seedfinder integration
- Data processing utilities

## Contributing

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Implement changes
4. Add tests
5. Update documentation
6. Submit pull request

### Code Review Guidelines
- Follow established patterns
- Maintain backward compatibility
- Add comprehensive tests
- Update documentation
- Pass all CI checks

### Issue Reporting
- Use GitHub issues
- Include Home Assistant version
- Include integration version
- Provide detailed reproduction steps
- Attach relevant logs (sanitize sensitive data)

### Feature Requests
- Open GitHub issues with "enhancement" label
- Describe use case and benefits
- Consider impact on existing functionality
- Propose implementation approach