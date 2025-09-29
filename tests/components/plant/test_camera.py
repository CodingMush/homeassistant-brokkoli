"""Tests for the plant camera integration."""

import os
import tempfile
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.components.camera import CameraEntityFeature
from homeassistant.const import ATTR_ENTITY_PICTURE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.plant import PlantDevice
from custom_components.plant.camera import PlantCamera
from custom_components.plant.const import (
    DOMAIN,
    FLOW_DOWNLOAD_PATH,
    FLOW_PLANT_INFO,
)


async def test_plant_camera_initialization(hass: HomeAssistant) -> None:
    """Test PlantCamera initialization."""
    # Create a mock plant entity
    plant_entity = Mock(spec=PlantDevice)
    plant_entity.name = "Test Plant"
    plant_entity.unique_id = "plant_test_123"
    plant_entity.entity_id = "plant.test_plant"
    
    # Create a mock config entry
    config_entry = Mock()
    config_entry.data = {FLOW_PLANT_INFO: {}}
    
    # Create camera instance
    with patch("os.path.exists", return_value=True):
        camera = PlantCamera(hass, plant_entity, config_entry)
    
    # Test basic properties
    assert camera.name == "Test Plant Camera"
    assert camera.unique_id == "plant_test_123_camera"
    assert camera.supported_features == CameraEntityFeature.ON_OFF
    assert camera.is_on is True


async def test_plant_camera_device_info(hass: HomeAssistant) -> None:
    """Test PlantCamera device_info property."""
    # Create a mock plant entity
    plant_entity = Mock(spec=PlantDevice)
    plant_entity.name = "Test Plant"
    plant_entity.unique_id = "plant_test_123"
    
    # Create a mock config entry
    config_entry = Mock()
    config_entry.data = {FLOW_PLANT_INFO: {}}
    
    # Create camera instance
    with patch("os.path.exists", return_value=True):
        camera = PlantCamera(hass, plant_entity, config_entry)
    
    # Test device_info
    device_info = camera.device_info
    assert device_info["identifiers"] == {(DOMAIN, "plant_test_123")}
    assert device_info["name"] == "Test Plant"
    assert device_info["manufacturer"] == "Home Assistant"
    assert device_info["model"] == "Plant Camera"


async def test_plant_camera_turn_on_off(hass: HomeAssistant) -> None:
    """Test PlantCamera turn on/off functionality."""
    # Create a mock plant entity
    plant_entity = Mock(spec=PlantDevice)
    plant_entity.name = "Test Plant"
    plant_entity.unique_id = "plant_test_123"
    
    # Create a mock config entry
    config_entry = Mock()
    config_entry.data = {FLOW_PLANT_INFO: {}}
    
    # Create camera instance
    with patch("os.path.exists", return_value=True):
        camera = PlantCamera(hass, plant_entity, config_entry)
    
    # Test initial state
    assert camera.is_on is True
    
    # Test turn off
    camera.turn_off()
    assert camera.is_on is False
    
    # Test turn on
    camera.turn_on()
    assert camera.is_on is True


async def test_plant_camera_async_camera_image(hass: HomeAssistant) -> None:
    """Test PlantCamera async_camera_image method."""
    # Create a mock plant entity
    plant_entity = Mock(spec=PlantDevice)
    plant_entity.name = "Test Plant"
    plant_entity.unique_id = "plant_test_123"
    
    # Create a mock config entry
    config_entry = Mock()
    config_entry.data = {FLOW_PLANT_INFO: {}}
    
    # Create camera instance
    with patch("os.path.exists", return_value=True):
        camera = PlantCamera(hass, plant_entity, config_entry)
    
    # Test with no image
    image = await camera.async_camera_image()
    assert image is None
    
    # Test with image
    test_image_data = b"test_image_data"
    camera._last_image = test_image_data
    
    image = await camera.async_camera_image()
    assert image == test_image_data


