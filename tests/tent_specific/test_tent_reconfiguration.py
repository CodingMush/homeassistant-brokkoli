"""Tests for tent reconfiguration functionality."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_NAME

from custom_components.plant.config_flow import OptionsFlowHandler
from custom_components.plant.tent import Tent
from custom_components.plant.const import (
    DOMAIN,
    DEVICE_TYPE_TENT,
    FLOW_PLANT_INFO,
    FLOW_SENSOR_ILLUMINANCE,
    FLOW_SENSOR_HUMIDITY,
    FLOW_SENSOR_CO2,
    FLOW_SENSOR_POWER_CONSUMPTION,
    FLOW_SENSOR_PH,
)


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = Mock(spec=HomeAssistant)
    hass.states = Mock()
    hass.config_entries = Mock()
    return hass


@pytest.fixture
def tent_config_entry():
    """Create a mock config entry for a tent."""
    entry = Mock(spec=ConfigEntry)
    entry.data = {
        FLOW_PLANT_INFO: {
            ATTR_NAME: "Test Tent",
            "tent_id": "tent_123",
            "device_type": DEVICE_TYPE_TENT,
            FLOW_SENSOR_ILLUMINANCE: "sensor.illuminance_1",
            FLOW_SENSOR_HUMIDITY: "sensor.humidity_1",
        }
    }
    entry.entry_id = "test_entry_id"
    return entry


@pytest.fixture
def tent_entity(mock_hass, tent_config_entry):
    """Create a tent entity."""
    tent = Tent(mock_hass, tent_config_entry)
    tent.device_type = DEVICE_TYPE_TENT
    tent.name = "Test Tent"
    return tent


@pytest.fixture
def options_flow_handler(mock_hass, tent_config_entry, tent_entity):
    """Create an options flow handler for tent."""
    handler = OptionsFlowHandler(tent_config_entry)
    handler.hass = mock_hass
    handler.entry = tent_config_entry
    handler.plant = tent_entity
    return handler


@pytest.mark.asyncio
async def test_tent_options_flow_init(options_flow_handler):
    """Test tent options flow initialization."""
    # Mock the plant to be a tent
    options_flow_handler.plant.device_type = DEVICE_TYPE_TENT
    
    # Call async_step_init
    result = await options_flow_handler.async_step_init()
    
    # Check that form is returned
    assert result["type"] == "form"
    assert result["step_id"] == "init"
    
    # Check that tent-specific fields are present in schema
    schema_keys = list(result["data_schema"].schema.keys())
    field_names = [key.schema for key in schema_keys if hasattr(key, 'schema')]
    
    # Should include name field
    assert any(ATTR_NAME in str(key) for key in schema_keys)


@pytest.mark.asyncio
async def test_tent_sensor_update(options_flow_handler, mock_hass):
    """Test updating tent sensors."""
    # Mock states for sensor validation
    mock_hass.states.get.side_effect = lambda entity_id: Mock(state="available") if entity_id else None
    
    user_input = {
        FLOW_SENSOR_ILLUMINANCE: "sensor.new_illuminance",
        FLOW_SENSOR_HUMIDITY: "sensor.new_humidity",
    }
    
    # Mock the plant to be a tent
    options_flow_handler.plant.device_type = DEVICE_TYPE_TENT
    options_flow_handler.plant.name = "Test Tent"
    options_flow_handler.plant.set_camera = Mock()
    options_flow_handler.plant.async_write_ha_state = Mock()
    
    # Mock config entry update
    mock_hass.config_entries.async_update_entry = Mock()
    
    # Call the handler with user input
    result = await options_flow_handler.async_step_init(user_input)
    
    # Check that entry was created
    assert result["type"] == "create_entry"
    
    # Verify config was updated
    mock_hass.config_entries.async_update_entry.assert_called_once()


@pytest.mark.asyncio
async def test_tent_camera_assignment(options_flow_handler, mock_hass):
    """Test assigning camera to tent."""
    # Mock camera entity state
    camera_state = Mock(state="idle")
    mock_hass.states.get.side_effect = lambda entity_id: camera_state if entity_id == "camera.test_cam" else Mock(state="available")
    
    user_input = {
        "camera_entity_id": "camera.test_cam",
    }
    
    # Mock the plant to be a tent
    options_flow_handler.plant.device_type = DEVICE_TYPE_TENT
    options_flow_handler.plant.name = "Test Tent"
    options_flow_handler.plant.set_camera = Mock()
    options_flow_handler.plant.async_write_ha_state = Mock()
    
    # Mock config entry update
    mock_hass.config_entries.async_update_entry = Mock()
    
    # Call the handler
    result = await options_flow_handler.async_step_init(user_input)
    
    # Check that camera was set
    options_flow_handler.plant.set_camera.assert_called_once_with("camera.test_cam")
    
    # Check that entry was created
    assert result["type"] == "create_entry"


@pytest.mark.asyncio
async def test_tent_area_assignment(options_flow_handler, mock_hass):
    """Test assigning tent to area."""
    # Mock area registry
    mock_area_registry = Mock()
    mock_area = Mock()
    mock_area_registry.async_get_area.return_value = mock_area
    
    # Mock device registry
    mock_device_registry = Mock()
    mock_device_registry.async_update_device = Mock()
    
    with patch('custom_components.plant.config_flow.ar.async_get', return_value=mock_area_registry), \
         patch('custom_components.plant.config_flow.dr.async_get', return_value=mock_device_registry):
        
        user_input = {
            "area_id": "living_room",
        }
        
        # Mock the plant to be a tent
        options_flow_handler.plant.device_type = DEVICE_TYPE_TENT
        options_flow_handler.plant.name = "Test Tent"
        options_flow_handler.plant.device_id = "device_123"
        options_flow_handler.plant.set_camera = Mock()
        options_flow_handler.plant.async_write_ha_state = Mock()
        
        # Mock config entry update
        mock_hass.config_entries.async_update_entry = Mock()
        
        # Call the handler
        result = await options_flow_handler.async_step_init(user_input)
        
        # Check that device was updated
        mock_device_registry.async_update_device.assert_called_once_with(
            "device_123",
            area_id="living_room"
        )
        
        # Check that entry was created
        assert result["type"] == "create_entry"


@pytest.mark.asyncio
async def test_tent_validation_errors(options_flow_handler, mock_hass):
    """Test validation errors for invalid entities."""
    # Mock states to return None (entity not found)
    mock_hass.states.get.return_value = None
    
    user_input = {
        FLOW_SENSOR_ILLUMINANCE: "sensor.nonexistent",
        "camera_entity_id": "camera.nonexistent",
    }
    
    # Mock the plant to be a tent
    options_flow_handler.plant.device_type = DEVICE_TYPE_TENT
    options_flow_handler.plant.name = "Test Tent"
    
    # Call the handler
    result = await options_flow_handler.async_step_init(user_input)
    
    # Check that form is returned with errors
    assert result["type"] == "form"
    assert "errors" in result
    assert FLOW_SENSOR_ILLUMINANCE in result["errors"]
    assert "camera_entity_id" in result["errors"]


@pytest.mark.asyncio
async def test_tent_name_update(options_flow_handler, mock_hass):
    """Test updating tent name."""
    user_input = {
        ATTR_NAME: "Updated Tent Name",
    }
    
    # Mock the plant to be a tent
    options_flow_handler.plant.device_type = DEVICE_TYPE_TENT
    options_flow_handler.plant.name = "Test Tent"
    options_flow_handler.plant.set_camera = Mock()
    options_flow_handler.plant.async_write_ha_state = Mock()
    
    # Mock config entry update
    mock_hass.config_entries.async_update_entry = Mock()
    
    # Call the handler
    result = await options_flow_handler.async_step_init(user_input)
    
    # Check that entry was created
    assert result["type"] == "create_entry"
    
    # Verify config was updated with new name
    mock_hass.config_entries.async_update_entry.assert_called_once()
    call_args = mock_hass.config_entries.async_update_entry.call_args
    updated_data = call_args[1]["data"]
    assert updated_data[FLOW_PLANT_INFO][ATTR_NAME] == "Updated Tent Name"
    assert updated_data[FLOW_PLANT_INFO]["name"] == "Updated Tent Name"


@pytest.mark.asyncio
async def test_tent_sensor_removal(options_flow_handler, mock_hass):
    """Test removing sensors from tent."""
    # Start with some sensors configured
    options_flow_handler.entry.data[FLOW_PLANT_INFO][FLOW_SENSOR_ILLUMINANCE] = "sensor.old_illuminance"
    
    user_input = {
        # Don't provide FLOW_SENSOR_ILLUMINANCE - this should remove it
    }
    
    # Mock the plant to be a tent
    options_flow_handler.plant.device_type = DEVICE_TYPE_TENT
    options_flow_handler.plant.name = "Test Tent"
    options_flow_handler.plant.set_camera = Mock()
    options_flow_handler.plant.async_write_ha_state = Mock()
    
    # Mock config entry update
    mock_hass.config_entries.async_update_entry = Mock()
    
    # Call the handler
    result = await options_flow_handler.async_step_init(user_input)
    
    # Check that entry was created
    assert result["type"] == "create_entry"
    
    # Verify sensor was removed from config
    mock_hass.config_entries.async_update_entry.assert_called_once()
    call_args = mock_hass.config_entries.async_update_entry.call_args
    updated_data = call_args[1]["data"]
    assert FLOW_SENSOR_ILLUMINANCE not in updated_data[FLOW_PLANT_INFO]