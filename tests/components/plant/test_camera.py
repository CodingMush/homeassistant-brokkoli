"""Tests for the camera platform."""

from datetime import datetime
import os
from unittest.mock import patch, MagicMock

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
import homeassistant.util.dt as dt_util
from homeassistant.components.camera import DOMAIN as CAMERA_DOMAIN
import pytest

from custom_components.plant.camera import PlantCamera
from custom_components.plant.const import DOMAIN


async def test_plant_camera_initialization(hass: HomeAssistant, mock_plant_entity):
    """Test plant camera initialization."""
    # Create a mock config entry
    mock_config_entry = MagicMock()
    mock_config_entry.data = {}
    
    # Initialize the camera
    camera = PlantCamera(hass, mock_plant_entity, mock_config_entry)
    
    # Check that the camera was initialized correctly
    assert camera.name == f"{mock_plant_entity.name} Camera"
    assert camera.unique_id == f"{mock_plant_entity.unique_id}_camera"
    assert camera.is_on is True


async def test_plant_camera_turn_on_off(hass: HomeAssistant, mock_plant_entity):
    """Test turning plant camera on and off."""
    # Create a mock config entry
    mock_config_entry = MagicMock()
    mock_config_entry.data = {}
    
    # Initialize the camera
    camera = PlantCamera(hass, mock_plant_entity, mock_config_entry)
    
    # Test turning off
    camera.turn_off()
    assert camera.is_on is False
    
    # Test turning on
    camera.turn_on()
    assert camera.is_on is True


async def test_plant_camera_take_snapshot(hass: HomeAssistant, mock_plant_entity):
    """Test taking a snapshot with the plant camera."""
    # Create a mock config entry
    mock_config_entry = MagicMock()
    mock_config_entry.data = {}
    
    # Initialize the camera
    camera = PlantCamera(hass, mock_plant_entity, mock_config_entry)
    
    # Mock the hass.async_add_executor_job method
    with patch.object(hass, 'async_add_executor_job') as mock_executor:
        # Mock the open function to avoid actual file operations
        with patch('builtins.open', MagicMock()):
            # Take a snapshot
            filepath = await camera.async_take_snapshot()
            
            # Check that a filepath was returned
            assert filepath is not None
            assert filepath.endswith('.jpg')
            
            # Check that the executor job was called
            mock_executor.assert_called_once()


async def test_plant_camera_image_storage(hass: HomeAssistant, mock_plant_entity):
    """Test plant camera image storage."""
    # Create a mock config entry
    mock_config_entry = MagicMock()
    mock_config_entry.data = {}
    
    # Initialize the camera
    camera = PlantCamera(hass, mock_plant_entity, mock_config_entry)
    
    # Check that the image storage path is set
    assert camera._image_storage_path is not None
    
    # Mock the hass.async_add_executor_job method
    with patch.object(hass, 'async_add_executor_job') as mock_executor:
        # Mock the open function to avoid actual file operations
        with patch('builtins.open', MagicMock()):
            # Take a snapshot
            filepath = await camera.async_take_snapshot()
            
            # Check that the filepath is within the storage path
            assert camera._image_storage_path in filepath


async def test_plant_camera_update_plant_image(hass: HomeAssistant, mock_plant_entity):
    """Test updating plant entity with new image."""
    # Create a mock config entry
    mock_config_entry = MagicMock()
    mock_config_entry.data = {}
    
    # Initialize the camera
    camera = PlantCamera(hass, mock_plant_entity, mock_config_entry)
    
    # Test image path
    test_image_path = "www/images/plants/test_image.jpg"
    
    # Mock the hass.config.path method to return a proper path
    with patch.object(hass.config, 'path', return_value="/config/www/images/plants"):
        await camera._update_plant_image(test_image_path)
        
        # Check that the plant entity was updated with the correct local URL
        expected_url = "/local/images/plants/test_image.jpg"
        assert mock_plant_entity._attr_entity_picture == expected_url


async def test_plant_camera_device_info(hass: HomeAssistant, mock_plant_entity):
    """Test plant camera device information."""
    # Create a mock config entry
    mock_config_entry = MagicMock()
    mock_config_entry.data = {}
    
    # Initialize the camera
    camera = PlantCamera(hass, mock_plant_entity, mock_config_entry)
    
    # Get device info
    device_info = camera.device_info
    
    # Check that device info is correct
    assert device_info["identifiers"] == {(DOMAIN, mock_plant_entity.unique_id)}
    assert device_info["name"] == mock_plant_entity.name
    assert device_info["manufacturer"] == "Home Assistant"
    assert device_info["model"] == "Plant Camera"
    assert device_info["via_device"] == (DOMAIN, mock_plant_entity.unique_id)


async def test_plant_camera_async_camera_image(hass: HomeAssistant, mock_plant_entity):
    """Test async camera image retrieval."""
    # Create a mock config entry
    mock_config_entry = MagicMock()
    mock_config_entry.data = {}
    
    # Initialize the camera
    camera = PlantCamera(hass, mock_plant_entity, mock_config_entry)
    
    # Set a mock image
    mock_image_data = b"test_image_data"
    camera._last_image = mock_image_data
    
    # Get the camera image
    image_data = await camera.async_camera_image()
    
    # Check that the correct image data was returned
    assert image_data == mock_image_data


async def test_plant_camera_error_handling(hass: HomeAssistant, mock_plant_entity):
    """Test plant camera error handling."""
    # Create a mock config entry
    mock_config_entry = MagicMock()
    mock_config_entry.data = {}
    
    # Initialize the camera
    camera = PlantCamera(hass, mock_plant_entity, mock_config_entry)
    
    # Test that errors during snapshot are handled gracefully
    with patch.object(camera, '_generate_placeholder_image', side_effect=Exception("Test error")):
        filepath = await camera.async_take_snapshot()
        assert filepath is None


async def test_plant_camera_fallback_paths(hass: HomeAssistant, mock_plant_entity):
    """Test plant camera fallback paths when default path is not accessible."""
    # Create a mock config entry
    mock_config_entry = MagicMock()
    mock_config_entry.data = {}
    
    # Mock the os.makedirs function to raise PermissionError
    with patch('os.makedirs', side_effect=PermissionError("Permission denied")):
        # Initialize the camera - this should trigger the fallback path
        camera = PlantCamera(hass, mock_plant_entity, mock_config_entry)
        
        # Check that a fallback path was used
        assert camera._image_storage_path is not None
        # The exact path may vary, but it should not be the original default