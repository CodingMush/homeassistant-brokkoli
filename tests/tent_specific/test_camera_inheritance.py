"""Tests for camera inheritance from tent to plant."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from custom_components.plant import PlantDevice
from custom_components.plant.tent import Tent
from custom_components.plant.const import (
    DOMAIN,
    DEVICE_TYPE_PLANT,
    DEVICE_TYPE_TENT,
    FLOW_PLANT_INFO,
)


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = Mock(spec=HomeAssistant)
    hass.states = Mock()
    hass.config_entries = Mock()
    hass.async_add_executor_job = AsyncMock()
    return hass


@pytest.fixture
def tent_config_entry():
    """Create a mock config entry for a tent."""
    entry = Mock(spec=ConfigEntry)
    entry.data = {
        FLOW_PLANT_INFO: {
            "name": "Test Tent",
            "tent_id": "tent_123",
            "device_type": DEVICE_TYPE_TENT,
            "camera_entity_id": "camera.tent_camera",
        }
    }
    entry.entry_id = "tent_entry_id"
    return entry


@pytest.fixture
def plant_config_entry():
    """Create a mock config entry for a plant."""
    entry = Mock(spec=ConfigEntry)
    entry.data = {
        FLOW_PLANT_INFO: {
            "name": "Test Plant",
            "plant_id": "plant_123",
            "device_type": DEVICE_TYPE_PLANT,
        }
    }
    entry.entry_id = "plant_entry_id"
    return entry


@pytest.fixture
def tent_entity(mock_hass, tent_config_entry):
    """Create a tent entity with camera."""
    tent = Tent(mock_hass, tent_config_entry)
    tent.set_camera("camera.tent_camera")
    return tent


@pytest.fixture
def plant_entity(mock_hass, plant_config_entry):
    """Create a plant entity."""
    plant = PlantDevice(mock_hass, plant_config_entry)
    plant.camera = None
    return plant


@pytest.mark.asyncio
async def test_camera_inheritance_from_tent(plant_entity, tent_entity, mock_hass):
    """Test that plant inherits camera from assigned tent."""
    # Mock config entry update
    mock_hass.config_entries.async_update_entry = Mock()
    
    # Assign tent to plant
    plant_entity.assign_tent(tent_entity)
    
    # Verify that assign_camera was called during tent assignment
    assert hasattr(plant_entity, '_assigned_tent')
    assert plant_entity._assigned_tent == tent_entity
    
    # Verify that config was updated with camera entity ID
    mock_hass.config_entries.async_update_entry.assert_called()


@pytest.mark.asyncio
async def test_inherit_tent_camera_direct_call(plant_entity, tent_entity, mock_hass):
    """Test direct call to inherit_tent_camera method."""
    # Mock config entry update
    mock_hass.config_entries.async_update_entry = Mock()
    
    # Mock PlantCamera creation
    with patch('custom_components.plant.PlantCamera') as mock_camera_class:
        mock_camera_instance = Mock()
        mock_camera_class.return_value = mock_camera_instance
        
        # Call inherit_tent_camera directly
        plant_entity.inherit_tent_camera(tent_entity)
        
        # Verify that camera was assigned
        mock_hass.config_entries.async_update_entry.assert_called()
        
        # Verify that PlantCamera was created if needed
        if plant_entity.camera is None:
            mock_camera_class.assert_called_once()


@pytest.mark.asyncio
async def test_inherit_tent_camera_no_camera_configured(plant_entity, mock_hass):
    """Test inherit_tent_camera when tent has no camera."""
    # Create tent without camera
    tent_without_camera = Mock()
    tent_without_camera.get_camera.return_value = None
    tent_without_camera.name = "Tent Without Camera"
    
    # Mock config entry update
    mock_hass.config_entries.async_update_entry = Mock()
    
    # Call inherit_tent_camera
    plant_entity.inherit_tent_camera(tent_without_camera)
    
    # Verify that no config update was made
    mock_hass.config_entries.async_update_entry.assert_not_called()


@pytest.mark.asyncio
async def test_inherit_tent_camera_invalid_tent(plant_entity, mock_hass):
    """Test inherit_tent_camera with invalid tent object."""
    # Test with None tent
    plant_entity.inherit_tent_camera(None)
    
    # Test with tent object without get_camera method
    invalid_tent = Mock()
    del invalid_tent.get_camera  # Remove the method
    plant_entity.inherit_tent_camera(invalid_tent)
    
    # Should not raise exceptions
    assert True


@pytest.mark.asyncio
async def test_assign_tent_complete_workflow(plant_entity, tent_entity, mock_hass):
    """Test complete tent assignment workflow with camera inheritance."""
    # Mock tent sensors
    tent_entity.get_sensors = Mock(return_value=["sensor.temp1", "sensor.humidity1"])
    
    # Mock plant methods
    plant_entity.replace_sensors = Mock()
    
    # Mock config entry update
    mock_hass.config_entries.async_update_entry = Mock()
    
    # Mock PlantCamera creation
    with patch('custom_components.plant.PlantCamera') as mock_camera_class:
        mock_camera_instance = Mock()
        mock_camera_class.return_value = mock_camera_instance
        
        # Assign tent to plant
        plant_entity.assign_tent(tent_entity)
        
        # Verify sensors were replaced
        plant_entity.replace_sensors.assert_called_once_with(["sensor.temp1", "sensor.humidity1"])
        
        # Verify tent was assigned
        assert plant_entity._assigned_tent == tent_entity
        assert plant_entity._tent_id == tent_entity.tent_id
        
        # Verify camera was inherited
        mock_hass.config_entries.async_update_entry.assert_called()


@pytest.mark.asyncio
async def test_change_tent_camera_inheritance(plant_entity, mock_hass):
    """Test changing from one tent to another with different cameras."""
    # Create two tents with different cameras
    tent1 = Mock()
    tent1.tent_id = "tent_001"
    tent1.name = "Tent 1"
    tent1.get_camera.return_value = "camera.tent1_camera"
    tent1.get_sensors.return_value = ["sensor.temp1"]
    
    tent2 = Mock()
    tent2.tent_id = "tent_002"
    tent2.name = "Tent 2"
    tent2.get_camera.return_value = "camera.tent2_camera"
    tent2.get_sensors.return_value = ["sensor.temp2"]
    
    # Mock plant methods
    plant_entity.replace_sensors = Mock()
    
    # Mock config entry update
    mock_hass.config_entries.async_update_entry = Mock()
    
    # Mock PlantCamera creation
    with patch('custom_components.plant.PlantCamera') as mock_camera_class:
        mock_camera_instance = Mock()
        mock_camera_class.return_value = mock_camera_instance
        
        # Assign first tent
        plant_entity.assign_tent(tent1)
        
        # Verify first assignment
        assert plant_entity._assigned_tent == tent1
        assert plant_entity._tent_id == "tent_001"
        
        # Change to second tent
        plant_entity.change_tent(tent2)
        
        # Verify second assignment
        assert plant_entity._assigned_tent == tent2
        assert plant_entity._tent_id == "tent_002"
        
        # Verify sensors were replaced twice
        assert plant_entity.replace_sensors.call_count == 2
        plant_entity.replace_sensors.assert_any_call(["sensor.temp1"])
        plant_entity.replace_sensors.assert_any_call(["sensor.temp2"])


@pytest.mark.asyncio
async def test_get_assigned_tent_and_tent_id(plant_entity, tent_entity):
    """Test getting assigned tent and tent ID."""
    # Initially no tent assigned
    assert plant_entity.get_assigned_tent() is None
    assert plant_entity.get_tent_id() is None
    
    # Assign tent
    plant_entity.assign_tent(tent_entity)
    
    # Verify tent assignment
    assert plant_entity.get_assigned_tent() == tent_entity
    assert plant_entity.get_tent_id() == tent_entity.tent_id
    
    # Clear tent assignment
    plant_entity.assign_tent(None)
    
    # Verify tent cleared
    assert plant_entity.get_assigned_tent() is None
    assert plant_entity.get_tent_id() is None


@pytest.mark.asyncio
async def test_tent_assign_to_plant_method(tent_entity, mock_hass):
    """Test tent's assign_to_plant method."""
    # Create mock plant
    mock_plant = Mock()
    mock_plant.replace_sensors = Mock()
    mock_plant.assign_camera = Mock()
    
    # Mock tent methods
    tent_entity.get_sensors = Mock(return_value=["sensor.temp1", "sensor.humidity1"])
    tent_entity.get_camera = Mock(return_value="camera.tent_camera")
    
    # Call assign_to_plant
    tent_entity.assign_to_plant(mock_plant)
    
    # Verify sensors were assigned
    mock_plant.replace_sensors.assert_called_once_with(["sensor.temp1", "sensor.humidity1"])
    
    # Verify camera was assigned
    mock_plant.assign_camera.assert_called_once_with("camera.tent_camera")


