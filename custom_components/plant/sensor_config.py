"""Centralized sensor configuration for the plant integration"""

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import (
    LIGHT_LUX,
    PERCENTAGE,
    UnitOfConductivity,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolume,
)

from .const import (
    ATTR_BATTERY,
    ATTR_BRIGHTNESS,
    ATTR_MOISTURE,
    ATTR_CONDUCTIVITY,
    ATTR_ILLUMINANCE,
    ATTR_HUMIDITY,
    ATTR_CO2,
    ATTR_PPFD,
    ATTR_MMOL,
    ATTR_MOL,
    ATTR_DLI,
    ATTR_WATER_CONSUMPTION,
    ATTR_FERTILIZER_CONSUMPTION,
    ATTR_POWER_CONSUMPTION,
    ATTR_PH,
    ATTR_TEMPERATURE,
    READING_BATTERY,
    READING_TEMPERATURE,
    READING_MOISTURE,
    READING_CONDUCTIVITY,
    READING_ILLUMINANCE,
    READING_HUMIDITY,
    READING_CO2,
    READING_PPFD,
    READING_MMOL,
    READING_MOL,
    READING_DLI,
    READING_MOISTURE_CONSUMPTION,
    READING_FERTILIZER_CONSUMPTION,
    READING_POWER_CONSUMPTION,
    READING_PH,
    DEFAULT_MIN_BATTERY_LEVEL,
    DEFAULT_MIN_TEMPERATURE,
    DEFAULT_MAX_TEMPERATURE,
    DEFAULT_MIN_MOISTURE,
    DEFAULT_MAX_MOISTURE,
    DEFAULT_MIN_CONDUCTIVITY,
    DEFAULT_MAX_CONDUCTIVITY,
    DEFAULT_MIN_ILLUMINANCE,
    DEFAULT_MAX_ILLUMINANCE,
    DEFAULT_MIN_HUMIDITY,
    DEFAULT_MAX_HUMIDITY,
    DEFAULT_MIN_CO2,
    DEFAULT_MAX_CO2,
    DEFAULT_MIN_MMOL,
    DEFAULT_MAX_MMOL,
    DEFAULT_MIN_MOL,
    DEFAULT_MAX_MOL,
    DEFAULT_MIN_DLI,
    DEFAULT_MAX_DLI,
    DEFAULT_MIN_WATER_CONSUMPTION,
    DEFAULT_MAX_WATER_CONSUMPTION,
    DEFAULT_MIN_FERTILIZER_CONSUMPTION,
    DEFAULT_MAX_FERTILIZER_CONSUMPTION,
    DEFAULT_MIN_POWER_CONSUMPTION,
    DEFAULT_MAX_POWER_CONSUMPTION,
    DEFAULT_MIN_PH,
    DEFAULT_MAX_PH,
    UNIT_PPFD,
    UNIT_DLI,
    UNIT_CONDUCTIVITY,
    UNIT_VOLUME,
    ICON_CONDUCTIVITY,
    ICON_DLI,
    ICON_HUMIDITY,
    ICON_CO2,
    ICON_ILLUMINANCE,
    ICON_MOISTURE,
    ICON_PPFD,
    ICON_TEMPERATURE,
    ICON_WATER_CONSUMPTION,
    ICON_FERTILIZER_CONSUMPTION,
    ICON_POWER_CONSUMPTION,
    ICON_PH,
    DEVICE_CLASS_PH,
)

