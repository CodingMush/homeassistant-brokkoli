"""Fixtures for plant integration tests."""

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from homeassistant.const import Platform


pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test directory."""
    yield


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    entry = MockConfigEntry(
        domain="plant",
        title="Test Plant",
        data={
            "plant_info": {
                "name": "Test Plant",
                "device_type": "plant",
            }
        },
    )
    return entry


@pytest.fixture
async def init_plant_integration(hass):
    """Initialize the plant integration."""
    await hass.async_block_till_done()
    yield
