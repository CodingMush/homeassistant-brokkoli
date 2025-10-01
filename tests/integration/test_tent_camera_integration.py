"""Integration tests for tent reconfiguration and camera inheritance."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import os
import tempfile
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_NAME

from custom_components.plant.config_flow import PlantConfigFlow, OptionsFlowHandler
from custom_components.plant import PlantDevice
from custom_components.plant.tent import Tent
from custom_components.plant.camera import PlantCamera
from custom_components.plant.const import (
    DOMAIN,
    DEVICE_TYPE_PLANT,
    DEVICE_TYPE_TENT,
    FLOW_PLANT_INFO,
    FLOW_SENSOR_ILLUMINANCE,
    FLOW_SENSOR_HUMIDITY,
    FLOW_SENSOR_CO2,
)


@pytest.fixture
def mock_hass():
    """Create a comprehensive mock Home Assistant instance."""
    hass = Mock(spec=HomeAssistant)
    hass.states = Mock()
    hass.config_entries = Mock()
    hass.async_add_executor_job = AsyncMock()
    hass.services = Mock()
    hass.config = Mock()
    hass.config.path = Mock(return_value="/config")
    hass.data = {DOMAIN: {}}
    return hass


@pytest.fixture
def temp_image_dir():
    """Create a temporary directory for test images."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


class TestTentReconfigurationIntegration:
    """Integration tests for tent reconfiguration functionality."""

    @pytest.mark.asyncio
    async def test_complete_tent_reconfiguration_workflow(self, mock_hass):
        """Test complete tent reconfiguration workflow."""
        # Create initial tent config
        tent_config = Mock(spec=ConfigEntry)
        tent_config.data = {
            FLOW_PLANT_INFO: {
                ATTR_NAME: "Original Tent",
                "tent_id": "tent_123",
                "device_type": DEVICE_TYPE_TENT,
                FLOW_SENSOR_ILLUMINANCE: "sensor.old_illuminance",
            }
        }
        tent_config.entry_id = "tent_entry"

        # Create tent entity
        tent = Tent(mock_hass, tent_config)
        tent.device_type = DEVICE_TYPE_TENT

        # Create options flow handler
        options_handler = OptionsFlowHandler(tent_config)
        options_handler.hass = mock_hass
        options_handler.entry = tent_config
        options_handler.plant = tent

        # Mock entity validation
        mock_hass.states.get.return_value = Mock(state="available")

        # Mock config update
        mock_hass.config_entries.async_update_entry = Mock()

        # Mock tent methods
        tent.set_camera = Mock()
        tent.async_write_ha_state = Mock()

        # Prepare update data
        user_input = {
            ATTR_NAME: "Updated Tent Name",
            FLOW_SENSOR_ILLUMINANCE: "sensor.new_illuminance",
            FLOW_SENSOR_HUMIDITY: "sensor.new_humidity",
            "camera_entity_id": "camera.new_camera",
        }

        # Execute reconfiguration
        result = await options_handler.async_step_init(user_input)

        # Verify result
        assert result["type"] == "create_entry"

        # Verify config was updated
        mock_hass.config_entries.async_update_entry.assert_called_once()
        
        # Verify camera was set
        tent.set_camera.assert_called_once_with("camera.new_camera")

        # Verify entity state was updated
        tent.async_write_ha_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_tent_validation_integration(self, mock_hass):
        """Test tent validation during reconfiguration."""
        # Create tent config
        tent_config = Mock(spec=ConfigEntry)
        tent_config.data = {
            FLOW_PLANT_INFO: {
                ATTR_NAME: "Test Tent",
                "tent_id": "tent_123",
                "device_type": DEVICE_TYPE_TENT,
            }
        }

        # Create tent entity
        tent = Tent(mock_hass, tent_config)
        tent.device_type = DEVICE_TYPE_TENT

        # Create options flow handler
        options_handler = OptionsFlowHandler(tent_config)
        options_handler.hass = mock_hass
        options_handler.entry = tent_config
        options_handler.plant = tent

        # Mock invalid entities
        mock_hass.states.get.return_value = None  # Entity not found

        # Prepare invalid input
        user_input = {
            FLOW_SENSOR_ILLUMINANCE: "sensor.nonexistent",
            "camera_entity_id": "not_a_camera_entity",
        }

        # Execute validation
        result = await options_handler.async_step_init(user_input)

        # Verify validation errors
        assert result["type"] == "form"
        assert "errors" in result
        assert FLOW_SENSOR_ILLUMINANCE in result["errors"]
        assert "camera_entity_id" in result["errors"]


