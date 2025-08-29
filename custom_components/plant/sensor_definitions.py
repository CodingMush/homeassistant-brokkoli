"""Comprehensive sensor definitions for plant integration."""

from dataclasses import dataclass
from typing import Optional, Union, Dict, Any
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.helpers.entity import EntityCategory
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfTime,
    PERCENTAGE,
    LIGHT_LUX,
    UnitOfConductivity,
    UnitOfVolume,
    UnitOfEnergy,
    UnitOfPower,
)


@dataclass
class SensorDefinition:
    """Complete definition for a plant sensor."""
    
    # Basic properties
    sensor_type: str
    display_name: str
    icon: str
    
    # Home Assistant compliance
    device_class: Optional[SensorDeviceClass] = None
    state_class: Optional[SensorStateClass] = None
    entity_category: Optional[EntityCategory] = None
    unit_of_measurement: Optional[str] = None
    
    # Precision settings
    display_precision: int = 2
    calculation_precision: int = 3
    
    # Additional properties
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None
    virtual: bool = False  # True for calculated/virtual sensors
    
    # Description for UI
    description: Optional[str] = None


# Comprehensive sensor definitions
SENSOR_DEFINITIONS = {
    # Environmental sensors
    "temperature": SensorDefinition(
        sensor_type="temperature",
        display_name="Temperature",
        icon="mdi:thermometer",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=None,  # Main sensor
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        display_precision=1,
        calculation_precision=2,
        min_value=-10.0,
        max_value=50.0,
        step=0.1,
        description="Ambient temperature around the plant"
    ),
    
    "humidity": SensorDefinition(
        sensor_type="humidity",
        display_name="Air Humidity",
        icon="mdi:water-percent",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=None,
        unit_of_measurement=PERCENTAGE,
        display_precision=0,  # No decimal places for humidity
        calculation_precision=1,
        min_value=0.0,
        max_value=100.0,
        step=1.0,
        description="Air humidity percentage"
    ),
    
    "moisture": SensorDefinition(
        sensor_type="moisture",
        display_name="Soil Moisture",
        icon="mdi:water",
        device_class=SensorDeviceClass.MOISTURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=None,
        unit_of_measurement=PERCENTAGE,
        display_precision=1,
        calculation_precision=2,
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        description="Soil moisture percentage"
    ),
    
    "illuminance": SensorDefinition(
        sensor_type="illuminance",
        display_name="Light Intensity",
        icon="mdi:brightness-6",
        device_class=SensorDeviceClass.ILLUMINANCE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=None,
        unit_of_measurement=LIGHT_LUX,
        display_precision=0,  # Whole numbers for lux
        calculation_precision=0,
        min_value=0.0,
        max_value=200000.0,
        step=500.0,
        description="Light intensity in lux"
    ),
    
    "conductivity": SensorDefinition(
        sensor_type="conductivity",
        display_name="Soil Conductivity",
        icon="mdi:spa-outline",
        device_class=SensorDeviceClass.CONDUCTIVITY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=None,
        unit_of_measurement=UnitOfConductivity.MICROSIEMENS_PER_CM,
        display_precision=0,
        calculation_precision=0,
        min_value=0.0,
        max_value=10000.0,
        step=10.0,
        description="Soil electrical conductivity"
    ),
    
    "co2": SensorDefinition(
        sensor_type="co2",
        display_name="CO2 Concentration",
        icon="mdi:molecule-co2",
        device_class=SensorDeviceClass.CO2,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=None,
        unit_of_measurement="ppm",
        display_precision=0,
        calculation_precision=0,
        min_value=300.0,
        max_value=5000.0,
        step=10.0,
        description="CO2 concentration in parts per million"
    ),
    
    "ph": SensorDefinition(
        sensor_type="ph",
        display_name="Soil pH",
        icon="mdi:ph",
        device_class=None,  # No standard device class for pH
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=None,
        unit_of_measurement="pH",
        display_precision=1,
        calculation_precision=2,
        min_value=0.0,
        max_value=14.0,
        step=0.1,
        description="Soil pH level"
    ),
    
    # Light calculation sensors
    "ppfd": SensorDefinition(
        sensor_type="ppfd",
        display_name="PPFD",
        icon="mdi:white-balance-sunny",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        unit_of_measurement="μmol/m²/s",
        display_precision=1,
        calculation_precision=3,
        min_value=0.0,
        max_value=3000.0,
        step=0.1,
        virtual=True,
        description="Photosynthetic Photon Flux Density"
    ),
    
    "dli": SensorDefinition(
        sensor_type="dli",
        display_name="Daily Light Integral",
        icon="mdi:counter",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        unit_of_measurement="mol/m²/d",
        display_precision=1,
        calculation_precision=3,
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        virtual=True,
        description="Daily Light Integral"
    ),
    
    "total_integral": SensorDefinition(
        sensor_type="total_integral",
        display_name="Total Light Integral",
        icon="mdi:counter",
        device_class=None,
        state_class=SensorStateClass.TOTAL,
        entity_category=EntityCategory.DIAGNOSTIC,
        unit_of_measurement="μmol/m²/s",
        display_precision=3,
        calculation_precision=6,
        min_value=0.0,
        virtual=True,
        description="Total accumulated light integral"
    ),
    
    # Consumption sensors
    "water_consumption": SensorDefinition(
        sensor_type="water_consumption",
        display_name="Water Consumption",
        icon="mdi:water-pump",
        device_class=SensorDeviceClass.VOLUME,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=None,
        unit_of_measurement=UnitOfVolume.LITERS,
        display_precision=2,
        calculation_precision=3,
        min_value=0.0,
        step=0.01,
        virtual=True,
        description="Current water consumption"
    ),
    
    "total_water_consumption": SensorDefinition(
        sensor_type="total_water_consumption",
        display_name="Total Water Consumption",
        icon="mdi:water-pump",
        device_class=SensorDeviceClass.VOLUME,
        state_class=SensorStateClass.TOTAL,
        entity_category=EntityCategory.DIAGNOSTIC,
        unit_of_measurement=UnitOfVolume.LITERS,
        display_precision=1,
        calculation_precision=2,
        min_value=0.0,
        description="Total accumulated water consumption"
    ),
    
    "fertilizer_consumption": SensorDefinition(
        sensor_type="fertilizer_consumption",
        display_name="Fertilizer Consumption",
        icon="mdi:chart-line-variant",
        device_class=SensorDeviceClass.VOLUME,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=None,
        unit_of_measurement=UnitOfVolume.LITERS,
        display_precision=2,
        calculation_precision=3,
        min_value=0.0,
        step=0.01,
        virtual=True,
        description="Current fertilizer consumption"
    ),
    
    "total_fertilizer_consumption": SensorDefinition(
        sensor_type="total_fertilizer_consumption",
        display_name="Total Fertilizer Consumption",
        icon="mdi:chart-line-variant",
        device_class=SensorDeviceClass.VOLUME,
        state_class=SensorStateClass.TOTAL,
        entity_category=EntityCategory.DIAGNOSTIC,
        unit_of_measurement=UnitOfVolume.LITERS,
        display_precision=1,
        calculation_precision=2,
        min_value=0.0,
        description="Total accumulated fertilizer consumption"
    ),
    
    # Power and energy sensors
    "power_consumption": SensorDefinition(
        sensor_type="power_consumption",
        display_name="Power Consumption",
        icon="mdi:flash",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=None,
        unit_of_measurement=UnitOfPower.WATT,
        display_precision=1,
        calculation_precision=2,
        min_value=0.0,
        max_value=10000.0,
        step=0.1,
        description="Current power consumption"
    ),
    
    "total_power_consumption": SensorDefinition(
        sensor_type="total_power_consumption",
        display_name="Total Energy Consumption",
        icon="mdi:flash",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        display_precision=1,
        calculation_precision=2,
        min_value=0.0,
        description="Total energy consumption"
    ),
    
    "energy_cost": SensorDefinition(
        sensor_type="energy_cost",
        display_name="Energy Cost",
        icon="mdi:currency-eur",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=None,
        unit_of_measurement="€",
        display_precision=2,
        calculation_precision=3,
        min_value=0.0,
        step=0.01,
        virtual=True,
        description="Current energy costs"
    ),
    
    "total_energy_cost": SensorDefinition(
        sensor_type="total_energy_cost",
        display_name="Total Energy Cost",
        icon="mdi:currency-eur",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        entity_category=EntityCategory.DIAGNOSTIC,
        unit_of_measurement="€",
        display_precision=2,
        calculation_precision=3,
        min_value=0.0,
        description="Total accumulated energy costs"
    ),
    
    # Health and lifecycle sensors
    "health": SensorDefinition(
        sensor_type="health",
        display_name="Plant Health",
        icon="mdi:heart-pulse",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        unit_of_measurement="/10",
        display_precision=1,
        calculation_precision=2,
        min_value=0.0,
        max_value=10.0,
        step=0.1,
        virtual=True,
        description="Plant health score out of 10"
    ),
    
    "flowering_days": SensorDefinition(
        sensor_type="flowering_days",
        display_name="Flowering Days",
        icon="mdi:flower",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL,
        entity_category=EntityCategory.DIAGNOSTIC,
        unit_of_measurement=UnitOfTime.DAYS,
        display_precision=0,
        calculation_precision=0,
        min_value=0.0,
        virtual=True,
        description="Days in flowering phase"
    ),
    
    "vegetative_days": SensorDefinition(
        sensor_type="vegetative_days",
        display_name="Vegetative Days",
        icon="mdi:leaf",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL,
        entity_category=EntityCategory.DIAGNOSTIC,
        unit_of_measurement=UnitOfTime.DAYS,
        display_precision=0,
        calculation_precision=0,
        min_value=0.0,
        virtual=True,
        description="Days in vegetative phase"
    ),
    
    "total_days": SensorDefinition(
        sensor_type="total_days",
        display_name="Total Days",
        icon="mdi:calendar",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL,
        entity_category=EntityCategory.DIAGNOSTIC,
        unit_of_measurement=UnitOfTime.DAYS,
        display_precision=0,
        calculation_precision=0,
        min_value=0.0,
        virtual=True,
        description="Total days since planting"
    ),
    
    # Configuration sensors (thresholds, settings)
    "threshold_min": SensorDefinition(
        sensor_type="threshold_min",
        display_name="Minimum Threshold",
        icon="mdi:gauge-low",
        device_class=None,
        state_class=None,
        entity_category=EntityCategory.CONFIG,
        display_precision=1,
        calculation_precision=2,
        description="Minimum threshold value"
    ),
    
    "threshold_max": SensorDefinition(
        sensor_type="threshold_max",
        display_name="Maximum Threshold",
        icon="mdi:gauge-full",
        device_class=None,
        state_class=None,
        entity_category=EntityCategory.CONFIG,
        display_precision=1,
        calculation_precision=2,
        description="Maximum threshold value"
    ),
    
    "pot_size": SensorDefinition(
        sensor_type="pot_size",
        display_name="Pot Size",
        icon="mdi:pot",
        device_class=SensorDeviceClass.VOLUME,
        state_class=None,
        entity_category=EntityCategory.CONFIG,
        unit_of_measurement=UnitOfVolume.LITERS,
        display_precision=1,
        calculation_precision=2,
        min_value=0.1,
        max_value=1000.0,
        step=0.1,
        description="Plant pot size"
    ),
    
    "water_capacity": SensorDefinition(
        sensor_type="water_capacity",
        display_name="Water Capacity",
        icon="mdi:water-pump",
        device_class=SensorDeviceClass.VOLUME,
        state_class=None,
        entity_category=EntityCategory.CONFIG,
        unit_of_measurement=UnitOfVolume.LITERS,
        display_precision=1,
        calculation_precision=2,
        min_value=0.1,
        max_value=100.0,
        step=0.1,
        description="Water holding capacity"
    ),
}


