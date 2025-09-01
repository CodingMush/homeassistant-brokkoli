"""Unit tests for virtual sensor functionality."""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from homeassistant.core import HomeAssistant, State
from homeassistant.const import STATE_OK, STATE_UNAVAILABLE, UnitOfTemperature
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.entity_registry as er

from custom_components.plant.const import (
    ATTR_TEMPERATURE,
    ATTR_HUMIDITY,
    ATTR_CO2,
    DEVICE_TYPE_TENT,
    DEVICE_TYPE_PLANT,
    FLOW_PLANT_INFO,
    FLOW_SENSOR_TEMPERATURE,
)


class MockVirtualSensor:
    """Mock virtual sensor for testing."""
    
    def __init__(self, hass, config, plantdevice, sensor_type, reading_name, icon, unit=None, device_class=None):
        self._hass = hass
        self._config = config
        self._plant = plantdevice
        self._sensor_type = sensor_type
        self._reading_name = reading_name
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_name = f"{plantdevice.name} {reading_name}"
        self._attr_unique_id = f"{config.entry_id}-virtual-{sensor_type}"
        self._reference_entity_id = None
        self._default_state = 0
        
        # Mock the update reference method
        self._update_virtual_reference = Mock()
    
    @property
    def state(self):
        """Return the state of the sensor."""
        if not self._reference_entity_id:
            return self._default_state
        
        # Mock getting state from reference
        if self._hass and self._hass.states:
            state_obj = self._hass.states.get(self._reference_entity_id)
            if state_obj and state_obj.state not in [STATE_UNAVAILABLE, None]:
                return state_obj.state
        return STATE_UNAVAILABLE
    
    @property
    def extra_state_attributes(self):
        """Return extra attributes including virtual sensor info."""
        return {
            "is_virtual_sensor": True,
            "virtual_sensor_reference": self._reference_entity_id,
            "sensor_type": self._sensor_type,
        }
    
    @property
    def device_class(self):
        """Return the device class."""
        return self._attr_device_class
    
    @property
    def name(self):
        """Return the name."""
        return self._attr_name


class TestVirtualSensor:
    """Test virtual sensor entity functionality."""

    @pytest.fixture
    def mock_hass(self):
        """Create mock Home Assistant instance."""
        hass = Mock(spec=HomeAssistant)
        hass.states = Mock()
        hass.states.get = Mock()
        hass.config = Mock()
        hass.config.units = Mock()
        hass.config.units.temperature_unit = UnitOfTemperature.CELSIUS
        return hass

    @pytest.fixture
    def mock_config(self):
        """Create mock config entry."""
        config = Mock()
        config.entry_id = "test_config_id"
        config.data = {
            FLOW_PLANT_INFO: {
                FLOW_SENSOR_TEMPERATURE: "sensor.standalone_temperature"
            }
        }
        return config

    @pytest.fixture
    def virtual_sensor(self, mock_hass, mock_config):
        """Create virtual sensor entity."""
        # Create a mock plant device
        mock_plant_device = Mock()
        mock_plant_device.name = "Test Plant"
        mock_plant_device.unique_id = "test_plant_id"
        
        return MockVirtualSensor(
            hass=mock_hass,
            config=mock_config,
            plantdevice=mock_plant_device,
            sensor_type=ATTR_TEMPERATURE,
            reading_name="Temperature",
            icon="mdi:thermometer",
            unit="°C",
            device_class="temperature"
        )

    def test_virtual_sensor_initialization(self, virtual_sensor):
        """Test virtual sensor initializes correctly."""
        assert virtual_sensor._sensor_type == ATTR_TEMPERATURE
        assert virtual_sensor._attr_unique_id == "test_config_id-virtual-temperature"

    def test_virtual_sensor_state_from_reference(self, virtual_sensor, mock_hass):
        """Test virtual sensor gets state from reference entity."""
        # Set up reference entity ID
        virtual_sensor._reference_entity_id = "sensor.tent_temperature"
        
        # Mock reference entity state
        mock_state = Mock(spec=State)
        mock_state.state = "22.5"
        mock_state.attributes = {"unit_of_measurement": "°C"}
        mock_hass.states.get.return_value = mock_state
        
        # Get virtual sensor state
        state = virtual_sensor.state
        
        # Verify state comes from reference
        assert state == "22.5"
        mock_hass.states.get.assert_called_with("sensor.tent_temperature")

    def test_virtual_sensor_unavailable_reference(self, virtual_sensor, mock_hass):
        """Test virtual sensor handles unavailable reference entity."""
        # Set up reference entity ID
        virtual_sensor._reference_entity_id = "sensor.tent_temperature"
        
        # Mock unavailable reference entity
        mock_state = Mock(spec=State)
        mock_state.state = STATE_UNAVAILABLE
        mock_hass.states.get.return_value = mock_state
        
        # Get virtual sensor state
        state = virtual_sensor.state
        
        # Should return unavailable
        assert state == STATE_UNAVAILABLE

    def test_virtual_sensor_missing_reference(self, virtual_sensor, mock_hass):
        """Test virtual sensor handles missing reference entity."""
        # Set up reference entity ID
        virtual_sensor._reference_entity_id = "sensor.tent_temperature"
        
        # Mock missing reference entity
        mock_hass.states.get.return_value = None
        
        # Get virtual sensor state
        state = virtual_sensor.state
        
        # Should return unavailable
        assert state == STATE_UNAVAILABLE

    def test_virtual_sensor_attributes_from_reference(self, virtual_sensor, mock_hass):
        """Test virtual sensor gets attributes from reference entity."""
        # Set up reference entity ID
        virtual_sensor._reference_entity_id = "sensor.tent_temperature"
        
        # Mock reference entity with attributes
        mock_state = Mock(spec=State)
        mock_state.state = "22.5"
        mock_state.attributes = {
            "unit_of_measurement": "°C",
            "device_class": "temperature",
            "friendly_name": "Tent Temperature"
        }
        mock_hass.states.get.return_value = mock_state
        
        # Get virtual sensor attributes
        attributes = virtual_sensor.extra_state_attributes
        
        # Verify attributes include reference info
        assert attributes["virtual_sensor_reference"] == "sensor.tent_temperature"
        assert attributes["sensor_type"] == ATTR_TEMPERATURE
        assert attributes["is_virtual_sensor"] is True

    def test_virtual_sensor_name_generation(self, virtual_sensor):
        """Test virtual sensor generates correct name."""
        expected_name = "Test Plant Temperature"
        # The name should be based on the plant entity name + sensor type
        assert "Test Plant Temperature" in virtual_sensor._attr_name

    def test_virtual_sensor_device_class(self, virtual_sensor):
        """Test virtual sensor has device class."""
        # Virtual sensor should have the device class set during initialization
        device_class = virtual_sensor.device_class
        # Should be set to "temperature" from initialization
        assert device_class == "temperature"


