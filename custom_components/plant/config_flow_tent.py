"""Config flow for Tent integration."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries, data_entry_flow
from homeassistant.const import ATTR_NAME
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class TentConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tent."""

    VERSION = 1

    def __init__(self):
        """Initialize flow."""
        self.tent_info = {}
        self.error = None

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input is not None:
            self.tent_info[ATTR_NAME] = user_input[ATTR_NAME]
            return self.async_create_entry(
                title=self.tent_info[ATTR_NAME],
                data=self.tent_info,
            )

        data_schema = {
            vol.Required(ATTR_NAME): str,
        }

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=errors
        )
