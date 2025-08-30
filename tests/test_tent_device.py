"""Unit tests for tent device management."""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OK, STATE_UNAVAILABLE
import homeassistant.helpers.entity_registry as er

from custom_components.plant import PlantDevice, DEVICE_TYPE_TENT, DEVICE_TYPE_PLANT
from custom_components.plant.const import (
    ATTR_ASSIGNED_PLANTS,
    ATTR_SHARED_THRESHOLDS,
    FLOW_PLANT_INFO,
    CONF_SENSORS,
    SENSOR_TEMPERATURE,
    SENSOR_HUMIDITY,
    SENSOR_CO2,
    SENSOR_LIGHT_HOURS,
    SENSOR_POWER_CONSUMPTION,
)


class TestTentDevice:
    """Test tent device functionality."""

    @pytest.fixture
    def mock_hass(self):
        """Create mock Home Assistant instance."""
        hass = Mock(spec=HomeAssistant)
        hass.config = Mock()
        hass.config.config_dir = "/config"
        hass.states = Mock()
        hass.states.get = Mock(return_value=None)
        hass.data = {}
        return hass

    @pytest.fixture
    def mock_config_entry(self):
        """Create mock config entry for tent."""
        entry = Mock(spec=ConfigEntry)
        entry.entry_id = "tent_test_entry"
        entry.data = {
            FLOW_PLANT_INFO: {
                "name": "Test Tent",
                "device_type": DEVICE_TYPE_TENT,
                CONF_SENSORS: {
                    SENSOR_TEMPERATURE: "sensor.tent_temperature",
                    SENSOR_HUMIDITY: "sensor.tent_humidity", 
                    SENSOR_CO2: "sensor.tent_co2",
                    SENSOR_LIGHT_HOURS: "sensor.tent_light_hours",
                    SENSOR_POWER_CONSUMPTION: "sensor.tent_power",
                }
            }
        }
        entry.options = {}
        return entry

    @pytest.fixture
    def tent_device(self, mock_hass, mock_config_entry):
        """Create tent device instance."""
        return PlantDevice(mock_hass, mock_config_entry)

    def test_tent_device_initialization(self, tent_device):
        """Test tent device initializes correctly."""
        assert tent_device.device_type == DEVICE_TYPE_TENT
        assert tent_device.name == "Test Tent"
        assert hasattr(tent_device, '_assigned_plants')
        assert tent_device._assigned_plants == []

    def test_register_plant(self, tent_device, mock_hass):
        """Test registering a plant to tent."""
        plant_entity_id = "plant.test_plant"
        
        # Mock plant entity
        mock_plant_state = Mock()
        mock_plant_state.entity_id = plant_entity_id
        mock_hass.states.get.return_value = mock_plant_state
        
        # Register plant
        tent_device.register_plant(plant_entity_id)
        
        # Verify plant was added
        assert plant_entity_id in tent_device._assigned_plants
        assert tent_device.extra_state_attributes[ATTR_ASSIGNED_PLANTS] == [plant_entity_id]

    def test_unregister_plant(self, tent_device):
        """Test unregistering a plant from tent."""
        plant_entity_id = "plant.test_plant" 
        
        # First register the plant
        tent_device._assigned_plants = [plant_entity_id]
        
        # Then unregister it
        tent_device.unregister_plant(plant_entity_id)
        
        # Verify plant was removed
        assert plant_entity_id not in tent_device._assigned_plants
        assert tent_device.extra_state_attributes[ATTR_ASSIGNED_PLANTS] == []

    def test_tent_device_info_correct(self, tent_device):
        """Test tent device info shows correct manufacturer and model."""
        device_info = tent_device.device_info
        
        assert device_info["manufacturer"] == "Plant Integration"
        assert device_info["model"] == "Tent"
        assert "Tent" in device_info["name"]

    def test_empty_tent_sensor_info(self, tent_device):
        """Test tent with no assigned plants shows empty sensor info."""
        tent_device._assigned_plants = []
        
        attributes = tent_device.extra_state_attributes
        assert attributes["plant_count"] == 0
        assert attributes[ATTR_ASSIGNED_PLANTS] == []
        assert "environmental_sensors" in attributes

    def test_tent_sensor_management(self, tent_device, mock_hass):
        """Test tent sensor management without thresholds."""
        plant_id = "plant.test_plant"
        
        # Register plant
        tent_device._assigned_plants = [plant_id]
        
        # Verify tent shows sensor info
        attributes = tent_device.extra_state_attributes
        assert attributes["plant_count"] == 1
        assert attributes[ATTR_ASSIGNED_PLANTS] == [plant_id]
        assert "environmental_sensors" in attributes