@pytest.mark.asyncio
async def test_tent_assign_to_plant_no_camera(tent_entity, mock_hass):
    """Test tent's assign_to_plant method when no camera is configured."""
    # Create mock plant
    mock_plant = Mock()
    mock_plant.replace_sensors = Mock()
    mock_plant.assign_camera = Mock()
    
    # Mock tent methods - no camera
    tent_entity.get_sensors = Mock(return_value=["sensor.temp1"])
    tent_entity.set_camera(None)  # Remove camera
    
    # Call assign_to_plant
    tent_entity.assign_to_plant(mock_plant)
    
    # Verify sensors were assigned
    mock_plant.replace_sensors.assert_called_once_with(["sensor.temp1"])
    
    # Verify camera assignment was not called
    mock_plant.assign_camera.assert_not_called()


@pytest.mark.asyncio
async def test_assign_camera_error_handling(plant_entity, mock_hass):
    """Test error handling in assign_camera method."""
    # Mock config entry update to raise exception
    mock_hass.config_entries.async_update_entry = Mock(side_effect=Exception("Test error"))
    
    # Mock logging
    with patch('custom_components.plant._LOGGER') as mock_logger:
        # Call assign_camera
        plant_entity.assign_camera("camera.test_camera")
        
        # Verify error was logged
        mock_logger.error.assert_called_once()