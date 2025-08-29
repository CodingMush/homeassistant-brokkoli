"""Home Assistant compliance utilities and improvements."""

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

# Entity category mappings for different sensor types
ENTITY_CATEGORIES = {
    # Diagnostic sensors (internal/computed values)
    "health": EntityCategory.DIAGNOSTIC,
    "problem_status": EntityCategory.DIAGNOSTIC,
    "growth_phase": EntityCategory.DIAGNOSTIC,
    "flowering_days": EntityCategory.DIAGNOSTIC,
    "vegetative_days": EntityCategory.DIAGNOSTIC,
    "total_days": EntityCategory.DIAGNOSTIC,
    "cycle_median_sensor": EntityCategory.DIAGNOSTIC,
    
    # Configuration sensors
    "threshold_min": EntityCategory.CONFIG,
    "threshold_max": EntityCategory.CONFIG,
    "pot_size": EntityCategory.CONFIG,
    "water_capacity": EntityCategory.CONFIG,
    
    # Main sensors (no category - appear in main dashboard)
    "temperature": None,
    "moisture": None,
    "conductivity": None,
    "illuminance": None,
    "humidity": None,
    "co2": None,
    "ph": None,
    "ppfd": None,
    "dli": None,
    "power_consumption": None,
    "energy_cost": None,
    "water_consumption": None,
    "fertilizer_consumption": None,
}

# Device class mappings
DEVICE_CLASSES = {
    "temperature": SensorDeviceClass.TEMPERATURE,
    "moisture": SensorDeviceClass.MOISTURE,
    "conductivity": SensorDeviceClass.CONDUCTIVITY,
    "illuminance": SensorDeviceClass.ILLUMINANCE,
    "humidity": SensorDeviceClass.HUMIDITY,
    "co2": SensorDeviceClass.CO2,
    "power_consumption": SensorDeviceClass.POWER,
    "energy_cost": SensorDeviceClass.MONETARY,
    "water_consumption": SensorDeviceClass.VOLUME,
    "fertilizer_consumption": SensorDeviceClass.VOLUME,
    "timestamp": SensorDeviceClass.TIMESTAMP,
    "duration": SensorDeviceClass.DURATION,
    # pH doesn't have a standard device class, use None
    "ph": None,
    "ppfd": None,  # Custom light measurement
    "dli": None,   # Custom daily light integral
}

# State class mappings
STATE_CLASSES = {
    # Measurement values
    "temperature": SensorStateClass.MEASUREMENT,
    "moisture": SensorStateClass.MEASUREMENT,
    "conductivity": SensorStateClass.MEASUREMENT,
    "illuminance": SensorStateClass.MEASUREMENT,
    "humidity": SensorStateClass.MEASUREMENT,
    "co2": SensorStateClass.MEASUREMENT,
    "ph": SensorStateClass.MEASUREMENT,
    "ppfd": SensorStateClass.MEASUREMENT,
    "dli": SensorStateClass.MEASUREMENT,
    "power_consumption": SensorStateClass.MEASUREMENT,
    "health": SensorStateClass.MEASUREMENT,
    
    # Total values (cumulative)
    "total_water_consumption": SensorStateClass.TOTAL,
    "total_fertilizer_consumption": SensorStateClass.TOTAL,
    "total_power_consumption": SensorStateClass.TOTAL,
    "total_energy_cost": SensorStateClass.TOTAL,
    "total_light_integral": SensorStateClass.TOTAL,
    "flowering_days": SensorStateClass.TOTAL,
    "vegetative_days": SensorStateClass.TOTAL,
    "total_days": SensorStateClass.TOTAL,
    
    # Increasing values (monotonic)
    "water_consumption": SensorStateClass.TOTAL_INCREASING,
    "fertilizer_consumption": SensorStateClass.TOTAL_INCREASING,
    "energy_cost": SensorStateClass.TOTAL_INCREASING,
}

# Unit of measurement mappings
UNITS_OF_MEASUREMENT = {
    "temperature": UnitOfTemperature.CELSIUS,
    "moisture": PERCENTAGE,
    "conductivity": UnitOfConductivity.MICROSIEMENS_PER_CENTIMETER,
    "illuminance": LIGHT_LUX,
    "humidity": PERCENTAGE,
    "co2": "ppm",
    "ph": "pH",
    "ppfd": "μmol/m²/s",
    "dli": "mol/m²/d",
    "power_consumption": UnitOfPower.WATT,
    "energy_cost": "€",  # or currency from config
    "water_consumption": UnitOfVolume.LITERS,
    "fertilizer_consumption": UnitOfVolume.LITERS,
    "total_water_consumption": UnitOfVolume.LITERS,
    "total_fertilizer_consumption": UnitOfVolume.LITERS,
    "total_power_consumption": UnitOfEnergy.KILO_WATT_HOUR,
    "total_energy_cost": "€",
    "flowering_days": UnitOfTime.DAYS,
    "vegetative_days": UnitOfTime.DAYS,
    "total_days": UnitOfTime.DAYS,
    "health": "/10",  # Health score out of 10
}


