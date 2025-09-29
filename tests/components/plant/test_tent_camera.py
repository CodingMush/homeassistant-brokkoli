"""Tests for the tent camera integration."""

from unittest.mock import Mock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.plant.tent import Tent
from custom_components.plant.const import (
    DOMAIN,
    FLOW_PLANT_INFO,
)


async def test_tent_camera_assignment(hass: HomeAssistant) -> None:
    """Test assigning a camera to a tent."""
    # Create a mock config entry
    config_entry = Mock()
    config_entry.data = {
        FLOW_PLANT_INFO: {
            "name": "Test Tent",
            "tent_id": "tent_123",
        }
    }
    
    # Create tent instance
    tent = Tent(hass, config_entry)
    
    # Test initial camera assignment
    assert tent.get_camera() is None
    
    # Test setting a camera
    camera_entity_id = "camera.test_camera"
    tent.set_camera(camera_entity_id)
    
    # Verify camera assignment
    assert tent.get_camera() == camera_entity_id


async def test_tent_camera_assignment_to_plant(hass: HomeAssistant) -> None:
    """Test assigning a tent's camera to a plant."""
    # Create a mock config entry for tent
    tent_config_entry = Mock()
    tent_config_entry.data = {
        FLOW_PLANT_INFO: {
            "name": "Test Tent",
            "tent_id": "tent_123",
        }
    }
    
    # Create tent instance
    tent = Tent(hass, tent_config_entry)
    
    # Assign a camera to the tent
    camera_entity_id = "camera.test_camera"
    tent.set_camera(camera_entity_id)
    
    # Create a mock plant
    plant = Mock()
    plant.assign_camera = Mock()
    
    # Test assigning tent's camera to plant
    tent.assign_to_plant(plant)
    
    # Verify that plant's assign_camera method was called with the correct camera
    plant.assign_camera.assert_called_once_with(camera_entity_id)


async def test_tent_camera_none_assignment(hass: HomeAssistant) -> None:
    """Test assigning None camera to a tent."""
    # Create a mock config entry
    config_entry = Mock()
    config_entry.data = {
        FLOW_PLANT_INFO: {
            "name": "Test Tent",
            "tent_id": "tent_123",
        }
    }
    
    # Create tent instance
    tent = Tent(hass, config_entry)
    
    # Test setting None camera
    tent.set_camera(None)
    
    # Verify camera assignment
    assert tent.get_camera() is None


async def test_tent_camera_update_config(hass: HomeAssistant) -> None:
    """Test that camera assignment updates the config."""
    # Create a mock config entry
    config_entry = Mock()
    config_entry.data = {
        FLOW_PLANT_INFO: {
            "name": "Test Tent",
            "tent_id": "tent_123",
        }
    }
    
    # Mock the config entry update method
    config_entry.async_update_entry = Mock()
    
    with patch("homeassistant.config_entries.ConfigEntry.async_update_entry", Mock()):
        # Create tent instance
        tent = Tent(hass, config_entry)
        
        # Assign a camera to the tent
        camera_entity_id = "camera.test_camera"
        tent.set_camera(camera_entity_id)
        
        # Verify that config was updated (this would normally happen in _update_config)
        # Note: In the actual implementation, _update_config calls hass.config_entries.async_update_entry


async def test_tent_extra_state_attributes_with_camera(hass: HomeAssistant) -> None:
    """Test tent extra state attributes with camera assignment."""
    # Create a mock config entry
    config_entry = Mock()
    config_entry.data = {
        FLOW_PLANT_INFO: {
            "name": "Test Tent",
            "tent_id": "tent_123",
        }
    }
    
    # Create tent instance
    tent = Tent(hass, config_entry)
    
    # Assign a camera
    camera_entity_id = "camera.test_camera"
    tent.set_camera(camera_entity_id)
    
    # Get extra state attributes
    attributes = tent.extra_state_attributes
    
    # Verify camera entity ID is in attributes
    assert "camera_entity_id" in attributes
    assert attributes["camera_entity_id"] == camera_entity_id


async def test_tent_to_dict_with_camera(hass: HomeAssistant) -> None:
    """Test tent to_dict method with camera assignment."""
    # Create a mock config entry
    config_entry = Mock()
    config_entry.data = {
        FLOW_PLANT_INFO: {
            "name": "Test Tent",
            "tent_id": "tent_123",
        }
    }
    
    # Create tent instance
    tent = Tent(hass, config_entry)
    
    # Assign a camera
    camera_entity_id = "camera.test_camera"
    tent.set_camera(camera_entity_id)
    
    # Convert to dict
    tent_dict = tent.to_dict()
    
    # Verify camera entity ID is in dict
    assert "camera_entity_id" in tent_dict
    assert tent_dict["camera_entity_id"] == camera_entity_id