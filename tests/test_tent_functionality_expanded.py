"""Expanded test for Tent functionality in the plant integration."""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from custom_components.plant.tent import Tent, JournalEntry, Journal, MaintenanceEntry
from custom_components.plant import PlantDevice


def test_journal_entry_creation():
    """Test creating a journal entry."""
    entry = JournalEntry("Test entry", "Test Author")
    assert entry.content == "Test entry"
    assert entry.author == "Test Author"
    assert isinstance(entry.timestamp, datetime)


def test_journal_entry_to_dict():
    """Test converting journal entry to dict."""
    entry = JournalEntry("Test entry", "Test Author")
    data = entry.to_dict()
    assert "timestamp" in data
    assert data["content"] == "Test entry"
    assert data["author"] == "Test Author"


def test_journal_entry_from_dict():
    """Test creating journal entry from dict."""
    timestamp = datetime.now()
    data = {
        "timestamp": timestamp.isoformat(),
        "content": "Test entry",
        "author": "Test Author"
    }
    entry = JournalEntry.from_dict(data)
    assert entry.content == "Test entry"
    assert entry.author == "Test Author"
    assert entry.timestamp == timestamp


def test_journal_creation():
    """Test creating a journal."""
    journal = Journal()
    assert len(journal.entries) == 0


def test_journal_add_entry():
    """Test adding entries to journal."""
    journal = Journal()
    entry = JournalEntry("Test entry")
    journal.add_entry(entry)
    assert len(journal.entries) == 1
    assert journal.entries[0] == entry


def test_journal_get_entries():
    """Test getting entries from journal."""
    journal = Journal()
    entry1 = JournalEntry("Test entry 1")
    entry2 = JournalEntry("Test entry 2")
    journal.add_entry(entry1)
    journal.add_entry(entry2)
    
    entries = journal.get_entries()
    assert len(entries) == 2
    assert entries[0] == entry1
    assert entries[1] == entry2
    # Test that it returns a copy
    assert entries is not journal.entries


def test_journal_to_dict():
    """Test converting journal to dict."""
    journal = Journal()
    entry = JournalEntry("Test entry", "Test Author")
    journal.add_entry(entry)
    
    data = journal.to_dict()
    assert "entries" in data
    assert len(data["entries"]) == 1


def test_journal_from_dict():
    """Test creating journal from dict."""
    timestamp = datetime.now()
    data = {
        "entries": [
            {
                "timestamp": timestamp.isoformat(),
                "content": "Test entry",
                "author": "Test Author"
            }
        ]
    }
    journal = Journal.from_dict(data)
    assert len(journal.entries) == 1
    assert journal.entries[0].content == "Test entry"


def test_maintenance_entry_creation():
    """Test creating a maintenance entry."""
    entry = MaintenanceEntry("Test maintenance", "Test Technician", 100.50)
    assert entry.description == "Test maintenance"
    assert entry.performed_by == "Test Technician"
    assert entry.cost == 100.50
    assert isinstance(entry.timestamp, datetime)


def test_maintenance_entry_to_dict():
    """Test converting maintenance entry to dict."""
    entry = MaintenanceEntry("Test maintenance", "Test Technician", 100.50)
    data = entry.to_dict()
    assert "timestamp" in data
    assert data["description"] == "Test maintenance"
    assert data["performed_by"] == "Test Technician"
    assert data["cost"] == 100.50


def test_maintenance_entry_from_dict():
    """Test creating maintenance entry from dict."""
    timestamp = datetime.now()
    data = {
        "timestamp": timestamp.isoformat(),
        "description": "Test maintenance",
        "performed_by": "Test Technician",
        "cost": 100.50
    }
    entry = MaintenanceEntry.from_dict(data)
    assert entry.description == "Test maintenance"
    assert entry.performed_by == "Test Technician"
    assert entry.cost == 100.50
    assert entry.timestamp == timestamp


@pytest.fixture
def hass():
    """Mock Home Assistant instance."""
    return Mock(spec=HomeAssistant)


@pytest.fixture
def config_entry():
    """Mock config entry."""
    entry = Mock(spec=ConfigEntry)
    entry.data = {
        "plant_info": {
            "name": "Test Plant",
            "device_type": "plant"
        }
    }
    entry.options = {}
    entry.entry_id = "test_entry_id"
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
    return entry


def test_tent_creation(hass, tent_config):
    """Test creating a tent."""
    tent = Tent(hass, tent_config)
    assert tent.name == "Test Tent"
    assert tent.tent_id == "tent_0001"
    assert tent.unique_id == "tent_tent_0001"
    assert tent.device_type == "tent"
    assert len(tent.get_sensors()) == 5


def test_tent_add_remove_sensor(hass, tent_config):
    """Test adding and removing sensors from tent."""
    tent = Tent(hass, tent_config)
    
    # Test adding a sensor
    tent.add_sensor("sensor.new_sensor")
    assert len(tent.get_sensors()) == 6
    assert "sensor.new_sensor" in tent.get_sensors()
    
    # Test removing a sensor
    tent.remove_sensor("sensor.new_sensor")
    assert len(tent.get_sensors()) == 5
    assert "sensor.new_sensor" not in tent.get_sensors()


def test_tent_journal_functionality(hass, tent_config):
    """Test tent journal functionality."""
    tent = Tent(hass, tent_config)
    
    # Test adding journal entry
    entry = JournalEntry("Test journal entry")
    tent.add_journal_entry(entry)
    
    # Test getting journal
    journal = tent.get_journal()
    assert len(journal.get_entries()) == 1
    assert journal.get_entries()[0].content == "Test journal entry"


