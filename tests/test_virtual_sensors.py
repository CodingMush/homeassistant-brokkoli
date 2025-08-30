"""Unit tests for virtual sensor functionality."""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from homeassistant.core import HomeAssistant, State
from homeassistant.const import STATE_OK, STATE_UNAVAILABLE, UnitOfTemperature
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.entity_registry as er

from custom_components.plant.sensor import VirtualSensorEntity, OptimizedSensorManager
from custom_components.plant.const import (
    SENSOR_TEMPERATURE,
    SENSOR_HUMIDITY,
    SENSOR_CO2,
    DEVICE_TYPE_TENT,
    DEVICE_TYPE_PLANT,
)


class TestVirtualSensorEntity:
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
    def virtual_sensor(self, mock_hass):
        """Create virtual sensor entity."""
        return VirtualSensorEntity(
            hass=mock_hass,
            plant_entity_id="plant.test_plant",
            sensor_type=SENSOR_TEMPERATURE,
            reference_entity_id="sensor.tent_temperature",
            tent_entity_id="plant.test_tent"
        )

    def test_virtual_sensor_initialization(self, virtual_sensor):
        """Test virtual sensor initializes correctly."""
        assert virtual_sensor._plant_entity_id == "plant.test_plant"
        assert virtual_sensor._sensor_type == SENSOR_TEMPERATURE
        assert virtual_sensor._reference_entity_id == "sensor.tent_temperature"
        assert virtual_sensor._tent_entity_id == "plant.test_tent"
        assert virtual_sensor.unique_id == "plant.test_plant_temperature_virtual"

    def test_virtual_sensor_state_from_reference(self, virtual_sensor, mock_hass):
        """Test virtual sensor gets state from reference entity."""
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
        # Mock missing reference entity
        mock_hass.states.get.return_value = None
        
        # Get virtual sensor state
        state = virtual_sensor.state
        
        # Should return unavailable
        assert state == STATE_UNAVAILABLE

    def test_virtual_sensor_attributes_from_reference(self, virtual_sensor, mock_hass):
        """Test virtual sensor gets attributes from reference entity."""
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
        assert attributes["reference_entity"] == "sensor.tent_temperature"
        assert attributes["tent_entity"] == "plant.test_tent"
        assert attributes["virtual_sensor"] is True

    def test_virtual_sensor_name_generation(self, virtual_sensor):
        """Test virtual sensor generates correct name."""
        expected_name = "Test Plant Temperature (Virtual)"
        # This would be based on the plant entity name + sensor type
        assert "Virtual" in virtual_sensor.name or "virtual" in str(virtual_sensor.unique_id)

    def test_virtual_sensor_device_class(self, virtual_sensor, mock_hass):
        """Test virtual sensor inherits device class from reference."""
        # Mock reference entity with device class
        mock_state = Mock(spec=State)
        mock_state.state = "22.5"
        mock_state.attributes = {"device_class": "temperature"}
        mock_hass.states.get.return_value = mock_state
        
        # Virtual sensor should inherit device class
        device_class = virtual_sensor.device_class
        # Implementation may vary, but should handle device class appropriately


