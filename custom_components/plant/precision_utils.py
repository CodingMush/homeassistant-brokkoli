"""Precision and rounding utilities for plant sensors.

⚠️  DEPRECATED: This module is deprecated. Use sensor_definitions.py instead.

This module will be removed in a future version. All functionality has been
consolidated into sensor_definitions.py for better maintainability.

For migration:
- Replace imports from precision_utils with sensor_definitions
- Use SensorDefinitionMixin instead of PrecisionMixin
- Use round_sensor_value() from sensor_definitions
"""

# Import from the new consolidated module for backwards compatibility
from .sensor_definitions import (
    round_sensor_value,
    format_sensor_value,
    apply_sensor_definition as apply_sensor_precision,
    SensorDefinitionMixin as PrecisionMixin,
    get_sensor_definition,
    SENSOR_DEFINITIONS,
)

# Re-export for backwards compatibility
__all__ = [
    'round_sensor_value',
    'format_sensor_value',
    'apply_sensor_precision',
    'PrecisionMixin',
    'get_sensor_definition',
]

# Legacy mappings for backwards compatibility
SENSOR_PRECISION = {k: v.display_precision for k, v in SENSOR_DEFINITIONS.items()}
CALCULATION_PRECISION = {k: v.calculation_precision for k, v in SENSOR_DEFINITIONS.items()}

def get_sensor_precision(sensor_type: str) -> int:
    """Legacy function - use get_sensor_definition() instead."""
    definition = get_sensor_definition(sensor_type)
    return definition.display_precision if definition else 2

def get_calculation_precision(sensor_type: str) -> int:
    """Legacy function - use get_sensor_definition() instead."""
    definition = get_sensor_definition(sensor_type)
    return definition.calculation_precision if definition else 3


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