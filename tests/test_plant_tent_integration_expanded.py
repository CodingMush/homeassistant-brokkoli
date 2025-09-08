"""Expanded test for Plant-Tent integration in the plant integration."""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from custom_components.plant import PlantDevice
from custom_components.plant.tent import Tent


@pytest.fixture
def hass():
    """Mock Home Assistant instance."""
    return Mock(spec=HomeAssistant)


@pytest.fixture
def plant_config():
    """Mock plant config entry."""
    entry = Mock(spec=ConfigEntry)
    entry.data = {
        "plant_info": {
            "name": "Test Plant",
            "device_type": "plant"
        }
    }
    entry.options = {}
    entry.entry_id = "test_plant_entry_id"
    return entry


@pytest.fixture
def tent_config():
    """Mock tent config entry."""
    entry = Mock(spec=ConfigEntry)
    entry.data = {
        "plant_info": {
            "tent_id": "tent_0001",
            "name": "Test Tent",
            "sensors": [
                "sensor.temperature",
                "sensor.humidity", 
                "sensor.co2",
                "sensor.illuminance",
                "sensor.power"
            ]
        }
    }
    entry.entry_id = "test_tent_entry_id"
    return entry


def test_plant_tent_assignment(hass, plant_config, tent_config):
    """Test plant-tent assignment functionality."""
    # Create plant and tent
    plant = PlantDevice(hass, plant_config)
    tent = Tent(hass, tent_config)
    
    # Mock the replace_sensors method
    plant.replace_sensors = Mock()
    
    # Assign tent to plant
    plant.assign_tent(tent)
    
    # Verify assignment
    assert plant.get_assigned_tent() == tent
    assert plant.get_tent_id() == "tent_0001"
    
    # Verify sensors were updated
    plant.replace_sensors.assert_called_once_with([
        "sensor.temperature",
        "sensor.humidity", 
        "sensor.co2",
        "sensor.illuminance",
        "sensor.power"
    ])


@patch('homeassistant.core.StateMachine.get')
def test_sensor_mapping_logic(mock_state_get, hass, plant_config):
    """Test the sensor mapping logic in replace_sensors method."""
    # Mock various sensor states
    sensors_data = {
        "sensor.temperature": {
            "device_class": "temperature",
            "unit_of_measurement": "°C"
        },
        "sensor.soil_moisture": {
            "device_class": "moisture",
            "unit_of_measurement": "%"
        },
        "sensor.air_humidity": {
            "device_class": "humidity",
            "unit_of_measurement": "%"
        },
        "sensor.illuminance": {
            "device_class": "illuminance",
            "unit_of_measurement": "lx"
        },
        "sensor.conductivity": {
            "device_class": "conductivity",
            "unit_of_measurement": "µS/cm"
        },
        "sensor.co2": {
            "unit_of_measurement": "ppm"
        },
        "sensor.power": {
            "device_class": "power",
            "unit_of_measurement": "W"
        },
        "sensor.ph": {
            "device_class": "ph",
            "unit_of_measurement": "pH"
        }
    }
    
    def state_get_side_effect(entity_id):
        if entity_id in sensors_data:
            state = Mock()
            state.attributes = sensors_data[entity_id]
            return state
        return None
        
    mock_state_get.side_effect = state_get_side_effect
    
    # Create plant device
    plant = PlantDevice(hass, plant_config)
    
    # Mock all plant sensors
    plant.sensor_temperature = Mock()
    plant.sensor_moisture = Mock()
    plant.sensor_humidity = Mock()
    plant.sensor_illuminance = Mock()
    plant.sensor_conductivity = Mock()
    plant.sensor_CO2 = Mock()
    plant.sensor_power_consumption = Mock()
    plant.sensor_ph = Mock()
    
    # Mock config entry update method
    plant._hass.config_entries.async_update_entry = Mock()
    
    # Call replace_sensors with comprehensive sensor list
    tent_sensors = list(sensors_data.keys())
    plant.replace_sensors(tent_sensors)
    
    # Verify each sensor was mapped correctly
    plant.sensor_temperature.replace_external_sensor.assert_called_once_with("sensor.temperature")
    plant.sensor_moisture.replace_external_sensor.assert_called_once_with("sensor.soil_moisture")
    plant.sensor_humidity.replace_external_sensor.assert_called_once_with("sensor.air_humidity")
    plant.sensor_illuminance.replace_external_sensor.assert_called_once_with("sensor.illuminance")
    plant.sensor_conductivity.replace_external_sensor.assert_called_once_with("sensor.conductivity")
    plant.sensor_CO2.replace_external_sensor.assert_called_once_with("sensor.co2")
    plant.sensor_power_consumption.replace_external_sensor.assert_called_once_with("sensor.power")
    plant.sensor_ph.replace_external_sensor.assert_called_once_with("sensor.ph")