def get_entity_category(sensor_type: str) -> EntityCategory | None:
    """Get appropriate entity category for sensor type."""
    return ENTITY_CATEGORIES.get(sensor_type.lower())


def get_device_class(sensor_type: str) -> SensorDeviceClass | None:
    """Get appropriate device class for sensor type."""
    return DEVICE_CLASSES.get(sensor_type.lower())


def get_state_class(sensor_type: str) -> SensorStateClass | None:
    """Get appropriate state class for sensor type."""
    return STATE_CLASSES.get(sensor_type.lower())


def get_unit_of_measurement(sensor_type: str) -> str | None:
    """Get appropriate unit of measurement for sensor type."""
    return UNITS_OF_MEASUREMENT.get(sensor_type.lower())


class HAComplianceMixin:
    """Mixin class to add HA compliance to sensor entities."""
    
    def __init__(self, sensor_type: str, *args, **kwargs):
        """Initialize with sensor type for compliance."""
        super().__init__(*args, **kwargs)
        self._sensor_type = sensor_type.lower()
        
        # Set compliance attributes
        self._attr_entity_category = get_entity_category(self._sensor_type)
        self._attr_device_class = get_device_class(self._sensor_type)
        self._attr_state_class = get_state_class(self._sensor_type)
        
        if not hasattr(self, '_attr_native_unit_of_measurement'):
            self._attr_native_unit_of_measurement = get_unit_of_measurement(self._sensor_type)
    
    @property
    def entity_category(self) -> EntityCategory | None:
        """Return entity category."""
        return self._attr_entity_category
    
    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Return device class."""
        return self._attr_device_class
    
    @property
    def state_class(self) -> SensorStateClass | None:
        """Return state class."""
        return self._attr_state_class


def validate_entity_compliance(entity) -> list[str]:
    """Validate entity compliance and return list of issues."""
    issues = []
    
    # Check if entity has proper device info
    if not hasattr(entity, 'device_info') or not entity.device_info:
        issues.append("Missing device_info")
    
    # Check unique_id
    if not hasattr(entity, 'unique_id') or not entity.unique_id:
        issues.append("Missing unique_id")
    
    # Check entity_id format
    if hasattr(entity, 'entity_id') and entity.entity_id:
        if not entity.entity_id.count('.') == 1:
            issues.append("Invalid entity_id format")
    
    # Check sensor-specific compliance
    if hasattr(entity, '_attr_device_class'):
        if entity._attr_device_class and not isinstance(entity._attr_device_class, SensorDeviceClass):
            issues.append("Invalid device_class type")
    
    if hasattr(entity, '_attr_state_class'):
        if entity._attr_state_class and not isinstance(entity._attr_state_class, SensorStateClass):
            issues.append("Invalid state_class type")
    
    # Check unit consistency
    if hasattr(entity, '_attr_native_unit_of_measurement') and hasattr(entity, '_attr_device_class'):
        device_class = entity._attr_device_class
        unit = entity._attr_native_unit_of_measurement
        
        # Basic unit validation for common device classes
        if device_class == SensorDeviceClass.TEMPERATURE and unit not in [UnitOfTemperature.CELSIUS, UnitOfTemperature.FAHRENHEIT, UnitOfTemperature.KELVIN]:
            issues.append(f"Invalid unit {unit} for temperature sensor")
        elif device_class == SensorDeviceClass.HUMIDITY and unit != PERCENTAGE:
            issues.append(f"Invalid unit {unit} for humidity sensor")
    
    return issues


def apply_compliance_fix(entity, sensor_type: str) -> None:
    """Apply compliance fixes to an entity."""
    # Set missing attributes based on sensor type
    if not hasattr(entity, '_attr_entity_category'):
        entity._attr_entity_category = get_entity_category(sensor_type)
    
    if not hasattr(entity, '_attr_device_class'):
        entity._attr_device_class = get_device_class(sensor_type)
    
    if not hasattr(entity, '_attr_state_class'):
        entity._attr_state_class = get_state_class(sensor_type)
    
    if not hasattr(entity, '_attr_native_unit_of_measurement'):
        entity._attr_native_unit_of_measurement = get_unit_of_measurement(sensor_type)
    
    # Ensure unique_id is set
    if not hasattr(entity, 'unique_id') or not entity.unique_id:
        if hasattr(entity, '_plant') and hasattr(entity._plant, 'unique_id'):
            entity._attr_unique_id = f"{entity._plant.unique_id}_{sensor_type}"


# Availability mixins for external sensors
class ExternalSensorAvailabilityMixin:
    """Mixin to handle availability for sensors with external dependencies."""
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if hasattr(self, '_external_sensor') and self._external_sensor:
            external_state = self.hass.states.get(self._external_sensor)
            if not external_state:
                return False
            return external_state.state not in ["unavailable", "unknown", None]
        return True
    
    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        attrs = super().extra_state_attributes if hasattr(super(), 'extra_state_attributes') else {}
        if hasattr(self, '_external_sensor') and self._external_sensor:
            attrs["external_sensor"] = self._external_sensor
            external_state = self.hass.states.get(self._external_sensor)
            if external_state:
                attrs["external_sensor_available"] = external_state.state not in ["unavailable", "unknown"]
        return attrs