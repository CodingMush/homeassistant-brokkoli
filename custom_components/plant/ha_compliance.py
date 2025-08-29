"""Home Assistant compliance utilities and improvements.

⚠️  DEPRECATED: This module is deprecated. Use sensor_definitions.py instead.

This module will be removed in a future version. All functionality has been
consolidated into sensor_definitions.py for better maintainability.

For migration:
- Replace imports from ha_compliance with sensor_definitions
- Use SensorDefinitionMixin instead of HAComplianceMixin
- Use apply_sensor_definition() for applying definitions to entities
"""

# Import from the new consolidated module for backwards compatibility
from .sensor_definitions import (
    SensorDefinitionMixin as HAComplianceMixin,
    apply_sensor_definition as apply_compliance_fix,
    get_sensor_definition,
    SENSOR_DEFINITIONS,
)

# Re-export for backwards compatibility
__all__ = [
    'HAComplianceMixin',
    'apply_compliance_fix', 
    'get_sensor_definition',
    'SENSOR_DEFINITIONS',
]

# Legacy mappings for backwards compatibility
ENTITY_CATEGORIES = {k: v.entity_category for k, v in SENSOR_DEFINITIONS.items()}
DEVICE_CLASSES = {k: v.device_class for k, v in SENSOR_DEFINITIONS.items()}
STATE_CLASSES = {k: v.state_class for k, v in SENSOR_DEFINITIONS.items()}
UNITS_OF_MEASUREMENT = {k: v.unit_of_measurement for k, v in SENSOR_DEFINITIONS.items()}

def get_entity_category(sensor_type: str):
    """Legacy function - use get_sensor_definition() instead."""
    definition = get_sensor_definition(sensor_type)
    return definition.entity_category if definition else None

def get_device_class(sensor_type: str):
    """Legacy function - use get_sensor_definition() instead."""
    definition = get_sensor_definition(sensor_type)
    return definition.device_class if definition else None

def get_state_class(sensor_type: str):
    """Legacy function - use get_sensor_definition() instead."""
    definition = get_sensor_definition(sensor_type)
    return definition.state_class if definition else None

def get_unit_of_measurement(sensor_type: str):
    """Legacy function - use get_sensor_definition() instead."""
    definition = get_sensor_definition(sensor_type)
    return definition.unit_of_measurement if definition else None


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