# Central sensor definitions
SENSOR_DEFINITIONS = {
    # Basic sensors
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
    ATTR_MOISTURE: {
        "sensor_id": ATTR_MOISTURE,
        "name": READING_MOISTURE,
        "unit": PERCENTAGE,
        "icon": ICON_MOISTURE,
        "device_class": SensorDeviceClass.MOISTURE,
        "min_value": DEFAULT_MIN_MOISTURE,
        "max_value": DEFAULT_MAX_MOISTURE,
        "backend_entity_type": "sensor",
        "frontend_field_type": "sensor",
        "is_calculated": False,
        "show_in_ui": True,
        "show_status_bar": True,
        "display_precision": 0,  # Whole numbers for moisture
        "calculation_precision": 1,  # 1 decimal place for calculations
    },
    ATTR_CONDUCTIVITY: {
        "sensor_id": ATTR_CONDUCTIVITY,
        "name": READING_CONDUCTIVITY,
        "unit": UNIT_CONDUCTIVITY,
        "icon": ICON_CONDUCTIVITY,
        "device_class": None,
        "min_value": DEFAULT_MIN_CONDUCTIVITY,
        "max_value": DEFAULT_MAX_CONDUCTIVITY,
        "backend_entity_type": "sensor",
        "frontend_field_type": "sensor",
        "is_calculated": False,
        "show_in_ui": True,
        "show_status_bar": True,
        "display_precision": 0,  # Whole numbers for conductivity
        "calculation_precision": 1,  # 1 decimal place for calculations
    },
    ATTR_ILLUMINANCE: {
        "sensor_id": ATTR_ILLUMINANCE,
        "name": READING_ILLUMINANCE,
        "unit": LIGHT_LUX,
        "icon": ICON_ILLUMINANCE,
        "device_class": SensorDeviceClass.ILLUMINANCE,
        "min_value": DEFAULT_MIN_ILLUMINANCE,
        "max_value": DEFAULT_MAX_ILLUMINANCE,
        "backend_entity_type": "sensor",
        "frontend_field_type": "sensor",
        "is_calculated": False,
        "show_in_ui": True,
        "show_status_bar": True,
        "display_precision": 0,  # Whole numbers for illuminance
        "calculation_precision": 1,  # 1 decimal place for calculations
    },
    ATTR_HUMIDITY: {
        "sensor_id": ATTR_HUMIDITY,
        "name": READING_HUMIDITY,
        "unit": PERCENTAGE,
        "icon": ICON_HUMIDITY,
        "device_class": SensorDeviceClass.HUMIDITY,
        "min_value": DEFAULT_MIN_HUMIDITY,
        "max_value": DEFAULT_MAX_HUMIDITY,
        "backend_entity_type": "sensor",
        "frontend_field_type": "sensor",
        "is_calculated": False,
        "show_in_ui": True,
        "show_status_bar": True,
        "display_precision": 1,  # Whole numbers for humidity
        "calculation_precision": 2,  # 1 decimal place for calculations
    },
    ATTR_CO2: {
        "sensor_id": ATTR_CO2,
        "name": READING_CO2,
        "unit": "ppm",
        "icon": ICON_CO2,
        "device_class": None,  # No specific device class for CO2 in HA
        "min_value": DEFAULT_MIN_CO2,
        "max_value": DEFAULT_MAX_CO2,
        "backend_entity_type": "sensor",
        "frontend_field_type": "sensor",
        "is_calculated": False,
        "show_in_ui": True,
        "show_status_bar": True,
        "display_precision": 0,  # Whole numbers for CO2
        "calculation_precision": 1,  # 1 decimal place for calculations
    },
    ATTR_BATTERY: {
        "sensor_id": ATTR_BATTERY,
        "name": READING_BATTERY,
        "unit": PERCENTAGE,
        "icon": "mdi:battery",
        "device_class": SensorDeviceClass.BATTERY,
        "min_value": DEFAULT_MIN_BATTERY_LEVEL,
        "max_value": 100,
        "backend_entity_type": "sensor",
        "frontend_field_type": "sensor",
        "is_calculated": False,
        "show_in_ui": True,
        "show_status_bar": True,
        "display_precision": 0,  # Whole numbers for battery
        "calculation_precision": 1,  # 1 decimal place for calculations
    },
    ATTR_PH: {
        "sensor_id": ATTR_PH,
        "name": READING_PH,
        "unit": None,  # pH is unitless
        "icon": ICON_PH,
        "device_class": DEVICE_CLASS_PH,
        "min_value": DEFAULT_MIN_PH,
        "max_value": DEFAULT_MAX_PH,
        "backend_entity_type": "sensor",
        "frontend_field_type": "sensor",
        "is_calculated": False,
        "show_in_ui": True,
        "show_status_bar": True,
        "display_precision": 1,  # 1 decimal place for pH
        "calculation_precision": 2,  # 2 decimal places for calculations
    },
    # Calculated sensors
    ATTR_PPFD: {
        "sensor_id": ATTR_PPFD,
        "name": READING_PPFD,
        "unit": UNIT_PPFD,
        "icon": ICON_PPFD,
        "device_class": None,
        "min_value": DEFAULT_MIN_MMOL,
        "max_value": DEFAULT_MAX_MMOL,
        "backend_entity_type": "sensor",
        "frontend_field_type": "sensor",
        "is_calculated": True,
        "aggregation_method": "trapezoidal",
        "show_in_ui": True,
        "show_status_bar": True,
        "display_precision": 1,  # 1 decimal place for PPFD
        "calculation_precision": 3,  # 3 decimal places for calculations
    },
    ATTR_DLI: {
        "sensor_id": ATTR_DLI,
        "name": READING_DLI,
        "unit": UNIT_DLI,
        "icon": ICON_DLI,
        "device_class": None,
        "min_value": DEFAULT_MIN_DLI,
        "max_value": DEFAULT_MAX_DLI,
        "backend_entity_type": "sensor",
        "frontend_field_type": "sensor",
        "is_calculated": True,
        "aggregation_method": "trapezoidal",
        "show_in_ui": True,
        "show_status_bar": True,
        "display_precision": 1,  # 1 decimal place for DLI
        "calculation_precision": 3,  # 3 decimal places for calculations
    },
    ATTR_WATER_CONSUMPTION: {
        "sensor_id": ATTR_WATER_CONSUMPTION,
        "name": READING_MOISTURE_CONSUMPTION,
        "unit": UnitOfVolume.MILLILITERS,
        "icon": ICON_WATER_CONSUMPTION,
        "device_class": None,
        "min_value": DEFAULT_MIN_WATER_CONSUMPTION,
        "max_value": DEFAULT_MAX_WATER_CONSUMPTION,
        "backend_entity_type": "sensor",
        "frontend_field_type": "sensor",
        "is_calculated": True,
        "aggregation_method": "trapezoidal",
        "show_in_ui": True,
        "show_status_bar": True,
        "display_precision": 2,  # 2 decimal places for water consumption
        "calculation_precision": 3,  # 3 decimal places for calculations
    },
    ATTR_FERTILIZER_CONSUMPTION: {
        "sensor_id": ATTR_FERTILIZER_CONSUMPTION,
        "name": READING_FERTILIZER_CONSUMPTION,
        "unit": UnitOfVolume.MILLILITERS,
        "icon": ICON_FERTILIZER_CONSUMPTION,
        "device_class": None,
        "min_value": DEFAULT_MIN_FERTILIZER_CONSUMPTION,
        "max_value": DEFAULT_MAX_FERTILIZER_CONSUMPTION,
        "backend_entity_type": "sensor",
        "frontend_field_type": "sensor",
        "is_calculated": True,
        "aggregation_method": "trapezoidal",
        "show_in_ui": True,
        "show_status_bar": True,
        "display_precision": 2,  # 2 decimal places for fertilizer consumption
        "calculation_precision": 3,  # 3 decimal places for calculations
    },
    ATTR_POWER_CONSUMPTION: {
        "sensor_id": ATTR_POWER_CONSUMPTION,
        "name": READING_POWER_CONSUMPTION,
        "unit": "kWh",
        "icon": ICON_POWER_CONSUMPTION,
        "device_class": SensorDeviceClass.ENERGY,
        "min_value": DEFAULT_MIN_POWER_CONSUMPTION,
        "max_value": DEFAULT_MAX_POWER_CONSUMPTION,
        "backend_entity_type": "sensor",
        "frontend_field_type": "sensor",
        "is_calculated": True,
        "aggregation_method": "trapezoidal",
        "show_in_ui": True,
        "show_status_bar": True,
        "display_precision": 2,  # 2 decimal places for power consumption
        "calculation_precision": 3,  # 3 decimal places for calculations
    },
}

