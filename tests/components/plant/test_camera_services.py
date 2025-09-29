"""Tests for the camera services."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from custom_components.plant.const import (
    DOMAIN,
    SERVICE_TAKE_SNAPSHOT,
    SERVICE_AUTO_SNAPSHOT,
)
from custom_components.plant.services import async_setup_services


async def test_take_snapshot_service(hass: HomeAssistant) -> None:
    """Test the take_snapshot service."""
    # Setup services
    await async_setup_services(hass)
    
    # Create a mock service call
    service_call = Mock()
    service_call.data = {
        "entity_id": "plant.test_plant"
    }
    
    # Create a mock plant entity
    mock_plant = Mock()
    mock_plant.entity_id = "plant.test_plant"
    
    # Create a mock camera
    mock_camera = AsyncMock()
    mock_camera.async_take_snapshot = AsyncMock(return_value="/test/path/snapshot.jpg")
    mock_plant.camera = mock_camera
    
    # Mock the hass data structure
    hass.data = {
        DOMAIN: {
            "test_entry": {
                "plant": mock_plant
            }
        }
    }
    
    # Get the service function
    from custom_components.plant.services import take_snapshot
    
    # Call the service
    await take_snapshot(service_call)
    
    # Verify that the camera's take_snapshot method was called
    mock_camera.async_take_snapshot.assert_called_once()


async def test_take_snapshot_service_no_plant(hass: HomeAssistant) -> None:
    """Test the take_snapshot service when plant is not found."""
    # Setup services
    await async_setup_services(hass)
    
    # Create a mock service call
    service_call = Mock()
    service_call.data = {
        "entity_id": "plant.nonexistent_plant"
    }
    
    # Mock the hass data structure with no matching plant
    hass.data = {
        DOMAIN: {
            "test_entry": {
                "plant": Mock()
            }
        }
    }
    hass.data[DOMAIN]["test_entry"]["plant"].entity_id = "plant.different_plant"
    
    # Get the service function
    from custom_components.plant.services import take_snapshot
    
    # Call the service (should not raise an exception)
    await take_snapshot(service_call)


async def test_take_snapshot_service_no_camera(hass: HomeAssistant) -> None:
    """Test the take_snapshot service when plant has no camera."""
    # Setup services
    await async_setup_services(hass)
    
    # Create a mock service call
    service_call = Mock()
    service_call.data = {
        "entity_id": "plant.test_plant"
    }
    
    # Create a mock plant entity without camera
    mock_plant = Mock()
    mock_plant.entity_id = "plant.test_plant"
    mock_plant.camera = None
    
    # Mock PlantCamera class
    with patch("custom_components.plant.services.PlantCamera") as mock_camera_class:
        mock_camera_instance = Mock()
        mock_camera_instance.async_take_snapshot = AsyncMock(return_value="/test/path/snapshot.jpg")
        mock_camera_class.return_value = mock_camera_instance
        
        # Mock the hass data structure
        hass.data = {
            DOMAIN: {
                "test_entry": {
                    "plant": mock_plant
                }
            }
        }
        
        # Get the service function
        from custom_components.plant.services import take_snapshot
        
        # Call the service
        await take_snapshot(service_call)
        
        # Verify that camera was created
        mock_camera_class.assert_called_once()


async def test_auto_snapshot_service(hass: HomeAssistant) -> None:
    """Test the auto_snapshot service."""
    # Setup services
    await async_setup_services(hass)
    
    # Create a mock service call
    service_call = Mock()
    service_call.data = {
        "entity_id": "plant.test_plant",
        "interval_minutes": 30,
        "enabled": True
    }
    
    # Create a mock plant entity
    mock_plant = Mock()
    mock_plant.entity_id = "plant.test_plant"
    mock_plant._config = Mock()
    mock_plant._config.data = {}
    
    # Mock the config entry update method
    hass.config_entries = Mock()
    hass.config_entries.async_update_entry = Mock()
    
    # Mock the hass data structure
    hass.data = {
        DOMAIN: {
            "test_entry": {
                "plant": mock_plant
            }
        }
    }
    
    # Get the service function
    from custom_components.plant.services import auto_snapshot
    
    # Call the service
    await auto_snapshot(service_call)
    
    # Verify that config entry was updated
    hass.config_entries.async_update_entry.assert_called_once()


async def test_auto_snapshot_service_no_plant(hass: HomeAssistant) -> None:
    """Test the auto_snapshot service when plant is not found."""
    # Setup services
    await async_setup_services(hass)
    
    # Create a mock service call
    service_call = Mock()
    service_call.data = {
        "entity_id": "plant.nonexistent_plant"
    }
    
    # Mock the hass data structure with no matching plant
    hass.data = {
        DOMAIN: {
            "test_entry": {
                "plant": Mock()
            }
        }
    }
    hass.data[DOMAIN]["test_entry"]["plant"].entity_id = "plant.different_plant"
    
    # Get the service function
    from custom_components.plant.services import auto_snapshot
    
    # Call the service (should not raise an exception)
    await auto_snapshot(service_call)


async def test_camera_services_registration(hass: HomeAssistant) -> None:
    """Test that camera services are properly registered."""
    # Setup services
    await async_setup_services(hass)
    
    # Verify that services are registered
    assert hass.services.has_service(DOMAIN, SERVICE_TAKE_SNAPSHOT)
    assert hass.services.has_service(DOMAIN, SERVICE_AUTO_SNAPSHOT)


async def test_take_snapshot_service_exception_handling(hass: HomeAssistant) -> None:
    """Test exception handling in take_snapshot service."""
    # Setup services
    await async_setup_services(hass)
    
    # Create a mock service call
    service_call = Mock()
    service_call.data = {
        "entity_id": "plant.test_plant"
    }
    
    # Create a mock plant entity
    mock_plant = Mock()
    mock_plant.entity_id = "plant.test_plant"
    
    # Create a mock camera that raises an exception
    mock_camera = AsyncMock()
    mock_camera.async_take_snapshot = AsyncMock(side_effect=Exception("Test error"))
    mock_plant.camera = mock_camera
    
    # Mock the hass data structure
    hass.data = {
        DOMAIN: {
            "test_entry": {
                "plant": mock_plant
            }
        }
    }
    
    # Get the service function
    from custom_components.plant.services import take_snapshot
    
    # Call the service (should not raise an exception)
    await take_snapshot(service_call)