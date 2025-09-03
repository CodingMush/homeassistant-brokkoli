"""Tests for the plant integration initialization."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.utility_meter.const import DATA_UTILITY
from custom_components.plant import (
    async_setup_entry,
    async_unload_entry,
    PlantDevice,
)
from custom_components.plant.const import (
    DOMAIN,
    FLOW_PLANT_INFO,
    DEVICE_TYPE_PLANT,
    ATTR_STRAIN,
    ATTR_PLANT,
)


@pytest.mark.asyncio
async def test_async_setup_entry_success(mock_hass, mock_config_entry):
    """Test successful setup of plant entry."""
    # Setup
    mock_config_entry.data = {
        FLOW_PLANT_INFO: {
            "name": "Test Plant",
            ATTR_STRAIN: "Test Strain",
            "device_type": DEVICE_TYPE_PLANT,
        }
    }
    
    # Mock the PlantDevice
    with patch('custom_components.plant.PlantDevice') as mock_plant_device:
        mock_plant_instance = Mock()
        mock_plant_instance.device_type = DEVICE_TYPE_PLANT
        mock_plant_instance.device_id = "test_device_id"
        mock_plant_instance.integral_entities = []
        mock_plant_instance.threshold_entities = []
        mock_plant_instance.meter_entities = []
        mock_plant_instance.dli = Mock()
        mock_plant_instance.dli.entity_id = "sensor.test_dli"
        # Mock the device_info property to return a proper dictionary
        mock_plant_instance.device_info = {
            "identifiers": {(DOMAIN, "test_entry_id")},
            "name": "Test Plant",
            "serial_number": "0001",
            "manufacturer": "Test Breeder",
            "model": "Test Strain",
            "model_id": "",
        }
        mock_plant_device.return_value = mock_plant_instance
        
        # Mock device registry
        with patch('custom_components.plant.dr.async_get') as mock_device_registry:
            mock_device_registry_instance = Mock()
            # Mock the async_get_or_create method to return a mock device
            mock_device_registry_instance.async_get_or_create = Mock(return_value=Mock())
            mock_device_registry.return_value = mock_device_registry_instance
            
            # Mock entity component
            with patch('custom_components.plant.EntityComponent') as mock_component:
                mock_component_instance = Mock()
                mock_component_instance.async_add_entities = AsyncMock()
                mock_component.return_value = mock_component_instance
                
                # Mock device registry functions
                with patch('custom_components.plant._plant_add_to_device_registry') as mock_add_to_registry:
                    mock_add_to_registry.return_value = AsyncMock()
                    
                    # Mock services setup
                    with patch('custom_components.plant.async_setup_services') as mock_setup_services:
                        mock_setup_services.return_value = AsyncMock()
                        
                        # Mock hass.config_entries.async_forward_entry_setups - correct path with proper async mock
                        mock_forward = AsyncMock()
                        mock_forward.return_value = None
                        with patch.object(mock_hass.config_entries, 'async_forward_entry_setups', mock_forward):
                            
                            # Mock _get_next_id
                            with patch('custom_components.plant._get_next_id') as mock_get_next_id:
                                mock_get_next_id.return_value = "0001"
                                
                                # Mock websocket commands
                                with patch('custom_components.plant.websocket_api.async_register_command') as mock_websocket:
                                    
                                    # Execute
                                    result = await async_setup_entry(mock_hass, mock_config_entry)
                                    
                                    # Verify
                                    assert result is True
                                    mock_plant_device.assert_called_once()
                                    mock_setup_services.assert_called_once()
                                    mock_component_instance.async_add_entities.assert_called_once()


@pytest.mark.asyncio
async def test_async_setup_entry_config_node(mock_hass, mock_config_entry):
    """Test setup of config node entry."""
    # Setup
    mock_config_entry.data = {
        "is_config": True,
        FLOW_PLANT_INFO: {
            "kwh_price": 0.3684
        }
    }
    
    # Execute
    result = await async_setup_entry(mock_hass, mock_config_entry)
    
    # Verify
    assert result is True
    assert mock_config_entry.entry_id in mock_hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_async_unload_entry_success(mock_hass, mock_config_entry):
    """Test successful unload of plant entry."""
    # Setup
    mock_hass.data[DOMAIN] = {
        mock_config_entry.entry_id: {
            ATTR_PLANT: Mock()
        }
    }
    # Initialize DATA_UTILITY in hass.data
    mock_hass.data[DATA_UTILITY] = {
        mock_config_entry.entry_id: {}
    }
    
    # Mock hass.config_entries.async_unload_platforms - correct path with AsyncMock
    mock_unload = AsyncMock()
    mock_unload.return_value = True
    with patch.object(mock_hass.config_entries, 'async_unload_platforms', mock_unload):
        
        # Mock async_unload_services
        mock_unload_services = AsyncMock()
        mock_unload_services.return_value = None
        with patch('custom_components.plant.async_unload_services', mock_unload_services):
            
            # Execute
            result = await async_unload_entry(mock_hass, mock_config_entry)
            
            # Verify
            assert result is True
            # After unloading, the entry should be removed from hass.data[DOMAIN]
            assert mock_config_entry.entry_id not in mock_hass.data.get(DOMAIN, {})


@pytest.mark.asyncio
async def test_async_unload_entry_config_node(mock_hass, mock_config_entry):
    """Test unload of config node entry."""
    # Setup
    mock_config_entry.data = {
        "is_config": True
    }
    mock_hass.data[DOMAIN] = {
        mock_config_entry.entry_id: {
            "config": {}
        }
    }
    
    # Execute
    result = await async_unload_entry(mock_hass, mock_config_entry)
    
    # Verify
    assert result is True
    assert mock_config_entry.entry_id not in mock_hass.data.get(DOMAIN, {})


def test_plant_device_initialization(mock_hass, mock_config_entry):
    """Test PlantDevice initialization."""
    # Setup
    mock_config_entry.data = {
        FLOW_PLANT_INFO: {
            "name": "Test Plant",
            ATTR_STRAIN: "Test Strain",
            "device_type": DEVICE_TYPE_PLANT,
        }
    }
    
    # Execute
    plant_device = PlantDevice(mock_hass, mock_config_entry)
    
    # Verify
    assert plant_device.name == "Test Plant"
    assert plant_device.device_type == DEVICE_TYPE_PLANT
    assert plant_device.entity_id is not None


def test_plant_device_device_info(mock_hass, mock_config_entry):
    """Test PlantDevice device_info property."""
    # Setup
    mock_config_entry.data = {
        FLOW_PLANT_INFO: {
            "name": "Test Plant",
            ATTR_STRAIN: "Test Strain",
            "device_type": DEVICE_TYPE_PLANT,
            "breeder": "Test Breeder",
        }
    }
    
    plant_device = PlantDevice(mock_hass, mock_config_entry)
    
    # Execute
    device_info = plant_device.device_info
    
    # Verify
    assert device_info is not None
    assert "identifiers" in device_info
    assert "name" in device_info
    assert device_info["name"] == "Test Plant"
    assert device_info["manufacturer"] == "Test Breeder"


def test_plant_device_extra_state_attributes(mock_hass, mock_config_entry):
    """Test PlantDevice extra_state_attributes property."""
    # Setup
    mock_config_entry.data = {
        FLOW_PLANT_INFO: {
            "name": "Test Plant",
            ATTR_STRAIN: "Test Strain",
            "device_type": DEVICE_TYPE_PLANT,
            "breeder": "Test Breeder",
        }
    }
    
    plant_device = PlantDevice(mock_hass, mock_config_entry)
    
    # Execute
    attributes = plant_device.extra_state_attributes
    
    # Verify
    assert attributes is not None
    assert "strain" in attributes
    assert "breeder" in attributes
    assert attributes["strain"] == "Test Strain"
    assert attributes["breeder"] == "Test Breeder"