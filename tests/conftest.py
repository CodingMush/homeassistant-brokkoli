"""Test fixtures for plant integration."""
import pytest
import asyncio
from unittest.mock import Mock, MagicMock, AsyncMock
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from custom_components.plant.const import (
    DOMAIN,
    FLOW_PLANT_INFO,
    FLOW_PLANT_LIMITS,
    DEVICE_TYPE_PLANT,
    ATTR_PLANT,
    ATTR_STRAIN,
    CONF_MAX_TEMPERATURE,
    CONF_MIN_TEMPERATURE,
    CONF_MAX_MOISTURE,
    CONF_MIN_MOISTURE,
    CONF_MAX_CONDUCTIVITY,
    CONF_MIN_CONDUCTIVITY,
    CONF_MAX_ILLUMINANCE,
    CONF_MIN_ILLUMINANCE,
    CONF_MAX_HUMIDITY,
    CONF_MIN_HUMIDITY,
    CONF_MAX_CO2,
    CONF_MIN_CO2,
    CONF_MAX_DLI,
    CONF_MIN_DLI,
    DEFAULT_MAX_TEMPERATURE,
    DEFAULT_MIN_TEMPERATURE,
    DEFAULT_MAX_MOISTURE,
    DEFAULT_MIN_MOISTURE,
    DEFAULT_MAX_CONDUCTIVITY,
    DEFAULT_MIN_CONDUCTIVITY,
    DEFAULT_MAX_ILLUMINANCE,
    DEFAULT_MIN_ILLUMINANCE,
    DEFAULT_MAX_HUMIDITY,
    DEFAULT_MIN_HUMIDITY,
    DEFAULT_MAX_CO2,
    DEFAULT_MIN_CO2,
    DEFAULT_MAX_DLI,
    DEFAULT_MIN_DLI,
)


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = Mock(spec=HomeAssistant)
    hass.data = {}
    
    # Create a more realistic services mock
    hass.services = Mock()
    hass.services._services = {}
    
    # Create a simple async_register function that directly populates the services
    async def async_register(domain, service, service_func, schema=None, supports_response=None):
        if domain not in hass.services._services:
            hass.services._services[domain] = {}
        hass.services._services[domain][service] = Mock()
        hass.services._services[domain][service].job = Mock()
        hass.services._services[domain][service].job.target = service_func
        hass.services._services[domain][service].schema = schema
    
    hass.services.async_register = async_register
    
    hass.config_entries = Mock()
    hass.config_entries.async_entries = Mock(return_value=[])
    hass.config_entries.async_update_entry = AsyncMock()
    hass.config_entries.async_remove = AsyncMock()
    hass.states = Mock()
    hass.states.get = Mock(return_value=None)
    hass.bus = Mock()
    hass.bus.async_listen = Mock()
    hass.config = Mock()
    hass.config.units = Mock()
    hass.config.units.temperature_unit = "°C"
    return hass


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    entry = Mock(spec=ConfigEntry)
    entry.entry_id = "test_entry_id"
    entry.data = {
        FLOW_PLANT_INFO: {
            "name": "Test Plant",
            ATTR_STRAIN: "Test Strain",
            "device_type": DEVICE_TYPE_PLANT,
            FLOW_PLANT_LIMITS: {
                CONF_MAX_TEMPERATURE: DEFAULT_MAX_TEMPERATURE,
                CONF_MIN_TEMPERATURE: DEFAULT_MIN_TEMPERATURE,
                CONF_MAX_MOISTURE: DEFAULT_MAX_MOISTURE,
                CONF_MIN_MOISTURE: DEFAULT_MIN_MOISTURE,
                CONF_MAX_CONDUCTIVITY: DEFAULT_MAX_CONDUCTIVITY,
                CONF_MIN_CONDUCTIVITY: DEFAULT_MIN_CONDUCTIVITY,
                CONF_MAX_ILLUMINANCE: DEFAULT_MAX_ILLUMINANCE,
                CONF_MIN_ILLUMINANCE: DEFAULT_MIN_ILLUMINANCE,
                CONF_MAX_HUMIDITY: DEFAULT_MAX_HUMIDITY,
                CONF_MIN_HUMIDITY: DEFAULT_MIN_HUMIDITY,
                CONF_MAX_CO2: DEFAULT_MAX_CO2,
                CONF_MIN_CO2: DEFAULT_MIN_CO2,
                CONF_MAX_DLI: DEFAULT_MAX_DLI,
                CONF_MIN_DLI: DEFAULT_MIN_DLI,
            }
        }
    }
    entry.options = {}
    return entry


@pytest.fixture
def mock_plant():
    """Create a mock plant entity."""
    plant = Mock()
    plant.device_type = DEVICE_TYPE_PLANT
    plant.entity_id = "plant.test_plant"
    plant.name = "Test Plant"
    plant.unique_id = "test_entry_id"
    return plant


@pytest.fixture
def mock_sensor_state():
    """Create a mock sensor state."""
    state = Mock()
    state.state = "25.5"
    state.attributes = {"unit_of_measurement": "°C"}
    return state