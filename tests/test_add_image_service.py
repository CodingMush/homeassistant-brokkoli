"""Integration tests for the add_image service."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from custom_components.plant.services import async_setup_services
from custom_components.plant.const import DOMAIN, SERVICE_ADD_IMAGE, DEVICE_TYPE_PLANT
from custom_components.plant.security_utils import SecurityError


class TestAddImageService:
    """Test add_image service functionality."""

    @pytest.fixture
    def mock_hass(self):
        """Create mock Home Assistant instance."""
        hass = Mock(spec=HomeAssistant)
        hass.data = {DOMAIN: {}}
        hass.states = Mock()
        hass.services = Mock()
        hass.config_entries = Mock()
        # Add async_add_executor_job to the mock hass object
        hass.async_add_executor_job = AsyncMock()
        return hass

    @pytest.fixture
    def mock_plant_device(self):
        """Create mock plant device with image functionality."""
        device = Mock()
        device.entity_id = "plant.test_plant"
        device.device_type = DEVICE_TYPE_PLANT
        device._images = []
        return device

    @pytest.mark.asyncio
    async def test_add_image_success(self, mock_hass, mock_plant_device):
        """Test successful image addition."""
        # Setup service call
        call = Mock(spec=ServiceCall)
        call.data = {
            "entity_id": "plant.test_plant",
            "image_url": "https://example.com/test_image.jpg"
        }

        # Setup hass.data with plant
        mock_hass.data[DOMAIN] = {
            "test_entry_id": {
                "plant": mock_plant_device
            }
        }

        # Setup config entries with download path
        mock_config_entry = Mock()
        mock_config_entry.data = {"is_config": True, "plant_info": {"download_path": "/config/www/images/plants/"}}
        mock_hass.config_entries.async_entries.return_value = [mock_config_entry]

        # Mock security validation functions
        with patch('custom_components.plant.services.validate_image_url', return_value=True):
            with patch('custom_components.plant.services.sanitize_entity_id', return_value="plant.test_plant"):
                with patch('custom_components.plant.services.secure_file_path', return_value="/config/www/images/plants/test_image.jpg"):
                    # Create proper async context managers for both session and response
                    class MockResponseContextManager:
                        async def __aenter__(self):
                            mock_response = AsyncMock()
                            mock_response.status = 200
                            mock_response.headers = {'content-type': 'image/jpeg', 'content-length': '1024'}
                            mock_response.read = AsyncMock(return_value=b"fake_image_data")
                            return mock_response
                        
                        async def __aexit__(self, exc_type, exc_val, exc_tb):
                            pass
                    
                    class MockSessionContextManager:
                        async def __aenter__(self):
                            self.session = Mock()
                            self.session.get = Mock(return_value=MockResponseContextManager())
                            return self.session
                        
                        async def __aexit__(self, exc_type, exc_val, exc_tb):
                            pass
                    
                    # Patch the ClientSession to return our custom context manager
                    with patch('custom_components.plant.services.aiohttp.ClientSession', return_value=MockSessionContextManager()):
                        # Mock async_add_executor_job to avoid actual file operations
                        mock_hass.async_add_executor_job = AsyncMock(return_value=None)
                        
                        # Mock the services.async_call to avoid calling the actual service
                        mock_hass.services.async_call = AsyncMock(return_value=None)

                        # Setup services
                        await async_setup_services(mock_hass)

                        # Find the service function
                        service_func = None
                        for call_args in mock_hass.services.async_register.call_args_list:
                            if call_args[0][1] == SERVICE_ADD_IMAGE:
                                service_func = call_args[0][2]
                                break

                        assert service_func is not None, "add_image service not found"
                        
                        # Call the service
                        await service_func(call)
                        
                        # Verify update_plant_attributes service was called
                        mock_hass.services.async_call.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_image_invalid_entity(self, mock_hass):
        """Test add_image with invalid entity."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "entity_id": "plant.invalid_plant",
            "image_url": "https://example.com/test_image.jpg"
        }

        # Setup empty hass.data
        mock_hass.data[DOMAIN] = {}

        # Mock security validation functions
        with patch('custom_components.plant.services.validate_image_url', return_value=True):
            with patch('custom_components.plant.services.sanitize_entity_id', return_value=None):
                # Setup services
                await async_setup_services(mock_hass)

                # Find the service function
                service_func = None
                for call_args in mock_hass.services.async_register.call_args_list:
                    if call_args[0][1] == SERVICE_ADD_IMAGE:
                        service_func = call_args[0][2]
                        break

                # Call the service and expect SecurityError (raised directly, not caught and re-raised)
                with pytest.raises(SecurityError, match="Invalid entity ID format"):
                    await service_func(call)

    @pytest.mark.asyncio
    async def test_add_image_security_error(self, mock_hass, mock_plant_device):
        """Test add_image with security validation error."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "entity_id": "plant.test_plant",
            "image_url": "https://example.com/test_image.jpg"
        }

        # Setup hass.data with plant
        mock_hass.data[DOMAIN] = {
            "test_entry_id": {
                "plant": mock_plant_device
            }
        }

        # Mock security validation functions to raise SecurityError
        with patch('custom_components.plant.services.validate_image_url', return_value=False):
            # Setup services
            await async_setup_services(mock_hass)

            # Find the service function
            service_func = None
            for call_args in mock_hass.services.async_register.call_args_list:
                if call_args[0][1] == SERVICE_ADD_IMAGE:
                    service_func = call_args[0][2]
                    break

            # Call the service and expect SecurityError (raised directly, not caught and re-raised)
            with pytest.raises(SecurityError, match="Invalid or unsafe image URL"):
                await service_func(call)

    @pytest.mark.asyncio
    async def test_add_image_missing_parameters(self, mock_hass):
        """Test add_image with missing parameters."""
        call = Mock(spec=ServiceCall)
        call.data = {
            # Missing entity_id and image_url
        }

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_ADD_IMAGE:
                service_func = call_args[0][2]
                break

        # Call the service and expect HomeAssistantError
        with pytest.raises(HomeAssistantError, match="Missing required parameters"):
            await service_func(call)