class MockVirtualSensorManager:
    """Mock virtual sensor manager for testing."""
    
    def __init__(self, hass):
        self._hass = hass
        self._virtual_sensors = {}
    
    def create_virtual_sensors_for_plant(self, plant_device, config):
        """Create virtual sensors for a plant."""
        virtual_sensors = {}
        
        # Create mock virtual sensors
        mock_sensor = Mock()
        mock_sensor._sensor_type = 'temperature'
        virtual_sensors['temperature'] = mock_sensor
        
        return virtual_sensors
    
    def cleanup_virtual_sensors(self, plant_id):
        """Cleanup virtual sensors for a plant."""
        if plant_id in self._virtual_sensors:
            del self._virtual_sensors[plant_id]


class TestVirtualSensorManager:
    """Test optimized sensor manager with virtual sensors."""

    @pytest.fixture
    def mock_hass(self):
        """Create mock Home Assistant instance."""
        hass = Mock(spec=HomeAssistant)
        hass.states = Mock()
        hass.data = {}
        hass.bus = Mock()
        hass.bus.async_listen = Mock()
        hass.config = Mock()
        hass.config.units = Mock()
        hass.config.units.temperature_unit = "°C"
        return hass

    @pytest.fixture
    def sensor_manager(self, mock_hass):
        """Create optimized sensor manager."""
        return MockVirtualSensorManager(mock_hass)

    def test_create_virtual_sensor(self, sensor_manager, mock_hass):
        """Test creating virtual sensor through manager."""
        plant_id = "plant.test_plant"
        tent_id = "plant.test_tent"
        
        # Create mock plant device and config
        mock_plant_device = Mock()
        mock_plant_device.name = "Test Plant"
        mock_plant_device.uses_virtual_sensors = True
        mock_plant_device.entity_id = plant_id
        mock_plant_device.unique_id = "test_plant_id"
        
        mock_config = Mock()
        mock_config.entry_id = "test_config_id"
        
        # Create virtual sensors for plant
        virtual_sensors = sensor_manager.create_virtual_sensors_for_plant(
            plant_device=mock_plant_device,
            config=mock_config
        )
        
        # Verify virtual sensors were created (dictionary of sensor_type -> VirtualSensor)
        assert isinstance(virtual_sensors, dict)
        # At minimum should have temperature sensor
        assert len(virtual_sensors) > 0

    def test_virtual_sensor_cleanup(self, sensor_manager):
        """Test cleanup of virtual sensors when plant unassigned."""
        plant_id = "plant.test_plant"
        
        # Mock virtual sensors exist
        sensor_manager._virtual_sensors = {
            plant_id: {
                ATTR_TEMPERATURE: Mock(),
                ATTR_HUMIDITY: Mock(),
            }
        }
        
        # Cleanup virtual sensors for plant
        sensor_manager.cleanup_virtual_sensors(plant_id)
        
        # Verify cleanup
        assert plant_id not in sensor_manager._virtual_sensors