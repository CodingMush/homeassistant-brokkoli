"""Tests for the plant integration config flow."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from homeassistant.data_entry_flow import FlowResultType
from custom_components.plant.config_flow import PlantConfigFlow
from custom_components.plant.const import (
    DOMAIN,
    FLOW_PLANT_INFO,
    DEVICE_TYPE_PLANT,
    DEVICE_TYPE_CONFIG,
    DEVICE_TYPE_CYCLE,
    ATTR_STRAIN,
    ATTR_DEVICE_TYPE,
)


@pytest.fixture
def config_flow():
    """Create a config flow instance."""
    flow = PlantConfigFlow()
    flow.hass = Mock()
    # Mock the _async_current_entries method to return a config entry
    mock_entry = Mock()
    mock_entry.data = {
        "is_config": True, 
        FLOW_PLANT_INFO: {
            ATTR_DEVICE_TYPE: DEVICE_TYPE_CONFIG,
            "default_icon": "🥦",
            "default_growth_phase": "vegetative",
            "default_pot_size": 10.0,
            "default_water_capacity": 1000,
        }
    }
    flow._async_current_entries = Mock(return_value=[mock_entry])
    return flow


def test_config_flow_initialization(config_flow):
    """Test PlantConfigFlow initialization."""
    # Verify
    assert hasattr(config_flow, "plant_info")
    assert config_flow.plant_info == {}
    assert config_flow.error is None


@pytest.mark.asyncio
async def test_config_flow_async_step_user(config_flow):
    """Test the user step of config flow."""
    # Execute - first call with no user input should show form
    result = await config_flow.async_step_user(user_input=None)
    
    # Should show the form to select device type
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"


@pytest.mark.asyncio
async def test_config_flow_async_step_user_with_input(config_flow):
    """Test the user step of config flow with input."""
    # Setup user input for plant device
    user_input = {
        ATTR_DEVICE_TYPE: DEVICE_TYPE_PLANT,
    }
    
    # Execute
    result = await config_flow.async_step_user(user_input=user_input)
    
    # Verify - should show the plant form
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "plant"


@pytest.mark.asyncio
async def test_config_flow_async_step_limits(config_flow):
    """Test the limits step of config flow."""
    # Setup
    config_flow.plant_info = {
        "name": "Test Plant",
        ATTR_STRAIN: "Test Strain",
    }
    
    # Mock PlantHelper
    with patch('custom_components.plant.config_flow.PlantHelper') as mock_helper:
        mock_helper_instance = Mock()
        mock_helper_instance.generate_configentry = AsyncMock(return_value={
            FLOW_PLANT_INFO: {
                "opb_display_pid": "Test Display PID"
            }
        })
        mock_helper.return_value = mock_helper_instance
        
        # Execute
        result = await config_flow.async_step_limits(user_input=None)
        
        # Verify
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "limits"


@pytest.mark.asyncio
async def test_config_flow_async_step_limits_with_input(config_flow):
    """Test the limits step of config flow with input."""
    # Setup
    config_flow.plant_info = {
        "name": "Test Plant",
        ATTR_STRAIN: "Test Strain",
    }
    
    user_input = {
        "max_temperature": 30,
        "min_temperature": 10,
        "max_moisture": 60,
        "min_moisture": 20,
        "right_plant": True,
    }
    
    # Mock PlantHelper
    with patch('custom_components.plant.config_flow.PlantHelper') as mock_helper:
        mock_helper_instance = Mock()
        mock_helper_instance.generate_configentry = AsyncMock(return_value={
            FLOW_PLANT_INFO: {}
        })
        mock_helper.return_value = mock_helper_instance
        
        # Mock config entries
        mock_entry = Mock()
        mock_entry.data = {"is_config": True, FLOW_PLANT_INFO: {
            "default_max_moisture": 60,
            "default_min_moisture": 20,
            "default_max_temperature": 30,
            "default_min_temperature": 10,
        }}
        config_flow._async_current_entries = Mock(return_value=[mock_entry])
        
        # Execute
        result = await config_flow.async_step_limits(user_input=user_input)
        
        # Verify
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"][FLOW_PLANT_INFO]["name"] == "Test Plant"


# Remove the tests for plant_details step since it doesn't exist in the actual implementation