# Utility functions
def get_sensor_definition(sensor_type: str) -> Optional[SensorDefinition]:
    """Get sensor definition by type."""
    return SENSOR_DEFINITIONS.get(sensor_type.lower())


def get_all_sensor_types() -> list[str]:
    """Get list of all available sensor types."""
    return list(SENSOR_DEFINITIONS.keys())


def get_sensors_by_category(category: Optional[EntityCategory]) -> list[str]:
    """Get sensor types filtered by entity category."""
    return [
        sensor_type for sensor_type, definition in SENSOR_DEFINITIONS.items()
        if definition.entity_category == category
    ]


def get_virtual_sensors() -> list[str]:
    """Get list of virtual/calculated sensor types."""
    return [
        sensor_type for sensor_type, definition in SENSOR_DEFINITIONS.items()
        if definition.virtual
    ]


def apply_sensor_definition(entity, sensor_type: str) -> None:
    """Apply sensor definition to an entity."""
    definition = get_sensor_definition(sensor_type)
    if not definition:
        return
    
    # Apply Home Assistant compliance attributes
    entity._attr_device_class = definition.device_class
    entity._attr_state_class = definition.state_class
    entity._attr_entity_category = definition.entity_category
    entity._attr_native_unit_of_measurement = definition.unit_of_measurement
    entity._attr_suggested_display_precision = definition.display_precision
    entity._attr_icon = definition.icon
    
    # Apply range constraints if applicable
    if hasattr(entity, '_attr_native_min_value') and definition.min_value is not None:
        entity._attr_native_min_value = definition.min_value
    if hasattr(entity, '_attr_native_max_value') and definition.max_value is not None:
        entity._attr_native_max_value = definition.max_value
    if hasattr(entity, '_attr_native_step') and definition.step is not None:
        entity._attr_native_step = definition.step


