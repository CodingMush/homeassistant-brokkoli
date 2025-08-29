"""Precision and rounding utilities for plant sensors."""

from homeassistant.components.sensor import SensorDeviceClass
from typing import Optional, Union

# Sensor precision mappings (suggested display precision)
SENSOR_PRECISION = {
    # Environmental sensors
    "temperature": 1,           # 20.5°C
    "humidity": 0,              # 65% (Luftfeuchtigkeit ohne Nachkommastellen)
    "moisture": 1,              # 45.5% (Bodenfeuchtigkeit mit 1 Nachkommastelle)
    "illuminance": 0,           # 25000 lux (Lux ohne Nachkommastellen)
    "conductivity": 0,          # 1500 µS/cm
    "co2": 0,                  # 400 ppm
    "ph": 1,                   # 6.5 pH
    
    # Light calculations
    "ppfd": 1,                 # 250.5 µmol/m²/s
    "dli": 1,                  # 15.2 mol/m²/d
    "total_integral": 3,       # 1250.456
    
    # Consumption sensors
    "water_consumption": 2,     # 1.25 L
    "fertilizer_consumption": 2, # 0.15 L
    "power_consumption": 1,     # 45.5 W
    "energy_cost": 2,          # 2.35 €
    
    # Totals
    "total_water_consumption": 1,      # 125.5 L
    "total_fertilizer_consumption": 1, # 15.5 L
    "total_power_consumption": 1,      # 1250.5 kWh
    "total_energy_cost": 2,           # 125.35 €
    
    # Health and diagnostics
    "health": 1,               # 7.5/10
    "flowering_days": 0,       # 45 days
    "vegetative_days": 0,      # 30 days
    "total_days": 0,           # 75 days
}

# Sensor rounding precision for calculations (kann mehr Nachkommastellen haben als Display)
CALCULATION_PRECISION = {
    "temperature": 2,
    "humidity": 1,
    "moisture": 2,
    "illuminance": 0,
    "conductivity": 0,
    "co2": 0,
    "ph": 2,
    "ppfd": 3,
    "dli": 3,
    "total_integral": 6,
    "water_consumption": 3,
    "fertilizer_consumption": 3,
    "power_consumption": 2,
    "energy_cost": 3,
    "total_water_consumption": 2,
    "total_fertilizer_consumption": 2,
    "total_power_consumption": 2,
    "total_energy_cost": 3,
    "health": 2,
    "flowering_days": 0,
    "vegetative_days": 0,
    "total_days": 0,
}


def get_sensor_precision(sensor_type: str) -> int:
    """Get suggested display precision for sensor type."""
    return SENSOR_PRECISION.get(sensor_type.lower(), 2)


def get_calculation_precision(sensor_type: str) -> int:
    """Get calculation precision for sensor type."""
    return CALCULATION_PRECISION.get(sensor_type.lower(), 3)


def round_sensor_value(value: Union[float, int, str, None], sensor_type: str, for_display: bool = True) -> Optional[Union[float, int]]:
    """
    Round sensor value according to sensor type.
    
    Args:
        value: The value to round
        sensor_type: Type of sensor (e.g., 'illuminance', 'humidity')
        for_display: If True, use display precision; if False, use calculation precision
        
    Returns:
        Rounded value or None if input is invalid
    """
    if value is None:
        return None
        
    try:
        numeric_value = float(value)
        precision = get_sensor_precision(sensor_type) if for_display else get_calculation_precision(sensor_type)
        
        if precision == 0:
            return int(round(numeric_value))
        else:
            return round(numeric_value, precision)
            
    except (ValueError, TypeError):
        return None


def apply_sensor_precision(sensor, sensor_type: str) -> None:
    """
    Apply appropriate precision settings to a sensor entity.
    
    Args:
        sensor: The sensor entity to modify
        sensor_type: Type of sensor for precision lookup
    """
    precision = get_sensor_precision(sensor_type)
    
    # Set suggested display precision if supported
    if hasattr(sensor, '_attr_suggested_display_precision'):
        sensor._attr_suggested_display_precision = precision
    
    # Round current value if it exists
    if hasattr(sensor, '_attr_native_value') and sensor._attr_native_value is not None:
        sensor._attr_native_value = round_sensor_value(
            sensor._attr_native_value, 
            sensor_type, 
            for_display=True
        )


class PrecisionMixin:
    """Mixin class to add precision handling to sensor entities."""
    
    def __init__(self, sensor_type: str, *args, **kwargs):
        """Initialize with sensor type for precision."""
        super().__init__(*args, **kwargs)
        self._sensor_type = sensor_type.lower()
        
        # Set precision attributes
        self._attr_suggested_display_precision = get_sensor_precision(self._sensor_type)
    
    def _round_value_for_display(self, value: Union[float, int, str, None]) -> Optional[Union[float, int]]:
        """Round value for display with appropriate precision."""
        return round_sensor_value(value, self._sensor_type, for_display=True)
    
    def _round_value_for_calculation(self, value: Union[float, int, str, None]) -> Optional[Union[float, int]]:
        """Round value for calculations with appropriate precision."""
        return round_sensor_value(value, self._sensor_type, for_display=False)
    
    @property
    def suggested_display_precision(self) -> int:
        """Return the suggested display precision."""
        return self._attr_suggested_display_precision
    
    def _set_rounded_native_value(self, value: Union[float, int, str, None]) -> None:
        """Set the native value with appropriate rounding."""
        rounded_value = self._round_value_for_display(value)
        if rounded_value is not None:
            self._attr_native_value = rounded_value


# Device class specific precision overrides
DEVICE_CLASS_PRECISION = {
    SensorDeviceClass.ILLUMINANCE: 0,    # Lux always whole numbers
    SensorDeviceClass.HUMIDITY: 0,       # Humidity always whole numbers
    SensorDeviceClass.TEMPERATURE: 1,    # Temperature 1 decimal place
    SensorDeviceClass.CONDUCTIVITY: 0,   # Conductivity whole numbers
    SensorDeviceClass.CO2: 0,           # CO2 whole numbers
    SensorDeviceClass.POWER: 1,         # Power 1 decimal place
    SensorDeviceClass.MONETARY: 2,      # Money 2 decimal places
    SensorDeviceClass.VOLUME: 2,        # Volume 2 decimal places
}


def get_precision_by_device_class(device_class: SensorDeviceClass) -> int:
    """Get precision based on device class."""
    return DEVICE_CLASS_PRECISION.get(device_class, 2)


def format_sensor_value(value: Union[float, int, str, None], sensor_type: str, unit: str = None) -> str:
    """
    Format sensor value with appropriate precision for display.
    
    Args:
        value: The value to format
        sensor_type: Type of sensor
        unit: Unit of measurement (optional)
        
    Returns:
        Formatted string representation
    """
    rounded_value = round_sensor_value(value, sensor_type, for_display=True)
    
    if rounded_value is None:
        return "Unknown"
    
    precision = get_sensor_precision(sensor_type)
    
    if precision == 0:
        formatted = f"{int(rounded_value)}"
    else:
        formatted = f"{rounded_value:.{precision}f}"
    
    if unit:
        formatted += f" {unit}"
        
    return formatted