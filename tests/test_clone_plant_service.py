"""Integration tests for the clone_plant service."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.entity_registry as er

from custom_components.plant.services import async_setup_services
from homeassistant.const import ATTR_NAME
from custom_components.plant.const import (
    DOMAIN, SERVICE_CLONE_PLANT, FLOW_PLANT_INFO, DEVICE_TYPE_PLANT
)


class TestClonePlantService:
    """Test clone_plant service functionality."""

    @pytest.fixture
    def mock_hass(self):
        """Create mock Home Assistant instance."""
        hass = Mock(spec=HomeAssistant)
        hass.data = {DOMAIN: {}}
        hass.states = Mock()
        hass.services = Mock()
        hass.config_entries = Mock()
        return hass

    @pytest.fixture
    def mock_source_plant(self):
        """Create mock source plant device."""
        device = Mock()
        device.entity_id = "plant.source_plant"
        device.device_type = DEVICE_TYPE_PLANT
        device._plant_info = {
            ATTR_NAME: "Source Plant",
            "strain": "Test Strain",
            "breeder": "Test Breeder",
            "device_type": DEVICE_TYPE_PLANT
        }
        device.flowering_duration = Mock()
        device.flowering_duration.native_value = 14
        return device

    @pytest.mark.asyncio
    async def test_clone_plant_success(self, mock_hass, mock_source_plant):
        """Test successful plant cloning."""
        # Setup service call
        call = Mock(spec=ServiceCall)
        call.data = {
            "source_entity_id": "plant.source_plant",
            "name": "Cloned Plant"
        }

        # Setup hass.data with source plant
        mock_hass.data[DOMAIN] = {
            "source_entry_id": {
                "plant": mock_source_plant
            }
        }

        # Setup mock entity registry
        mock_entity_registry = Mock()
        mock_entity = Mock()
        mock_entity.original_name = "Cloned Plant"
        mock_entity.entity_id = "plant.cloned_plant"
        mock_entity_registry.entities.values.return_value = [mock_entity]
        
        # Setup mock config entry with proper data structure
        mock_source_entry = Mock()
        mock_source_entry.data = {
            FLOW_PLANT_INFO: {
                ATTR_NAME: "Source Plant",
                "strain": "Test Strain",
                "breeder": "Test Breeder"
            }
        }
        mock_hass.config_entries.async_get_entry = Mock(return_value=mock_source_entry)
        
        # Setup mock config entry flow
        mock_result = {
            "type": FlowResultType.CREATE_ENTRY,
            "result": Mock(entry_id="cloned_entry_id")
        }
        mock_hass.config_entries.flow.async_init = AsyncMock(return_value=mock_result)

        with patch('custom_components.plant.services.er.async_get', return_value=mock_entity_registry):
            # Setup services
            await async_setup_services(mock_hass)

            # Find the service function
            service_func = None
            for call_args in mock_hass.services.async_register.call_args_list:
                if call_args[0][1] == SERVICE_CLONE_PLANT:
                    service_func = call_args[0][2]
                    break

            assert service_func is not None, "clone_plant service not found"
            
            # Call the service
            response = await service_func(call)
            
            # Verify config entry flow was called
            mock_hass.config_entries.flow.async_init.assert_called_once()
            assert "success" in response

    @pytest.mark.asyncio
    async def test_clone_plant_source_not_found(self, mock_hass):
        """Test clone_plant with non-existent source plant."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "source_entity_id": "plant.nonexistent_plant",
            "name": "Cloned Plant"
        }

        # Setup empty hass.data
        mock_hass.data[DOMAIN] = {}

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_CLONE_PLANT:
                service_func = call_args[0][2]
                break

        # Call the service and expect HomeAssistantError
        with pytest.raises(HomeAssistantError, match="Source plant plant.nonexistent_plant not found"):
            await service_func(call)

    @pytest.mark.asyncio
    async def test_clone_plant_missing_source(self, mock_hass):
        """Test clone_plant with missing source entity."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "name": "Cloned Plant"
            # No source_entity_id provided
        }

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_CLONE_PLANT:
                service_func = call_args[0][2]
                break

        # Call the service and expect HomeAssistantError
        with pytest.raises(HomeAssistantError, match="Source plant entity ID is required"):
            await service_func(call)