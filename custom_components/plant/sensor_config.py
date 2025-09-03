"""Centralized sensor configuration for the plant integration."""

# Try to import Home Assistant constants, but provide fallbacks if not available
try:
    from homeassistant.const import (
        PERCENTAGE,
        UnitOfTemperature,
        LIGHT_LUX,
        CONDUCTIVITY,
        UnitOfVolume,
        UnitOfPower,
    )
    # Constants are available
    HAS_HA_CONSTANTS = True
except ImportError:
    # Provide fallback constants for testing
    PERCENTAGE = "%"
    class UnitOfTemperature:
        CELSIUS = "°C"
    LIGHT_LUX = "lx"
    CONDUCTIVITY = "µS/cm"
    class UnitOfVolume:
        LITERS = "L"
    class UnitOfPower:
        KILO_WATT = "kW"
    HAS_HA_CONSTANTS = False

# Try to import our own constants
try:
    from .const import (
        READING_TEMPERATURE,
        READING_MOISTURE,
        READING_CONDUCTIVITY,
        READING_ILLUMINANCE,
        READING_HUMIDITY,
        READING_CO2,
        READING_PPFD,
        READING_DLI,
        READING_MOISTURE_CONSUMPTION,
        READING_FERTILIZER_CONSUMPTION,
        READING_POWER_CONSUMPTION,
        READING_PH,
        READING_ENERGY_COST,
        UNIT_CONDUCTIVITY,
        UNIT_PPFD,
        UNIT_DLI,
        UNIT_VOLUME,
        ICON_TEMPERATURE,
        ICON_MOISTURE,
        ICON_CONDUCTIVITY,
        ICON_ILLUMINANCE,
        ICON_HUMIDITY,
        ICON_CO2,
        ICON_PPFD,
        ICON_DLI,
        ICON_WATER_CONSUMPTION,
        ICON_FERTILIZER_CONSUMPTION,
        ICON_POWER_CONSUMPTION,
        ICON_PH,
        ICON_ENERGY_COST,
        DEVICE_CLASS_PH,
    )
    HAS_OWN_CONSTANTS = True
except ImportError:
    # Provide fallback constants for testing
    READING_TEMPERATURE = "temperature"
    READING_MOISTURE = "soil moisture"
    READING_CONDUCTIVITY = "conductivity"
    READING_ILLUMINANCE = "illuminance"
    READING_HUMIDITY = "air humidity"
    READING_CO2 = "air CO2"
    READING_PPFD = "ppfd (mol)"
    READING_DLI = "dli"
    READING_MOISTURE_CONSUMPTION = "water consumption"
    READING_FERTILIZER_CONSUMPTION = "fertilizer consumption"
    READING_POWER_CONSUMPTION = "power consumption"
    READING_PH = "soil pH"
    READING_ENERGY_COST = "energy cost"
    UNIT_CONDUCTIVITY = "μS/cm"
    UNIT_PPFD = "mol/s⋅m²s"
    UNIT_DLI = "mol/d⋅m²"
    UNIT_VOLUME = "L"
    ICON_TEMPERATURE = "mdi:thermometer"
    ICON_MOISTURE = "mdi:water"
    ICON_CONDUCTIVITY = "mdi:spa-outline"
    ICON_ILLUMINANCE = "mdi:brightness-6"
    ICON_HUMIDITY = "mdi:water-percent"
    ICON_CO2 = "mdi:molecule-co2"
    ICON_PPFD = "mdi:white-balance-sunny"
    ICON_DLI = "mdi:counter"
    ICON_WATER_CONSUMPTION = "mdi:water-pump"
    ICON_FERTILIZER_CONSUMPTION = "mdi:chart-line-variant"
    ICON_POWER_CONSUMPTION = "mdi:flash"
    ICON_PH = "mdi:ph"
    ICON_ENERGY_COST = "mdi:cash-multiple"
    DEVICE_CLASS_PH = "ph"
    HAS_OWN_CONSTANTS = False

