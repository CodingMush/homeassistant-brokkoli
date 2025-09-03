"""Tests for plant helper functions."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from custom_components.plant.plant_helpers import PlantHelper
from custom_components.plant.const import (
    DOMAIN,
    READING_TEMPERATURE,
    READING_MOISTURE,
    READING_CONDUCTIVITY,
    READING_ILLUMINANCE,
    READING_HUMIDITY,
    READING_CO2,
    READING_PPFD,
    READING_DLI,
    FLOW_PLANT_INFO,
    CONF_DEFAULT_MAX_MOISTURE,
    CONF_DEFAULT_MIN_MOISTURE,
    CONF_DEFAULT_MAX_ILLUMINANCE,
    CONF_DEFAULT_MIN_ILLUMINANCE,
    CONF_DEFAULT_MAX_DLI,
    CONF_DEFAULT_MIN_DLI,
    CONF_DEFAULT_MAX_TEMPERATURE,
    CONF_DEFAULT_MIN_TEMPERATURE,
    CONF_DEFAULT_MAX_CONDUCTIVITY,
    CONF_DEFAULT_MIN_CONDUCTIVITY,
    CONF_DEFAULT_MAX_HUMIDITY,
    CONF_DEFAULT_MIN_HUMIDITY,
    CONF_DEFAULT_MAX_CO2,
    CONF_DEFAULT_MIN_CO2,
    CONF_DEFAULT_MAX_WATER_CONSUMPTION,
    CONF_DEFAULT_MIN_WATER_CONSUMPTION,
    CONF_DEFAULT_MAX_FERTILIZER_CONSUMPTION,
    CONF_DEFAULT_MIN_FERTILIZER_CONSUMPTION,
    CONF_DEFAULT_MAX_POWER_CONSUMPTION,
    CONF_DEFAULT_MIN_POWER_CONSUMPTION,
    ATTR_STRAIN,
    ATTR_BREEDER,
    DATA_SOURCE_PLANTBOOK,
    DOMAIN_PLANTBOOK,  # This is "seedfinder"
)


@pytest.mark.asyncio
async def test_plant_helper_initialization(mock_hass):
    """Test PlantHelper initialization."""
    # Setup
    mock_hass.config.components = []
    helper = PlantHelper(hass=mock_hass)
    
    # Verify
    assert helper._hass == mock_hass


@pytest.mark.asyncio
async def test_plant_helper_generate_configentry(mock_hass):
    """Test PlantHelper generate_configentry method."""
    # Setup
    mock_hass.config.components = []
    mock_hass.config_entries = Mock()
    mock_hass.config_entries.async_entries = Mock(return_value=[])
    
    helper = PlantHelper(hass=mock_hass)
    
    test_config = {
        "name": "Test Plant",
        "strain": "Test Strain",
        "sensors": {},
    }
    
    # Execute
    result = await helper.generate_configentry(config=test_config)
    
    # Verify
    assert result is not None
    assert FLOW_PLANT_INFO in result
    assert result[FLOW_PLANT_INFO]["name"] == "Test Plant"
    assert result[FLOW_PLANT_INFO]["strain"] == "Test Strain"


@pytest.mark.asyncio
async def test_plant_helper_get_plantbook_data_success(mock_hass):
    """Test PlantHelper get_plantbook_data method with successful response."""
    # Setup
    mock_hass.config.components = [DOMAIN_PLANTBOOK]  # This is "seedfinder"
    mock_hass.services = Mock()
    mock_hass.services.async_call = AsyncMock(return_value={
        "pid": "test_pid",
        "strain": "Test Strain",
        "breeder": "Test Breeder",
        "flowertime": "60",
        "image_url": "http://example.com/image.jpg",
        "type": "test_type",
        "feminized": "yes",
        "timestamp": "2023-01-01",
        "website": "http://example.com",
        "infotext1": "info1",
        "infotext2": "info2",
        "effects": "effects",
        "smell": "smell",
        "taste": "taste",
        "lineage": "lineage",
    })
    
    helper = PlantHelper(hass=mock_hass)
    
    test_config = {
        "strain": "Test Strain",
        "breeder": "Test Breeder"
    }
    
    # Execute
    result = await helper.get_plantbook_data(config=test_config)
    
    # Verify
    assert result is not None
    assert FLOW_PLANT_INFO in result
    assert result[FLOW_PLANT_INFO]["strain"] == "Test Strain"
    assert result[FLOW_PLANT_INFO]["data_source"] == DATA_SOURCE_PLANTBOOK


@pytest.mark.asyncio
async def test_plant_helper_get_plantbook_data_no_token(mock_hass):
    """Test PlantHelper get_plantbook_data method when no token is available."""
    # Setup
    mock_hass.config.components = []  # No plantbook component
    
    helper = PlantHelper(hass=mock_hass)
    
    test_config = {
        "strain": "Test Strain",
        "breeder": "Test Breeder"
    }
    
    # Execute
    result = await helper.get_plantbook_data(config=test_config)
    
    # Verify
    assert result == {}


@pytest.mark.asyncio
async def test_plant_helper_get_plantbook_data_exception(mock_hass):
    """Test PlantHelper get_plantbook_data method when exception occurs."""
    # Setup
    mock_hass.config.components = [DOMAIN_PLANTBOOK]  # This is "seedfinder"
    mock_hass.services = Mock()
    mock_hass.services.async_call = AsyncMock(side_effect=Exception("Test error"))
    
    helper = PlantHelper(hass=mock_hass)
    
    test_config = {
        "strain": "Test Strain",
        "breeder": "Test Breeder"
    }
    
    # Execute
    result = await helper.get_plantbook_data(config=test_config)
    
    # Verify
    assert result == {}


# Remove the tests for get_dli_from_ppfd method since it doesn't exist in the actual implementation