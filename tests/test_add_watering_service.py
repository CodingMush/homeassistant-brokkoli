"""Integration tests for the add_watering service."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from homeassistant.core import HomeAssistant, ServiceCall
from datetime import datetime

from custom_components.plant.services import async_setup_services
from custom_components.plant.const import DOMAIN, SERVICE_ADD_WATERING, DEVICE_TYPE_PLANT


class TestAddWateringService:
    """Test add_watering service functionality."""

    @pytest.fixture
    def mock_hass(self):
        """Create mock Home Assistant instance."""
        hass = Mock(spec=HomeAssistant)
        hass.data = {DOMAIN: {}}
        hass.states = Mock()
        hass.services = Mock()
        return hass

    @pytest.fixture
    def mock_plant_device(self):
        """Create mock plant device with watering functionality."""
        device = Mock()
        device.entity_id = "plant.test_plant"
        device.device_type = DEVICE_TYPE_PLANT
        
        # Mock journal attribute with async method
        mock_journal = Mock()
        mock_journal.state = "Previous entry"
        mock_journal.async_set_value = AsyncMock()
        device.journal = mock_journal
        
        # Mock total_water_consumption attribute
        mock_twc = Mock()
        mock_twc.state = "1.5"
        mock_twc.async_write_ha_state = Mock()
        mock_twc.add_manual_watering = AsyncMock()
        device.total_water_consumption = mock_twc
        
        return device

    @pytest.mark.asyncio
    async def test_add_watering_success(self, mock_hass, mock_plant_device):
        """Test successful watering addition."""
        # Setup service call
        call = Mock(spec=ServiceCall)
        call.data = {
            "entity_id": "plant.test_plant",
            "amount_liters": 0.5,
            "note": "Test watering"
        }

        # Setup hass.data with plant
        mock_hass.data[DOMAIN] = {
            "test_entry_id": {
                "plant": mock_plant_device
            }
        }

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_ADD_WATERING:
                service_func = call_args[0][2]
                break

        assert service_func is not None, "add_watering service not found"
        
        # Call the service
        await service_func(call)
        
        # Verify journal was updated
        mock_plant_device.journal.async_set_value.assert_called_once()
        
        # Verify total water consumption was updated
        mock_plant_device.total_water_consumption.add_manual_watering.assert_called_once_with(0.5, "Test watering")

    @pytest.mark.asyncio
    async def test_add_watering_no_amount(self, mock_hass, mock_plant_device):
        """Test add_watering with no amount specified."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "entity_id": "plant.test_plant"
            # No amount_liters specified
        }

        # Setup hass.data with plant
        mock_hass.data[DOMAIN] = {
            "test_entry_id": {
                "plant": mock_plant_device
            }
        }

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_ADD_WATERING:
                service_func = call_args[0][2]
                break

        # Call the service - should return early without error
        await service_func(call)
        
        # Verify no updates were made
        mock_plant_device.journal.async_set_value.assert_not_called()
        mock_plant_device.total_water_consumption.add_manual_watering.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_watering_plant_not_found(self, mock_hass):
        """Test add_watering with non-existent plant."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "entity_id": "plant.nonexistent_plant",
            "amount_liters": 0.5
        }

        # Setup empty hass.data
        mock_hass.data[DOMAIN] = {}

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_ADD_WATERING:
                service_func = call_args[0][2]
                break

        # Call the service - should return early without error
        await service_func(call)