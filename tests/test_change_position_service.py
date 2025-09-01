"""Integration tests for the change_position service."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from custom_components.plant.services import async_setup_services
from custom_components.plant.const import DOMAIN, SERVICE_CHANGE_POSITION, DEVICE_TYPE_PLANT, ATTR_POSITION_X, ATTR_POSITION_Y


class TestChangePositionService:
    """Test change_position service functionality."""

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
        """Create mock plant device with position functionality."""
        device = Mock()
        device.entity_id = "plant.test_plant"
        device.device_type = DEVICE_TYPE_PLANT
        
        # Mock location history
        mock_location_history = Mock()
        mock_location_history.add_position = Mock()
        device.location_history = mock_location_history
        
        return device

    @pytest.mark.asyncio
    async def test_change_position_success(self, mock_hass, mock_plant_device):
        """Test successful position change."""
        # Setup service call
        call = Mock(spec=ServiceCall)
        call.data = {
            "entity_id": "plant.test_plant",
            ATTR_POSITION_X: 10.5,
            ATTR_POSITION_Y: 20.3
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
            if call_args[0][1] == SERVICE_CHANGE_POSITION:
                service_func = call_args[0][2]
                break

        assert service_func is not None, "change_position service not found"
        
        # Call the service
        await service_func(call)
        
        # Verify position was updated
        mock_plant_device.location_history.add_position.assert_called_once_with(10.5, 20.3)

    @pytest.mark.asyncio
    async def test_change_position_missing_entity(self, mock_hass):
        """Test change_position with missing entity."""
        call = Mock(spec=ServiceCall)
        call.data = {
            ATTR_POSITION_X: 10.5,
            ATTR_POSITION_Y: 20.3
            # No entity_id specified
        }

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_CHANGE_POSITION:
                service_func = call_args[0][2]
                break

        # Call the service and expect HomeAssistantError
        with pytest.raises(HomeAssistantError, match="Keine Pflanzen-Entity angegeben"):
            await service_func(call)

    @pytest.mark.asyncio
    async def test_change_position_plant_not_found(self, mock_hass):
        """Test change_position with non-existent plant."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "entity_id": "plant.nonexistent_plant",
            ATTR_POSITION_X: 10.5,
            ATTR_POSITION_Y: 20.3
        }

        # Setup empty hass.data
        mock_hass.data[DOMAIN] = {}

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_CHANGE_POSITION:
                service_func = call_args[0][2]
                break

        # Call the service and expect HomeAssistantError
        with pytest.raises(HomeAssistantError, match="Pflanze plant.nonexistent_plant nicht gefunden"):
            await service_func(call)

    @pytest.mark.asyncio
    async def test_change_position_no_location_sensor(self, mock_hass):
        """Test change_position with plant that has no location sensor."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "entity_id": "plant.test_plant",
            ATTR_POSITION_X: 10.5,
            ATTR_POSITION_Y: 20.3
        }

        # Create plant device without location history
        mock_plant_device = Mock()
        mock_plant_device.entity_id = "plant.test_plant"
        mock_plant_device.device_type = DEVICE_TYPE_PLANT
        mock_plant_device.location_history = None

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
            if call_args[0][1] == SERVICE_CHANGE_POSITION:
                service_func = call_args[0][2]
                break

        # Call the service - should log warning but not raise error
        await service_func(call)