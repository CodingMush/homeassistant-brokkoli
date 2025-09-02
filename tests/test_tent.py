"""Tests for the tent integration."""

from unittest.mock import patch, MagicMock
from custom_components.plant.tent import TentDevice


async def test_tent_device_initialization(hass):
    """Test TentDevice initialization."""
    # Create the tent device
    tent = TentDevice(hass, name="Test Tent")

    # Verify initialization
    assert tent.name == "Test Tent"
    assert tent.state == "ok"  # Assuming STATE_OK = "ok"


async def test_tent_device_sensor_addition(hass):
    """Test adding sensors to TentDevice."""
    # Create the tent device
    tent = TentDevice(hass, name="Test Tent")

    # Add sensors
    tent.add_sensors(
        temperature_sensor="sensor.tent_temperature",
        humidity_sensor="sensor.tent_humidity",
        conductivity_sensor="sensor.tent_conductivity",
        illuminance_sensor="sensor.tent_illuminance",
        co2_sensor="sensor.tent_co2",
        ph_sensor="sensor.tent_ph",
    )

    # Verify sensors were added
    assert tent.temperature_sensor == "sensor.tent_temperature"
    assert tent.humidity_sensor == "sensor.tent_humidity"
    assert tent.conductivity_sensor == "sensor.tent_conductivity"
    assert tent.illuminance_sensor == "sensor.tent_illuminance"
    assert tent.co2_sensor == "sensor.tent_co2"
    assert tent.ph_sensor == "sensor.tent_ph"


async def test_tent_device_extra_state_attributes(hass):
    """Test TentDevice extra state attributes."""
    # Create the tent device
    tent = TentDevice(hass, name="Test Tent")

    # Add sensors
    tent.add_sensors(
        temperature_sensor="sensor.tent_temperature",
        humidity_sensor="sensor.tent_humidity",
        conductivity_sensor="sensor.tent_conductivity",
        illuminance_sensor="sensor.tent_illuminance",
        co2_sensor="sensor.tent_co2",
        ph_sensor="sensor.tent_ph",
    )

    # Get extra state attributes
    attributes = tent.extra_state_attributes

    # Verify attributes
    assert "temperature_sensor" in attributes
    assert attributes["temperature_sensor"] == "sensor.tent_temperature"
    assert "humidity_sensor" in attributes
    assert attributes["humidity_sensor"] == "sensor.tent_humidity"
    assert "conductivity_sensor" in attributes
    assert attributes["conductivity_sensor"] == "sensor.tent_conductivity"
    assert "illuminance_sensor" in attributes
    assert attributes["illuminance_sensor"] == "sensor.tent_illuminance"
    assert "co2_sensor" in attributes
    assert attributes["co2_sensor"] == "sensor.tent_co2"
    assert "ph_sensor" in attributes
    assert attributes["ph_sensor"] == "sensor.tent_ph"