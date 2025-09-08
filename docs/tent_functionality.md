# Tent Functionality in Brokkoli Plant Integration

## Overview

The Tent functionality in the Brokkoli Plant Integration allows users to group environmental sensors together and assign them to multiple plants. This simplifies sensor management for grow operations where multiple plants share the same environmental conditions.

## Key Concepts

### Tent Entity
A Tent is a special device type in the Brokkoli integration that serves as a container for environmental sensors. Tents can be assigned to Plants, allowing the plants to inherit sensor data from the tent.

### Sensor Inheritance
When a Plant is assigned to a Tent, it automatically inherits the sensor mappings from the Tent. This means that if you update the sensors in a Tent, all Plants assigned to that Tent will automatically use the updated sensors.

## Tent Services

### create_tent
Creates a new Tent entity with optional initial sensors.

**Parameters:**
- `name` (string, required): The name of the tent to create
- `sensors` (list of entity IDs, optional): Initial list of sensor entities to associate with the tent

**Example:**
```yaml
service: plant.create_tent
data:
  name: "Grow Tent 1"
  sensors:
    - sensor.temperature
    - sensor.humidity
    - sensor.co2
```

### change_tent
Changes the tent assignment for a plant and updates its sensors.

**Parameters:**
- `entity_id` (entity ID, required): The plant entity to change tent assignment for
- `tent_id` (string, required): The ID of the tent to assign to the plant

**Example:**
```yaml
service: plant.change_tent
data:
  entity_id: plant.my_plant
  tent_id: tent_12345
```

### update_tent_sensors
Updates the sensors associated with a tent. All plants assigned to this tent will automatically inherit the new sensor mappings.

**Parameters:**
- `tent_id` (string, required): The ID of the tent to update sensors for
- `sensors` (list of entity IDs, required): List of sensor entities to associate with the tent

**Example:**
```yaml
service: plant.update_tent_sensors
data:
  tent_id: tent_12345
  sensors:
    - sensor.new_temperature
    - sensor.new_humidity
    - sensor.new_co2
```

## Sensor Mapping Logic

When sensors are assigned to a Tent or when a Plant inherits sensors from a Tent, the system uses the following logic to map sensors to plant sensor types:

1. **Temperature sensors**: device_class="temperature" or units "°C", "°F", "K"
2. **Humidity sensors**: device_class="humidity" or unit "%"
3. **Illuminance sensors**: device_class="illuminance" or units "lx", "lux"
4. **Conductivity sensors**: device_class="conductivity" or unit "µS/cm"
5. **CO2 sensors**: device_class="carbon_dioxide" or unit "ppm"
6. **Power sensors**: device_class="power" or units "W", "kW"
7. **pH sensors**: device_class="ph" or unit "pH"

## Implementation Details

### Tent Class
The [Tent](file:///d:/Python/2/homeassistant-brokkoli/custom_components/plant/tent.py#L72-L259) class extends the Home Assistant Entity class and provides the following functionality:

- Storage of sensor entity IDs
- Journal functionality for documenting events
- Maintenance entry tracking
- Device registry integration

### Plant-Tent Integration
The PlantDevice class has been extended with methods to support tent integration:

- `assign_tent(tent)`: Assigns a tent to the plant
- `replace_sensors(tent_sensors)`: Replaces the plant's sensors with those from a tent
- `get_assigned_tent()`: Returns the currently assigned tent
- `get_tent_id()`: Returns the ID of the assigned tent

## Benefits

1. **Simplified Management**: Manage environmental sensors in one place and apply to multiple plants
2. **Automatic Updates**: When tent sensors are updated, all assigned plants automatically inherit the changes
3. **Consistent Configuration**: Ensures all plants in the same environment use the same sensor mappings
4. **Reduced Configuration Errors**: Clear naming and validation reduce misconfigurations

## Best Practices

1. **Naming Convention**: Use descriptive names for tents that indicate their purpose or location
2. **Sensor Grouping**: Group sensors logically based on the environment they monitor
3. **Regular Updates**: Keep tent sensors updated as your grow operation evolves
4. **Documentation**: Use the journal functionality to document important events and changes

## Troubleshooting

### Tent Not Appearing in UI
- Ensure the tent was created successfully
- Check that the tent entity is properly registered in Home Assistant

### Sensors Not Updating
- Verify that the tent sensors are correctly mapped to plant sensor types
- Check that the plant is properly assigned to the tent
- Ensure that sensor entities are available and reporting data

### Plant Not Inheriting Sensors
- Confirm that the plant is assigned to the tent
- Check that the tent has sensors configured
- Verify that sensor mapping logic can properly identify sensor types