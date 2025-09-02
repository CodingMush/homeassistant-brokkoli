"""Tests for the plant integration."""

from unittest.mock import patch, MagicMock
from homeassistant.const import STATE_OK, STATE_PROBLEM
from custom_components.plant.const import (
    DOMAIN,
    DEVICE_TYPE_PLANT,
    ATTR_TEMPERATURE,
    ATTR_MOISTURE,
    ATTR_CONDUCTIVITY,
    ATTR_ILLUMINANCE,
    ATTR_HUMIDITY,
    ATTR_CO2,
    ATTR_DLI,
)
from custom_components.plant import PlantDevice


async def test_plant_device_initialization(hass):
    """Test PlantDevice initialization."""
    # Create a mock config entry
    config_entry = MagicMock()
    config_entry.data = {
        "plant_info": {
            "name": "Test Plant",
            "device_type": DEVICE_TYPE_PLANT,
        }
    }
    config_entry.entry_id = "test_entry_id"

    # Create the plant device
    with patch("custom_components.plant.PlantDevice._get_next_id") as mock_get_next_id:
        mock_get_next_id.return_value = "0001"
        plant = PlantDevice(hass, config_entry)

    # Verify initialization
    assert plant.name == "Test Plant"
    assert plant.device_type == DEVICE_TYPE_PLANT
    assert plant.state == STATE_OK


async def test_plant_device_sensor_addition(hass):
    """Test adding sensors to PlantDevice."""
    # Create a mock config entry
    config_entry = MagicMock()
    config_entry.data = {
        "plant_info": {
            "name": "Test Plant",
            "device_type": DEVICE_TYPE_PLANT,
        }
    }
    config_entry.entry_id = "test_entry_id"

    # Create the plant device
    with patch("custom_components.plant.PlantDevice._get_next_id") as mock_get_next_id:
        mock_get_next_id.return_value = "0001"
        plant = PlantDevice(hass, config_entry)

    # Create mock sensors
    mock_temperature_sensor = MagicMock()
    mock_temperature_sensor.state = "22.5"
    mock_moisture_sensor = MagicMock()
    mock_moisture_sensor.state = "45.0"

    # Add sensors
    plant.add_sensors(
        temperature=mock_temperature_sensor,
        moisture=mock_moisture_sensor,
        conductivity=None,
        illuminance=None,
        humidity=None,
        CO2=None,
        power_consumption=None,
        ph=None,
    )

    # Verify sensors were added
    assert plant.sensor_temperature == mock_temperature_sensor
    assert plant.sensor_moisture == mock_moisture_sensor


async def test_plant_device_threshold_addition(hass):
    """Test adding thresholds to PlantDevice."""
    # Create a mock config entry
    config_entry = MagicMock()
    config_entry.data = {
        "plant_info": {
            "name": "Test Plant",
            "device_type": DEVICE_TYPE_PLANT,
        }
    }
    config_entry.entry_id = "test_entry_id"

    # Create the plant device
    with patch("custom_components.plant.PlantDevice._get_next_id") as mock_get_next_id:
        mock_get_next_id.return_value = "0001"
        plant = PlantDevice(hass, config_entry)

    # Create mock thresholds
    mock_max_temperature = MagicMock()
    mock_max_temperature.state = "30.0"
    mock_min_temperature = MagicMock()
    mock_min_temperature.state = "10.0"

    # Add thresholds
    plant.add_thresholds(
        max_moisture=None,
        min_moisture=None,
        max_temperature=mock_max_temperature,
        min_temperature=mock_min_temperature,
        max_conductivity=None,
        min_conductivity=None,
        max_illuminance=None,
        min_illuminance=None,
        max_humidity=None,
        min_humidity=None,
        max_CO2=None,
        min_CO2=None,
        max_dli=None,
        min_dli=None,
        max_water_consumption=None,
        min_water_consumption=None,
        max_fertilizer_consumption=None,
        min_fertilizer_consumption=None,
        max_power_consumption=None,
        min_power_consumption=None,
        max_ph=None,
        min_ph=None,
    )

    # Verify thresholds were added
    assert plant.max_temperature == mock_max_temperature
    assert plant.min_temperature == mock_min_temperature


async def test_plant_device_dli_addition(hass):
    """Test adding DLI to PlantDevice."""
    # Create a mock config entry
    config_entry = MagicMock()
    config_entry.data = {
        "plant_info": {
            "name": "Test Plant",
            "device_type": DEVICE_TYPE_PLANT,
        }
    }
    config_entry.entry_id = "test_entry_id"

    # Create the plant device
    with patch("custom_components.plant.PlantDevice._get_next_id") as mock_get_next_id:
        mock_get_next_id.return_value = "0001"
        plant = PlantDevice(hass, config_entry)

    # Create mock DLI sensor
    mock_dli_sensor = MagicMock()
    mock_dli_sensor.state = "15.0"

    # Add DLI
    plant.add_dli(dli=mock_dli_sensor)

    # Verify DLI was added
    assert plant.dli == mock_dli_sensor
    assert plant.plant_complete is True


async def test_plant_device_websocket_info(hass):
    """Test PlantDevice websocket_info property."""
    # Create a mock config entry
    config_entry = MagicMock()
    config_entry.data = {
        "plant_info": {
            "name": "Test Plant",
            "device_type": DEVICE_TYPE_PLANT,
        }
    }
    config_entry.entry_id = "test_entry_id"

    # Create the plant device
    with patch("custom_components.plant.PlantDevice._get_next_id") as mock_get_next_id:
        mock_get_next_id.return_value = "0001"
        plant = PlantDevice(hass, config_entry)

    # Set up mock sensors and thresholds
    mock_temperature_sensor = MagicMock()
    mock_temperature_sensor.state = "22.5"
    mock_temperature_sensor.icon = "mdi:thermometer"
    mock_temperature_sensor.unit_of_measurement = "°C"
    mock_temperature_sensor.entity_id = "sensor.temperature"

    mock_max_temperature = MagicMock()
    mock_max_temperature.state = "30.0"
    mock_min_temperature = MagicMock()
    mock_min_temperature.state = "10.0"

    plant.add_sensors(
        temperature=mock_temperature_sensor,
        moisture=None,
        conductivity=None,
        illuminance=None,
        humidity=None,
        CO2=None,
        power_consumption=None,
        ph=None,
    )

    plant.add_thresholds(
        max_moisture=None,
        min_moisture=None,
        max_temperature=mock_max_temperature,
        min_temperature=mock_min_temperature,
        max_conductivity=None,
        min_conductivity=None,
        max_illuminance=None,
        min_illuminance=None,
        max_humidity=None,
        min_humidity=None,
        max_CO2=None,
        min_CO2=None,
        max_dli=None,
        min_dli=None,
        max_water_consumption=None,
        min_water_consumption=None,
        max_fertilizer_consumption=None,
        min_fertilizer_consumption=None,
        max_power_consumption=None,
        min_power_consumption=None,
        max_ph=None,
        min_ph=None,
    )

    # Mark plant as complete
    plant.plant_complete = True

    # Get websocket info
    info = plant.websocket_info

    # Verify the structure
    assert "device_type" in info
    assert "entity_id" in info
    assert "name" in info
    assert "icon" in info
    assert "state" in info
    assert ATTR_TEMPERATURE in info
    assert info[ATTR_TEMPERATURE]["current"] == "22.5"
    assert info[ATTR_TEMPERATURE]["max"] == "30.0"
    assert info[ATTR_TEMPERATURE]["min"] == "10.0"