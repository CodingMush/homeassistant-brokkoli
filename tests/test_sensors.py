"""Tests for plant sensor entities."""
import pytest
from unittest.mock import Mock, patch
from homeassistant.const import (
    STATE_UNKNOWN,
    STATE_UNAVAILABLE,
    STATE_OK,
    STATE_PROBLEM,
)
from custom_components.plant.sensor import (
    PlantCurrentStatus,
    PlantCurrentTemperature,
    PlantCurrentMoisture,
    PlantCurrentConductivity,
    PlantCurrentIlluminance,
    PlantCurrentHumidity,
    PlantCurrentCO2,
    PlantCurrentPpfd,
)
from custom_components.plant.const import (
    READING_TEMPERATURE,
    READING_MOISTURE,
    READING_CONDUCTIVITY,
    READING_ILLUMINANCE,
    READING_HUMIDITY,
    READING_CO2,
    READING_PPFD,
    ICON_TEMPERATURE,
    ICON_MOISTURE,
    ICON_CONDUCTIVITY,
    ICON_ILLUMINANCE,
    ICON_HUMIDITY,
    ICON_CO2,
    ICON_PPFD,
    DOMAIN,
)


def test_temperature_sensor_valid_value(mock_hass, mock_config_entry, mock_plant):
    """Test temperature sensor with valid numeric value."""
    # Setup
    sensor = PlantCurrentTemperature(mock_hass, mock_config_entry, mock_plant)
    
    # Mock state with valid value
    mock_state = Mock()
    mock_state.state = "25.5"
    mock_state.attributes = {"unit_of_measurement": "°C"}
    
    # Execute
    sensor.state_changed("sensor.test_temperature", mock_state)
    
    # Verify
    assert sensor.native_value == 25.5
    assert isinstance(sensor.native_value, float)


def test_temperature_sensor_invalid_value(mock_hass, mock_config_entry, mock_plant):
    """Test temperature sensor with invalid string value."""
    # Setup
    sensor = PlantCurrentTemperature(mock_hass, mock_config_entry, mock_plant)
    
    # Mock state with invalid value
    mock_state = Mock()
    mock_state.state = "unknown"
    mock_state.attributes = {"unit_of_measurement": "°C"}
    
    # Execute
    sensor.state_changed("sensor.test_temperature", mock_state)
    
    # Verify
    assert sensor.native_value is None


def test_temperature_sensor_unavailable_state(mock_hass, mock_config_entry, mock_plant):
    """Test temperature sensor with unavailable state."""
    # Setup
    sensor = PlantCurrentTemperature(mock_hass, mock_config_entry, mock_plant)
    
    # Mock state with unavailable value
    mock_state = Mock()
    mock_state.state = "unavailable"
    mock_state.attributes = {"unit_of_measurement": "°C"}
    
    # Execute
    sensor.state_changed("sensor.test_temperature", mock_state)
    
    # Verify
    assert sensor.native_value is None


def test_temperature_sensor_boundary_conditions(mock_hass, mock_config_entry, mock_plant):
    """Test temperature sensor with boundary condition values."""
    # Setup
    sensor = PlantCurrentTemperature(mock_hass, mock_config_entry, mock_plant)
    
    # Test zero value
    mock_state = Mock()
    mock_state.state = "0"
    mock_state.attributes = {"unit_of_measurement": "°C"}
    
    # Execute
    sensor.state_changed("sensor.test_temperature", mock_state)
    
    # Verify
    assert sensor.native_value == 0.0
    assert isinstance(sensor.native_value, float)


def test_moisture_sensor_valid_value(mock_hass, mock_config_entry, mock_plant):
    """Test moisture sensor with valid numeric value."""
    # Setup
    sensor = PlantCurrentMoisture(mock_hass, mock_config_entry, mock_plant)
    
    # Mock state with valid value
    mock_state = Mock()
    mock_state.state = "45.2"
    mock_state.attributes = {"unit_of_measurement": "%"}
    
    # Execute
    sensor.state_changed("sensor.test_moisture", mock_state)
    
    # Verify
    assert sensor.native_value == 45.2
    assert isinstance(sensor.native_value, float)


