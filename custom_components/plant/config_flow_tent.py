"""Config flow for Tent integration."""

import logging
from typing import Any, Dict, List, Optional

import voluptuous as vol
from homeassistant.helpers import selector
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.area_registry import async_get as async_get_area_registry

from homeassistant import config_entries, data_entry_flow
from homeassistant.const import ATTR_NAME, ATTR_DEVICE_CLASS, ATTR_DOMAIN
from homeassistant.core import HomeAssistant, callback

from .const import (
    DOMAIN,
    DOMAIN_SENSOR,
    ATTR_ENTITY,
    FLOW_TENT_NAME,
    FLOW_TENT_AREA,
    FLOW_TENT_DESCRIPTION,
    FLOW_TENT_SENSORS,
    FLOW_SENSOR_TEMPERATURE,
    FLOW_SENSOR_HUMIDITY,
    FLOW_SENSOR_CO2,
    FLOW_SENSOR_ILLUMINANCE,
    FLOW_SENSOR_CONDUCTIVITY,
    FLOW_SENSOR_PH,
)
from .tent import TentDevice

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class TentConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tent with enhanced sensor management."""

    VERSION = 1

    def __init__(self):
        """Initialize flow."""
        self.tent_info = {}
        self.tent_sensors = {}
        self.available_sensors = {}
        self.error = None

    async def async_step_user(self, user_input=None):
        """Handle the initial step - basic tent information."""
        errors = {}

        if user_input is not None:
            # Validate tent name uniqueness
            if await self._tent_name_exists(user_input[FLOW_TENT_NAME]):
                errors["base"] = "name_exists"
            else:
                self.tent_info[ATTR_NAME] = user_input[FLOW_TENT_NAME]
                if FLOW_TENT_AREA in user_input:
                    self.tent_info["area_id"] = user_input[FLOW_TENT_AREA]
                if FLOW_TENT_DESCRIPTION in user_input:
                    self.tent_info["description"] = user_input[FLOW_TENT_DESCRIPTION]
                
                # Discover available sensors for next step
                self.available_sensors = await self._discover_sensors()
                return await self.async_step_sensors()

        # Get available areas for selection
        area_registry = async_get_area_registry(self.hass)
        area_options = [(area.id, area.name) for area in area_registry.areas.values()]

        data_schema = {
            vol.Required(FLOW_TENT_NAME): str,
            vol.Optional(FLOW_TENT_AREA): selector({
                "select": {
                    "options": area_options,
                    "mode": "dropdown"
                }
            }) if area_options else str,
            vol.Optional(FLOW_TENT_DESCRIPTION): str,
        }

        return self.async_show_form(
            step_id="user", 
            data_schema=vol.Schema(data_schema), 
            errors=errors,
            description_placeholders={
                "name": "Tent configuration"
            }
        )

    async def async_step_sensors(self, user_input=None):
        """Handle sensor assignment step."""
        errors = {}

        if user_input is not None:
            # Validate sensor assignments
            validation_result = await self._validate_sensor_assignments(user_input)
            if validation_result["valid"]:
                # Store sensor assignments
                for sensor_type in ["temperature", "humidity", "co2", "illuminance", "conductivity", "ph"]:
                    sensor_key = f"{sensor_type}_sensor"
                    if sensor_key in user_input and user_input[sensor_key]:
                        self.tent_sensors[sensor_type] = user_input[sensor_key]
                
                # Create tent entry
                return await self._create_tent_entry()
            else:
                errors.update(validation_result["errors"])

        # Build sensor selection schema
        data_schema = await self._build_sensor_schema()

        return self.async_show_form(
            step_id="sensors",
            data_schema=vol.Schema(data_schema),
            errors=errors,
            description_placeholders={
                "tent_name": self.tent_info[ATTR_NAME],
                "sensor_count": len(self.available_sensors)
            }
        )

    async def _tent_name_exists(self, name: str) -> bool:
        """Check if tent name already exists."""
        existing_entries = self._async_current_entries()
        return any(
            entry.data.get(ATTR_NAME, "").lower() == name.lower() 
            for entry in existing_entries
            if entry.data.get("is_tent", False)
        )

    async def _discover_sensors(self) -> Dict[str, List[Dict[str, str]]]:
        """Discover available sensor entities by device class."""
        entity_registry = async_get_entity_registry(self.hass)
        sensors_by_type = {
            "temperature": [],
            "humidity": [],
            "co2": [],
            "illuminance": [],
            "conductivity": [],
            "ph": []
        }

        # Map device classes to sensor types
        device_class_mapping = {
            SensorDeviceClass.TEMPERATURE: "temperature",
            SensorDeviceClass.HUMIDITY: "humidity",
            SensorDeviceClass.CO2: "co2",
            SensorDeviceClass.ILLUMINANCE: "illuminance",
            "conductivity": "conductivity",  # Custom device class
            SensorDeviceClass.PH: "ph",
            "ph": "ph",  # Alternative device class
        }

        # Scan entity registry for sensor entities
        for entity in entity_registry.entities.values():
            if entity.domain == DOMAIN_SENSOR and entity.device_class:
                sensor_type = device_class_mapping.get(entity.device_class)
                if sensor_type:
                    # Get entity state to check availability
                    state = self.hass.states.get(entity.entity_id)
                    if state:
                        sensors_by_type[sensor_type].append({
                            "entity_id": entity.entity_id,
                            "name": state.attributes.get("friendly_name", entity.entity_id),
                            "device_class": entity.device_class,
                            "available": state.state not in ["unavailable", "unknown"]
                        })

        # Also check state registry for entities not in entity registry
        for entity_id, state in self.hass.states.async_all().items():
            if entity_id.startswith("sensor.") and entity_id not in [e.entity_id for e in entity_registry.entities.values()]:
                device_class = state.attributes.get("device_class")
                sensor_type = device_class_mapping.get(device_class) if device_class else None
                if sensor_type:
                    sensors_by_type[sensor_type].append({
                        "entity_id": entity_id,
                        "name": state.attributes.get("friendly_name", entity_id),
                        "device_class": device_class,
                        "available": state.state not in ["unavailable", "unknown"]
                    })

        return sensors_by_type

    async def _build_sensor_schema(self) -> Dict:
        """Build the sensor selection schema."""
        schema = {}

        # Temperature sensor selection
        if self.available_sensors.get("temperature"):
            temp_options = [(s["entity_id"], s["name"]) for s in self.available_sensors["temperature"]]
            schema[vol.Optional(FLOW_SENSOR_TEMPERATURE)] = selector({
                "entity": {
                    "filter": {
                        "domain": DOMAIN_SENSOR,
                        "device_class": SensorDeviceClass.TEMPERATURE
                    }
                }
            })

        # Humidity sensor selection
        if self.available_sensors.get("humidity"):
            schema[vol.Optional(FLOW_SENSOR_HUMIDITY)] = selector({
                "entity": {
                    "filter": {
                        "domain": DOMAIN_SENSOR,
                        "device_class": SensorDeviceClass.HUMIDITY
                    }
                }
            })

        # CO2 sensor selection
        if self.available_sensors.get("co2"):
            schema[vol.Optional(FLOW_SENSOR_CO2)] = selector({
                "entity": {
                    "filter": {
                        "domain": DOMAIN_SENSOR,
                        "device_class": SensorDeviceClass.CO2
                    }
                }
            })

        # Illuminance sensor selection
        if self.available_sensors.get("illuminance"):
            schema[vol.Optional(FLOW_SENSOR_ILLUMINANCE)] = selector({
                "entity": {
                    "filter": {
                        "domain": DOMAIN_SENSOR,
                        "device_class": SensorDeviceClass.ILLUMINANCE
                    }
                }
            })

        # Conductivity sensor selection
        if self.available_sensors.get("conductivity"):
            schema[vol.Optional(FLOW_SENSOR_CONDUCTIVITY)] = selector({
                "entity": {
                    "filter": {
                        "domain": DOMAIN_SENSOR
                    }
                }
            })

        # pH sensor selection
        if self.available_sensors.get("ph"):
            schema[vol.Optional(FLOW_SENSOR_PH)] = selector({
                "entity": {
                    "filter": {
                        "domain": DOMAIN_SENSOR,
                        "device_class": SensorDeviceClass.PH
                    }
                }
            })

        return schema

    async def _validate_sensor_assignments(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate sensor entity assignments."""
        errors = {}
        
        # Check each sensor assignment
        for sensor_type in ["temperature", "humidity", "co2", "illuminance", "conductivity", "ph"]:
            sensor_key = f"{sensor_type}_sensor"
            if sensor_key in user_input and user_input[sensor_key]:
                entity_id = user_input[sensor_key]
                
                # Check if entity exists
                state = self.hass.states.get(entity_id)
                if not state:
                    errors[sensor_key] = "entity_not_found"
                    continue
                
                # Check if entity is available
                if state.state in ["unavailable", "unknown"]:
                    errors[sensor_key] = "entity_unavailable"
                    continue
                
                # Check if entity is already assigned to another tent
                if await self._sensor_already_assigned(entity_id):
                    errors[sensor_key] = "sensor_already_assigned"

        return {"valid": len(errors) == 0, "errors": errors}

    async def _sensor_already_assigned(self, entity_id: str) -> bool:
        """Check if sensor is already assigned to another tent."""
        # Check existing tent entries
        for entry in self._async_current_entries():
            if entry.data.get("is_tent", False):
                tent_sensors = entry.data.get(FLOW_TENT_SENSORS, {})
                if entity_id in tent_sensors.values():
                    return True
        return False

    async def _create_tent_entry(self) -> Dict[str, Any]:
        """Create the tent configuration entry."""
        tent_data = {
            "is_tent": True,
            ATTR_NAME: self.tent_info[ATTR_NAME],
            "area_id": self.tent_info.get("area_id"),
            "description": self.tent_info.get("description", ""),
            FLOW_TENT_SENSORS: self.tent_sensors,
            "created_at": self.hass.bus.loop.time(),
        }

        return self.async_create_entry(
            title=f"Tent: {self.tent_info[ATTR_NAME]}",
            data=tent_data,
        )
