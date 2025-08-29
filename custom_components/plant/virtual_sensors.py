"""Virtual sensor system for database optimization in tent-plant integration."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, Optional, Union

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, State, callback
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.components.sensor import SensorEntity

_LOGGER = logging.getLogger(__name__)


class VirtualPlantSensor(SensorEntity):
    """
    Virtual sensor that references external sensors without creating database records.
    
    This sensor:
    - Does NOT store states in the database (should_poll=False, no state class)
    - References external sensor values directly  
    - Updates only when external sensor changes
    - Provides real-time values without historical storage
    """
    
    def __init__(
        self,
        hass: HomeAssistant,
        plant_device: Entity,
        sensor_type: str,
        external_sensor_id: Optional[str] = None,
        unique_id_suffix: str = "",
    ) -> None:
        """Initialize virtual sensor."""
        self.hass = hass
        self._plant = plant_device
        self._sensor_type = sensor_type
        self._external_sensor_id = external_sensor_id
        self._cached_state = None
        self._cached_attributes = {}
        self._last_updated = None
        self._state_listener = None
        
        # Entity configuration
        self._attr_name = f"{plant_device.name} {sensor_type.title()}"
        self._attr_unique_id = f"{plant_device.unique_id}_{sensor_type}{unique_id_suffix}"
        self._attr_has_entity_name = False
        
        # Prevent database recording
        self._attr_should_poll = False
        self._attr_state_class = None  # No state class = no long-term statistics
        self._attr_entity_category = None  # Not diagnostic, config, or system
        
    @property
    def should_poll(self) -> bool:
        """Disable polling to prevent database writes."""
        return False
    
    @property
    def native_value(self) -> Union[str, int, float, None]:
        """Return the current state from external sensor."""
        if not self._external_sensor_id:
            return self._cached_state
        
        external_state = self.hass.states.get(self._external_sensor_id)
        if not external_state or external_state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return self._cached_state
        
        try:
            # Cache the value
            self._cached_state = float(external_state.state)
            self._last_updated = datetime.now()
            return self._cached_state
        except (ValueError, TypeError):
            return self._cached_state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional attributes."""
        attrs = self._cached_attributes.copy()
        attrs.update({
            "external_sensor": self._external_sensor_id or "none",
            "sensor_type": self._sensor_type,
            "plant_device": self._plant.unique_id,
            "last_updated": self._last_updated.isoformat() if self._last_updated else None,
            "virtual_sensor": True,  # Flag to identify virtual sensors
        })
        
        # Add source sensor attributes if available
        if self._external_sensor_id:
            external_state = self.hass.states.get(self._external_sensor_id)
            if external_state:
                attrs["source_unit"] = external_state.attributes.get("unit_of_measurement")
                attrs["source_device_class"] = external_state.attributes.get("device_class")
        
        return attrs
    
    @property
    def device_info(self) -> Dict[str, Any]:
        """Return device info for grouping."""
        return {
            "identifiers": {("plant", self._plant.unique_id)},
            "name": self._plant.name,
            "manufacturer": "Brokkoli Suite",
            "model": "Plant Monitor",
        }
    
    async def async_added_to_hass(self) -> None:
        """Set up state tracking when added to hass."""
        await super().async_added_to_hass()
        
        if self._external_sensor_id:
            self._setup_state_listener()
    
    async def async_will_remove_from_hass(self) -> None:
        """Clean up when removed."""
        if self._state_listener:
            self._state_listener()
            self._state_listener = None
        await super().async_will_remove_from_hass()
    
    def _setup_state_listener(self) -> None:
        """Set up listener for external sensor state changes."""
        if not self._external_sensor_id:
            return
            
        @callback
        def state_changed_callback(event):
            """Handle external sensor state changes."""
            new_state = event.data.get("new_state")
            if new_state and new_state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                try:
                    self._cached_state = float(new_state.state)
                    self._last_updated = datetime.now()
                    self.async_write_ha_state()
                except (ValueError, TypeError):
                    pass
        
        self._state_listener = async_track_state_change_event(
            self.hass, [self._external_sensor_id], state_changed_callback
        )
    
    def update_external_sensor(self, new_sensor_id: Optional[str]) -> None:
        """Update the external sensor reference."""
        # Remove old listener
        if self._state_listener:
            self._state_listener()
            self._state_listener = None
        
        # Update sensor
        self._external_sensor_id = new_sensor_id
        
        # Set up new listener
        if new_sensor_id:
            self._setup_state_listener()
            # Immediately update state
            external_state = self.hass.states.get(new_sensor_id)
            if external_state and external_state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                try:
                    self._cached_state = float(external_state.state)
                    self._last_updated = datetime.now()
                except (ValueError, TypeError):
                    pass
        
        self.async_write_ha_state()
    
    def set_manual_value(self, value: Any) -> None:
        """Set a manual value (for plant-specific measurements)."""
        try:
            self._cached_state = float(value) if value is not None else None
            self._last_updated = datetime.now()
            self.async_write_ha_state()
        except (ValueError, TypeError):
            _LOGGER.warning(f"Invalid manual value for {self.entity_id}: {value}")


