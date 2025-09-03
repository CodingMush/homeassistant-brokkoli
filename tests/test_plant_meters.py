"""Tests for plant meter entities."""
import pytest
from unittest.mock import Mock, patch
from homeassistant.const import (
    STATE_UNKNOWN,
    STATE_UNAVAILABLE,
)
from custom_components.plant.plant_meters import (
    PlantCurrentStatus,
    PlantCurrentIlluminance,
    PlantCurrentConductivity,
    PlantCurrentMoisture,
    PlantCurrentTemperature,
    PlantCurrentHumidity,
    PlantCurrentCO2,
)
from custom_components.plant.const import (
    READING_ILLUMINANCE,
    READING_CONDUCTIVITY,
    READING_MOISTURE,
    READING_TEMPERATURE,
    READING_HUMIDITY,
    READING_CO2,
    DOMAIN,
)


def test_plant_current_status_base_class(mock_hass, mock_config_entry, mock_plant):
    """Test the base PlantCurrentStatus class."""
    # Setup
    with patch('custom_components.plant.plant_meters.async_generate_entity_id'):
        sensor = PlantCurrentStatus(mock_hass, mock_config_entry, mock_plant)
        # _external_sensor is now initialized in the base class
        
        # Verify default properties
        assert sensor.state_class is not None
        assert sensor.external_sensor is None


def test_plant_current_illuminance_initialization(mock_hass, mock_config_entry, mock_plant):
    """Test PlantCurrentIlluminance initialization."""
    # Setup
    with patch('custom_components.plant.plant_meters.async_generate_entity_id'):
        sensor = PlantCurrentIlluminance(mock_hass, mock_config_entry, mock_plant)
        
        # Verify properties
        assert READING_ILLUMINANCE in sensor.name
        assert sensor.external_sensor is None  # No sensor configured in mock


def test_plant_current_conductivity_initialization(mock_hass, mock_config_entry, mock_plant):
    """Test PlantCurrentConductivity initialization."""
    # Setup
    with patch('custom_components.plant.plant_meters.async_generate_entity_id'):
        sensor = PlantCurrentConductivity(mock_hass, mock_config_entry, mock_plant)
        
        # Verify properties
        assert READING_CONDUCTIVITY in sensor.name
        assert sensor.external_sensor is None  # No sensor configured in mock


def test_plant_current_moisture_initialization(mock_hass, mock_config_entry, mock_plant):
    """Test PlantCurrentMoisture initialization."""
    # Setup
    with patch('custom_components.plant.plant_meters.async_generate_entity_id'):
        sensor = PlantCurrentMoisture(mock_hass, mock_config_entry, mock_plant)
        
        # Verify properties
        assert READING_MOISTURE in sensor.name
        assert sensor.external_sensor is None  # No sensor configured in mock


def test_plant_current_temperature_initialization(mock_hass, mock_config_entry, mock_plant):
    """Test PlantCurrentTemperature initialization."""
    # Setup
    with patch('custom_components.plant.plant_meters.async_generate_entity_id'):
        sensor = PlantCurrentTemperature(mock_hass, mock_config_entry, mock_plant)
        
        # Verify properties
        assert READING_TEMPERATURE in sensor.name
        assert sensor.external_sensor is None  # No sensor configured in mock


def test_plant_current_humidity_initialization(mock_hass, mock_config_entry, mock_plant):
    """Test PlantCurrentHumidity initialization."""
    # Setup
    with patch('custom_components.plant.plant_meters.async_generate_entity_id'):
        sensor = PlantCurrentHumidity(mock_hass, mock_config_entry, mock_plant)
        
        # Verify properties
        assert READING_HUMIDITY in sensor.name
        assert sensor.external_sensor is None  # No sensor configured in mock


def test_plant_current_co2_initialization(mock_hass, mock_config_entry, mock_plant):
    """Test PlantCurrentCO2 initialization."""
    # Setup
    with patch('custom_components.plant.plant_meters.async_generate_entity_id'):
        sensor = PlantCurrentCO2(mock_hass, mock_config_entry, mock_plant)
        
        # Verify properties
        assert READING_CO2 in sensor.name
        assert sensor.external_sensor is None  # No sensor configured in mock


def test_sensor_state_changed_valid_state(mock_hass, mock_config_entry, mock_plant):
    """Test sensor state change with valid state."""
    # Setup better mock for hass
    mock_hass.loop_thread_id = 12345  # Add the missing attribute
    mock_hass.states.get.return_value = Mock()
    mock_hass.states.get.return_value.attributes = {"external_sensor": "sensor.test_temperature"}
    
    with patch('custom_components.plant.plant_meters.async_generate_entity_id'):
        sensor = PlantCurrentTemperature(mock_hass, mock_config_entry, mock_plant)
        sensor._external_sensor = "sensor.test_temperature"
        sensor.entity_id = "sensor.test_temperature_entity"
        # Set the hass attribute manually
        sensor.hass = mock_hass
        # Initialize native_value to avoid "unknown" state issues
        sensor._attr_native_value = None
        
        # Mock external sensor state
        mock_external_state = Mock()
        mock_external_state.state = "22.5"
        mock_external_state.attributes = {"unit_of_measurement": "°C"}
        
        # Mock hass.states.get to return the external sensor
        mock_hass.states.get.side_effect = lambda entity_id: mock_external_state if entity_id == "sensor.test_temperature" else Mock(attributes={"external_sensor": "sensor.test_temperature"})
        
        with patch.object(sensor, 'async_write_ha_state'):
            # Execute
            sensor.state_changed("sensor.test_temperature", mock_external_state)
            
            # Verify
            assert float(sensor.native_value) == 22.5


