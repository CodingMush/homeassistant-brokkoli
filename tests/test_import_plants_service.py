"""Integration tests for the import_plants service."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from custom_components.plant.services import async_setup_services
from custom_components.plant.const import (
    DOMAIN, SERVICE_IMPORT_PLANTS, FLOW_PLANT_INFO, DEVICE_TYPE_PLANT
)


class TestImportPlantsService:
    """Test import_plants service functionality."""

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
    async def test_import_plants_success(self, mock_hass, mock_plant_config):
        """Test successful plant import."""
        # Setup service call
        call = Mock(spec=ServiceCall)
        call.data = {
            "file_path": "/config/test_import.zip",
            "new_plant_name": "Imported Plant",
            "overwrite_existing": False,
            "include_images": False
        }

        # Setup mock import data
        import_data = {
            "plants": [
                {
                    "plant_info": mock_plant_config,
                    "options": {}
                }
            ]
        }
        
        # Setup mock config entries
        mock_config_entry = Mock()
        mock_config_entry.data = {FLOW_PLANT_INFO: mock_plant_config}
        mock_hass.config_entries.async_entries.return_value = [mock_config_entry]

        # Mock async_add_executor_job to avoid actual file operations
        mock_hass.async_add_executor_job = AsyncMock()
        mock_hass.async_add_executor_job.return_value = (import_data, {})
        
        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_IMPORT_PLANTS:
                service_func = call_args[0][2]
                break

        assert service_func is not None, "import_plants service not found"
        
        # Call the service
        response = await service_func(call)
        
        # Verify response
        assert "imported_plants" in response
        assert response["file_path"] == "/config/test_import.zip"

    @pytest.mark.asyncio
    async def test_import_plants_file_not_found(self, mock_hass):
        """Test import_plants with file not found."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "file_path": "/config/nonexistent.zip"
        }

        # Mock async_add_executor_job to raise FileNotFoundError
        mock_hass.async_add_executor_job = AsyncMock()
        mock_hass.async_add_executor_job.side_effect = FileNotFoundError("File not found")
        
        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_IMPORT_PLANTS:
                service_func = call_args[0][2]
                break

        # Call the service and expect HomeAssistantError
        with pytest.raises(HomeAssistantError, match="Error importing plants"):
            await service_func(call)

    @pytest.mark.asyncio
    async def test_import_plants_invalid_zip(self, mock_hass):
        """Test import_plants with invalid ZIP file."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "file_path": "/config/invalid.zip"
        }

        # Mock async_add_executor_job to raise BadZipFile
        mock_hass.async_add_executor_job = AsyncMock()
        mock_hass.async_add_executor_job.side_effect = Exception("BadZipFile")
        
        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_IMPORT_PLANTS:
                service_func = call_args[0][2]
                break

        # Call the service and expect HomeAssistantError
        with pytest.raises(HomeAssistantError, match="Error importing plants"):
            await service_func(call)

    @pytest.mark.asyncio
    async def test_import_plants_empty_file(self, mock_hass):
        """Test import_plants with empty ZIP file."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "file_path": "/config/empty.zip"
        }

        # Mock async_add_executor_job to return empty data
        mock_hass.async_add_executor_job = AsyncMock()
        mock_hass.async_add_executor_job.return_value = ({"plants": []}, {})
        
        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_IMPORT_PLANTS:
                service_func = call_args[0][2]
                break

        # Call the service and expect HomeAssistantError
        with pytest.raises(HomeAssistantError, match="No plants found in import file"):
            await service_func(call)