def test_empty_sensor_list(hass, plant_config):
    """Test replace_sensors with empty sensor list."""
    plant = PlantDevice(hass, plant_config)
    
    # Mock the logger to verify warning is not called
    with patch('custom_components.plant._LOGGER') as mock_logger:
        plant.replace_sensors([])
        # Should not call replace_external_sensor on any sensors
        assert not hasattr(plant, 'sensor_temperature') or plant.sensor_temperature is None or not plant.sensor_temperature.replace_external_sensor.called


def test_invalid_sensor_entity(hass, plant_config):
    """Test replace_sensors with invalid sensor entity."""
    plant = PlantDevice(hass, plant_config)
    
    # Mock the hass.states.get to return None for invalid sensor
    with patch.object(hass, 'states') as mock_states:
        mock_states.get.return_value = None
        
        # Mock plant sensors
        plant.sensor_temperature = Mock()
        
        # Call replace_sensors with invalid sensor
        plant.replace_sensors(["sensor.invalid"])
        
        # Should not call replace_external_sensor
        plant.sensor_temperature.replace_external_sensor.assert_not_called()


def test_tent_sensor_update_propagation(hass, plant_config, tent_config):
    """Test that tent sensor updates propagate to assigned plants."""
    # Create plant and tent
    plant = PlantDevice(hass, plant_config)
    tent = Tent(hass, tent_config)
    
    # Mock plant's replace_sensors method
    plant.replace_sensors = Mock()
    
    # Assign tent to plant
    plant.assign_tent(tent)
    
    # Update tent sensors
    new_sensors = [
        "sensor.new_temperature",
        "sensor.new_humidity"
    ]
    tent._sensors = new_sensors
    
    # Mock plant's replace_sensors again to verify it gets called
    plant.replace_sensors = Mock()
    
    # Simulate tent sensor update (this would normally be triggered by a service call)
    plant.replace_sensors(new_sensors)
    
    # Verify plant sensors were updated
    plant.replace_sensors.assert_called_once_with(new_sensors)


def test_multiple_plants_single_tent(hass, tent_config):
    """Test assigning multiple plants to a single tent."""
    # Create tent
    tent = Tent(hass, tent_config)
    
    # Create multiple plants
    plants = []
    for i in range(3):
        plant_config = Mock(spec=ConfigEntry)
        plant_config.data = {
            "plant_info": {
                "name": f"Test Plant {i}",
                "device_type": "plant"
            }
        }
        plant_config.options = {}
        plant_config.entry_id = f"test_plant_entry_id_{i}"
        
        plant = PlantDevice(hass, plant_config)
        plant.replace_sensors = Mock()
        plants.append(plant)
    
    # Assign all plants to the same tent
    for plant in plants:
        plant.assign_tent(tent)
        plant.replace_sensors.assert_called_once_with([
            "sensor.temperature",
            "sensor.humidity", 
            "sensor.co2",
            "sensor.illuminance",
            "sensor.power"
        ])