def test_sensor_state_changed_unknown_state(mock_hass, mock_config_entry, mock_plant):
    """Test sensor state change with unknown state."""
    # Setup better mock for hass
    mock_hass.loop_thread_id = 12345  # Add the missing attribute
    mock_hass.states.get.return_value = Mock()
    mock_hass.states.get.return_value.attributes = {"external_sensor": "sensor.test_temperature"}
    
    with patch('custom_components.plant.plant_meters.async_generate_entity_id'):
        sensor = PlantCurrentTemperature(mock_hass, mock_config_entry, mock_plant)
        sensor._external_sensor = "sensor.test_temperature"
        sensor.entity_id = "sensor.test_temperature_entity"
        # Set the hass attribute manually
        sensor.hass = mock_hass
        # Initialize native_value to avoid "unknown" state issues
        sensor._attr_native_value = None
        
        # Mock external sensor state
        mock_external_state = Mock()
        mock_external_state.state = STATE_UNKNOWN
        mock_external_state.attributes = {"unit_of_measurement": "°C"}
        
        # Mock hass.states.get to return the external sensor
        mock_hass.states.get.side_effect = lambda entity_id: mock_external_state if entity_id == "sensor.test_temperature" else Mock(attributes={"external_sensor": "sensor.test_temperature"})
        
        with patch.object(sensor, 'async_write_ha_state'):
            # Execute
            sensor.state_changed("sensor.test_temperature", mock_external_state)
            
            # Verify - for numeric sensors, STATE_UNKNOWN should result in None
            assert sensor.native_value is None


def test_sensor_state_changed_unavailable_state(mock_hass, mock_config_entry, mock_plant):
    """Test sensor state change with unavailable state."""
    # Setup better mock for hass
    mock_hass.loop_thread_id = 12345  # Add the missing attribute
    mock_hass.states.get.return_value = Mock()
    mock_hass.states.get.return_value.attributes = {"external_sensor": "sensor.test_temperature"}
    
    with patch('custom_components.plant.plant_meters.async_generate_entity_id'):
        sensor = PlantCurrentTemperature(mock_hass, mock_config_entry, mock_plant)
        sensor._external_sensor = "sensor.test_temperature"
        sensor.entity_id = "sensor.test_temperature_entity"
        # Set the hass attribute manually
        sensor.hass = mock_hass
        # Initialize native_value to avoid "unknown" state issues
        sensor._attr_native_value = None
        
        # Mock external sensor state
        mock_external_state = Mock()
        mock_external_state.state = STATE_UNAVAILABLE
        mock_external_state.attributes = {"unit_of_measurement": "°C"}
        
        # Mock hass.states.get to return the external sensor
        mock_hass.states.get.side_effect = lambda entity_id: mock_external_state if entity_id == "sensor.test_temperature" else Mock(attributes={"external_sensor": "sensor.test_temperature"})
        
        with patch.object(sensor, 'async_write_ha_state'):
            # Execute
            sensor.state_changed("sensor.test_temperature", mock_external_state)
            
            # Verify - for numeric sensors, STATE_UNAVAILABLE should result in None
            assert sensor.native_value is None


def test_sensor_replace_external_sensor(mock_hass, mock_config_entry, mock_plant):
    """Test replacing external sensor."""
    # Setup better mock for hass
    mock_hass.loop_thread_id = 12345  # Add the missing attribute
    
    # Setup
    with patch('custom_components.plant.plant_meters.async_generate_entity_id'):
        sensor = PlantCurrentTemperature(mock_hass, mock_config_entry, mock_plant)
        sensor.entity_id = "sensor.test_temperature_entity"
        # Set the hass attribute manually
        sensor.hass = mock_hass
        original_sensor = sensor.external_sensor
        
        # Mock async_track_state_change_event
        with patch('custom_components.plant.plant_meters.async_track_state_change_event'):
            with patch.object(sensor, 'async_write_ha_state'):
                # Execute
                sensor.replace_external_sensor("sensor.new_temperature_sensor")
                
                # Verify
                assert sensor.external_sensor == "sensor.new_temperature_sensor"


def test_sensor_extra_state_attributes(mock_hass, mock_config_entry, mock_plant):
    """Test sensor extra state attributes."""
    # Setup
    with patch('custom_components.plant.plant_meters.async_generate_entity_id'):
        sensor = PlantCurrentTemperature(mock_hass, mock_config_entry, mock_plant)
        sensor._external_sensor = "sensor.test_temperature"
        sensor.entity_id = "sensor.test_temperature_entity"
        
        # Execute
        attributes = sensor.extra_state_attributes
        
        # Verify
        assert attributes is not None
        assert "external_sensor" in attributes
        assert attributes["external_sensor"] == "sensor.test_temperature"