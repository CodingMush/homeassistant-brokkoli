# Sensor Precision Improvements for homeassistant-brokkoli

## Problem
Lux and humidity sensors were displaying too many decimal places, which affected user experience.

## Solution Implemented

### 1. New Precision Utils (`precision_utils.py`)
- **Central precision management** for all sensor types
- **Device-class specific rounding**
- **Display vs. calculation precision** distinction
- **PrecisionMixin** for easy integration

### 2. Sensor Precision Mappings

```python
SENSOR_PRECISION = {
    "illuminance": 0,        # 25000 lux (no decimal places)
    "humidity": 0,           # 65% (no decimal places)
    "temperature": 1,        # 20.5°C
    "moisture": 1,           # 45.5%
    "ppfd": 1,              # 250.5 µmol/m²/s
    "dli": 1,               # 15.2 mol/m²/d
    "conductivity": 0,       # 1500 µS/cm
    "co2": 0,               # 400 ppm
    "ph": 1,                # 6.5 pH
}
```

### 3. Updated Sensor Classes

#### PlantCurrentIlluminance
- **`suggested_display_precision = 0`** added
- **Automatic rounding** in `state_changed()` and `async_update()`
- **Whole numbers** for lux values (e.g. 25000 instead of 25000.0)

#### PlantCurrentHumidity
- **`suggested_display_precision = 0`** added
- **Automatic rounding** in `state_changed()` and `async_update()`
- **Whole numbers** for humidity (e.g. 65 instead of 65.0)

#### PlantCurrentPpfd
- **`suggested_display_precision = 1`** added
- **1 decimal place** for PPFD values (e.g. 250.5)

#### CycleMedianSensor
- **Individual precision** for each sensor type
- **0 decimal places** for lux and humidity
- **1 decimal place** for temperature, PPFD, DLI

### 4. Improved Median Value Calculation
In `__init__.py`, the rounding logic was revised:

```python
# Old logic:
elif sensor_type in [\"temperature\", \"moisture\", \"humidity\", \"moisture_consumption\", \"CO2\"]:
    self._median_sensors[sensor_type] = round(value, 1)
else:  # conductivity, illuminance, fertilizer_consumption
    self._median_sensors[sensor_type] = round(value)

# New logic:
elif sensor_type in [\"humidity\", \"illuminance\", \"CO2\", \"conductivity\"]:
    self._median_sensors[sensor_type] = round(value)  # No decimal places
elif sensor_type in [\"ppfd\", \"dli\"]:
    self._median_sensors[sensor_type] = round(value, 1)  # 1 decimal place
```

## Benefits of Implementation

### 1. **Better User Experience**
- Lux values: `25000` instead of `25000.0000`
- Humidity: `65%` instead of `65.000%`
- PPFD values: `250.5` instead of `250.5678`

### 2. **Home Assistant Standard Compliance**
- Uses `suggested_display_precision` attribute
- Follows Home Assistant best practices
- Consistent with other integrations

### 3. **Extensibility**
- Central configuration in `precision_utils.py`
- Easy adaptation for new sensor types
- Separation between display and calculation precision

### 4. **Performance**
- Reduced data transfer
- Less memory usage in database
- Faster UI rendering

## Usage

### For New Sensors
```python
from .precision_utils import PrecisionMixin, apply_sensor_precision

class NewSensor(PrecisionMixin, SensorEntity):
    def __init__(self, sensor_type: str, *args, **kwargs):
        super().__init__(sensor_type, *args, **kwargs)
        # Automatically set correct precision
```

### For Existing Sensors
```python
# Automatic precision application
apply_sensor_precision(sensor, "illuminance")
```

## Testing

### Before Implementation
- Lux: `25384.567890 lux`
- Humidity: `65.00000 %`
- PPFD: `250.567890 µmol/m²/s`

### After Implementation
- Lux: `25385 lux`
- Humidity: `65 %`
- PPFD: `250.6 µmol/m²/s`

## Migration

The changes are **backward compatible**:
- Existing sensor data is preserved
- Home Assistant automatically recognizes the new precision
- No manual steps required

## Maintenance

For future precision adjustments:
1. Edit `SENSOR_PRECISION` in `precision_utils.py`
2. Restart Home Assistant
3. Changes are automatically applied