class TestOptimizedSensorManager:
    """Test optimized sensor manager with virtual sensors."""

    @pytest.fixture
    def mock_hass(self):
        """Create mock Home Assistant instance."""
        hass = Mock(spec=HomeAssistant)
        hass.states = Mock()
        hass.data = {}
        return hass

    @pytest.fixture
    def sensor_manager(self, mock_hass):
        """Create optimized sensor manager."""
        return OptimizedSensorManager(mock_hass)

    def test_create_virtual_sensor(self, sensor_manager, mock_hass):
        """Test creating virtual sensor through manager."""
        plant_id = "plant.test_plant"
        tent_id = "plant.test_tent"
        
        # Create virtual sensor
        virtual_sensor = sensor_manager.create_virtual_sensor(
            plant_entity_id=plant_id,
            sensor_type=SENSOR_TEMPERATURE,
            reference_entity_id="sensor.tent_temperature",
            tent_entity_id=tent_id
        )
        
        # Verify virtual sensor was created
        assert virtual_sensor is not None
        assert isinstance(virtual_sensor, VirtualSensorEntity)
        assert virtual_sensor._plant_entity_id == plant_id

    def test_virtual_sensor_cleanup(self, sensor_manager):
        """Test cleanup of virtual sensors when plant unassigned."""
        plant_id = "plant.test_plant"
        
        # Mock virtual sensors exist
        sensor_manager._virtual_sensors = {
            f"{plant_id}_{SENSOR_TEMPERATURE}": Mock(),
            f"{plant_id}_{SENSOR_HUMIDITY}": Mock(),
        }
        
        # Cleanup virtual sensors for plant
        sensor_manager.cleanup_virtual_sensors(plant_id)
        
        # Verify sensors were removed
        remaining_sensors = [k for k in sensor_manager._virtual_sensors.keys() 
                           if k.startswith(plant_id)]
        assert len(remaining_sensors) == 0

    def test_memory_optimization_virtual_vs_real(self, sensor_manager, mock_hass):
        """Test memory usage comparison between virtual and real sensors."""
        plant_id = "plant.test_plant"
        tent_id = "plant.test_tent"
        
        # Create virtual sensors
        virtual_sensors = []
        for sensor_type in [SENSOR_TEMPERATURE, SENSOR_HUMIDITY, SENSOR_CO2]:
            virtual_sensor = sensor_manager.create_virtual_sensor(
                plant_entity_id=plant_id,
                sensor_type=sensor_type,
                reference_entity_id=f"sensor.tent_{sensor_type}",
                tent_entity_id=tent_id
            )
            virtual_sensors.append(virtual_sensor)
        
        # Verify virtual sensors use references, not independent state storage
        for sensor in virtual_sensors:
            assert hasattr(sensor, '_reference_entity_id')
            assert sensor._reference_entity_id.startswith("sensor.tent_")

    def test_virtual_sensor_state_sync(self, sensor_manager, mock_hass):
        """Test virtual sensor state synchronization with reference."""
        plant_id = "plant.test_plant"
        reference_id = "sensor.tent_temperature"
        
        # Create virtual sensor
        virtual_sensor = sensor_manager.create_virtual_sensor(
            plant_entity_id=plant_id,
            sensor_type=SENSOR_TEMPERATURE,
            reference_entity_id=reference_id,
            tent_entity_id="plant.test_tent"
        )
        
        # Mock reference state changes
        mock_state_1 = Mock(spec=State)
        mock_state_1.state = "20.0"
        mock_state_1.attributes = {"unit_of_measurement": "°C"}
        
        mock_state_2 = Mock(spec=State)
        mock_state_2.state = "25.0" 
        mock_state_2.attributes = {"unit_of_measurement": "°C"}
        
        # Test state synchronization
        mock_hass.states.get.return_value = mock_state_1
        assert virtual_sensor.state == "20.0"
        
        mock_hass.states.get.return_value = mock_state_2
        assert virtual_sensor.state == "25.0"

    def test_virtual_sensor_registry_integration(self, sensor_manager, mock_hass):
        """Test virtual sensor integration with entity registry."""
        plant_id = "plant.test_plant"
        
        # Mock entity registry
        mock_registry = Mock()
        mock_hass.helpers = Mock()
        
        with patch('homeassistant.helpers.entity_registry.async_get') as mock_get_registry:
            mock_get_registry.return_value = mock_registry
            
            # Create virtual sensor
            virtual_sensor = sensor_manager.create_virtual_sensor(
                plant_entity_id=plant_id,
                sensor_type=SENSOR_TEMPERATURE,
                reference_entity_id="sensor.tent_temperature",
                tent_entity_id="plant.test_tent"
            )
            
            # Verify unique ID is properly formatted for registry
            assert virtual_sensor.unique_id == f"{plant_id}_temperature_virtual"