class TestCameraInheritanceIntegration:
    """Integration tests for camera inheritance functionality."""

    @pytest.mark.asyncio
    async def test_complete_camera_inheritance_workflow(self, mock_hass, temp_image_dir):
        """Test complete camera inheritance from tent to plant."""
        # Create tent with camera
        tent_config = Mock(spec=ConfigEntry)
        tent_config.data = {
            FLOW_PLANT_INFO: {
                "name": "Camera Tent",
                "tent_id": "tent_with_camera",
                "device_type": DEVICE_TYPE_TENT,
                "camera_entity_id": "camera.tent_camera",
            }
        }

        tent = Tent(mock_hass, tent_config)
        tent.get_sensors = Mock(return_value=["sensor.temp1", "sensor.humidity1"])
        tent.set_camera("camera.tent_camera")

        # Create plant
        plant_config = Mock(spec=ConfigEntry)
        plant_config.data = {
            FLOW_PLANT_INFO: {
                "name": "Test Plant",
                "plant_id": "plant_123",
                "device_type": DEVICE_TYPE_PLANT,
            }
        }

        plant = PlantDevice(mock_hass, plant_config)
        plant.replace_sensors = Mock()

        # Mock config update
        mock_hass.config_entries.async_update_entry = Mock()

        # Mock PlantCamera
        with patch('custom_components.plant.PlantCamera') as mock_camera_class:
            mock_camera_instance = Mock()
            mock_camera_class.return_value = mock_camera_instance

            # Execute tent assignment with camera inheritance
            plant.assign_tent(tent)

            # Verify tent assignment
            assert plant.get_assigned_tent() == tent
            assert plant.get_tent_id() == tent.tent_id

            # Verify sensors were inherited
            plant.replace_sensors.assert_called_once_with(["sensor.temp1", "sensor.humidity1"])

            # Verify camera was inherited
            mock_hass.config_entries.async_update_entry.assert_called()

    @pytest.mark.asyncio
    async def test_camera_integration_with_external_entity(self, mock_hass, temp_image_dir):
        """Test camera integration with actual external camera entity."""
        # Create plant config with camera
        plant_config = Mock(spec=ConfigEntry)
        plant_config.data = {
            FLOW_PLANT_INFO: {
                "name": "Plant with Camera",
                "plant_id": "plant_cam",
                "device_type": DEVICE_TYPE_PLANT,
                "camera_entity_id": "camera.external_cam",
            }
        }

        plant = PlantDevice(mock_hass, plant_config)

        # Create PlantCamera with temp directory
        with patch('custom_components.plant.camera.DEFAULT_IMAGE_PATH', temp_image_dir):
            camera = PlantCamera(mock_hass, plant, plant_config)
            plant.camera = camera

            # Mock external camera state
            camera_state = Mock(state="idle")
            mock_hass.states.get.return_value = camera_state

            # Mock camera service call
            mock_hass.services.async_call = AsyncMock()

            # Mock file operations
            test_image_data = b"fake_image_data"
            
            def mock_executor_job(func):
                if "read_captured_image" in str(func):
                    return test_image_data
                else:
                    return func()

            mock_hass.async_add_executor_job.side_effect = mock_executor_job

            # Test taking snapshot
            filepath = await camera.async_take_snapshot()

            # Verify service was called
            mock_hass.services.async_call.assert_called_once()

            # Verify snapshot was created
            assert filepath is not None
            assert temp_image_dir in filepath

    @pytest.mark.asyncio
    async def test_tent_plant_assignment_integration(self, mock_hass):
        """Test integration between tent assignment and plant configuration."""
        # Create tent
        tent_config = Mock(spec=ConfigEntry)
        tent_config.data = {
            FLOW_PLANT_INFO: {
                "name": "Integration Tent",
                "tent_id": "int_tent",
                "device_type": DEVICE_TYPE_TENT,
                "camera_entity_id": "camera.int_camera",
                FLOW_SENSOR_ILLUMINANCE: "sensor.int_illuminance",
                FLOW_SENSOR_HUMIDITY: "sensor.int_humidity",
            }
        }

        tent = Tent(mock_hass, tent_config)
        tent.get_sensors = Mock(return_value=[
            "sensor.int_illuminance",
            "sensor.int_humidity"
        ])

        # Create multiple plants
        plants = []
        for i in range(3):
            plant_config = Mock(spec=ConfigEntry)
            plant_config.data = {
                FLOW_PLANT_INFO: {
                    "name": f"Plant {i+1}",
                    "plant_id": f"plant_{i+1}",
                    "device_type": DEVICE_TYPE_PLANT,
                }
            }

            plant = PlantDevice(mock_hass, plant_config)
            plant.replace_sensors = Mock()
            plants.append(plant)

        # Mock config updates
        mock_hass.config_entries.async_update_entry = Mock()

        # Mock PlantCamera creation
        with patch('custom_components.plant.PlantCamera') as mock_camera_class:
            mock_camera_class.return_value = Mock()

            # Assign tent to all plants
            for plant in plants:
                plant.assign_tent(tent)

            # Verify all plants inherited tent configuration
            for plant in plants:
                assert plant.get_assigned_tent() == tent
                assert plant.get_tent_id() == tent.tent_id
                plant.replace_sensors.assert_called_once_with([
                    "sensor.int_illuminance",
                    "sensor.int_humidity"
                ])

            # Verify config was updated for each plant
            assert mock_hass.config_entries.async_update_entry.call_count == len(plants)


