import pytest


@pytest.fixture
def hass(event_loop):
    # Lazy import HA test helpers only if available in dev env
    try:
        from pytest_homeassistant_custom_component.common import (  # type: ignore
            async_test_home_assistant,
        )
    except Exception:  # pragma: no cover - optional dev dependency missing
        pytest.skip("pytest-homeassistant-custom-component not installed")

    hass = event_loop.run_until_complete(async_test_home_assistant())
    yield hass
    event_loop.run_until_complete(hass.async_stop())



