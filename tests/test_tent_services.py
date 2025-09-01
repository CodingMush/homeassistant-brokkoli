"""Unit tests for tent assignment services."""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
import homeassistant.helpers.entity_registry as er

from custom_components.plant.services import async_setup_services
from custom_components.plant.const import (
    DOMAIN,
    SERVICE_CREATE_TENT,
    SERVICE_ASSIGN_TO_TENT,
    SERVICE_UNASSIGN_FROM_TENT,
    SERVICE_REMOVE_TENT,
    SERVICE_REASSIGN_TO_TENT,
    # SERVICE_MIGRATE_TO_VIRTUAL_SENSORS,
    ATTR_TENT_ASSIGNMENT,
    ATTR_ASSIGNED_PLANTS,
    FLOW_TENT_INFO,
    FLOW_TENT_ENTITY,
    FLOW_MIGRATE_SENSORS,
    DEVICE_TYPE_PLANT,
    DEVICE_TYPE_TENT,
)


class TestTentAssignmentServices:
    """Test tent assignment service functionality."""

    @pytest.fixture
    def mock_hass(self):
        """Create mock Home Assistant instance."""
        hass = Mock(spec=HomeAssistant)
        hass.states = Mock()
        hass.data = {DOMAIN: {}}
        hass.services = Mock()
        hass.config_entries = Mock()
        hass.config_entries.async_entries = Mock(return_value=[])
        return hass

    @pytest.fixture
    def mock_plant_device(self):
        """Create mock plant device."""
        device = Mock()
        device.entity_id = "plant.test_plant"
        device.device_type = DEVICE_TYPE_PLANT
        device.tent_assignment = None
        device.assign_to_tent = Mock()
        device.unassign_from_tent = Mock()
        device.migrate_to_tent = AsyncMock()
        return device

    @pytest.fixture
    def mock_tent_device(self):
        """Create mock tent device."""
        device = Mock()
        device.entity_id = "plant.test_tent"
        device.device_type = DEVICE_TYPE_TENT
        device._assigned_plants = []
        device.register_plant = Mock()
        device.unregister_plant = Mock()
        return device

    @pytest.mark.asyncio
    async def test_assign_to_tent_success(self, mock_hass, mock_plant_device, mock_tent_device):
        """Test successful plant assignment to tent."""
        # Mock service call data
        call = Mock(spec=ServiceCall)
        call.data = {
            "plant_entity": "plant.test_plant",
            FLOW_TENT_ENTITY: "plant.test_tent",
            FLOW_MIGRATE_SENSORS: True
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
            if call_args[0][1] == SERVICE_ASSIGN_TO_TENT:
                service_func = call_args[0][2]
                break

        assert service_func is not None, "assign_to_tent service not found"

        # Call assign service
        await service_func(call)

        # Verify plant was assigned to tent
        mock_plant_device.assign_to_tent.assert_called_once_with(
            "plant.test_tent", True
        )

    @pytest.mark.asyncio
    async def test_assign_to_tent_invalid_plant(self, mock_hass):
        """Test assignment fails with invalid plant entity."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "plant_entity": "plant.nonexistent",
            FLOW_TENT_ENTITY: "plant.test_tent",
        }

        # Setup empty hass.data
        mock_hass.data[DOMAIN] = {}

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_ASSIGN_TO_TENT:
                service_func = call_args[0][2]
                break

        assert service_func is not None, "assign_to_tent service not found"

        # Should raise HomeAssistantError
        with pytest.raises(Exception):
            await service_func(call)

    @pytest.mark.asyncio
    async def test_assign_to_tent_invalid_tent(self, mock_hass, mock_plant_device):
        """Test assignment fails with invalid tent entity.""" 
        call = Mock(spec=ServiceCall)
        call.data = {
            "plant_entity": "plant.test_plant",
            FLOW_TENT_ENTITY: "plant.nonexistent_tent",
        }

        # Setup hass.data with only plant
        mock_hass.data[DOMAIN] = {
            "plant_entry_id": {
                "plant": mock_plant_device
            }
        }

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_ASSIGN_TO_TENT:
                service_func = call_args[0][2]
                break

        assert service_func is not None, "assign_to_tent service not found"

        # Should raise HomeAssistantError
        with pytest.raises(Exception):
            await service_func(call)

    @pytest.mark.asyncio
    async def test_unassign_from_tent_success(self, mock_hass, mock_plant_device, mock_tent_device):
        """Test successful plant unassignment from tent."""
        # Plant is assigned to tent
        mock_plant_device.tent_assignment = "plant.test_tent"
        mock_tent_device._assigned_plants = ["plant.test_plant"]
        
        call = Mock(spec=ServiceCall)
        call.data = {"plant_entity": "plant.test_plant"}

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
            if call_args[0][1] == SERVICE_UNASSIGN_FROM_TENT:
                service_func = call_args[0][2]
                break

        assert service_func is not None, "unassign_from_tent service not found"

        # Call unassign service
        await service_func(call)

        # Verify plant was unassigned from tent
        mock_plant_device.unassign_from_tent.assert_called_once()

    @pytest.mark.asyncio
    async def test_unassign_from_tent_not_assigned(self, mock_hass, mock_plant_device):
        """Test unassigning plant that's not assigned to any tent."""
        # Plant has no tent assignment
        mock_plant_device.tent_assignment = None
        
        call = Mock(spec=ServiceCall)
        call.data = {"plant_entity": "plant.test_plant"}

        # Setup hass.data with plant
        mock_hass.data[DOMAIN] = {
            "plant_entry_id": {
                "plant": mock_plant_device
            }
        }

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_UNASSIGN_FROM_TENT:
                service_func = call_args[0][2]
                break

        assert service_func is not None, "unassign_from_tent service not found"

        # Call the service - should not raise an error but should log a warning
        await service_func(call)

    def test_service_registration(self, mock_hass):
        """Test tent services are properly registered."""
        # Setup services
        import asyncio
        asyncio.run(async_setup_services(mock_hass))
        
        # Verify the services were registered
        registered_services = []
        for call_args in mock_hass.services.async_register.call_args_list:
            registered_services.append(call_args[0][1])
        
        assert SERVICE_ASSIGN_TO_TENT in registered_services
        assert SERVICE_UNASSIGN_FROM_TENT in registered_services
        assert SERVICE_REASSIGN_TO_TENT in registered_services
        assert SERVICE_CREATE_TENT in registered_services
        assert SERVICE_REMOVE_TENT in registered_services