async def test_plant_camera_async_take_snapshot(hass: HomeAssistant) -> None:
    """Test PlantCamera async_take_snapshot method."""
    # Create a mock plant entity
    plant_entity = Mock(spec=PlantDevice)
    plant_entity.name = "Test Plant"
    plant_entity.unique_id = "plant_test_123"
    plant_entity.entity_id = "plant.test_plant"
    
    # Create a mock config entry
    config_entry = Mock()
    config_entry.data = {FLOW_PLANT_INFO: {}}
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch("os.path.exists", return_value=True), \
             patch.object(PlantCamera, "_image_storage_path", temp_dir):
            
            # Create camera instance
            camera = PlantCamera(hass, plant_entity, config_entry)
            
            # Mock the _update_plant_image method
            camera._update_plant_image = AsyncMock()
            
            # Test taking a snapshot
            filepath = await camera.async_take_snapshot()
            
            # Verify the result
            assert filepath is not None
            assert filepath.endswith(".jpg")
            assert os.path.exists(filepath)
            
            # Verify that _update_plant_image was called
            camera._update_plant_image.assert_called_once()


async def test_plant_camera_update_plant_image(hass: HomeAssistant) -> None:
    """Test PlantCamera _update_plant_image method."""
    # Create a mock plant entity
    plant_entity = Mock(spec=PlantDevice)
    plant_entity.name = "Test Plant"
    plant_entity.unique_id = "plant_test_123"
    plant_entity._attr_entity_picture = None
    plant_entity.async_write_ha_state = Mock()
    
    # Create a mock config entry
    config_entry = Mock()
    config_entry.data = {FLOW_PLANT_INFO: {}}
    config_entry.entry_id = "test_entry_id"
    
    # Mock hass.config_entries.async_update_entry
    hass.config_entries.async_update_entry = Mock()
    
    # Create camera instance
    with patch("os.path.exists", return_value=True):
        camera = PlantCamera(hass, plant_entity, config_entry)
    
    # Test updating plant image
    test_image_path = "/config/www/images/plants/test_image.jpg"
    await camera._update_plant_image(test_image_path)
    
    # Verify the results
    assert plant_entity._attr_entity_picture == "/local/images/plants/test_image.jpg"
    hass.config_entries.async_update_entry.assert_called_once()
    plant_entity.async_write_ha_state.assert_called_once()


async def test_plant_camera_storage_path_creation(hass: HomeAssistant) -> None:
    """Test that storage path is created if it doesn't exist."""
    # Create a mock plant entity
    plant_entity = Mock(spec=PlantDevice)
    plant_entity.name = "Test Plant"
    plant_entity.unique_id = "plant_test_123"
    
    # Create a mock config entry
    config_entry = Mock()
    config_entry.data = {FLOW_PLANT_INFO: {}}
    
    # Test with non-existent path
    with patch("os.path.exists", return_value=False) as mock_exists, \
         patch("os.makedirs") as mock_makedirs:
        
        camera = PlantCamera(hass, plant_entity, config_entry)
        
        # Verify that makedirs was called
        mock_makedirs.assert_called_once()


async def test_plant_camera_with_custom_storage_path(hass: HomeAssistant) -> None:
    """Test PlantCamera with custom storage path."""
    # Create a mock plant entity
    plant_entity = Mock(spec=PlantDevice)
    plant_entity.name = "Test Plant"
    plant_entity.unique_id = "plant_test_123"
    
    # Create a mock config entry with custom download path
    config_entry = Mock()
    config_entry.data = {FLOW_PLANT_INFO: {FLOW_DOWNLOAD_PATH: "/custom/path/"}}
    
    # Test with custom path
    with patch("os.path.exists", return_value=True) as mock_exists:
        camera = PlantCamera(hass, plant_entity, config_entry)
        
        # Verify the storage path is set correctly
        assert camera._image_storage_path == "/custom/path/"