# Temperature Sensor Precision Fix

## Issue
Plants without tents were showing temperature values with more decimal places than plants with tents. This inconsistency was caused by the fact that:
- Regular temperature sensors ([PlantCurrentTemperature](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L798-L817)) were not using the sensor definitions for precision control
- Virtual temperature sensors (used for tent-assigned plants) were properly using sensor definitions

## Root Cause
The [PlantCurrentTemperature](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L798-L817) class was not inheriting from [SensorDefinitionMixin](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor_definitions.py#L549-L570), which is responsible for applying sensor definitions including precision settings.

According to the sensor definitions in [sensor_definitions.py](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor_definitions.py), temperature sensors should have:
- `display_precision=1` (1 decimal place for display)
- `calculation_precision=2` (2 decimal places for calculations)

## Fix Applied
Modified the [PlantCurrentTemperature](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L798-L817) class in `sensor.py` to:

1. **Inherit from [SensorDefinitionMixin](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor_definitions.py#L549-L570)**: Added `SensorDefinitionMixin` to the class inheritance
2. **Use sensor definition in constructor**: Changed `super().__init__(hass, config, plantdevice)` to `super().__init__("temperature", hass, config, plantdevice)`
3. **Add state_changed method**: Override to apply rounding to temperature values using sensor definition
4. **Add async_update method**: Override to apply rounding during async updates

## Result
Both regular temperature sensors (for plants without tents) and virtual temperature sensors (for plants with tents) now:
- Use the same precision settings from sensor definitions
- Display temperature values with consistent formatting (1 decimal place)
- Maintain consistent behavior across all plant types

## Files Modified
- `custom_components/plant/sensor.py` - Updated [PlantCurrentTemperature](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L798-L817) class to use sensor definitions

## Verification
- Syntax check passed successfully
- Implementation now matches the pattern used by [PlantCurrentHumidity](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L819-L844) and other sensor classes
- Consistent with the project's requirement to use sensor_definitions configuration