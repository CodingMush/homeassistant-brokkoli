"""Tent integration for the plant integration."""

from __future__ import annotations

import logging
from typing import Optional, Dict, Any

from homeassistant.const import (
    ATTR_NAME,
    STATE_OK,
    STATE_PROBLEM,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import Entity, async_generate_entity_id

from .const import (
    DOMAIN,
    DEVICE_TYPE_PLANT,
)

_LOGGER = logging.getLogger(__name__)


class TentIntegration:
    """Tent integration for plants."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the tent integration."""
        self._hass = hass
        self._tents: Dict[str, TentInfo] = {}

    def add_tent(self, tent_id: str, tent_info: Dict[str, Any]) -> None:
        """Add a tent to the integration."""
        self._tents[tent_id] = TentInfo(tent_id, tent_info)

    def get_tent(self, tent_id: str) -> Optional[TentInfo]:
        """Get a tent by ID."""
        return self._tents.get(tent_id)

    def get_tent_sensors(self, tent_id: str) -> Dict[str, str]:
        """Get all sensors for a tent."""
        tent = self.get_tent(tent_id)
        if tent:
            return tent.sensors
        return {}

    def assign_plant_to_tent(self, plant_entity_id: str, tent_id: str) -> None:
        """Assign a plant to a tent."""
        tent = self.get_tent(tent_id)
        if tent:
            tent.add_plant(plant_entity_id)

    def get_tent_for_plant(self, plant_entity_id: str) -> Optional[str]:
        """Get the tent ID for a plant."""
        for tent_id, tent in self._tents.items():
            if plant_entity_id in tent.plants:
                return tent_id
        return None


class TentInfo:
    """Information about a tent."""

    def __init__(self, tent_id: str, tent_info: Dict[str, Any]) -> None:
        """Initialize tent information."""
        self.tent_id = tent_id
        self.name = tent_info.get(ATTR_NAME, f"Tent {tent_id}")
        self.sensors: Dict[str, str] = tent_info.get("sensors", {})
        self.plants: set = set()
        self.controls: Dict[str, str] = tent_info.get("controls", {})

    def add_plant(self, plant_entity_id: str) -> None:
        """Add a plant to this tent."""
        self.plants.add(plant_entity_id)

    def remove_plant(self, plant_entity_id: str) -> None:
        """Remove a plant from this tent."""
        self.plants.discard(plant_entity_id)


# Functions to extend PlantDevice functionality for tent integration


def add_tent_attributes(plant_device: Entity) -> None:
    """Add tent attributes to a plant device."""
    # Add tent-related attributes to the plant
    plant_device.tent_id = None
    plant_device.tent_sensors = {}
    plant_device.tent_controls = {}


def assign_plant_to_tent(plant_device: Entity, tent_id: str, tent_sensors: Dict[str, str]) -> None:
    """Assign a plant to a tent."""
    plant_device.tent_id = tent_id
    plant_device.tent_sensors = tent_sensors.copy()


def get_tent_sensor_for_plant(plant_device: Entity, sensor_type: str) -> Optional[str]:
    """Get the tent sensor for a specific plant sensor type."""
    if hasattr(plant_device, 'tent_sensors') and sensor_type in plant_device.tent_sensors:
        return plant_device.tent_sensors[sensor_type]
    return None


def is_plant_in_tent(plant_device: Entity) -> bool:
    """Check if a plant is assigned to a tent."""
    return hasattr(plant_device, 'tent_id') and plant_device.tent_id is not None


# Functions to extend sensor functionality for tent integration


def create_tent_sensor_proxy(hass: HomeAssistant, plant_sensor: Entity, tent_sensor_entity_id: str) -> Entity:
    """Create a proxy sensor that uses tent sensor data."""
    # This function would create a sensor that mirrors the tent sensor data
    # For now, we'll just return the tent sensor entity ID
    # In a full implementation, this would create a proper sensor entity
    return tent_sensor_entity_id


# WebSocket API extensions for tent integration


def extend_websocket_info_with_tent_data(plant_info: dict, plant_device: Entity) -> dict:
    """Extend websocket info with tent data."""
    # Add tent information to the websocket response
    if is_plant_in_tent(plant_device):
        tent_info = {
            "tent_id": plant_device.tent_id,
            "tent_sensors": plant_device.tent_sensors,
        }
        plant_info["tent"] = tent_info
    
    return plant_info