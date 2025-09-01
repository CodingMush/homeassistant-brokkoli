"""Integration tests for the export_plants service."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from custom_components.plant.services import async_setup_services
from custom_components.plant.const import (
    DOMAIN, SERVICE_EXPORT_PLANTS, FLOW_PLANT_INFO, DEVICE_TYPE_PLANT
)


class TestExportPlantsService:
    """Test export_plants service functionality."""

    @pytest.fixture
    def mock_hass(self):
        """Create mock Home Assistant instance."""
        hass = Mock(spec=HomeAssistant)
        hass.data = {DOMAIN: {}}
        hass.states = Mock()
        hass.services = Mock()
        hass.config_entries = Mock()
        # Fix: Make async_entries return an empty list instead of being a plain Mock
        hass.config_entries.async_entries = Mock(return_value=[])
        # Fix: Add async_get_entry method
        hass.config_entries.async_get_entry = Mock(return_value=None)
        # Fix: Add config attribute with components
        hass.config = Mock()
        hass.config.components = set()
        # Fix: Add config_dir attribute
        hass.config.config_dir = "/config"
        # Fix: Add bus attribute
        hass.bus = Mock()
        hass.bus.async_listen = Mock()
        return hass

    @pytest.fixture
    def mock_plant_config(self):
        """Create mock plant configuration."""
        return {
            "name": "Test Plant",
            "strain": "Test Strain",
            "breeder": "Test Breeder",
            "device_type": DEVICE_TYPE_PLANT
        }

    @pytest.mark.asyncio
    async def test_export_plants_success(self, mock_hass, mock_plant_config):
        """Test successful plant export."""
        # Setup service call
        call = Mock(spec=ServiceCall)
        call.data = {
            "plant_entities": ["plant.test_plant"],
            "file_path": "/config/test_export.zip",
            "include_images": False,
            "include_sensor_data": False
        }

        # Setup hass.data with plant
        mock_hass.data[DOMAIN] = {
            "test_entry_id": {
                "plant": Mock(entity_id="plant.test_plant")
            }
        }

        # Setup config entries
        mock_config_entry = Mock()
        mock_config_entry.data = {FLOW_PLANT_INFO: mock_plant_config}
        mock_config_entry.entry_id = "test_entry_id"
        mock_hass.config_entries.async_entries.return_value = [mock_config_entry]
        mock_hass.config_entries.async_get_entry.return_value = mock_config_entry

        # Setup states
        mock_state = Mock()
        mock_state.attributes = {"friendly_name": "Test Plant"}
        mock_hass.states.get.return_value = mock_state

        # Mock async_add_executor_job to avoid actual file operations
        mock_hass.async_add_executor_job = AsyncMock()
        mock_hass.async_add_executor_job.return_value = None
        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_EXPORT_PLANTS:
                service_func = call_args[0][2]
                break

        assert service_func is not None, "export_plants service not found"
        
        # Call the service
        response = await service_func(call)
        
        # Verify response
        assert "exported_plants" in response
        assert response["file_path"] == "/config/test_export.zip"

    @pytest.mark.asyncio
    async def test_export_plants_empty_list(self, mock_hass):
        """Test export_plants with empty plant list."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "plant_entities": [],
            "file_path": "/config/test_export.zip"
        }

        # Mock async_add_executor_job to avoid actual file operations
        mock_hass.async_add_executor_job = AsyncMock()
        mock_hass.async_add_executor_job.return_value = None

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_EXPORT_PLANTS:
                service_func = call_args[0][2]
                break

        # Call the service
        response = await service_func(call)
        
        # Verify response
        assert response["exported_plants"] == 0
        assert response["file_path"] == "/config/test_export.zip"

    @pytest.mark.asyncio
    async def test_export_plants_file_error(self, mock_hass, mock_plant_config):
        """Test export_plants with file operation error."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "plant_entities": ["plant.test_plant"],
            "file_path": "/config/test_export.zip"
        }

        # Setup hass.data with plant
        mock_hass.data[DOMAIN] = {
            "test_entry_id": {
                "plant": Mock(entity_id="plant.test_plant")
            }
        }

        # Setup config entries
        mock_config_entry = Mock()
        mock_config_entry.data = {FLOW_PLANT_INFO: mock_plant_config}
        mock_config_entry.entry_id = "test_entry_id"
        mock_hass.config_entries.async_entries.return_value = [mock_config_entry]
        mock_hass.config_entries.async_get_entry.return_value = mock_config_entry

        # Mock async_add_executor_job to raise an exception
        mock_hass.async_add_executor_job = AsyncMock()
        mock_hass.async_add_executor_job.side_effect = Exception("File operation failed")
        
        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_EXPORT_PLANTS:
                service_func = call_args[0][2]
                break

        # Call the service and expect HomeAssistantError
        with pytest.raises(HomeAssistantError, match="Error exporting plants"):
            await service_func(call)