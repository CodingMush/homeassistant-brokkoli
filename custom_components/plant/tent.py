"""Tent entity for the plant integration"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from homeassistant.const import (
    ATTR_NAME,
    STATE_OK,
    STATE_PROBLEM,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import Entity, async_generate_entity_id
from homeassistant.helpers.entity_registry import async_get
from homeassistant.components.sensor import SensorDeviceClass

from .const import (
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class TentDevice(Entity):
    """Enhanced tent device with comprehensive sensor management"""

    def __init__(self, hass: HomeAssistant, name: str, sensors: Optional[Dict[str, str]] = None, area_id: Optional[str] = None) -> None:
        """Initialize the tent device."""
        self._hass = hass
        self._attr_name = name
        self._attr_unique_id = f"tent_{name.lower().replace(' ', '_')}"
        self.entity_id = async_generate_entity_id(
            f"{DOMAIN}.{{}}", self.name, current_ids={}
        )
        
        # External sensor entity IDs (reference to existing HA sensors)
        self._external_sensors = sensors or {}
        self.temperature_sensor = self._external_sensors.get("temperature")
        self.humidity_sensor = self._external_sensors.get("humidity")
        self.conductivity_sensor = self._external_sensors.get("conductivity")
        self.illuminance_sensor = self._external_sensors.get("illuminance")
        self.co2_sensor = self._external_sensors.get("co2")
        self.ph_sensor = self._external_sensors.get("ph")
        
        # Tent metadata
        self._area_id = area_id
        self._assigned_plants: List[str] = []
        self._last_updated = datetime.now()
        self._configuration_status = "configured" if sensors else "incomplete"

    @property
    def state(self) -> str:
        """Return the state of the tent device based on sensor availability."""
        if self._configuration_status == "sensors_unavailable":
            return STATE_UNAVAILABLE
        elif self._configuration_status == "incomplete":
            return STATE_UNKNOWN
        else:
            return STATE_OK

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes with enhanced sensor information."""
        return {
            "temperature_sensor": self.temperature_sensor,
            "humidity_sensor": self.humidity_sensor,
            "conductivity_sensor": self.conductivity_sensor,
            "illuminance_sensor": self.illuminance_sensor,
            "co2_sensor": self.co2_sensor,
            "ph_sensor": self.ph_sensor,
            "sensor_count": self.get_sensor_count(),
            "assigned_plants": self._assigned_plants,
            "sensor_mappings": self._external_sensors,
            "last_updated": self._last_updated.isoformat(),
            "configuration_status": self._configuration_status,
            "area_id": self._area_id,
        }

    async def add_sensors(
        self,
        temperature_sensor: str | None = None,
        humidity_sensor: str | None = None,
        conductivity_sensor: str | None = None,
        illuminance_sensor: str | None = None,
        co2_sensor: str | None = None,
        ph_sensor: str | None = None,
    ) -> bool:
        """Add/update external sensors to the tent device with validation."""
        sensor_updates = {}
        
        # Validate and update each sensor
        for sensor_type, sensor_entity in [
            ("temperature", temperature_sensor),
            ("humidity", humidity_sensor),
            ("conductivity", conductivity_sensor),
            ("illuminance", illuminance_sensor),
            ("co2", co2_sensor),
            ("ph", ph_sensor),
        ]:
            if sensor_entity is not None:
                if await self.validate_sensor_assignment(sensor_entity, sensor_type):
                    sensor_updates[sensor_type] = sensor_entity
                    self._external_sensors[sensor_type] = sensor_entity
                else:
                    _LOGGER.warning(f"Invalid sensor assignment: {sensor_entity} for {sensor_type}")
                    return False
        
        # Update individual sensor properties
        self.temperature_sensor = self._external_sensors.get("temperature")
        self.humidity_sensor = self._external_sensors.get("humidity")
        self.conductivity_sensor = self._external_sensors.get("conductivity")
        self.illuminance_sensor = self._external_sensors.get("illuminance")
        self.co2_sensor = self._external_sensors.get("co2")
        self.ph_sensor = self._external_sensors.get("ph")
        
        self._last_updated = datetime.now()
        self._configuration_status = "configured" if self.get_sensor_count() > 0 else "incomplete"
        
        # Trigger state update
        self.async_write_ha_state()
        return True

    async def validate_sensor_assignment(self, sensor_entity: str, sensor_type: str) -> bool:
        """Validate that a sensor entity is compatible with the expected sensor type."""
        if not sensor_entity:
            return True  # None/empty is valid (optional sensor)
            
        # Get entity registry to check if entity exists
        entity_registry = async_get(self._hass)
        entity_entry = entity_registry.async_get(sensor_entity)
        
        if not entity_entry:
            # Check if entity exists in state registry
            state = self._hass.states.get(sensor_entity)
            if not state:
                _LOGGER.error(f"Sensor entity {sensor_entity} does not exist")
                return False
        
        # Validate device class compatibility (optional but recommended)
        expected_device_classes = {
            "temperature": [SensorDeviceClass.TEMPERATURE],
            "humidity": [SensorDeviceClass.HUMIDITY],
            "co2": [SensorDeviceClass.CO2],
            "illuminance": [SensorDeviceClass.ILLUMINANCE],
            "conductivity": ["conductivity"],  # Custom device class
            "ph": [SensorDeviceClass.PH, "ph"],
        }
        
        if sensor_type in expected_device_classes:
            # This is optional validation - we allow any sensor to be assigned
            # but log a warning if device class doesn't match
            if entity_entry and hasattr(entity_entry, 'device_class'):
                if entity_entry.device_class not in expected_device_classes[sensor_type]:
                    _LOGGER.warning(
                        f"Sensor {sensor_entity} device class '{entity_entry.device_class}' "
                        f"may not be compatible with expected type '{sensor_type}'"
                    )
        
        return True
    
    def get_sensor_count(self) -> int:
        """Return the number of configured sensors."""
        return len([s for s in self._external_sensors.values() if s])
    
    def get_sensor_config(self) -> Dict[str, str]:
        """Return the current sensor configuration."""
        return self._external_sensors.copy()
    
    def assign_plant(self, plant_id: str) -> None:
        """Assign a plant to this tent."""
        if plant_id not in self._assigned_plants:
            self._assigned_plants.append(plant_id)
            self._last_updated = datetime.now()
            self.async_write_ha_state()
    
    def unassign_plant(self, plant_id: str) -> None:
        """Unassign a plant from this tent."""
        if plant_id in self._assigned_plants:
            self._assigned_plants.remove(plant_id)
            self._last_updated = datetime.now()
            self.async_write_ha_state()
    
    def get_assigned_plants(self) -> List[str]:
        """Return list of assigned plant IDs."""
        return self._assigned_plants.copy()
    
    async def async_update(self) -> None:
        """Update the tent device state."""
        # Update configuration status based on sensor availability
        available_sensors = 0
        for sensor_entity in self._external_sensors.values():
            if sensor_entity:
                state = self._hass.states.get(sensor_entity)
                if state and state.state not in [STATE_UNAVAILABLE, STATE_UNKNOWN]:
                    available_sensors += 1
        
        if available_sensors == 0 and self.get_sensor_count() > 0:
            self._configuration_status = "sensors_unavailable"
        elif self.get_sensor_count() == 0:
            self._configuration_status = "incomplete"
        else:
            self._configuration_status = "configured"
