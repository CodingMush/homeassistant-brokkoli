"""Integration tests for the move_to_cycle service."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.device_registry as dr
import homeassistant.helpers.entity_registry as er

from custom_components.plant.services import async_setup_services
from custom_components.plant.const import DOMAIN, SERVICE_MOVE_TO_CYCLE, DEVICE_TYPE_PLANT, DEVICE_TYPE_CYCLE


class TestMoveToCycleService:
    """Test move_to_cycle service functionality."""

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
        """Create mock plant device."""
        device = Mock()
        device.entity_id = "plant.test_plant"
        device.device_type = DEVICE_TYPE_PLANT
        device.unique_id = "plant_unique_id"
        return device

    @pytest.fixture
    def mock_cycle_device(self):
        """Create mock cycle device."""
        device = Mock()
        device.entity_id = "cycle.test_cycle"
        device.device_type = DEVICE_TYPE_CYCLE
        device.unique_id = "cycle_unique_id"
        # Add flowering_duration as an AsyncMock
        device.flowering_duration = AsyncMock()
        device.flowering_duration._update_cycle_duration = AsyncMock()
        return device

    @pytest.mark.asyncio
    async def test_move_to_cycle_success(self, mock_hass, mock_plant_device, mock_cycle_device):
        """Test successful move to cycle."""
        # Setup service call
        call = Mock(spec=ServiceCall)
        call.data = {
            "plant_entity": ["plant.test_plant"],
            "cycle_entity": "cycle.test_cycle"
        }

        # Setup hass.data with plant and cycle
        mock_hass.data[DOMAIN] = {
            "plant_entry_id": {
                "plant": mock_plant_device
            },
            "cycle_entry_id": {
                "plant": mock_cycle_device
            }
        }

        # Setup mock device registry
        mock_device_registry = Mock()
        mock_plant_device_obj = Mock()
        mock_plant_device_obj.id = "plant_device_id"
        mock_plant_device_obj.via_device_id = None
        mock_plant_device_obj.unique_id = "plant_unique_id"
        mock_cycle_device_obj = Mock()
        mock_cycle_device_obj.id = "cycle_device_id"
        mock_cycle_device_obj.unique_id = "cycle_unique_id"
        
        # Mock device_registry.async_get_device to return the right devices
        def mock_async_get_device(identifiers):
            identifier_tuple = tuple(identifiers)[0]
            if identifier_tuple == (DOMAIN, "plant_unique_id"):
                return mock_plant_device_obj
            elif identifier_tuple == (DOMAIN, "cycle_unique_id"):
                return mock_cycle_device_obj
            return None
            
        mock_device_registry.async_get_device.side_effect = mock_async_get_device
        mock_device_registry.async_update_device = Mock()

        # Setup mock entity registry
        mock_entity_registry = Mock()
        mock_cycle_entity = Mock()
        mock_cycle_entity.unique_id = "cycle_unique_id"
        mock_plant_entity = Mock()
        mock_plant_entity.unique_id = "plant_unique_id"
        
        def mock_async_get(entity_id):
            if entity_id == "cycle.test_cycle":
                return mock_cycle_entity
            elif entity_id == "plant.test_plant":
                return mock_plant_entity
            return None
            
        mock_entity_registry.async_get.side_effect = mock_async_get

        with patch('custom_components.plant.services.dr.async_get', return_value=mock_device_registry):
            with patch('custom_components.plant.services.er.async_get', return_value=mock_entity_registry):
                # Setup services
                await async_setup_services(mock_hass)

                # Find the service function
                service_func = None
                for call_args in mock_hass.services.async_register.call_args_list:
                    if call_args[0][1] == SERVICE_MOVE_TO_CYCLE:
                        service_func = call_args[0][2]
                        break

                assert service_func is not None, "move_to_cycle service not found"

                # Call the service
                await service_func(call)

                # Verify device was updated with cycle
                mock_device_registry.async_update_device.assert_called_once_with(
                    "plant_device_id",
                    via_device_id="cycle_device_id"
                )

    @pytest.mark.asyncio
    async def test_move_to_cycle_invalid_plant(self, mock_hass, mock_cycle_device):
        """Test move_to_cycle with invalid plant entity."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "plant_entity": ["plant.invalid_plant"],
            "cycle_entity": "cycle.test_cycle"
        }

        # Setup hass.data with only cycle
        mock_hass.data[DOMAIN] = {
            "cycle_entry_id": {
                "plant": mock_cycle_device
            }
        }

        # Setup mock device registry
        mock_device_registry = Mock()
        mock_device_registry.async_get_device.return_value = None

        # Setup mock entity registry
        mock_entity_registry = Mock()
        mock_cycle_entity = Mock()
        mock_cycle_entity.unique_id = "cycle_unique_id"
        mock_entity_registry.async_get.side_effect = lambda entity_id: mock_cycle_entity if entity_id == "cycle.test_cycle" else None

        with patch('custom_components.plant.services.dr.async_get', return_value=mock_device_registry):
            with patch('custom_components.plant.services.er.async_get', return_value=mock_entity_registry):
                # Setup services
                await async_setup_services(mock_hass)

                # Find the service function
                service_func = None
                for call_args in mock_hass.services.async_register.call_args_list:
                    if call_args[0][1] == SERVICE_MOVE_TO_CYCLE:
                        service_func = call_args[0][2]
                        break

                # Call the service - should log error and continue
                await service_func(call)

    @pytest.mark.asyncio
    async def test_move_to_cycle_invalid_cycle(self, mock_hass, mock_plant_device):
        """Test move_to_cycle with invalid cycle entity."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "plant_entity": ["plant.test_plant"],
            "cycle_entity": "cycle.invalid_cycle"
        }

        # Setup hass.data with only plant
        mock_hass.data[DOMAIN] = {
            "plant_entry_id": {
                "plant": mock_plant_device
            }
        }

        # Setup mock device registry
        mock_device_registry = Mock()
        mock_device_registry.async_get_device.return_value = None

        # Setup mock entity registry
        mock_entity_registry = Mock()
        mock_plant_entity = Mock()
        mock_plant_entity.unique_id = "plant_unique_id"
        mock_entity_registry.async_get.side_effect = lambda entity_id: mock_plant_entity if entity_id == "plant.test_plant" else None

        with patch('custom_components.plant.services.dr.async_get', return_value=mock_device_registry):
            with patch('custom_components.plant.services.er.async_get', return_value=mock_entity_registry):
                # Setup services
                await async_setup_services(mock_hass)

                # Find the service function
                service_func = None
                for call_args in mock_hass.services.async_register.call_args_list:
                    if call_args[0][1] == SERVICE_MOVE_TO_CYCLE:
                        service_func = call_args[0][2]
                        break

                # Call the service - should log error and continue
                await service_func(call)

    @pytest.mark.asyncio
    async def test_move_to_cycle_single_plant(self, mock_hass, mock_plant_device, mock_cycle_device):
        """Test move_to_cycle with single plant (not list)."""
        # Setup service call with single plant entity
        call = Mock(spec=ServiceCall)
        call.data = {
            "plant_entity": "plant.test_plant",
            "cycle_entity": "cycle.test_cycle"
        }

        # Setup hass.data with plant and cycle
        mock_hass.data[DOMAIN] = {
            "plant_entry_id": {
                "plant": mock_plant_device
            },
            "cycle_entry_id": {
                "plant": mock_cycle_device
            }
        }

        # Setup mock device registry
        mock_device_registry = Mock()
        mock_plant_device_obj = Mock()
        mock_plant_device_obj.id = "plant_device_id"
        mock_plant_device_obj.via_device_id = None
        mock_plant_device_obj.unique_id = "plant_unique_id"
        mock_cycle_device_obj = Mock()
        mock_cycle_device_obj.id = "cycle_device_id"
        mock_cycle_device_obj.unique_id = "cycle_unique_id"
        
        # Mock device_registry.async_get_device to return the right devices
        def mock_async_get_device(identifiers):
            identifier_tuple = tuple(identifiers)[0]
            if identifier_tuple == (DOMAIN, "plant_unique_id"):
                return mock_plant_device_obj
            elif identifier_tuple == (DOMAIN, "cycle_unique_id"):
                return mock_cycle_device_obj
            return None
            
        mock_device_registry.async_get_device.side_effect = mock_async_get_device
        mock_device_registry.async_update_device = Mock()

        # Setup mock entity registry
        mock_entity_registry = Mock()
        mock_cycle_entity = Mock()
        mock_cycle_entity.unique_id = "cycle_unique_id"
        mock_plant_entity = Mock()
        mock_plant_entity.unique_id = "plant_unique_id"
        
        def mock_async_get(entity_id):
            if entity_id == "cycle.test_cycle":
                return mock_cycle_entity
            elif entity_id == "plant.test_plant":
                return mock_plant_entity
            return None
            
        mock_entity_registry.async_get.side_effect = mock_async_get

        with patch('custom_components.plant.services.dr.async_get', return_value=mock_device_registry):
            with patch('custom_components.plant.services.er.async_get', return_value=mock_entity_registry):
                # Setup services
                await async_setup_services(mock_hass)

                # Find the service function
                service_func = None
                for call_args in mock_hass.services.async_register.call_args_list:
                    if call_args[0][1] == SERVICE_MOVE_TO_CYCLE:
                        service_func = call_args[0][2]
                        break

                # Call the service
                await service_func(call)

                # Verify device was updated with cycle
                mock_device_registry.async_update_device.assert_called_once_with(
                    "plant_device_id",
                    via_device_id="cycle_device_id"
                )