class TestErrorHandlingIntegration:
    """Integration tests for error handling scenarios."""

    @pytest.mark.asyncio
    async def test_tent_reconfiguration_with_unavailable_entities(self, mock_hass):
        """Test tent reconfiguration when entities become unavailable."""
        # Create tent config
        tent_config = Mock(spec=ConfigEntry)
        tent_config.data = {
            FLOW_PLANT_INFO: {
                ATTR_NAME: "Test Tent",
                "tent_id": "tent_123",
                "device_type": DEVICE_TYPE_TENT,
            }
        }

        tent = Tent(mock_hass, tent_config)
        tent.device_type = DEVICE_TYPE_TENT

        # Create options flow handler
        options_handler = OptionsFlowHandler(tent_config)
        options_handler.hass = mock_hass
        options_handler.entry = tent_config
        options_handler.plant = tent

        # Mock unavailable entities
        unavailable_state = Mock(state="unavailable")
        mock_hass.states.get.return_value = unavailable_state

        # Prepare input with unavailable entities
        user_input = {
            FLOW_SENSOR_ILLUMINANCE: "sensor.unavailable_sensor",
            "camera_entity_id": "camera.unavailable_camera",
        }

        # Execute and expect validation errors
        result = await options_handler.async_step_init(user_input)

        # Verify validation errors for unavailable entities
        assert result["type"] == "form"
        assert "errors" in result
        assert FLOW_SENSOR_ILLUMINANCE in result["errors"]
        assert "camera_entity_id" in result["errors"]

    @pytest.mark.asyncio
    async def test_camera_inheritance_error_recovery(self, mock_hass):
        """Test error recovery during camera inheritance."""
        # Create tent with camera
        tent = Mock()
        tent.tent_id = "tent_error"
        tent.name = "Error Tent"
        tent.get_camera.return_value = "camera.error_camera"
        tent.get_sensors.return_value = ["sensor.temp1"]

        # Create plant
        plant_config = Mock(spec=ConfigEntry)
        plant_config.data = {
            FLOW_PLANT_INFO: {
                "name": "Error Plant",
                "plant_id": "plant_error",
                "device_type": DEVICE_TYPE_PLANT,
            }
        }

        plant = PlantDevice(mock_hass, plant_config)
        plant.replace_sensors = Mock()

        # Mock config update to raise exception
        mock_hass.config_entries.async_update_entry = Mock(
            side_effect=Exception("Config update failed")
        )

        # Mock logging
        with patch('custom_components.plant._LOGGER') as mock_logger:
            # Execute tent assignment (should not crash)
            plant.assign_tent(tent)

            # Verify error was logged
            mock_logger.error.assert_called()

            # Verify tent was still assigned (graceful degradation)
            assert plant.get_assigned_tent() == tent

    @pytest.mark.asyncio
    async def test_snapshot_fallback_mechanism(self, mock_hass, temp_image_dir):
        """Test camera snapshot fallback when external camera fails."""
        # Create plant config with camera
        plant_config = Mock(spec=ConfigEntry)
        plant_config.data = {
            FLOW_PLANT_INFO: {
                "name": "Fallback Plant",
                "plant_id": "plant_fallback",
                "device_type": DEVICE_TYPE_PLANT,
                "camera_entity_id": "camera.failing_camera",
            }
        }

        plant = PlantDevice(mock_hass, plant_config)

        # Create PlantCamera
        with patch('custom_components.plant.camera.DEFAULT_IMAGE_PATH', temp_image_dir):
            camera = PlantCamera(mock_hass, plant, plant_config)

            # Mock camera service to fail
            mock_hass.services.async_call = AsyncMock(
                side_effect=Exception("Camera service failed")
            )

            # Mock file operations for fallback
            def mock_executor_job(func):
                return func()

            mock_hass.async_add_executor_job.side_effect = mock_executor_job

            # Test taking snapshot (should fallback to placeholder)
            filepath = await camera.async_take_snapshot()

            # Verify snapshot was still created (using placeholder)
            assert filepath is not None
            assert temp_image_dir in filepath
            assert os.path.exists(filepath)