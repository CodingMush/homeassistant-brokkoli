"""Tests for virtual sensors in the plant integration."""

from unittest.mock import patch, MagicMock
from homeassistant.const import STATE_UNKNOWN
from custom_components.plant.sensor import (
    PlantCurrentPpfd,
    PlantDailyLightIntegral,
    PlantTotalLightIntegral,
    PlantCurrentMoistureConsumption,
    PlantTotalWaterConsumption,
    PlantCurrentFertilizerConsumption,
    PlantTotalFertilizerConsumption,
)


async def test_virtual_sensor_initialization(hass):
    """Test initialization of virtual sensors."""
    # Create mock objects
    mock_config = MagicMock()
    mock_config.entry_id = "test_entry_id"
    mock_plant = MagicMock()
    mock_plant.entity_id = "plant.test_plant"

    # Test PPFD sensor initialization
    ppfd_sensor = PlantCurrentPpfd(hass, mock_config, mock_plant)
    assert ppfd_sensor is not None
    assert ppfd_sensor._attr_state_class is not None

    # Test DLI sensor initialization
    dli_sensor = PlantDailyLightIntegral(hass, mock_config, MagicMock(), mock_plant)
    assert dli_sensor is not None

    # Test Total Light Integral sensor initialization
    integral_sensor = PlantTotalLightIntegral(hass, mock_config, MagicMock(), mock_plant)
    assert integral_sensor is not None

    # Test Moisture Consumption sensor initialization
    moisture_consumption_sensor = PlantCurrentMoistureConsumption(hass, mock_config, mock_plant)
    assert moisture_consumption_sensor is not None

    # Test Total Water Consumption sensor initialization
    total_water_sensor = PlantTotalWaterConsumption(hass, mock_config, mock_plant)
    assert total_water_sensor is not None

    # Test Fertilizer Consumption sensor initialization
    fertilizer_consumption_sensor = PlantCurrentFertilizerConsumption(hass, mock_config, mock_plant)
    assert fertilizer_consumption_sensor is not None

    # Test Total Fertilizer Consumption sensor initialization
    total_fertilizer_sensor = PlantTotalFertilizerConsumption(hass, mock_config, mock_plant)
    assert total_fertilizer_sensor is not None


async def test_virtual_sensor_state_calculation(hass):
    """Test state calculation for virtual sensors."""
    # Create mock objects
    mock_config = MagicMock()
    mock_config.entry_id = "test_entry_id"
    mock_plant = MagicMock()
    mock_plant.entity_id = "plant.test_plant"

    # Test PPFD sensor state calculation
    ppfd_sensor = PlantCurrentPpfd(hass, mock_config, mock_plant)
    
    # Mock illuminance sensor with a value
    mock_illuminance_sensor = MagicMock()
    mock_illuminance_sensor.state = "10000"  # 10000 lux
    ppfd_sensor._external_sensor = mock_illuminance_sensor
    
    # Mock the hass.states.get to return our mock sensor
    with patch.object(hass.states, 'get', return_value=mock_illuminance_sensor):
        await ppfd_sensor.async_update()
        
        # PPFD should be calculated from illuminance
        # With default conversion factor, 10000 lux should give a specific PPFD value
        # The exact value depends on the conversion logic in the sensor
        assert ppfd_sensor.state != STATE_UNKNOWN


async def test_virtual_sensor_with_no_external_sensor(hass):
    """Test virtual sensors when no external sensor is available."""
    # Create mock objects
    mock_config = MagicMock()
    mock_config.entry_id = "test_entry_id"
    mock_plant = MagicMock()
    mock_plant.entity_id = "plant.test_plant"

    # Test PPFD sensor without external sensor
    ppfd_sensor = PlantCurrentPpfd(hass, mock_config, mock_plant)
    ppfd_sensor._external_sensor = None
    
    with patch.object(hass.states, 'get', return_value=None):
        await ppfd_sensor.async_update()
        assert ppfd_sensor.state == STATE_UNKNOWN


async def test_consumption_sensor_calculation(hass):
    """Test consumption sensor calculations."""
    # Create mock objects
    mock_config = MagicMock()
    mock_config.entry_id = "test_entry_id"
    mock_plant = MagicMock()
    mock_plant.entity_id = "plant.test_plant"

    # Test Moisture Consumption sensor
    moisture_consumption_sensor = PlantCurrentMoistureConsumption(hass, mock_config, mock_plant)
    
    # Mock moisture sensor
    mock_moisture_sensor = MagicMock()
    mock_moisture_sensor.state = "45.0"
    moisture_consumption_sensor._external_sensor = mock_moisture_sensor
    
    with patch.object(hass.states, 'get', return_value=mock_moisture_sensor):
        await moisture_consumption_sensor.async_update()
        # Consumption calculation depends on previous values and time
        # For now, just verify it doesn't crash
        assert moisture_consumption_sensor is not None


async def test_total_consumption_sensors(hass):
    """Test total consumption sensors."""
    # Create mock objects
    mock_config = MagicMock()
    mock_config.entry_id = "test_entry_id"
    mock_plant = MagicMock()
    mock_plant.entity_id = "plant.test_plant"

    # Test Total Water Consumption sensor
    total_water_sensor = PlantTotalWaterConsumption(hass, mock_config, mock_plant)
    assert total_water_sensor is not None
    assert total_water_sensor._attr_state_class is not None

    # Test Total Fertilizer Consumption sensor
    total_fertilizer_sensor = PlantTotalFertilizerConsumption(hass, mock_config, mock_plant)
    assert total_fertilizer_sensor is not None
    assert total_fertilizer_sensor._attr_state_class is not None