def test_tent_maintenance_functionality(hass, tent_config):
    """Test tent maintenance functionality."""
    tent = Tent(hass, tent_config)
    
    # Test adding maintenance entry
    entry = MaintenanceEntry("Test maintenance", "Technician", 50.0)
    tent.add_maintenance_entry(entry)
    
    # Test getting maintenance entries
    entries = tent.get_maintenance_entries()
    assert len(entries) == 1
    assert entries[0].description == "Test maintenance"
    assert entries[0].performed_by == "Technician"
    assert entries[0].cost == 50.0


@patch('homeassistant.core.StateMachine.get')
def test_replace_sensors_with_valid_sensors(mock_state_get, hass, config_entry):
    """Test replace_sensors with valid sensor list."""
    # Mock sensor states with device classes and units
    temp_sensor_state = Mock()
    temp_sensor_state.attributes = {
        "device_class": "temperature",
        "unit_of_measurement": "°C"
    }
    
    humidity_sensor_state = Mock()
    humidity_sensor_state.attributes = {
        "device_class": "humidity",
        "unit_of_measurement": "%"
    }
    
    co2_sensor_state = Mock()
    co2_sensor_state.attributes = {
        "unit_of_measurement": "ppm"
    }
    
    illuminance_sensor_state = Mock()
    illuminance_sensor_state.attributes = {
        "device_class": "illuminance",
        "unit_of_measurement": "lx"
    }
    
    power_sensor_state = Mock()
    power_sensor_state.attributes = {
        "unit_of_measurement": "W"
    }
    
    def state_get_side_effect(entity_id):
        if entity_id == "sensor.temperature":
            return temp_sensor_state
        elif entity_id == "sensor.humidity":
            return humidity_sensor_state
        elif entity_id == "sensor.co2":
            return co2_sensor_state
        elif entity_id == "sensor.illuminance":
            return illuminance_sensor_state
        elif entity_id == "sensor.power":
            return power_sensor_state
        return None
        
    mock_state_get.side_effect = state_get_side_effect
    
    # Create plant device
    plant = PlantDevice(hass, config_entry)
    
    # Mock plant sensors with replace_external_sensor methods
    plant.sensor_temperature = Mock()
    plant.sensor_humidity = Mock()
    plant.sensor_illuminance = Mock()
    plant.sensor_CO2 = Mock()
    plant.sensor_power_consumption = Mock()
    
    # Mock config entry update method
    plant._hass.config_entries.async_update_entry = Mock()
    
    # Call replace_sensors with sensor list
    tent_sensors = [
        "sensor.temperature", 
        "sensor.humidity", 
        "sensor.co2", 
        "sensor.illuminance", 
        "sensor.power"
    ]
    plant.replace_sensors(tent_sensors)
    
    # Verify sensors were replaced correctly
    plant.sensor_temperature.replace_external_sensor.assert_called_once_with("sensor.temperature")
    plant.sensor_humidity.replace_external_sensor.assert_called_once_with("sensor.humidity")
    plant.sensor_CO2.replace_external_sensor.assert_called_once_with("sensor.co2")
    plant.sensor_illuminance.replace_external_sensor.assert_called_once_with("sensor.illuminance")
    plant.sensor_power_consumption.replace_external_sensor.assert_called_once_with("sensor.power")
    
    # Verify config entry was updated
    plant._hass.config_entries.async_update_entry.assert_called_once()


def test_assign_tent_success(hass, config_entry, tent_config):
    """Test successful tent assignment to plant."""
    # Create plant device
    plant = PlantDevice(hass, config_entry)
    
    # Create tent
    tent = Tent(hass, tent_config)
    
    # Mock the replace_sensors method to verify it's called
    plant.replace_sensors = Mock()
    
    # Assign tent to plant
    plant.assign_tent(tent)
    
    # Verify tent was assigned
    assert plant.get_assigned_tent() == tent
    assert plant.get_tent_id() == "tent_0001"
    
    # Verify replace_sensors was called with tent sensors
    plant.replace_sensors.assert_called_once_with([
        "sensor.temperature",
        "sensor.humidity", 
        "sensor.co2",
        "sensor.illuminance",
        "sensor.power"
    ])


def test_tent_to_dict(hass, tent_config):
    """Test converting tent to dictionary."""
    tent = Tent(hass, tent_config)
    
    # Add some data
    entry = JournalEntry("Test entry")
    tent.add_journal_entry(entry)
    
    maintenance = MaintenanceEntry("Test maintenance", "Technician", 100.0)
    tent.add_maintenance_entry(maintenance)
    
    # Convert to dict
    data = tent.to_dict()
    
    assert data["tent_id"] == "tent_0001"
    assert data["name"] == "Test Tent"
    assert len(data["sensors"]) == 5
    assert "journal" in data
    assert "maintenance_entries" in data
    assert "created_at" in data
    assert "updated_at" in data


if __name__ == "__main__":
    test_journal_entry_creation()
    test_journal_entry_to_dict()
    test_journal_entry_from_dict()
    test_journal_creation()
    test_journal_add_entry()
    test_journal_get_entries()
    test_journal_to_dict()
    test_journal_from_dict()
    test_maintenance_entry_creation()
    test_maintenance_entry_to_dict()
    test_maintenance_entry_from_dict()
    print("All expanded tent functionality tests passed!")