# Helper function to get sensor definition by sensor ID
def get_sensor_definition(sensor_id):
    """Get sensor definition by sensor ID."""
    return SENSOR_DEFINITIONS.get(sensor_id)

# Helper function to get all sensor definitions
def get_all_sensor_definitions():
    """Get all sensor definitions."""
    return SENSOR_DEFINITIONS

# Helper function to get basic sensors (non-calculated)
def get_basic_sensors():
    """Get all basic (non-calculated) sensors."""
    return {k: v for k, v in SENSOR_DEFINITIONS.items() if not v.get("is_calculated", False)}

# Helper function to get calculated sensors
def get_calculated_sensors():
    """Get all calculated sensors."""
    return {k: v for k, v in SENSOR_DEFINITIONS.items() if v.get("is_calculated", False)}

# Helper function to round sensor values based on precision settings
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
    if value is None:
        return None
    
    sensor_def = get_sensor_definition(sensor_id)
    if not sensor_def:
        return value
    
    try:
        numeric_value = float(value)
        precision = sensor_def.get("display_precision", 1) if for_display else sensor_def.get("calculation_precision", 2)
        
        if precision == 0:
            return int(round(numeric_value))
        else:
            return round(numeric_value, precision)
            
    except (ValueError, TypeError):
        return value

# Helper function to get display precision for a sensor
def get_display_precision(sensor_id):
    """Get the display precision for a sensor."""
    sensor_def = get_sensor_definition(sensor_id)
    if sensor_def:
        return sensor_def.get("display_precision", 1)
    return 1

# Helper function to get calculation precision for a sensor
def get_calculation_precision(sensor_id):
    """Get the calculation precision for a sensor."""
    sensor_def = get_sensor_definition(sensor_id)
    if sensor_def:
        return sensor_def.get("calculation_precision", 2)
    return 2