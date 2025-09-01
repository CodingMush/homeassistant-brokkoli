"""Integration tests for the move_to_area service."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.device_registry as dr
import homeassistant.helpers.area_registry as ar

from custom_components.plant.services import async_setup_services
from custom_components.plant.const import DOMAIN, SERVICE_MOVE_TO_AREA


class TestMoveToAreaService:
    """Test move_to_area service functionality."""

    @pytest.fixture
    def mock_hass(self):
        """Create mock Home Assistant instance."""
        hass = Mock(spec=HomeAssistant)
        hass.data = {DOMAIN: {}}
        hass.states = Mock()
        hass.services = Mock()
        return hass

    @pytest.mark.asyncio
    async def test_move_to_area_success(self, mock_hass):
        """Test successful move to area."""
        # Setup service call
        call = Mock(spec=ServiceCall)
        call.data = {
            "device_id": ["device.test_device"],
            "area_id": "area.test_area"
        }

        # Setup mock device registry
        mock_device_registry = Mock()
        mock_device = Mock()
        mock_device_registry.async_get.return_value = mock_device
        
        # Setup mock area registry
        mock_area_registry = Mock()
        mock_area = Mock()
        mock_area.name = "Test Area"
        mock_area_registry.async_get_area.return_value = mock_area

        with patch('custom_components.plant.services.dr.async_get', return_value=mock_device_registry):
            with patch('custom_components.plant.services.ar.async_get', return_value=mock_area_registry):
                # Setup services
                await async_setup_services(mock_hass)

                # Find the service function
                service_func = None
                for call_args in mock_hass.services.async_register.call_args_list:
                    if call_args[0][1] == SERVICE_MOVE_TO_AREA:
                        service_func = call_args[0][2]
                        break

                assert service_func is not None, "move_to_area service not found"

                # Call the service
                await service_func(call)

                # Verify device was updated with area
                mock_device_registry.async_update_device.assert_called_once_with(
                    "device.test_device",
                    area_id="area.test_area"
                )

    @pytest.mark.asyncio
    async def test_move_to_area_invalid_area(self, mock_hass):
        """Test move_to_area with invalid area."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "device_id": ["device.test_device"],
            "area_id": "area.invalid_area"
        }

        # Setup mock device registry
        mock_device_registry = Mock()
        mock_device = Mock()
        mock_device_registry.async_get.return_value = mock_device
        
        # Setup mock area registry with no area found
        mock_area_registry = Mock()
        mock_area_registry.async_get_area.return_value = None

        with patch('custom_components.plant.services.dr.async_get', return_value=mock_device_registry):
            with patch('custom_components.plant.services.ar.async_get', return_value=mock_area_registry):
                # Setup services
                await async_setup_services(mock_hass)

                # Find the service function
                service_func = None
                for call_args in mock_hass.services.async_register.call_args_list:
                    if call_args[0][1] == SERVICE_MOVE_TO_AREA:
                        service_func = call_args[0][2]
                        break

                # Call the service - should return early without error
                await service_func(call)

                # Verify device was not updated
                mock_device_registry.async_update_device.assert_not_called()

    @pytest.mark.asyncio
    async def test_move_to_area_invalid_device(self, mock_hass):
        """Test move_to_area with invalid device."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "device_id": ["device.invalid_device"],
            "area_id": "area.test_area"
        }

        # Setup mock device registry with no device found
        mock_device_registry = Mock()
        mock_device_registry.async_get.return_value = None
        
        # Setup mock area registry
        mock_area_registry = Mock()
        mock_area = Mock()
        mock_area.name = "Test Area"
        mock_area_registry.async_get_area.return_value = mock_area

        with patch('custom_components.plant.services.dr.async_get', return_value=mock_device_registry):
            with patch('custom_components.plant.services.ar.async_get', return_value=mock_area_registry):
                # Setup services
                await async_setup_services(mock_hass)

                # Find the service function
                service_func = None
                for call_args in mock_hass.services.async_register.call_args_list:
                    if call_args[0][1] == SERVICE_MOVE_TO_AREA:
                        service_func = call_args[0][2]
                        break

                # Call the service - should return early without error
                await service_func(call)

                # Verify device was not updated
                mock_device_registry.async_update_device.assert_not_called()

    @pytest.mark.asyncio
    async def test_move_to_area_single_device(self, mock_hass):
        """Test move_to_area with single device (not list)."""
        # Setup service call with single device ID (not list)
        call = Mock(spec=ServiceCall)
        call.data = {
            "device_id": "device.test_device",
            "area_id": "area.test_area"
        }

        # Setup mock device registry
        mock_device_registry = Mock()
        mock_device = Mock()
        mock_device_registry.async_get.return_value = mock_device
        
        # Setup mock area registry
        mock_area_registry = Mock()
        mock_area = Mock()
        mock_area.name = "Test Area"
        mock_area_registry.async_get_area.return_value = mock_area

        with patch('custom_components.plant.services.dr.async_get', return_value=mock_device_registry):
            with patch('custom_components.plant.services.ar.async_get', return_value=mock_area_registry):
                # Setup services
                await async_setup_services(mock_hass)

                # Find the service function
                service_func = None
                for call_args in mock_hass.services.async_register.call_args_list:
                    if call_args[0][1] == SERVICE_MOVE_TO_AREA:
                        service_func = call_args[0][2]
                        break

                # Call the service
                await service_func(call)

                # Verify device was updated with area
                mock_device_registry.async_update_device.assert_called_once_with(
                    "device.test_device",
                    area_id="area.test_area"
                )

    @pytest.mark.asyncio
    async def test_move_to_area_remove_from_area(self, mock_hass):
        """Test move_to_area with empty area_id to remove from area."""
        # Setup service call with empty area_id
        call = Mock(spec=ServiceCall)
        call.data = {
            "device_id": ["device.test_device"],
            "area_id": ""  # Empty area_id to remove from area
        }

        # Setup mock device registry
        mock_device_registry = Mock()
        mock_device = Mock()
        mock_device_registry.async_get.return_value = mock_device
        
        # Setup mock area registry
        mock_area_registry = Mock()
        mock_area_registry.async_get_area.return_value = None  # No area validation for empty ID

        with patch('custom_components.plant.services.dr.async_get', return_value=mock_device_registry):
            with patch('custom_components.plant.services.ar.async_get', return_value=mock_area_registry):
                # Setup services
                await async_setup_services(mock_hass)

                # Find the service function
                service_func = None
                for call_args in mock_hass.services.async_register.call_args_list:
                    if call_args[0][1] == SERVICE_MOVE_TO_AREA:
                        service_func = call_args[0][2]
                        break

                # Call the service
                await service_func(call)

                # Verify device was updated with empty area_id
                mock_device_registry.async_update_device.assert_called_once_with(
                    "device.test_device",
                    area_id=""
                )