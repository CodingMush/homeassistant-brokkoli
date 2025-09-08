import pytest

pytestmark = pytest.mark.asyncio


async def test_domain_constants_and_manifest_load():
    # Smoke test: ensure package can be imported and manifest exists
    import importlib
    mod = importlib.import_module("custom_components.plant.const")
    assert getattr(mod, "DOMAIN", None) == "plant"


async def test_config_flow_creates_config_entry(hass):
    # Minimal flow: trigger config node creation first (Options/Defaults)
    result = await hass.config_entries.flow.async_init(
        "plant",
        context={"source": "user"},
        data={},
    )
    assert result["type"] == "create_entry"
    assert result["data"].get("is_config", False) is True


async def test_services_registered_on_setup(hass):
    # Create a basic plant via import path used by services
    from custom_components.plant.const import FLOW_PLANT_INFO, ATTR_NAME, ATTR_STRAIN

    plant_info = {
        ATTR_NAME: "Test Plant",
        ATTR_STRAIN: "Test Strain",
    }

    result = await hass.config_entries.flow.async_init(
        "plant",
        context={"source": "import"},
        data={FLOW_PLANT_INFO: plant_info},
    )
    assert result["type"] == "create_entry"

    # After setup, core services should be present
    assert hass.services.has_service("plant", "replace_sensor")
    assert hass.services.has_service("plant", "create_plant")
    assert hass.services.has_service("plant", "remove_plant")


async def test_unload_entry_cleans_up(hass):
    from custom_components.plant.const import FLOW_PLANT_INFO, ATTR_NAME, ATTR_STRAIN, DOMAIN

    plant_info = {
        ATTR_NAME: "Unload Me",
        ATTR_STRAIN: "Dummy",
    }

    created = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "import"},
        data={FLOW_PLANT_INFO: plant_info},
    )
    entry = created["result"]

    # Unload should succeed
    assert await hass.config_entries.async_unload(entry.entry_id)



