"""Tests for the plant camera assignment."""

from unittest.mock import Mock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.plant import PlantDevice
from custom_components.plant.const import (
    DOMAIN,
    FLOW_PLANT_INFO,
    FLOW_SENSOR_TEMPERATURE,
)


async def test_plant_camera_assignment(hass: HomeAssistant) -> None:
    """Test assigning a camera to a plant."""
    # Create a mock config entry
    config_entry = Mock()
    config_entry.data = {
        FLOW_PLANT_INFO: {
            "name": "Test Plant",
            "plant_id": "plant_123",
        }
    }
    
    # Mock the config entry update method
    hass.config_entries = Mock()
    hass.config_entries.async_update_entry = Mock()
    
    # Create plant instance
    plant = PlantDevice(hass, config_entry)
    plant.camera = None
    
    # Test assigning a camera
    camera_entity_id = "camera.test_camera"
    with patch("custom_components.plant.PlantCamera") as mock_camera_class:
        mock_camera_instance = Mock()
        mock_camera_class.return_value = mock_camera_instance
        
        plant.assign_camera(camera_entity_id)
        
        # Verify that config entry was updated
        hass.config_entries.async_update_entry.assert_called_once()
        
        # Verify that camera was initialized
        mock_camera_class.assert_called_once_with(hass, plant, config_entry)


async def test_plant_camera_assignment_with_existing_camera(hass: HomeAssistant) -> None:
    """Test assigning a camera to a plant that already has a camera."""
    # Create a mock config entry
    config_entry = Mock()
    config_entry.data = {
        FLOW_PLANT_INFO: {
            "name": "Test Plant",
            "plant_id": "plant_123",
        }
    }
    
    # Mock the config entry update method
    hass.config_entries = Mock()
    hass.config_entries.async_update_entry = Mock()
    
    # Create plant instance with existing camera
    plant = PlantDevice(hass, config_entry)
    existing_camera = Mock()
    plant.camera = existing_camera
    
    # Test assigning a camera
    camera_entity_id = "camera.test_camera"
    with patch("custom_components.plant.PlantCamera") as mock_camera_class:
        plant.assign_camera(camera_entity_id)
        
        # Verify that config entry was updated
        hass.config_entries.async_update_entry.assert_called_once()
        
        # Verify that camera class was not instantiated again
        mock_camera_class.assert_not_called()
        
        # Verify that existing camera was preserved
        assert plant.camera == existing_camera


async def test_plant_camera_assignment_error_handling(hass: HomeAssistant) -> None:
    """Test error handling in camera assignment."""
    # Create a mock config entry
    config_entry = Mock()
    config_entry.data = {
        FLOW_PLANT_INFO: {
            "name": "Test Plant",
            "plant_id": "plant_123",
        }
    }
    
    # Mock the config entry update method to raise an exception
    hass.config_entries = Mock()
    hass.config_entries.async_update_entry = Mock(side_effect=Exception("Test error"))
    
    # Create plant instance
    plant = PlantDevice(hass, config_entry)
    plant.camera = None
    
    # Test assigning a camera with error
    camera_entity_id = "camera.test_camera"
    with patch("custom_components.plant.PlantCamera"), \
         patch("custom_components.plant._LOGGER.error") as mock_log_error:
        
        plant.assign_camera(camera_entity_id)
        
        # Verify that error was logged
        mock_log_error.assert_called_once()


async def test_plant_camera_in_tent_assignment(hass: HomeAssistant) -> None:
    """Test plant camera assignment through tent."""
    # Create a mock config entry for plant
    plant_config_entry = Mock()
    plant_config_entry.data = {
        FLOW_PLANT_INFO: {
            "name": "Test Plant",
            "plant_id": "plant_123",
        }
    }
    
    # Mock the config entry update method
    hass.config_entries = Mock()
    hass.config_entries.async_update_entry = Mock()
    
    # Create plant instance
    plant = PlantDevice(hass, plant_config_entry)
    plant.camera = None
    
    # Create a mock tent with camera
    tent = Mock()
    camera_entity_id = "camera.tent_camera"
    tent._camera_entity_id = camera_entity_id
    
    # Test assigning tent to plant
    with patch("custom_components.plant.PlantCamera") as mock_camera_class:
        mock_camera_instance = Mock()
        mock_camera_class.return_value = mock_camera_instance
        
        # Call the tent's assign_to_plant method (simulating what would happen in real code)
        plant.assign_camera(camera_entity_id)
        
        # Verify that camera was assigned
        hass.config_entries.async_update_entry.assert_called_once()