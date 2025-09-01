# 🔄 Sensor Definition Consolidation Guide

## Problem Solved
Previously, sensor definitions were scattered across multiple files:
- **ha_compliance.py** - EntityCategory, DeviceClass, StateClass, Units
- **precision_utils.py** - Display precision, calculation precision, rounding logic
- **sensor.py** - Individual sensor class implementations

This made maintenance difficult and created potential inconsistencies.

## ✅ New Consolidated Approach

### Single Source of Truth: `sensor_definitions.py`

All sensor properties are now defined in one comprehensive file with a structured approach:

```python
@dataclass
class SensorDefinition:
    sensor_type: str
    display_name: str
    icon: str
    device_class: Optional[SensorDeviceClass] = None
    state_class: Optional[SensorStateClass] = None
    entity_category: Optional[EntityCategory] = None
    unit_of_measurement: Optional[str] = None
    display_precision: int = 2
    calculation_precision: int = 3
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None
    virtual: bool = False
    description: Optional[str] = None
```

### Example Definition

```python
"illuminance": SensorDefinition(
    sensor_type="illuminance",
    display_name="Light Intensity",
    icon="mdi:brightness-6",
    device_class=SensorDeviceClass.ILLUMINANCE,
    state_class=SensorStateClass.MEASUREMENT,
    unit_of_measurement=LIGHT_LUX,
    display_precision=0,  # No decimal places
    calculation_precision=0,
    min_value=0.0,
    max_value=200000.0,
    step=500.0,
    description="Light intensity in lux"
),
```

## 🚀 Migration Guide

### Before (Old Approach)
```python
# Multiple imports from different files
from .ha_compliance import get_device_class, get_entity_category
from .precision_utils import get_sensor_precision, round_sensor_value

class PlantCurrentIlluminance(PlantCurrentStatus):
    def __init__(self, hass, config, plantdevice):
        # Manual setup of all attributes
        self._attr_icon = ICON_ILLUMINANCE
        self._attr_device_class = SensorDeviceClass.ILLUMINANCE
        self._attr_native_unit_of_measurement = LIGHT_LUX
        self._attr_suggested_display_precision = 0
        super().__init__(hass, config, plantdevice)
    
    def state_changed(self, entity_id, new_state):
        super().state_changed(entity_id, new_state)
        # Manual rounding logic
        if self._attr_native_value is not None:
            try:
                self._attr_native_value = round(float(self._attr_native_value))
            except (ValueError, TypeError):
                pass
```

### After (New Approach)
```python
# Single import
from .sensor_definitions import SensorDefinitionMixin

class PlantCurrentIlluminance(SensorDefinitionMixin, PlantCurrentStatus):
    def __init__(self, hass, config, plantdevice):
        # Automatic setup from sensor definition
        super().__init__("illuminance", hass, config, plantdevice)
    
    def state_changed(self, entity_id, new_state):
        super().state_changed(entity_id, new_state)
        # Automatic rounding using sensor definition
        if self._attr_native_value is not None:
            self._attr_native_value = self._round_value_for_display(self._attr_native_value)
```

## 📋 Benefits

### 1. **Centralized Configuration**
- All sensor properties in one file
- Easy to modify precision, units, or classes
- Single source of truth prevents inconsistencies

### 2. **Simplified Sensor Implementation**
- Less boilerplate code in sensor classes
- Automatic application of all sensor properties
- Built-in rounding and formatting functions

### 3. **Better Maintainability**
- Adding new sensors requires only one definition
- Changes propagate automatically to all sensors
- Clear separation of concerns

### 4. **Enhanced Features**
- Virtual sensor flagging for performance optimization
- Min/max value constraints
- Step values for UI controls
- Comprehensive descriptions for documentation

## 🔧 Implementation Examples

### Simple Sensor with Automatic Configuration
```python
class NewTemperatureSensor(SensorDefinitionMixin, RestoreSensor):
    def __init__(self, hass, config, plant):
        # All properties automatically applied from "temperature" definition
        super().__init__("temperature", hass, config, plant)
```

### Custom Sensor with Additional Logic
```python
class CustomHumiditySensor(SensorDefinitionMixin, SensorEntity):
    def __init__(self, hass, config, plant):
        super().__init__("humidity", hass, config, plant)
        # Additional custom initialization
        self._plant = plant
    
    async def async_update(self):
        # Custom logic here
        raw_value = await self._get_raw_humidity()
        # Automatic rounding applied
        self._attr_native_value = self._round_value_for_display(raw_value)
```

### Applying Definitions to Existing Entities
```python
# For existing entities that can't inherit from SensorDefinitionMixin
from .sensor_definitions import apply_sensor_definition

existing_sensor = SomeExistingSensor()
apply_sensor_definition(existing_sensor, "illuminance")
# Now has correct precision, device class, etc.
```

### Getting Sensor Information
```python
from .sensor_definitions import get_sensor_definition

definition = get_sensor_definition("humidity")
print(f"Precision: {definition.display_precision}")  # 0
print(f"Unit: {definition.unit_of_measurement}")     # %
print(f"Icon: {definition.icon}")                    # mdi:water-percent
```

## 🔄 Backwards Compatibility

The old files (`ha_compliance.py` and `precision_utils.py`) are now deprecated but still work:

```python
# Still works but deprecated
from .ha_compliance import get_device_class
from .precision_utils import get_sensor_precision

# New recommended approach
from .sensor_definitions import get_sensor_definition

definition = get_sensor_definition("temperature")
device_class = definition.device_class
precision = definition.display_precision
```

## 📝 Adding New Sensors

To add a new sensor type:

1. **Add definition to `sensor_definitions.py`:**
```python
"new_sensor": SensorDefinition(
    sensor_type="new_sensor",
    display_name="New Sensor",
    icon="mdi:new-icon",
    device_class=SensorDeviceClass.MEASUREMENT,
    state_class=SensorStateClass.MEASUREMENT,
    unit_of_measurement="unit",
    display_precision=1,
    description="Description of new sensor"
),
```

2. **Create sensor class:**
```python
class NewSensor(SensorDefinitionMixin, SensorEntity):
    def __init__(self, hass, config, plant):
        super().__init__("new_sensor", hass, config, plant)
```

3. **Done!** All properties are automatically applied.

## 🚀 Performance Benefits

### Calculated Sensor Support
```python
# Mark sensors as calculated for performance optimization
"calculated_sensor": SensorDefinition(
    sensor_type="calculated_sensor",
    virtual=True,  # Calculated sensors
    # ... other properties
)

# Check if sensor is calculated
definition = get_sensor_definition("ppfd")
if definition.virtual:
    # Use calculated sensor architecture
    pass
```

### Batch Operations
```python
# Get all calculated sensors for optimization
# Note: Virtual sensors that reference external entities have been removed
# Calculated sensors are defined with virtual=True in SENSOR_DEFINITIONS
calculated_sensor_types = [sensor_type for sensor_type, definition in SENSOR_DEFINITIONS.items() if definition.virtual]
# ['ppfd', 'dli', 'total_integral', ...]
```

This consolidation dramatically improves code maintainability while providing more functionality and better performance options! 🎯