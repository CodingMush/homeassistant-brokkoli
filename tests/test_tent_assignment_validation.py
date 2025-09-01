"""Test cases for tent assignment validation."""

import pytest
from unittest.mock import Mock
from homeassistant.core import HomeAssistant
from homeassistant.helpers.service import ServiceCall

from custom_components.plant.const import DOMAIN, DEVICE_TYPE_PLANT, DEVICE_TYPE_TENT
from custom_components.plant.services import async_setup_services


class TestTentAssignmentValidation:
    """Test tent assignment validation."""

    @pytest.fixture
    def mock_hass(self):
        """Create mock Home Assistant instance."""
        hass = Mock(spec=HomeAssistant)
        hass.data = {DOMAIN: {}}
        hass.services = Mock()
        return hass

    @pytest.fixture
    def mock_plant_device(self):
        """Create mock plant device."""
        device = Mock()
        device.entity_id = "plant.test_plant"
        device.device_type = DEVICE_TYPE_PLANT
        device.assign_to_tent = Mock()
        return device

    @pytest.fixture
    def mock_tent_device(self):
        """Create mock tent device."""
        device = Mock()
        device.entity_id = "plant.test_tent"
        device.device_type = DEVICE_TYPE_TENT
        return device

    @pytest.mark.asyncio
    async def test_assign_plant_to_itself_raises_error(self, mock_hass, mock_plant_device):
        """Test that assigning a plant to itself raises an error."""
        # Setup service call with same plant and tent entity IDs
        call = Mock(spec=ServiceCall)
        call.data = {
            "plant_entity": "plant.test_plant",
            "tent_entity": "plant.test_plant"  # Same as plant_entity
        }

        # Create a mock tent device that's the same as the plant device
        mock_tent_device = Mock()
        mock_tent_device.entity_id = "plant.test_plant"
        mock_tent_device.device_type = DEVICE_TYPE_TENT

        # Setup hass.data with plant and tent (same entity ID)
        mock_hass.data[DOMAIN] = {
            "plant_entry_id": {
                "plant": mock_plant_device
            },
            "tent_entry_id": {
                "plant": mock_tent_device  # Same entity_id but as tent
            }
        }
        
        # Make sure the plant device has the correct type
        mock_plant_device.device_type = DEVICE_TYPE_PLANT

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == "assign_to_tent":
                service_func = call_args[0][2]
                break

        assert service_func is not None, "assign_to_tent service not found"

        # Call the service - should raise an error
        with pytest.raises(Exception) as exc_info:
            await service_func(call)

        # Verify the error message - updated to match the new validation logic
        assert "is not a tent" in str(exc_info.value)

        # Verify plant assign_to_tent was not called
        mock_plant_device.assign_to_tent.assert_not_called()

    @pytest.mark.asyncio
    async def test_assign_plant_to_different_tent_succeeds(self, mock_hass, mock_plant_device, mock_tent_device):
        """Test that assigning a plant to a different tent succeeds."""
        # Setup service call with different plant and tent entity IDs
        call = Mock(spec=ServiceCall)
        call.data = {
            "plant_entity": "plant.test_plant",
            "tent_entity": "plant.test_tent"
        }

        # Setup hass.data with plant and tent
        mock_hass.data[DOMAIN] = {
            "plant_entry_id": {
                "plant": mock_plant_device
            },
            "tent_entry_id": {
                "plant": mock_tent_device
            }
        }

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == "assign_to_tent":
                service_func = call_args[0][2]
                break

        assert service_func is not None, "assign_to_tent service not found"

        # Call the service - should succeed
        await service_func(call)

        # Verify plant assign_to_tent was called
        mock_plant_device.assign_to_tent.assert_called_once_with("plant.test_tent", True)