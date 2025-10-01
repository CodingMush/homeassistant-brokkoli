"""Camera platform for Brokkoli Plant Manager."""

import logging
from datetime import datetime
import os
import io
from typing import Any

from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import ATTR_NAME
from homeassistant.util import slugify

from .const import (
    DOMAIN,
    FLOW_PLANT_INFO,
    FLOW_DOWNLOAD_PATH,
    DEFAULT_IMAGE_PATH,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Brokkoli Plant cameras based on a config entry."""
    # This platform is only for plant entities that have cameras
    # Camera entities are created dynamically and added via the plant entity
    
    # Get all plant entities and add their cameras if they exist
    if DOMAIN in hass.data:
        camera_entities = []
        for entry_id in hass.data[DOMAIN]:
            if "plant" in hass.data[DOMAIN][entry_id]:
                plant = hass.data[DOMAIN][entry_id]["plant"]
                if hasattr(plant, 'camera') and plant.camera:
                    camera_entities.append(plant.camera)
        
        if camera_entities:
            async_add_entities(camera_entities)


class PlantCamera(Camera):
    """Representation of a plant camera."""

    def __init__(self, hass: HomeAssistant, plant_entity, config_entry: ConfigEntry) -> None:
        """Initialize the plant camera."""
        super().__init__()
        self._hass = hass
        self._plant_entity = plant_entity
        self._config_entry = config_entry
        self._attr_name = f"{plant_entity.name} Camera"
        self._attr_unique_id = f"{plant_entity.unique_id}_camera"
        
        # Set supported features
        self._attr_supported_features = CameraEntityFeature.ON_OFF
        
        # Camera state
        self._attr_is_on = True
        self._last_image = None
        self._last_image_timestamp = None
        
        # Get image storage path from config
        config_data = {}
        for entry in hass.config_entries.async_entries(DOMAIN):
            if entry.data.get("is_config", False):
                config_data = entry.data.get(FLOW_PLANT_INFO, {})
                break
                
        self._image_storage_path = config_data.get(FLOW_DOWNLOAD_PATH, DEFAULT_IMAGE_PATH)
        
        # Ensure storage directory exists with proper error handling
        try:
            if not os.path.exists(self._image_storage_path):
                os.makedirs(self._image_storage_path)
        except PermissionError:
            # If we can't create the directory, use a fallback path
            fallback_path = hass.config.path("www", "images", "plants")
            if not os.path.exists(fallback_path):
                try:
                    os.makedirs(fallback_path)
                except Exception:
                    # If we still can't create directories, use the config directory
                    fallback_path = hass.config.path("plant_images")
                    if not os.path.exists(fallback_path):
                        os.makedirs(fallback_path)
            self._image_storage_path = fallback_path
            _LOGGER.warning(
                "Permission denied for image storage path %s. Using fallback path: %s",
                config_data.get(FLOW_DOWNLOAD_PATH, DEFAULT_IMAGE_PATH),
                fallback_path
            )
        except Exception as e:
            # Use Home Assistant's config directory as ultimate fallback
            fallback_path = hass.config.path("plant_images")
            if not os.path.exists(fallback_path):
                os.makedirs(fallback_path)
            self._image_storage_path = fallback_path
            _LOGGER.warning(
                "Error accessing image storage path %s: %s. Using fallback path: %s",
                config_data.get(FLOW_DOWNLOAD_PATH, DEFAULT_IMAGE_PATH),
                str(e),
                fallback_path
            )

    @property
    def device_info(self) -> dict:
        """Return device information about this plant camera."""
        return {
            "identifiers": {(DOMAIN, self._plant_entity.unique_id)},
            "name": self._plant_entity.name,
            "manufacturer": "Home Assistant",
            "model": "Plant Camera",
            "via_device": (DOMAIN, self._plant_entity.unique_id),
        }

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return bytes of camera image."""
        # Check if we have an external camera entity configured
        plant_config = self._config_entry.data.get(FLOW_PLANT_INFO, {})
        external_camera_id = plant_config.get("camera_entity_id")
        
        if external_camera_id:
            # Try to get image from external camera
            try:
                camera_entity = self._hass.states.get(external_camera_id)
                if camera_entity and camera_entity.state != "unavailable":
                    # Get the camera entity from Home Assistant
                    camera_component = self._hass.data.get("camera")
                    if camera_component:
                        for camera in camera_component.entities:
                            if camera.entity_id == external_camera_id:
                                return await camera.async_camera_image(width, height)
                                
                    # Alternative: Use camera.snapshot service
                    try:
                        await self._hass.services.async_call(
                            "camera",
                            "snapshot",
                            {
                                "entity_id": external_camera_id,
                                "filename": "/tmp/temp_snapshot.jpg"
                            },
                            blocking=True
                        )
                        
                        # Read the temporary file
                        def read_snapshot():
                            try:
                                with open("/tmp/temp_snapshot.jpg", "rb") as f:
                                    return f.read()
                            except FileNotFoundError:
                                return None
                                
                        image_data = await self._hass.async_add_executor_job(read_snapshot)
                        if image_data:
                            return image_data
                    except Exception as e:
                        _LOGGER.debug("Could not get image from external camera %s: %s", 
                                    external_camera_id, e)
                        
            except Exception as e:
                _LOGGER.warning("Error accessing external camera %s: %s", 
                              external_camera_id, e)
        
        # Fallback to last captured image or placeholder
        return self._last_image or self._generate_placeholder_image()

    def turn_on(self) -> None:
        """Turn on camera."""
        self._attr_is_on = True
        self.schedule_update_ha_state()

    def turn_off(self) -> None:
        """Turn off camera."""
        self._attr_is_on = False
        self.schedule_update_ha_state()

    async def async_take_snapshot(self) -> str | None:
        """Take a snapshot and save it to storage."""
        try:
            image_data = None
            
            # Check if we have an external camera entity configured
            plant_config = self._config_entry.data.get(FLOW_PLANT_INFO, {})
            external_camera_id = plant_config.get("camera_entity_id")
            
            if external_camera_id:
                # Try to get image from external camera first
                try:
                    camera_entity = self._hass.states.get(external_camera_id)
                    if camera_entity and camera_entity.state != "unavailable":
                        # Use camera.snapshot service to capture image
                        temp_filepath = f"/tmp/plant_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                        
                        await self._hass.services.async_call(
                            "camera",
                            "snapshot",
                            {
                                "entity_id": external_camera_id,
                                "filename": temp_filepath
                            },
                            blocking=True
                        )
                        
                        # Read the captured image
                        def read_captured_image():
                            try:
                                with open(temp_filepath, "rb") as f:
                                    data = f.read()
                                # Clean up temp file
                                try:
                                    os.remove(temp_filepath)
                                except Exception:
                                    pass
                                return data
                            except FileNotFoundError:
                                return None
                                
                        image_data = await self._hass.async_add_executor_job(read_captured_image)
                        
                        if image_data:
                            _LOGGER.info("Successfully captured image from external camera %s", external_camera_id)
                        else:
                            _LOGGER.warning("Failed to capture image from external camera %s", external_camera_id)
                            
                except Exception as e:
                    _LOGGER.warning("Error capturing from external camera %s: %s", external_camera_id, e)
            
            # Fallback to placeholder if external camera failed or not configured
            if not image_data:
                _LOGGER.debug("Using placeholder image for plant %s", self._plant_entity.name)
                image_data = self._generate_placeholder_image()
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plant_name_slug = slugify(self._plant_entity.name)
            filename = f"{plant_name_slug}_snapshot_{timestamp}.jpg"
            filepath = os.path.join(self._image_storage_path, filename)
            
            # Save image to file
            def write_image():
                with open(filepath, "wb") as f:
                    f.write(image_data)
                    
            await self._hass.async_add_executor_job(write_image)
            
            # Store as last image
            self._last_image = image_data
            self._last_image_timestamp = datetime.now()
            
            # Update plant entity with new image
            await self._update_plant_image(filepath)
            
            self.schedule_update_ha_state()
            
            camera_type = "external camera" if external_camera_id else "placeholder"
            _LOGGER.info("Snapshot taken for %s using %s: %s", 
                        self._plant_entity.name, camera_type, filepath)
            return filepath
            
        except Exception as e:
            _LOGGER.error("Error taking snapshot for %s: %s", self._plant_entity.name, e)
            return None

    def _generate_placeholder_image(self) -> bytes:
        """Generate a placeholder image."""
        # This is a simple placeholder - in a real implementation, you would capture from a camera
        # Create a simple JPEG header for a minimal image
        return b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xdb\x00C\x01\x09\t\t\x0c\x0b\x0c\x18\r\r\x182!\x1c!22222222222222222222222222222222222222222222222222\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\xff\xc4\x00\xb5\x10\x00\x01\x02\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02\x7f\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x01\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x10\x00\x01\x04\x01\x03\x02\x04\x02\x05\x07\x06\x08\x05\x03\x0c6\x01\x02\x03\x00\x04\x11\x05\x12!1\x06\x134\x14Q\xa1q\x07\x15R\xa2\xb1\x16#2\xd1\xc1\xa3\x08\x17B\xb2\xc23\x18S\xb3\xc3\x09\x19\x1a456789:DEFHIJTUVWXYZdefghijrstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xdf\xf8g\xff\x00\x13\xef\xf8I\xff\x00\xe9\xe7\xff\x00g\xaf\xff\xd9'

    async def _update_plant_image(self, image_path: str) -> None:
        """Update the plant entity with the new image."""
        try:
            # Convert file path to local URL
            # Handle different path formats for cross-platform compatibility
            if image_path.startswith(self._hass.config.path("www")):
                # Path is within www directory, convert to local URL
                local_url = image_path.replace(self._hass.config.path("www"), "/local")
            elif "/www/" in image_path:
                # Path contains www, convert to local URL
                local_url = image_path.split("/www/", 1)[1]
                local_url = f"/local/{local_url}"
            else:
                # Fallback: use the filename only
                filename = os.path.basename(image_path)
                local_url = f"/local/images/plants/{filename}"
            
            # Update plant entity's entity_picture
            self._plant_entity._attr_entity_picture = local_url
            
            # Update plant config entry
            data = dict(self._config_entry.data)
            plant_info = dict(data.get(FLOW_PLANT_INFO, {}))
            plant_info["entity_picture"] = local_url
            data[FLOW_PLANT_INFO] = plant_info
            self._hass.config_entries.async_update_entry(self._config_entry, data=data)
            
            # Update plant entity
            self._plant_entity.async_write_ha_state()
            
        except Exception as e:
            _LOGGER.error("Error updating plant image: %s", e)            
        except Exception as e:
            _LOGGER.error("Error taking snapshot: %s", e)
            return None

    def _generate_placeholder_image(self) -> bytes:
        """Generate a placeholder image."""
        # This is a simple placeholder - in a real implementation, you would capture from a camera
        # Create a simple JPEG header for a minimal image
        return b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xdb\x00C\x01\x09\t\t\x0c\x0b\x0c\x18\r\r\x182!\x1c!22222222222222222222222222222222222222222222222222\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\xff\xc4\x00\xb5\x10\x00\x01\x02\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02\x7f\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x01\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x10\x00\x01\x04\x01\x03\x02\x04\x02\x05\x07\x06\x08\x05\x03\x0c6\x01\x02\x03\x00\x04\x11\x05\x12!1\x06\x134\x14Q\xa1q\x07\x15R\xa2\xb1\x16#2\xd1\xc1\xa3\x08\x17B\xb2\xc23\x18S\xb3\xc3\x09\x19\x1a456789:DEFHIJTUVWXYZdefghijrstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xdf\xf8g\xff\x00\x13\xef\xf8I\xff\x00\xe9\xe7\xff\x00g\xaf\xff\xd9'

    async def _update_plant_image(self, image_path: str) -> None:
        """Update the plant entity with the new image."""
        try:
            # Convert file path to local URL
            # Handle different path formats for cross-platform compatibility
            if image_path.startswith(self._hass.config.path("www")):
                # Path is within www directory, convert to local URL
                local_url = image_path.replace(self._hass.config.path("www"), "/local")
            elif "/www/" in image_path:
                # Path contains www, convert to local URL
                local_url = image_path.split("/www/", 1)[1]
                local_url = f"/local/{local_url}"
            else:
                # Fallback: use the filename only
                filename = os.path.basename(image_path)
                local_url = f"/local/images/plants/{filename}"
            
            # Update plant entity's entity_picture
            self._plant_entity._attr_entity_picture = local_url
            
            # Update plant config entry
            data = dict(self._config_entry.data)
            plant_info = dict(data.get(FLOW_PLANT_INFO, {}))
            plant_info["entity_picture"] = local_url
            data[FLOW_PLANT_INFO] = plant_info
            self._hass.config_entries.async_update_entry(self._config_entry, data=data)
            
            # Update plant entity
            self._plant_entity.async_write_ha_state()
            
        except Exception as e:
            _LOGGER.error("Error updating plant image: %s", e)