# Sensor configuration with precision settings
SENSOR_CONFIG = {
    "temperature": {
        "name": READING_TEMPERATURE,
        "device_class": "temperature",
        "unit": UnitOfTemperature.CELSIUS if HAS_HA_CONSTANTS else "°C",
        "icon": ICON_TEMPERATURE,
        "display_precision": 1,
        "calculation_precision": 2,
        "default_aggregation": "mean",
        "min_value": -10,
        "max_value": 50
    },
    "moisture": {
        "name": READING_MOISTURE,
        "device_class": "moisture",
        "unit": PERCENTAGE if HAS_HA_CONSTANTS else "%",
        "icon": ICON_MOISTURE,
        "display_precision": 1,
        "calculation_precision": 3,
        "default_aggregation": "median",
        "min_value": 0,
        "max_value": 100
    },
    "conductivity": {
        "name": READING_CONDUCTIVITY,
        "device_class": "conductivity",
        "unit": UNIT_CONDUCTIVITY,
        "icon": ICON_CONDUCTIVITY,
        "display_precision": 1,
        "calculation_precision": 2,
        "default_aggregation": "median",
        "min_value": 0,
        "max_value": 3000
    },
    "illuminance": {
        "name": READING_ILLUMINANCE,
        "device_class": "illuminance",
        "unit": LIGHT_LUX if HAS_HA_CONSTANTS else "lx",
        "icon": ICON_ILLUMINANCE,
        "display_precision": 0,
        "calculation_precision": 1,
        "default_aggregation": "mean",
        "min_value": 0,
        "max_value": 100000
    },
    "humidity": {
        "name": READING_HUMIDITY,
        "device_class": "humidity",
        "unit": PERCENTAGE if HAS_HA_CONSTANTS else "%",
        "icon": ICON_HUMIDITY,
        "display_precision": 1,
        "calculation_precision": 2,
        "default_aggregation": "mean",
        "min_value": 0,
        "max_value": 100
    },
    "co2": {
        "name": READING_CO2,
        "device_class": "carbon_dioxide",
        "unit": "ppm",
        "icon": ICON_CO2,
        "display_precision": 0,
        "calculation_precision": 1,
        "default_aggregation": "mean",
        "min_value": 0,
        "max_value": 2000
    },
    "ppfd": {
        "name": READING_PPFD,
        "device_class": "illuminance",
        "unit": UNIT_PPFD,
        "icon": ICON_PPFD,
        "display_precision": 2,
        "calculation_precision": 4,
        "default_aggregation": "original",
        "min_value": 0,
        "max_value": 2000
    },
    "dli": {
        "name": READING_DLI,
        "device_class": "illuminance",
        "unit": UNIT_DLI,
        "icon": ICON_DLI,
        "display_precision": 2,
        "calculation_precision": 4,
        "default_aggregation": "original",
        "min_value": 0,
        "max_value": 100
    },
    "moisture_consumption": {
        "name": READING_MOISTURE_CONSUMPTION,
        "device_class": "volume",
        "unit": UNIT_VOLUME,
        "icon": ICON_WATER_CONSUMPTION,
        "display_precision": 2,
        "calculation_precision": 3,
        "default_aggregation": "original",
        "min_value": 0,
        "max_value": 100
    },
    "fertilizer_consumption": {
        "name": READING_FERTILIZER_CONSUMPTION,
        "device_class": "conductivity",
        "unit": UNIT_CONDUCTIVITY,
        "icon": ICON_FERTILIZER_CONSUMPTION,
        "display_precision": 2,
        "calculation_precision": 3,
        "default_aggregation": "original",
        "min_value": 0,
        "max_value": 1000
    },
    "power_consumption": {
        "name": READING_POWER_CONSUMPTION,
        "device_class": "power",
        "unit": UnitOfPower.KILO_WATT if HAS_HA_CONSTANTS else "kW",
        "icon": ICON_POWER_CONSUMPTION,
        "display_precision": 2,
        "calculation_precision": 3,
        "default_aggregation": "mean",
        "min_value": 0,
        "max_value": 10
    },
    "ph": {
        "name": READING_PH,
        "device_class": DEVICE_CLASS_PH,
        "unit": "pH",
        "icon": ICON_PH,
        "display_precision": 2,
        "calculation_precision": 3,
        "default_aggregation": "median",
        "min_value": 0,
        "max_value": 14
    },
    "energy_cost": {
        "name": READING_ENERGY_COST,
        "device_class": "monetary",
        "unit": "€",
        "icon": ICON_ENERGY_COST,
        "display_precision": 2,
        "calculation_precision": 4,
        "default_aggregation": "mean",
        "min_value": 0,
        "max_value": 100
    }
}


def get_sensor_config(sensor_type):
    """Get configuration for a specific sensor type."""
    return SENSOR_CONFIG.get(sensor_type, {})


def round_sensor_value(value, sensor_type, context="display"):
    """Round sensor value according to precision settings."""
    config = get_sensor_config(sensor_type)
    if not config:
        return value
        
    precision = config.get("calculation_precision" if context == "calculation" else "display_precision", 2)
    if isinstance(value, (int, float)):
        return round(value, precision)
    return value


def format_sensor_value(value, sensor_type):
    """Format sensor value for display."""
    config = get_sensor_config(sensor_type)
    if not config:
        return value
        
    precision = config.get("display_precision", 2)
    if isinstance(value, (int, float)):
        return round(value, precision)
    return value