# Virtual Sensors in Home Assistant Plant Integration

## Overview

Virtual sensors are a specialized type of sensor entity that references other entities instead of maintaining their own state storage. They are primarily used in two scenarios:

1. **Tent-assigned plants**: Plants that inherit sensor data from a tent device
2. **Standalone plants with virtual sensors enabled**: Plants that use virtual sensors but maintain their own sensor references

## Benefits

### Memory Efficiency
Virtual sensors reduce memory usage by:
- Sharing state references instead of duplicating data
- Reducing the number of independent state storage objects

### Consistent Behavior
Virtual sensors provide a unified interface for:
- Tent-assigned plants
- Standalone plants (when properly implemented)
- Simplified sensor management

## Implementation Details

### VirtualSensor Class
The [VirtualSensor](file://d:\Python\git\homeassistant-brokkoli\custom_components\plant\sensor.py#L2284-L2431) class extends [PlantCurrentStatus](file://d:\Python\git\homeassistant-brokkoli\custom_components\plant\sensor.py#L375-L500) and implements reference-based sensor behavior.

Key features:
- References other entities instead of storing independent state
- Automatically updates when referenced entities change
- Returns `STATE_UNKNOWN` when references are missing (instead of `STATE_UNAVAILABLE`)

### VirtualSensorManager Class
The [VirtualSensorManager](file://d:\Python\git\homeassistant-brokkoli\custom_components\plant\sensor.py#L2433-L2540) handles creation and management of virtual sensors.

Key features:
- Creates virtual sensors for plants that use them
- Updates sensor references when tent assignments change
- Manages sensor lifecycle

## Usage Scenarios

### Tent-Assigned Plants
When a plant is assigned to a tent:
1. Virtual sensors are automatically created for the plant
2. These sensors reference the tent's environmental sensors
3. Changes to tent sensors automatically propagate to plant sensors

### Standalone Plants with Virtual Sensors
Plants can use virtual sensors without tent assignment:
1. Enabled by setting `uses_virtual_sensors = True`
2. Can reference external sensors directly
3. Provides consistent behavior with tent-assigned plants

### Regular Plants (Non-Virtual)
Traditional plant implementation:
1. Uses regular sensor entities with independent state storage
2. Directly references external sensors
3. No virtual sensor overhead

## Configuration

### Enabling Virtual Sensors for Standalone Plants
To enable virtual sensors for a standalone plant:
1. Set `uses_virtual_sensors = True` in the plant configuration
2. Configure sensor references in the plant's config data

### Tent Assignment
When assigning a plant to a tent:
1. The system automatically enables virtual sensors
2. Sensor references are inherited from the tent
3. Area assignments can also be inherited from the tent

## Troubleshooting

### Missing Sensor References
If virtual sensors show `STATE_UNKNOWN`:
1. Check that sensor references are properly configured
2. Verify that referenced entities exist and are available
3. For tent-assigned plants, ensure the tent has the required sensors configured

### Performance Issues
If experiencing performance issues with virtual sensors:
1. Check that sensor reference updates are not causing excessive state changes
2. Verify that virtual sensor managers are properly cleaning up unused sensors
3. Consider using regular sensors for plants that don't require reference-based behavior

## Best Practices

1. **Use virtual sensors for tent-assigned plants**: This is the primary use case and provides the most benefit
2. **Enable virtual sensors for standalone plants only when needed**: They add complexity that may not be necessary
3. **Always handle `STATE_UNKNOWN` in plant logic**: Virtual sensors return `STATE_UNKNOWN` when references are missing
4. **Test reference resolution thoroughly**: Ensure all sensor types properly resolve references in both tent-assigned and standalone scenarios