"""Select entities for tent maintenance."""
from __future__ import annotations

import logging
import asyncio
from datetime import datetime

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    ATTR_PLANT,
    DOMAIN,
    DEVICE_TYPE_TENT,
    TREATMENT_OPTIONS,
    TREATMENT_NONE,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the tent select entities."""
    tent = hass.data[DOMAIN][entry.entry_id][ATTR_PLANT]
    
    # Only set up select entities for tents
    if tent.device_type != DEVICE_TYPE_TENT:
        return
        
    entities = []
    
    # Maintenance Select for tents
    maintenance_select = TentMaintenanceSelect(hass, entry, tent)
    entities.append(maintenance_select)
    
    async_add_entities(entities)

class TentMaintenanceSelect(SelectEntity, RestoreEntity):
    """Representation of a tent maintenance selector."""

    def __init__(self, hass: HomeAssistant, config: ConfigEntry, tent_device) -> None:
        """Initialize the maintenance select entity."""
        self._attr_options = [TREATMENT_NONE] + TREATMENT_OPTIONS  # Empty option at the beginning
        self._attr_current_option = TREATMENT_NONE  # Empty option as default
        self._config = config
        self._hass = hass
        self._tent = tent_device
        self._attr_name = f"{tent_device.name} Maintenance"
        self._attr_unique_id = f"{config.entry_id}-tent-maintenance"
        
        # Initialize basic attributes
        self._attr_extra_state_attributes = {
            "friendly_name": self._attr_name
        }

    @property
    def device_info(self) -> dict:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._tent.unique_id)},
        }

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        
        # Restore last state
        last_state = await self.async_get_last_state()
        if last_state:
            self._attr_current_option = last_state.state if last_state.state != "None" else TREATMENT_NONE
            if last_state.attributes:
                self._attr_extra_state_attributes.update(last_state.attributes)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option == TREATMENT_NONE:  # If empty option was selected
            self._attr_current_option = TREATMENT_NONE
            self.async_write_ha_state()
            return

        self._attr_current_option = option
        self.async_write_ha_state()

        _LOGGER.debug(
            "Selected maintenance %s for %s",
            option,
            self._tent.entity_id
        )

        # Add maintenance entry to tent
        if self._tent:
            from .tent import MaintenanceEntry, JournalEntry
            # Create maintenance entry
            maintenance_entry = MaintenanceEntry(option, "User")
            self._tent.add_maintenance_entry(maintenance_entry)
            
            # Also add to journal
            journal_entry = JournalEntry(f"Maintenance performed: {option}", "System")
            self._tent.add_journal_entry(journal_entry)

        # Reset to empty string after 2 seconds
        async def reset_maintenance():
            await asyncio.sleep(2)
            self._attr_current_option = TREATMENT_NONE
            self.async_write_ha_state()

        # Start the reset timer
        asyncio.create_task(reset_maintenance())