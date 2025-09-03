# Precision Configuration for Plant Integration

## Overview

This document describes the precision configuration system implemented in the Home Assistant Brokkoli plant integration. The system allows configurable decimal places for different sensor types, providing consistent and appropriate precision across all sensor readings and calculations.

## Features

- **Centralized Configuration**: All precision settings are defined in a single location
- **Sensor-Specific Precision**: Different sensors can have different precision levels
- **Display vs. Calculation Precision**: Separate precision settings for display and internal calculations
- **Configurable Decimal Places**: Users can adjust precision settings as needed

## Precision Settings by Sensor Type

### Environmental Sensors

| Sensor Type | Display Precision | Calculation Precision | Example Display |
|-------------|------------------|----------------------|-----------------|
| Temperature | 1 decimal place | 2 decimal places | 20.5°C |
| Moisture | 0 decimal places | 1 decimal place | 45% |
| Conductivity | 0 decimal places | 1 decimal place | 1500 μS/cm |
| Illuminance | 0 decimal places | 1 decimal place | 25000 lux |
| Humidity | 0 decimal places | 1 decimal place | 65% |
| CO2 | 0 decimal places | 1 decimal place | 400 ppm |
| Battery | 0 decimal places | 1 decimal place | 85% |
| pH | 1 decimal place | 2 decimal places | 6.5 pH |

### Light Calculation Sensors

| Sensor Type | Display Precision | Calculation Precision | Example Display |
|-------------|------------------|----------------------|-----------------|
| PPFD | 1 decimal place | 3 decimal places | 250.5 μmol/m²/s |
| DLI | 1 decimal place | 3 decimal places | 15.2 mol/m²/d |

### Consumption Sensors

| Sensor Type | Display Precision | Calculation Precision | Example Display |
|-------------|------------------|----------------------|-----------------|
| Water Consumption | 2 decimal places | 3 decimal places | 1.25 L |
| Fertilizer Consumption | 2 decimal places | 3 decimal places | 0.75 mL |
| Power Consumption | 2 decimal places | 3 decimal places | 125.50 kWh |

## Implementation Details

### Centralized Sensor Configuration

All precision settings are defined in `sensor_config.py`:

```python
SENSOR_DEFINITIONS = {
    ATTR_TEMPERATURE: {
        "sensor_id": ATTR_TEMPERATURE,
        "name": READING_TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "icon": ICON_TEMPERATURE,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "min_value": DEFAULT_MIN_TEMPERATURE,
        "max_value": DEFAULT_MAX_TEMPERATURE,
        "backend_entity_type": "sensor",
        "frontend_field_type": "sensor",
        "is_calculated": False,
        "show_in_ui": True,
        "show_status_bar": True,
        "display_precision": 1,  # 1 decimal place for temperature
        "calculation_precision": 2,  # 2 decimal places for calculations
    },
    # ... other sensors
}
```

### Precision Utility Functions

The `sensor_config.py` file includes utility functions for precision handling:

```python
def round_sensor_value(value, sensor_id, for_display=True):
    """
    Round sensor value according to sensor definition precision settings.
    
    Args:
        value: The value to round
        sensor_id: The sensor ID to get precision settings for
        for_display: If True, use display precision; if False, use calculation precision
    
    Returns:
        The rounded value according to the sensor's precision settings
    """
    # Implementation details...

def get_display_precision(sensor_id):
    """Get the display precision for a sensor."""
    # Implementation details...

def get_calculation_precision(sensor_id):
    """Get the calculation precision for a sensor."""
    # Implementation details...
```

### Usage in Sensor Implementations

Sensor implementations use the centralized precision utilities:

```python
# In sensor.py
from .sensor_config import get_sensor_definition, round_sensor_value

class PlantCurrentMoistureConsumption(RestoreSensor):
    def _state_changed_event(self, event):
        # ... calculation code ...
        volume_drop = (total_drop / 100) * pot_size * water_capacity
        # Use centralized precision handling
        self._attr_native_value = round_sensor_value(volume_drop, "water_consumption")
```

## Benefits

1. **Consistency**: All sensors follow the same precision rules
2. **Maintainability**: Precision settings are centralized and easy to modify
3. **Flexibility**: Different precision levels for different use cases
4. **Accuracy**: Appropriate precision for display vs. calculations
5. **User Experience**: Clean, readable sensor values

## Future Improvements

1. **User-Configurable Precision**: Allow users to adjust precision settings through the UI
2. **Dynamic Precision**: Adjust precision based on value ranges
3. **Localization**: Support different decimal separators based on user locale