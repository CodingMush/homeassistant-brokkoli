"""Simple integration test to verify the plant integration can be loaded."""

def test_imports():
    """Test that all modules can be imported."""
    # Test importing the main module
    import custom_components.plant
    assert custom_components.plant is not None
    
    # Test importing const module
    import custom_components.plant.const
    assert custom_components.plant.const is not None
    
    # Test importing sensor module
    import custom_components.plant.sensor
    assert custom_components.plant.sensor is not None
    
    # Test importing the PlantDevice class
    from custom_components.plant import PlantDevice
    assert PlantDevice is not None


def test_constants():
    """Test that critical constants are defined."""
    from custom_components.plant.const import (
        READING_DLI,
        READING_PPFD,
        READING_MOISTURE_CONSUMPTION,
        READING_FERTILIZER_CONSUMPTION,
        UNIT_PPFD,
        UNIT_DLI,
        ICON_PPFD,
        ICON_DLI,
        ICON_CO2,
        ICON_WATER_CONSUMPTION,
        ICON_FERTILIZER_CONSUMPTION,
        ICON_POWER_CONSUMPTION,
    )
    
    # Verify all constants are defined and are strings
    assert isinstance(READING_DLI, str)
    assert isinstance(READING_PPFD, str)
    assert isinstance(READING_MOISTURE_CONSUMPTION, str)
    assert isinstance(READING_FERTILIZER_CONSUMPTION, str)
    assert isinstance(UNIT_PPFD, str)
    assert isinstance(UNIT_DLI, str)
    assert isinstance(ICON_PPFD, str)
    assert isinstance(ICON_DLI, str)
    assert isinstance(ICON_CO2, str)
    assert isinstance(ICON_WATER_CONSUMPTION, str)
    assert isinstance(ICON_FERTILIZER_CONSUMPTION, str)
    assert isinstance(ICON_POWER_CONSUMPTION, str)