def test_conductivity_sensor_valid_value(mock_hass, mock_config_entry, mock_plant):
    """Test conductivity sensor with valid numeric value."""
    # Setup
    sensor = PlantCurrentConductivity(mock_hass, mock_config_entry, mock_plant)
    
    # Mock state with valid value
    mock_state = Mock()
    mock_state.state = "1200"
    mock_state.attributes = {"unit_of_measurement": "µS/cm"}
    
    # Execute
    sensor.state_changed("sensor.test_conductivity", mock_state)
    
    # Verify
    assert sensor.native_value == 1200
    assert isinstance(sensor.native_value, int)


def test_illuminance_sensor_valid_value(mock_hass, mock_config_entry, mock_plant):
    """Test illuminance sensor with valid numeric value."""
    # Setup
    sensor = PlantCurrentIlluminance(mock_hass, mock_config_entry, mock_plant)
    
    # Mock state with valid value
    mock_state = Mock()
    mock_state.state = "5000"
    mock_state.attributes = {"unit_of_measurement": "lx"}
    
    # Execute
    sensor.state_changed("sensor.test_illuminance", mock_state)
    
    # Verify
    assert sensor.native_value == 5000
    assert isinstance(sensor.native_value, int)


def test_humidity_sensor_valid_value(mock_hass, mock_config_entry, mock_plant):
    """Test humidity sensor with valid numeric value."""
    # Setup
    sensor = PlantCurrentHumidity(mock_hass, mock_config_entry, mock_plant)
    
    # Mock state with valid value
    mock_state = Mock()
    mock_state.state = "65.3"
    mock_state.attributes = {"unit_of_measurement": "%"}
    
    # Execute
    sensor.state_changed("sensor.test_humidity", mock_state)
    
    # Verify
    assert sensor.native_value == 65.3
    assert isinstance(sensor.native_value, float)


def test_co2_sensor_valid_value(mock_hass, mock_config_entry, mock_plant):
    """Test CO2 sensor with valid numeric value."""
    # Setup
    sensor = PlantCurrentCO2(mock_hass, mock_config_entry, mock_plant)
    
    # Mock state with valid value
    mock_state = Mock()
    mock_state.state = "450"
    mock_state.attributes = {"unit_of_measurement": "ppm"}
    
    # Execute
    sensor.state_changed("sensor.test_co2", mock_state)
    
    # Verify
    assert sensor.native_value == 450
    assert isinstance(sensor.native_value, int)


def test_ppfd_sensor_calculation(mock_hass, mock_config_entry, mock_plant):
    """Test PPFD sensor calculation from illuminance."""
    # Setup
    sensor = PlantCurrentPpfd(mock_hass, mock_config_entry, mock_plant)
    
    # Mock state with valid illuminance value
    mock_state = Mock()
    mock_state.state = "50000"  # 50000 lux
    mock_state.attributes = {"unit_of_measurement": "lx"}
    
    # Execute
    sensor.state_changed("sensor.test_illuminance", mock_state)
    
    # Verify - 50000 * 0.0185 / 1000000 = 0.000925 mol/s⋅m²
    expected_ppfd = 50000 * 0.0185 / 1000000
    assert sensor.native_value == expected_ppfd
    assert isinstance(sensor.native_value, float)


def test_sensor_external_sensor_replacement(mock_hass, mock_config_entry, mock_plant):
    """Test replacing external sensor."""
    # Setup
    sensor = PlantCurrentTemperature(mock_hass, mock_config_entry, mock_plant)
    original_sensor = sensor.external_sensor
    
    # Execute
    sensor.replace_external_sensor("sensor.new_temperature")
    
    # Verify
    assert sensor.external_sensor == "sensor.new_temperature"


def test_sensor_device_info(mock_hass, mock_config_entry, mock_plant):
    """Test sensor device info."""
    # Setup
    sensor = PlantCurrentTemperature(mock_hass, mock_config_entry, mock_plant)
    
    # Execute
    device_info = sensor.device_info
    
    # Verify
    assert device_info is not None
    assert "identifiers" in device_info
    assert (DOMAIN, mock_plant.unique_id) in device_info["identifiers"]