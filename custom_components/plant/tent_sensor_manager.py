"""Tent sensor management and inheritance logic."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_registry import async_get

from .const import (
    DOMAIN,
    FLOW_TENT_SENSORS,
    FLOW_TENT_ENTITY,
    FLOW_INHERIT_TENT_SENSORS,
    FLOW_SENSOR_TEMPERATURE,
    FLOW_SENSOR_HUMIDITY,
    FLOW_SENSOR_CO2,
    FLOW_SENSOR_ILLUMINANCE,
    FLOW_SENSOR_CONDUCTIVITY,
    FLOW_SENSOR_PH,
)

_LOGGER = logging.getLogger(__name__)


class TentSensorManager:
    """Manage sensor inheritance between tents and plants."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the tent sensor manager."""
        self.hass = hass

    async def resolve_plant_sensors(
        self, 
        plant_config: Dict, 
        tent_entry_id: Optional[str] = None,
        inherit_sensors: bool = True
    ) -> Dict[str, str]:
        """
        Resolve final sensor assignments for a plant considering tent inheritance.
        
        Priority order:
        1. Plant-specific sensor overrides
        2. Tent sensor inheritance (if enabled)
        3. None (no sensor)
        """
        resolved_sensors = {}
        
        # Define sensor types to process
        sensor_types = [
            "temperature", "humidity", "co2", 
            "illuminance", "conductivity", "ph"
        ]
        
        # Get tent sensors if tent is assigned and inheritance is enabled
        tent_sensors = {}
        if tent_entry_id and inherit_sensors:
            tent_sensors = await self.get_tent_sensor_config(tent_entry_id)
        
        # Resolve each sensor type
        for sensor_type in sensor_types:
            sensor_key = f"{sensor_type}_sensor"
            
            # Priority 1: Plant-specific override
            plant_sensor = plant_config.get(sensor_key)
            if plant_sensor:
                resolved_sensors[sensor_type] = plant_sensor
                continue
            
            # Priority 2: Tent inheritance
            tent_sensor = tent_sensors.get(sensor_type)
            if tent_sensor and inherit_sensors:
                resolved_sensors[sensor_type] = tent_sensor
                continue
            
            # Priority 3: No sensor (None)
            # We don't add None values to keep the dict clean
        
        return resolved_sensors

    async def get_tent_sensor_config(self, tent_entry_id: str) -> Dict[str, str]:
        """Get sensor configuration from a tent entry."""
        # Get all config entries for this domain
        entries = self.hass.config_entries.async_entries(DOMAIN)
        
        for entry in entries:
            if entry.entry_id == tent_entry_id and entry.data.get("is_tent", False):
                return entry.data.get(FLOW_TENT_SENSORS, {})
        
        _LOGGER.warning(f"Tent entry {tent_entry_id} not found")
        return {}

    async def validate_tent_assignment(self, tent_entry_id: str) -> bool:
        """Validate that a tent entry exists and is properly configured."""
        tent_sensors = await self.get_tent_sensor_config(tent_entry_id)
        return len(tent_sensors) > 0

    async def get_available_tents(self) -> List[Dict[str, str]]:
        """Get list of available tent entries."""
        entries = self.hass.config_entries.async_entries(DOMAIN)
        tents = []
        
        for entry in entries:
            if entry.data.get("is_tent", False):
                tent_sensors = entry.data.get(FLOW_TENT_SENSORS, {})
                sensor_count = len([s for s in tent_sensors.values() if s])
                
                tents.append({
                    "entry_id": entry.entry_id,
                    "name": entry.data.get("name", "Unknown Tent"),
                    "sensor_count": sensor_count,
                    "sensors": tent_sensors
                })
        
        return tents

    async def apply_tent_sensors_to_plant(
        self, 
        plant_entry: ConfigEntry, 
        tent_entry_id: str,
        inherit_sensors: bool = True
    ) -> bool:
        """Apply tent sensor configuration to an existing plant entry."""
        if not inherit_sensors:
            return True
            
        tent_sensors = await self.get_tent_sensor_config(tent_entry_id)
        if not tent_sensors:
            _LOGGER.warning(f"No sensors found for tent {tent_entry_id}")
            return False
        
        # Update plant configuration with tent sensors
        plant_data = dict(plant_entry.data)
        plant_info = dict(plant_data.get("plant_info", {}))
        
        # Apply tent sensors where plant doesn't have specific sensors
        for sensor_type, sensor_entity in tent_sensors.items():
            sensor_key = f"{sensor_type}_sensor"
            if not plant_info.get(sensor_key) and sensor_entity:
                plant_info[sensor_key] = sensor_entity
        
        # Store tent relationship
        plant_info[FLOW_TENT_ENTITY] = tent_entry_id
        plant_info[FLOW_INHERIT_TENT_SENSORS] = inherit_sensors
        
        plant_data["plant_info"] = plant_info
        
        # Update the config entry
        self.hass.config_entries.async_update_entry(
            plant_entry, data=plant_data
        )
        
        return True

    async def handle_tent_sensor_update(self, tent_entry_id: str) -> List[str]:
        """
        Handle updates when a tent's sensor configuration changes.
        Returns list of affected plant entry IDs.
        """
        affected_plants = []
        tent_sensors = await self.get_tent_sensor_config(tent_entry_id)
        
        # Find all plants assigned to this tent
        entries = self.hass.config_entries.async_entries(DOMAIN)
        for entry in entries:
            plant_info = entry.data.get("plant_info", {})
            
            # Check if plant is assigned to this tent and inherits sensors
            if (plant_info.get(FLOW_TENT_ENTITY) == tent_entry_id and 
                plant_info.get(FLOW_INHERIT_TENT_SENSORS, True)):
                
                # Update plant sensors
                updated_plant_info = dict(plant_info)
                
                # Re-apply tent sensors (preserve plant overrides)
                for sensor_type, sensor_entity in tent_sensors.items():
                    sensor_key = f"{sensor_type}_sensor"
                    # Only update if plant doesn't have a specific override
                    if not self._has_plant_override(updated_plant_info, sensor_key):
                        if sensor_entity:
                            updated_plant_info[sensor_key] = sensor_entity
                        else:
                            # Remove sensor if tent no longer has it
                            updated_plant_info.pop(sensor_key, None)
                
                # Update the entry
                updated_data = dict(entry.data)
                updated_data["plant_info"] = updated_plant_info
                
                self.hass.config_entries.async_update_entry(
                    entry, data=updated_data
                )
                
                affected_plants.append(entry.entry_id)
                
                # Schedule entity reloading for this plant
                await self.hass.config_entries.async_reload(entry.entry_id)
        
        return affected_plants

    def _has_plant_override(self, plant_info: Dict, sensor_key: str) -> bool:
        """Check if plant has a specific sensor override."""
        # This could be enhanced to track which sensors are overrides vs inherited
        # For now, we assume any sensor present in plant_info is intentional
        return sensor_key in plant_info

    async def get_plant_sensor_sources(self, plant_entry: ConfigEntry) -> Dict[str, str]:
        """
        Get the source of each sensor for a plant (tent/direct/none).
        Returns mapping of sensor_type -> source.
        """
        plant_info = plant_entry.data.get("plant_info", {})
        tent_entry_id = plant_info.get(FLOW_TENT_ENTITY)
        inherit_sensors = plant_info.get(FLOW_INHERIT_TENT_SENSORS, True)
        
        sources = {}
        tent_sensors = {}
        
        if tent_entry_id and inherit_sensors:
            tent_sensors = await self.get_tent_sensor_config(tent_entry_id)
        
        sensor_types = ["temperature", "humidity", "co2", "illuminance", "conductivity", "ph"]
        
        for sensor_type in sensor_types:
            sensor_key = f"{sensor_type}_sensor"
            plant_sensor = plant_info.get(sensor_key)
            tent_sensor = tent_sensors.get(sensor_type)
            
            if plant_sensor:
                if tent_sensor == plant_sensor and inherit_sensors:
                    sources[sensor_type] = "tent"
                else:
                    sources[sensor_type] = "direct"
            else:
                sources[sensor_type] = "none"
        
        return sources