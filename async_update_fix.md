# Async Update Method Fix

## Issue
Multiple sensors were throwing AttributeError when trying to update:
```
AttributeError: 'super' object has no attribute 'async_update'
```

This was affecting:
- PlantCurrentTemperature sensors
- PlantCurrentHumidity sensors  
- PlantCurrentIlluminance sensors

## Root Cause
The [PlantCurrentStatus](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L385-L521) class (which inherits from [RestoreSensor](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L385-L521)) does not have an `async_update` method, but the sensor classes were calling `await super().async_update()` in their [async_update](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L1319-L1323) methods.

This was the same issue that was previously fixed in other sensor classes, where we removed the call to `super().async_update()` with a comment explaining why.

## Fix Applied
Removed calls to `await super().async_update()` from the following classes:
- [PlantCurrentTemperature](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L798-L827)
- [PlantCurrentHumidity](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L829-L854)
- [PlantCurrentIlluminance](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L523-L548)

Added explanatory comments following the same pattern used in previously fixed sensor classes.

## Result
All sensor classes now properly implement their [async_update](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L1319-L1323) methods without attempting to call a non-existent parent method, eliminating the AttributeError.

## Files Modified
- `custom_components/plant/sensor.py` - Updated [PlantCurrentTemperature](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L798-L827), [PlantCurrentHumidity](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L829-L854), and [PlantCurrentIlluminance](file:///d:/Python/git/homeassistant-brokkoli/custom_components/plant/sensor.py#L523-L548) classes

## Verification
- Syntax check passed successfully
- Implementation now matches the pattern used in previously fixed sensor classes
- Consistent with the project's requirement to avoid calling non-existent parent methods