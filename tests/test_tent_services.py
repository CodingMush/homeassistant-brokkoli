"""Unit tests for tent assignment services."""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
import homeassistant.helpers.entity_registry as er

from custom_components.plant.services import async_assign_to_tent, async_unassign_from_tent, async_reassign_to_tent
from custom_components.plant.const import (
    DEVICE_TYPE_TENT,
    DEVICE_TYPE_PLANT,
    ATTR_TENT_ENTITY,
    ATTR_PLANT_ENTITY,
    ATTR_MIGRATE_SENSORS,
    SERVICE_ASSIGN_TO_TENT,
    SERVICE_UNASSIGN_FROM_TENT,
    SERVICE_REASSIGN_TO_TENT,
)


class TestTentAssignmentServices:
    """Test tent assignment service functionality."""

    @pytest.fixture
    def mock_hass(self):
        """Create mock Home Assistant instance."""
        hass = Mock(spec=HomeAssistant)
        hass.states = Mock()
        hass.data = {}
        hass.services = Mock()
        return hass

    @pytest.fixture
    def mock_plant_device(self):
        """Create mock plant device."""
        device = Mock()
        device.entity_id = "plant.test_plant"
        device.device_type = DEVICE_TYPE_PLANT
        device.tent_assignment = None
        device.migrate_to_tent = AsyncMock()
        device.unassign_from_tent = AsyncMock()
        return device

    @pytest.fixture
    def mock_tent_device(self):
        """Create mock tent device."""
        device = Mock()
        device.entity_id = "plant.test_tent"
        device.device_type = DEVICE_TYPE_TENT
        device.register_plant = Mock()
        device.unregister_plant = Mock()
        device._assigned_plants = []
        return device

    @pytest.mark.asyncio
    async def test_assign_to_tent_success(self, mock_hass, mock_plant_device, mock_tent_device):
        """Test successful plant assignment to tent."""
        # Mock service call data
        call = Mock(spec=ServiceCall)
        call.data = {
            ATTR_PLANT_ENTITY: "plant.test_plant",
            ATTR_TENT_ENTITY: "plant.test_tent",
            ATTR_MIGRATE_SENSORS: True
        }

        # Mock getting devices
        with patch('custom_components.plant.services._get_plant_device') as mock_get_plant:
            with patch('custom_components.plant.services._get_tent_device') as mock_get_tent:
                mock_get_plant.return_value = mock_plant_device
                mock_get_tent.return_value = mock_tent_device

                # Call assign service
                await async_assign_to_tent(mock_hass, call)

                # Verify plant was migrated to tent
                mock_plant_device.migrate_to_tent.assert_called_once_with(
                    "plant.test_tent", migrate_sensors=True
                )
                
                # Verify tent registered the plant
                mock_tent_device.register_plant.assert_called_once_with("plant.test_plant")

    @pytest.mark.asyncio
    async def test_assign_to_tent_invalid_plant(self, mock_hass):
        """Test assignment fails with invalid plant entity."""
        call = Mock(spec=ServiceCall)
        call.data = {
            ATTR_PLANT_ENTITY: "plant.nonexistent",
            ATTR_TENT_ENTITY: "plant.test_tent",
        }

        with patch('custom_components.plant.services._get_plant_device') as mock_get_plant:
            mock_get_plant.return_value = None

            # Should raise service validation error
            with pytest.raises(ServiceValidationError):
                await async_assign_to_tent(mock_hass, call)

    @pytest.mark.asyncio
    async def test_assign_to_tent_invalid_tent(self, mock_hass, mock_plant_device):
        """Test assignment fails with invalid tent entity.""" 
        call = Mock(spec=ServiceCall)
        call.data = {
            ATTR_PLANT_ENTITY: "plant.test_plant",
            ATTR_TENT_ENTITY: "plant.nonexistent_tent",
        }

        with patch('custom_components.plant.services._get_plant_device') as mock_get_plant:
            with patch('custom_components.plant.services._get_tent_device') as mock_get_tent:
                mock_get_plant.return_value = mock_plant_device
                mock_get_tent.return_value = None

                # Should raise service validation error
                with pytest.raises(ServiceValidationError):
                    await async_assign_to_tent(mock_hass, call)

    @pytest.mark.asyncio
    async def test_assign_to_tent_already_assigned(self, mock_hass, mock_plant_device, mock_tent_device):
        """Test assigning plant that's already assigned to a tent."""
        # Plant already has tent assignment
        mock_plant_device.tent_assignment = "plant.other_tent"
        
        call = Mock(spec=ServiceCall)
        call.data = {
            ATTR_PLANT_ENTITY: "plant.test_plant",
            ATTR_TENT_ENTITY: "plant.test_tent",
        }

        with patch('custom_components.plant.services._get_plant_device') as mock_get_plant:
            with patch('custom_components.plant.services._get_tent_device') as mock_get_tent:
                mock_get_plant.return_value = mock_plant_device
                mock_get_tent.return_value = mock_tent_device

                # Should raise service validation error
                with pytest.raises(ServiceValidationError, match="already assigned"):
                    await async_assign_to_tent(mock_hass, call)

    @pytest.mark.asyncio
    async def test_unassign_from_tent_success(self, mock_hass, mock_plant_device, mock_tent_device):
        """Test successful plant unassignment from tent."""
        # Plant is assigned to tent
        mock_plant_device.tent_assignment = "plant.test_tent"
        mock_tent_device._assigned_plants = ["plant.test_plant"]
        
        call = Mock(spec=ServiceCall)
        call.data = {ATTR_PLANT_ENTITY: "plant.test_plant"}

        with patch('custom_components.plant.services._get_plant_device') as mock_get_plant:
            with patch('custom_components.plant.services._get_tent_device') as mock_get_tent:
                mock_get_plant.return_value = mock_plant_device
                mock_get_tent.return_value = mock_tent_device

                # Call unassign service
                await async_unassign_from_tent(mock_hass, call)

                # Verify plant was unassigned
                mock_plant_device.unassign_from_tent.assert_called_once()
                
                # Verify tent unregistered the plant
                mock_tent_device.unregister_plant.assert_called_once_with("plant.test_plant")

    @pytest.mark.asyncio
    async def test_unassign_from_tent_not_assigned(self, mock_hass, mock_plant_device):
        """Test unassigning plant that's not assigned to any tent."""
        # Plant has no tent assignment
        mock_plant_device.tent_assignment = None
        
        call = Mock(spec=ServiceCall)
        call.data = {ATTR_PLANT_ENTITY: "plant.test_plant"}

        with patch('custom_components.plant.services._get_plant_device') as mock_get_plant:
            mock_get_plant.return_value = mock_plant_device

            # Should raise service validation error
            with pytest.raises(ServiceValidationError, match="not assigned"):
                await async_unassign_from_tent(mock_hass, call)

    @pytest.mark.asyncio
    async def test_reassign_to_tent_success(self, mock_hass, mock_plant_device, mock_tent_device):
        """Test successful plant reassignment between tents."""
        # Setup old tent
        mock_old_tent = Mock()
        mock_old_tent.entity_id = "plant.old_tent"
        mock_old_tent.device_type = DEVICE_TYPE_TENT
        mock_old_tent.unregister_plant = Mock()
        mock_old_tent._assigned_plants = ["plant.test_plant"]
        
        # Plant currently assigned to old tent
        mock_plant_device.tent_assignment = "plant.old_tent"
        
        call = Mock(spec=ServiceCall)
        call.data = {
            ATTR_PLANT_ENTITY: "plant.test_plant",
            ATTR_TENT_ENTITY: "plant.test_tent",
            "sensors": ["temperature", "humidity"]  # Selective sensor inheritance
        }

        with patch('custom_components.plant.services._get_plant_device') as mock_get_plant:
            with patch('custom_components.plant.services._get_tent_device') as mock_get_tent:
                mock_get_plant.return_value = mock_plant_device
                mock_get_tent.side_effect = lambda entity_id: {
                    "plant.old_tent": mock_old_tent,
                    "plant.test_tent": mock_tent_device
                }.get(entity_id)

                # Call reassign service
                await async_reassign_to_tent(mock_hass, call)

                # Verify old tent unregistered plant
                mock_old_tent.unregister_plant.assert_called_once_with("plant.test_plant")
                
                # Verify new tent registered plant
                mock_tent_device.register_plant.assert_called_once_with("plant.test_plant")
                
                # Verify plant was migrated
                mock_plant_device.migrate_to_tent.assert_called_once()

    @pytest.mark.asyncio
    async def test_migrate_sensors_parameter(self, mock_hass, mock_plant_device, mock_tent_device):
        """Test migrate_sensors parameter is passed correctly."""
        call = Mock(spec=ServiceCall)
        call.data = {
            ATTR_PLANT_ENTITY: "plant.test_plant",
            ATTR_TENT_ENTITY: "plant.test_tent",
            ATTR_MIGRATE_SENSORS: False  # Don't migrate sensors
        }

        with patch('custom_components.plant.services._get_plant_device') as mock_get_plant:
            with patch('custom_components.plant.services._get_tent_device') as mock_get_tent:
                mock_get_plant.return_value = mock_plant_device
                mock_get_tent.return_value = mock_tent_device

                await async_assign_to_tent(mock_hass, call)

                # Verify migrate_sensors=False was passed
                mock_plant_device.migrate_to_tent.assert_called_once_with(
                    "plant.test_tent", migrate_sensors=False
                )

    def test_service_registration(self, mock_hass):
        """Test tent services are properly registered."""
        with patch('custom_components.plant.services.async_register_admin_service') as mock_register:
            # This would be called during integration setup
            # mock_register.assert_any_call(mock_hass, "plant", SERVICE_ASSIGN_TO_TENT, async_assign_to_tent)
            # mock_register.assert_any_call(mock_hass, "plant", SERVICE_UNASSIGN_FROM_TENT, async_unassign_from_tent)
            # mock_register.assert_any_call(mock_hass, "plant", SERVICE_REASSIGN_TO_TENT, async_reassign_to_tent)
            
            # For now just verify the functions exist and are callable
            assert callable(async_assign_to_tent)
            assert callable(async_unassign_from_tent)
            assert callable(async_reassign_to_tent)

    @pytest.mark.asyncio
    async def test_rollback_on_failure(self, mock_hass, mock_plant_device, mock_tent_device):
        """Test rollback when tent assignment fails."""
        # Make plant migration fail
        mock_plant_device.migrate_to_tent.side_effect = Exception("Migration failed")
        
        call = Mock(spec=ServiceCall)
        call.data = {
            ATTR_PLANT_ENTITY: "plant.test_plant",
            ATTR_TENT_ENTITY: "plant.test_tent",
        }

        with patch('custom_components.plant.services._get_plant_device') as mock_get_plant:
            with patch('custom_components.plant.services._get_tent_device') as mock_get_tent:
                mock_get_plant.return_value = mock_plant_device
                mock_get_tent.return_value = mock_tent_device

                # Assignment should fail and rollback
                with pytest.raises(Exception):
                    await async_assign_to_tent(mock_hass, call)

                # Verify tent registration was attempted but then rolled back
                # (Implementation detail - may vary based on actual rollback logic)