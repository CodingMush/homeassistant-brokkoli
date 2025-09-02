"""Comprehensive tests for the tent integration with PlantDevice."""

import pytest
from unittest.mock import patch, MagicMock
from homeassistant.const import STATE_OK, STATE_UNKNOWN
from custom_components.plant import PlantDevice
from custom_components.plant.tent_integration import TentIntegration, TentInfo


async def test_plant_device_with_tent_integration():
    """Test PlantDevice with tent integration."""
    # Create a mock config entry
    config_entry = MagicMock()
    config_entry.data = {
        "plant_info": {
            "name": "Test Plant",
            "device_type": "plant",
        }
    }
    config_entry.entry_id = "test_entry_id"

    # Create the plant device
    with patch("custom_components.plant.PlantDevice._get_next_id") as mock_get_next_id:
        mock_get_next_id.return_value = "0001"
        plant = PlantDevice(MagicMock(), config_entry)

    # Verify that tent attributes were added
    assert hasattr(plant, 'tent_id')
    assert hasattr(plant, 'tent_sensors')
    assert plant.tent_id is None
    assert plant.tent_sensors == {}


async def test_plant_device_websocket_info_with_tent():
    """Test PlantDevice websocket_info includes tent data."""
    # Create a mock config entry
    config_entry = MagicMock()
    config_entry.data = {
        "plant_info": {
            "name": "Test Plant",
            "device_type": "plant",
        }
    }
    config_entry.entry_id = "test_entry_id"

    # Create the plant device
    with patch("custom_components.plant.PlantDevice._get_next_id") as mock_get_next_id:
        mock_get_next_id.return_value = "0001"
        plant = PlantDevice(MagicMock(), config_entry)

    # Mark plant as complete
    plant.plant_complete = True

    # Get websocket info
    info = plant.websocket_info

    # Verify tent data is included
    assert "tent" in info
    assert info["tent"]["tent_id"] is None
    assert info["tent"]["tent_sensors"] == {}


async def test_tent_integration_with_plant_assignment():
    """Test tent integration with plant assignment."""
    # Create tent integration
    tent_integration = TentIntegration(MagicMock())

    # Add a tent
    tent_info_data = {
        "name": "Test Tent",
        "sensors": {
            "temperature": "sensor.tent_temperature",
            "humidity": "sensor.tent_humidity"
        }
    }
    tent_integration.add_tent("tent_1", tent_info_data)

    # Create a mock config entry
    config_entry = MagicMock()
    config_entry.data = {
        "plant_info": {
            "name": "Test Plant",
            "device_type": "plant",
        }
    }
    config_entry.entry_id = "test_entry_id"

    # Create the plant device
    with patch("custom_components.plant.PlantDevice._get_next_id") as mock_get_next_id:
        mock_get_next_id.return_value = "0001"
        plant = PlantDevice(MagicMock(), config_entry)

    # Assign plant to tent
    tent_integration.assign_plant_to_tent(plant.entity_id, "tent_1")

    # Verify assignment
    tent_id = tent_integration.get_tent_for_plant(plant.entity_id)
    assert tent_id == "tent_1"

    # Get tent sensors
    tent_sensors = tent_integration.get_tent_sensors("tent_1")
    assert "temperature" in tent_sensors
    assert "humidity" in tent_sensors


async def test_plant_device_tent_sensor_functionality():
    """Test PlantDevice tent sensor functionality."""
    # Create tent integration
    mock_hass = MagicMock()
    tent_integration = TentIntegration(mock_hass)

    # Add a tent with sensors
    tent_info_data = {
        "name": "Test Tent",
        "sensors": {
            "temperature": "sensor.tent_temperature",
            "humidity": "sensor.tent_humidity"
        }
    }
    tent_integration.add_tent("tent_1", tent_info_data)

    # Create a mock config entry
    config_entry = MagicMock()
    config_entry.data = {
        "plant_info": {
            "name": "Test Plant",
            "device_type": "plant",
        }
    }
    config_entry.entry_id = "test_entry_id"

    # Create the plant device
    with patch("custom_components.plant.PlantDevice._get_next_id") as mock_get_next_id:
        mock_get_next_id.return_value = "0001"
        plant = PlantDevice(mock_hass, config_entry)

    # Assign plant to tent
    tent_integration.assign_plant_to_tent(plant.entity_id, "tent_1")

    # Verify plant has tent attributes
    assert plant.tent_id == "tent_1"
    assert "temperature" in plant.tent_sensors
    assert "humidity" in plant.tent_sensors


async def test_tent_integration_sensor_sharing():
    """Test tent integration sensor sharing functionality."""
    # Create tent integration
    mock_hass = MagicMock()
    tent_integration = TentIntegration(mock_hass)

    # Add a tent with sensors
    tent_info_data = {
        "name": "Test Tent",
        "sensors": {
            "temperature": "sensor.tent_temperature"
        }
    }
    tent_integration.add_tent("tent_1", tent_info_data)

    # Create a mock config entry
    config_entry = MagicMock()
    config_entry.data = {
        "plant_info": {
            "name": "Test Plant",
            "device_type": "plant",
        }
    }
    config_entry.entry_id = "test_entry_id"

    # Create the plant device
    with patch("custom_components.plant.PlantDevice._get_next_id") as mock_get_next_id:
        mock_get_next_id.return_value = "0001"
        plant = PlantDevice(mock_hass, config_entry)

    # Assign plant to tent
    tent_integration.assign_plant_to_tent(plant.entity_id, "tent_1")

    # Test is_plant_in_tent function
    from custom_components.plant.tent_integration import is_plant_in_tent
    assert is_plant_in_tent(plant) is True

    # Test get_tent_sensor_for_plant function
    from custom_components.plant.tent_integration import get_tent_sensor_for_plant
    tent_sensor = get_tent_sensor_for_plant(plant, "temperature")
    assert tent_sensor == "sensor.tent_temperature"

    # Test with non-existent sensor type
    tent_sensor = get_tent_sensor_for_plant(plant, "non_existent")
    assert tent_sensor is None