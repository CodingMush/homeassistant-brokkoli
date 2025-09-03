"""Tests for plant number entities."""
import pytest
from unittest.mock import Mock, patch
from homeassistant.const import STATE_UNKNOWN
from custom_components.plant.plant_thresholds import (
    PlantMinMax,
    PlantMinMoisture,
    PlantMaxMoisture,
    PlantMinTemperature,
    PlantMaxTemperature,
    PlantMinConductivity,
    PlantMaxConductivity,
    PlantMinIlluminance,
    PlantMaxIlluminance,
    PlantMinHumidity,
    PlantMaxHumidity,
    PlantMinCO2,
    PlantMaxCO2,
    PlantMinDli,
    PlantMaxDli,
    PlantMinWaterConsumption,
    PlantMaxWaterConsumption,
    PlantMinFertilizerConsumption,
    PlantMaxFertilizerConsumption,
    PlantMinPowerConsumption,
    PlantMaxPowerConsumption,
    PlantMinPh,
    PlantMaxPh,
)
from custom_components.plant.number import (
    FloweringDurationNumber,
    PotSizeNumber,
    WaterCapacityNumber,
    PlantHealthNumber,
)
from custom_components.plant.const import (
    ATTR_MIN,
    ATTR_MAX,
    READING_TEMPERATURE,
    READING_MOISTURE,
    READING_CONDUCTIVITY,
    READING_ILLUMINANCE,
    READING_HUMIDITY,
    READING_CO2,
    READING_DLI,
    READING_MOISTURE_CONSUMPTION,
    READING_FERTILIZER_CONSUMPTION,
    READING_POWER_CONSUMPTION,
    READING_PH,
    DOMAIN,
    ICON_TEMPERATURE,
    ICON_MOISTURE,
    ICON_CONDUCTIVITY,
    ICON_ILLUMINANCE,
    ICON_HUMIDITY,
    ICON_CO2,
    ICON_DLI,
)


def test_plant_min_threshold_temperature(mock_hass, mock_config_entry, mock_plant):
    """Test PlantMinThreshold for temperature."""
    # Setup
    with patch('custom_components.plant.plant_thresholds.async_generate_entity_id') as mock_generate_id:
        mock_generate_id.return_value = "plant.test_plant_min_temperature"
        threshold = PlantMinTemperature(mock_hass, mock_config_entry, mock_plant)
        
        # Verify properties
        assert "min" in threshold.name.lower()
        assert threshold.icon == ICON_TEMPERATURE


def test_plant_max_threshold_temperature(mock_hass, mock_config_entry, mock_plant):
    """Test PlantMaxThreshold for temperature."""
    # Setup
    with patch('custom_components.plant.plant_thresholds.async_generate_entity_id') as mock_generate_id:
        mock_generate_id.return_value = "plant.test_plant_max_temperature"
        threshold = PlantMaxTemperature(mock_hass, mock_config_entry, mock_plant)
        
        # Verify properties
        assert "max" in threshold.name.lower()
        assert threshold.icon == ICON_TEMPERATURE


def test_plant_min_threshold_moisture(mock_hass, mock_config_entry, mock_plant):
    """Test PlantMinThreshold for moisture."""
    # Setup
    with patch('custom_components.plant.plant_thresholds.async_generate_entity_id') as mock_generate_id:
        mock_generate_id.return_value = "plant.test_plant_min_moisture"
        threshold = PlantMinMoisture(mock_hass, mock_config_entry, mock_plant)
        
        # Verify properties
        assert "min" in threshold.name.lower()
        assert threshold.icon == ICON_MOISTURE


def test_plant_max_threshold_moisture(mock_hass, mock_config_entry, mock_plant):
    """Test PlantMaxThreshold for moisture."""
    # Setup
    with patch('custom_components.plant.plant_thresholds.async_generate_entity_id') as mock_generate_id:
        mock_generate_id.return_value = "plant.test_plant_max_moisture"
        threshold = PlantMaxMoisture(mock_hass, mock_config_entry, mock_plant)
        
        # Verify properties
        assert "max" in threshold.name.lower()
        assert threshold.icon == ICON_MOISTURE


def test_plant_min_threshold_conductivity(mock_hass, mock_config_entry, mock_plant):
    """Test PlantMinThreshold for conductivity."""
    # Setup
    with patch('custom_components.plant.plant_thresholds.async_generate_entity_id') as mock_generate_id:
        mock_generate_id.return_value = "plant.test_plant_min_conductivity"
        threshold = PlantMinConductivity(mock_hass, mock_config_entry, mock_plant)
        
        # Verify properties
        assert "min" in threshold.name.lower()
        assert threshold.icon == ICON_CONDUCTIVITY


def test_plant_max_threshold_conductivity(mock_hass, mock_config_entry, mock_plant):
    """Test PlantMaxThreshold for conductivity."""
    # Setup
    with patch('custom_components.plant.plant_thresholds.async_generate_entity_id') as mock_generate_id:
        mock_generate_id.return_value = "plant.test_plant_max_conductivity"
        threshold = PlantMaxConductivity(mock_hass, mock_config_entry, mock_plant)
        
        # Verify properties
        assert "max" in threshold.name.lower()
        assert threshold.icon == ICON_CONDUCTIVITY


def test_plant_number_device_info(mock_hass, mock_config_entry, mock_plant):
    """Test PlantNumber device info."""
    # Setup
    with patch('custom_components.plant.plant_thresholds.async_generate_entity_id') as mock_generate_id:
        mock_generate_id.return_value = "plant.test_plant_min_temperature"
        number = PlantMinTemperature(mock_hass, mock_config_entry, mock_plant)
        
        # Set the hass attribute manually since it's not set in the mock
        number.hass = mock_hass
        
        # Execute
        device_info = number.device_info
        
        # Verify
        assert device_info is not None
        assert "identifiers" in device_info
        assert (DOMAIN, mock_plant.unique_id) in device_info["identifiers"]