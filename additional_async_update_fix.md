# Additional Async Update Method Fix

## Issue
More sensors were throwing AttributeError when trying to update:
```
AttributeError: 'super' object has no attribute 'async_update'
```

This was affecting:
- PlantCurrentConductivity sensors
- PlantCurrentMoisture sensors

## Root Cause
The [PlantCurrentStatus](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L385-L521) class (which inherits from [RestoreSensor](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L385-L521)) does not have an `async_update` method, but the sensor classes were calling `await super().async_update()` in their [async_update](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L1319-L1323) methods.

This was the same issue that was previously fixed in [PlantCurrentTemperature](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L798-L827), [PlantCurrentHumidity](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L829-L854), [PlantCurrentIlluminance](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L523-L548), and [VirtualSensor](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L2253-L2387) classes.

## Fix Applied
Removed calls to `await super().async_update()` from the following classes:
- [PlantCurrentConductivity](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L550-L593)
- [PlantCurrentMoisture](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L595-L655)

Added explanatory comments following the same pattern used in previously fixed classes.

## Result
All sensor classes now properly implement their [async_update](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L1319-L1323) methods without attempting to call a non-existent parent method, eliminating the AttributeError.

## Files Modified
- `custom_components/plant/sensor.py` - Updated [PlantCurrentConductivity](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L550-L593) and [PlantCurrentMoisture](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L595-L655) classes

## Verification
- Syntax check passed successfully
- Implementation now matches the pattern used in other fixed sensor classes
- Consistent with the project's requirement to avoid calling non-existent parent methods