class TentSensorProxy:
    """
    Proxy for tent sensors that provides centralized access without entity creation.
    
    This system:
    - Maintains references to external tent sensors
    - Provides cached access to current values
    - Updates only when tent assignments change
    - Eliminates redundant sensor entities
    """
    
    def __init__(self, hass: HomeAssistant):
        """Initialize tent sensor proxy."""
        self.hass = hass
        self._tent_sensors: Dict[str, Dict[str, str]] = {}  # tent_id -> sensor_type -> entity_id
        self._cached_values: Dict[str, Dict[str, Any]] = {}  # tent_id -> sensor_type -> value
        self._last_updates: Dict[str, datetime] = {}  # tent_id -> last_update
        
    def register_tent_sensors(self, tent_id: str, sensors: Dict[str, str]) -> None:
        """Register sensors for a tent."""
        self._tent_sensors[tent_id] = sensors.copy()
        self._cached_values[tent_id] = {}
        self._last_updates[tent_id] = datetime.now()
        
        # Initial cache population
        self._update_tent_cache(tent_id)
    
    def unregister_tent(self, tent_id: str) -> None:
        """Unregister a tent and clean up its data."""
        self._tent_sensors.pop(tent_id, None)
        self._cached_values.pop(tent_id, None)
        self._last_updates.pop(tent_id, None)
    
    def get_tent_sensor_value(self, tent_id: str, sensor_type: str) -> Optional[Any]:
        """Get current value for a tent sensor."""
        if tent_id not in self._tent_sensors:
            return None
        
        sensor_entity = self._tent_sensors[tent_id].get(sensor_type)
        if not sensor_entity:
            return None
        
        # Check cache first
        cached_value = self._cached_values.get(tent_id, {}).get(sensor_type)
        if cached_value is not None:
            return cached_value
        
        # Get from state registry
        state = self.hass.states.get(sensor_entity)
        if state and state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            try:
                value = float(state.state)
                # Update cache
                if tent_id not in self._cached_values:
                    self._cached_values[tent_id] = {}
                self._cached_values[tent_id][sensor_type] = value
                return value
            except (ValueError, TypeError):
                pass
        
        return None
    
    def get_tent_sensor_entity(self, tent_id: str, sensor_type: str) -> Optional[str]:
        """Get the entity ID for a tent sensor."""
        return self._tent_sensors.get(tent_id, {}).get(sensor_type)
    
    def _update_tent_cache(self, tent_id: str) -> None:
        """Update cached values for a tent."""
        if tent_id not in self._tent_sensors:
            return
        
        tent_cache = {}
        for sensor_type, entity_id in self._tent_sensors[tent_id].items():
            state = self.hass.states.get(entity_id)
            if state and state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                try:
                    tent_cache[sensor_type] = float(state.state)
                except (ValueError, TypeError):
                    pass
        
        self._cached_values[tent_id] = tent_cache
        self._last_updates[tent_id] = datetime.now()
    
    def update_tent_sensor(self, tent_id: str, sensor_type: str, entity_id: Optional[str]) -> None:
        """Update a specific sensor for a tent."""
        if tent_id not in self._tent_sensors:
            self._tent_sensors[tent_id] = {}
            self._cached_values[tent_id] = {}
        
        if entity_id:
            self._tent_sensors[tent_id][sensor_type] = entity_id
        else:
            self._tent_sensors[tent_id].pop(sensor_type, None)
            self._cached_values[tent_id].pop(sensor_type, None)
        
        self._last_updates[tent_id] = datetime.now()
    
    def get_tent_info(self, tent_id: str) -> Dict[str, Any]:
        """Get comprehensive tent sensor information."""
        if tent_id not in self._tent_sensors:
            return {}
        
        return {
            "sensors": self._tent_sensors[tent_id].copy(),
            "cached_values": self._cached_values.get(tent_id, {}).copy(),
            "last_updated": self._last_updates.get(tent_id),
            "sensor_count": len(self._tent_sensors[tent_id]),
        }


# Global tent sensor proxy instance
_tent_proxy: Optional[TentSensorProxy] = None

def get_tent_sensor_proxy(hass: HomeAssistant) -> TentSensorProxy:
    """Get or create the global tent sensor proxy."""
    global _tent_proxy
    if _tent_proxy is None:
        _tent_proxy = TentSensorProxy(hass)
    return _tent_proxy