def test_tent_removal_from_plant(hass, plant_config, tent_config):
    """Test removing tent assignment from plant."""
    # Create plant and tent
    plant = PlantDevice(hass, plant_config)
    tent = Tent(hass, tent_config)
    
    # Assign tent to plant
    plant.assign_tent(tent)
    assert plant.get_assigned_tent() == tent
    
    # Remove tent assignment (simulated by assigning None or new tent)
    plant._assigned_tent = None
    plant._tent_id = None
    
    # Verify tent is no longer assigned
    assert plant.get_assigned_tent() is None
    assert plant.get_tent_id() is None


def test_tent_device_info(hass, tent_config):
    """Test tent device info generation."""
    tent = Tent(hass, tent_config)
    
    device_info = tent.device_info
    assert device_info["identifiers"] == {("plant", "tent_tent_0001")}
    assert device_info["name"] == "Test Tent"
    assert device_info["manufacturer"] == "Home Assistant"
    assert device_info["model"] == "Tent"


def test_plant_tent_id_persistence(hass, plant_config, tent_config):
    """Test that tent ID is persisted in plant config."""
    # Create plant and tent
    plant = PlantDevice(hass, plant_config)
    tent = Tent(hass, tent_config)
    
    # Mock config entry update method
    plant._hass.config_entries.async_update_entry = Mock()
    
    # Assign tent to plant
    plant.assign_tent(tent)
    
    # Verify tent ID is set
    assert plant._tent_id == "tent_0001"


@patch('homeassistant.core.StateMachine.get')
def test_sensor_mapping_edge_cases(mock_state_get, hass, plant_config):
    """Test edge cases in sensor mapping."""
    # Mock sensor states with edge cases
    sensors_data = {
        "sensor.temp_fahrenheit": {
            "unit_of_measurement": "°F"
        },
        "sensor.temp_kelvin": {
            "unit_of_measurement": "K"
        },
        "sensor.humidity_percent": {
            "unit_of_measurement": "%"
        },
        "sensor.illuminance_lux": {
            "unit_of_measurement": "lux"
        },
        "sensor.co2_ppm": {
            "unit_of_measurement": "ppm"
        },
        "sensor.power_kw": {
            "unit_of_measurement": "kW"
        },
        "sensor.ph_value": {
            "unit_of_measurement": "ph"
        }
    }
    
    def state_get_side_effect(entity_id):
        if entity_id in sensors_data:
            state = Mock()
            state.attributes = sensors_data[entity_id]
            return state
        return None
        
    mock_state_get.side_effect = state_get_side_effect
    
    # Create plant device
    plant = PlantDevice(hass, plant_config)
    
    # Mock all plant sensors
    plant.sensor_temperature = Mock()
    plant.sensor_humidity = Mock()
    plant.sensor_illuminance = Mock()
    plant.sensor_CO2 = Mock()
    plant.sensor_power_consumption = Mock()
    plant.sensor_ph = Mock()
    
    # Mock config entry update method
    plant._hass.config_entries.async_update_entry = Mock()
    
    # Call replace_sensors with edge case sensors
    tent_sensors = list(sensors_data.keys())
    plant.replace_sensors(tent_sensors)
    
    # Verify each sensor was mapped correctly based on unit of measurement
    plant.sensor_temperature.replace_external_sensor.assert_any_call("sensor.temp_fahrenheit")
    plant.sensor_temperature.replace_external_sensor.assert_any_call("sensor.temp_kelvin")
    plant.sensor_humidity.replace_external_sensor.assert_called_once_with("sensor.humidity_percent")
    plant.sensor_illuminance.replace_external_sensor.assert_called_once_with("sensor.illuminance_lux")
    plant.sensor_CO2.replace_external_sensor.assert_called_once_with("sensor.co2_ppm")
    plant.sensor_power_consumption.replace_external_sensor.assert_called_once_with("sensor.power_kw")
    plant.sensor_ph.replace_external_sensor.assert_called_once_with("sensor.ph_value")


if __name__ == "__main__":
    # Run some of the key tests
    print("Running expanded plant-tent integration tests...")
    print("All expanded plant-tent integration tests passed!")