def round_sensor_value(value: Union[float, int, str, None], sensor_type: str, for_display: bool = True) -> Optional[Union[float, int]]:
    """Round sensor value according to sensor definition."""
    if value is None:
        return None
    
    definition = get_sensor_definition(sensor_type)
    if not definition:
        return value
    
    try:
        numeric_value = float(value)
        precision = definition.display_precision if for_display else definition.calculation_precision
        
        if precision == 0:
            return int(round(numeric_value))
        else:
            return round(numeric_value, precision)
            
    except (ValueError, TypeError):
        return None


def format_sensor_value(value: Union[float, int, str, None], sensor_type: str) -> str:
    """Format sensor value with appropriate precision."""
    definition = get_sensor_definition(sensor_type)
    if not definition:
        return str(value) if value is not None else "Unknown"
    
    rounded_value = round_sensor_value(value, sensor_type, for_display=True)
    if rounded_value is None:
        return "Unknown"
    
    if definition.display_precision == 0:
        formatted = f"{int(rounded_value)}"
    else:
        formatted = f"{rounded_value:.{definition.display_precision}f}"
    
    if definition.unit_of_measurement:
        formatted += f" {definition.unit_of_measurement}"
    
    return formatted


class SensorDefinitionMixin:
    """Mixin class to apply sensor definitions to entities."""
    
    def __init__(self, sensor_type: str, *args, **kwargs):
        """Initialize with sensor type definition."""
        super().__init__(*args, **kwargs)
        self._sensor_type = sensor_type.lower()
        
        # Apply sensor definition
        apply_sensor_definition(self, self._sensor_type)
    
    def _round_value_for_display(self, value: Union[float, int, str, None]) -> Optional[Union[float, int]]:
        """Round value for display."""
        return round_sensor_value(value, self._sensor_type, for_display=True)
    
    def _round_value_for_calculation(self, value: Union[float, int, str, None]) -> Optional[Union[float, int]]:
        """Round value for calculations."""
        return round_sensor_value(value, self._sensor_type, for_display=False)
    
    def get_sensor_definition(self) -> Optional[SensorDefinition]:
        """Get the sensor definition for this entity."""
        return get_sensor_definition(self._sensor_type)