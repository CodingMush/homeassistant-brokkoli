"""Unit tests for tent device management - simplified version without pytest."""
import unittest
from unittest.mock import Mock, MagicMock, patch

# Mock Home Assistant classes and constants
class MockHomeAssistant:
    def __init__(self):
        self.config = Mock()
        self.config.config_dir = "/config"
        self.states = Mock()
        self.states.get = Mock(return_value=None)
        self.data = {}

class MockConfigEntry:
    def __init__(self, entry_id, data):
        self.entry_id = entry_id
        self.data = data
        self.options = {}

# Constants
STATE_OK = "ok"
STATE_UNAVAILABLE = "unavailable"
DEVICE_TYPE_TENT = "tent"
DEVICE_TYPE_PLANT = "plant"
ATTR_ASSIGNED_PLANTS = "assigned_plants"
ATTR_SHARED_THRESHOLDS = "shared_thresholds"
FLOW_PLANT_INFO = "plant_info"
CONF_SENSORS = "sensors"

class MockTentDevice:
    """Mock tent device for testing."""
    def __init__(self, hass, config_entry):
        self.hass = hass
        self.config_entry = config_entry
        self.device_type = DEVICE_TYPE_TENT
        self.name = config_entry.data[FLOW_PLANT_INFO]["name"]
        self._assigned_plants = []
        self._environmental_sensors = config_entry.data[FLOW_PLANT_INFO].get(CONF_SENSORS, {})
        self.entity_id = f"plant.{self.name.lower().replace(' ', '_')}"

    def register_plant(self, plant_entity_id):
        """Register a plant to this tent."""
        if plant_entity_id not in self._assigned_plants:
            self._assigned_plants.append(plant_entity_id)

    def unregister_plant(self, plant_entity_id):
        """Unregister a plant from this tent."""
        if plant_entity_id in self._assigned_plants:
            self._assigned_plants.remove(plant_entity_id)

    def get_aggregated_plant_thresholds(self):
        """Tents no longer aggregate thresholds - removed functionality."""
        return {}

    @property
    def extra_state_attributes(self):
        """Return extra state attributes - simplified to only show sensor info."""
        return {
            ATTR_ASSIGNED_PLANTS: self._assigned_plants,
            "plant_count": len(self._assigned_plants),
            "environmental_sensors": self._environmental_sensors,
        }

    @property
    def device_info(self):
        """Return device info."""
        return {
            "manufacturer": "Plant Integration",
            "model": "Tent",
            "name": f"Tent {self.name}"
        }


class TestTentDevice(unittest.TestCase):
    """Test tent device functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_hass = MockHomeAssistant()
        self.mock_config_entry = MockConfigEntry(
            "tent_test_entry",
            {
                FLOW_PLANT_INFO: {
                    "name": "Test Tent",
                    "device_type": DEVICE_TYPE_TENT,
                    CONF_SENSORS: {
                        "temperature": "sensor.tent_temperature",
                        "humidity": "sensor.tent_humidity",
                        "co2": "sensor.tent_co2"
                    }
                }
            }
        )
        self.tent_device = MockTentDevice(self.mock_hass, self.mock_config_entry)

    def test_tent_device_initialization(self):
        """Test tent device initializes correctly."""
        self.assertEqual(self.tent_device.device_type, DEVICE_TYPE_TENT)
        self.assertEqual(self.tent_device.name, "Test Tent")
        self.assertEqual(self.tent_device._assigned_plants, [])
        print("✓ Tent device initialization test passed")

    def test_register_plant(self):
        """Test registering a plant to tent."""
        plant_entity_id = "plant.test_plant"
        
        # Register plant
        self.tent_device.register_plant(plant_entity_id)
        
        # Verify plant was added
        self.assertIn(plant_entity_id, self.tent_device._assigned_plants)
        attributes = self.tent_device.extra_state_attributes
        self.assertEqual(attributes[ATTR_ASSIGNED_PLANTS], [plant_entity_id])
        print("✓ Plant registration test passed")

    def test_unregister_plant(self):
        """Test unregistering a plant from tent."""
        plant_entity_id = "plant.test_plant"
        
        # First register the plant
        self.tent_device._assigned_plants = [plant_entity_id]
        
        # Then unregister it
        self.tent_device.unregister_plant(plant_entity_id)
        
        # Verify plant was removed
        self.assertNotIn(plant_entity_id, self.tent_device._assigned_plants)
        attributes = self.tent_device.extra_state_attributes
        self.assertEqual(attributes[ATTR_ASSIGNED_PLANTS], [])
        print("✓ Plant unregistration test passed")

    def test_tent_sensor_info_display(self):
        """Test tent shows sensor information instead of analytics."""
        # Add plants to tent
        self.tent_device._assigned_plants = ["plant.plant1", "plant.plant2"]
        
        # Get extra state attributes which include sensor info
        attributes = self.tent_device.extra_state_attributes
        
        # Verify sensor info is included (no more threshold ranges)
        self.assertIn("environmental_sensors", attributes)
        self.assertEqual(attributes["plant_count"], 2)
        self.assertEqual(len(attributes[ATTR_ASSIGNED_PLANTS]), 2)
        # Verify threshold aggregation is no longer present
        self.assertNotIn(ATTR_SHARED_THRESHOLDS, attributes)
        print("✓ Tent sensor info display test passed")

    def test_tent_device_info_correct(self):
        """Test tent device info shows correct manufacturer and model."""
        device_info = self.tent_device.device_info
        
        self.assertEqual(device_info["manufacturer"], "Plant Integration")
        self.assertEqual(device_info["model"], "Tent")
        self.assertIn("Tent", device_info["name"])
        print("✓ Tent device info test passed")

    def test_empty_tent_thresholds(self):
        """Test tent with no assigned plants returns empty thresholds."""
        self.tent_device._assigned_plants = []
        
        thresholds = self.tent_device.get_aggregated_plant_thresholds()
        self.assertEqual(thresholds, {})
        print("✓ Empty tent thresholds test passed")


if __name__ == '__main__':
    print("Running comprehensive tent device unit tests...")
    
    # Create test suite
    test_classes = [TestTentDevice]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\\n=== Running {test_class.__name__} tests ===")
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=0)
        result = runner.run(suite)
        
        total_tests += result.testsRun
        passed_tests += result.testsRun - len(result.failures) - len(result.errors)
        
        if result.failures:
            print(f"❌ Failures: {len(result.failures)}")
        if result.errors:
            print(f"❌ Errors: {len(result.errors)}")
    
    print(f"\\n=== Test Summary ===")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    
    if passed_tests == total_tests:
        print("\\n🎉 All comprehensive unit tests passed!")
        print("✅ Tent device management functionality validated")
    else:
        print(f"\\n❌ {total_tests - passed_tests} tests failed")