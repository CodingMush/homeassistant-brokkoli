# Camera Integration for Brokkoli Plant Manager

The Brokkoli Plant Manager includes a camera integration that allows you to take snapshots of your plants either on-demand or automatically at regular intervals. This feature is particularly useful for monitoring plant growth, documenting plant health, or creating time-lapse videos of your plants.

## Overview

The camera integration provides the following features:

1. **On-demand snapshots** - Take snapshots of your plants whenever you want
2. **Automatic snapshots** - Configure your plants to take snapshots at regular intervals
3. **Tent camera inheritance** - Assign cameras to tents, which are then inherited by plants
4. **Local storage** - Snapshots are stored locally on your Home Assistant instance
5. **Plant image integration** - The latest snapshot becomes the plant's main image

## Setup and Configuration

### Adding Camera Support to Plants

To use the camera integration, you need to assign a camera entity to your plants. This can be done in two ways:

1. **Direct assignment** - Assign a camera directly to a plant
2. **Tent inheritance** - Assign a camera to a tent, which is then inherited by all plants in that tent

### Direct Camera Assignment

You can assign a camera to a plant using the `assign_camera` method or through tent configuration.

### Tent Camera Assignment

To assign a camera to a tent:

1. Create or edit a tent using the `create_tent` service
2. Include the `camera_entity_id` parameter with the entity ID of your camera
3. Plants assigned to this tent will automatically inherit the camera

Example service call:
```yaml
service: plant.create_tent
data:
  name: "Grow Tent 1"
  camera_entity_id: "camera.grow_tent_camera"
```

## Services

### Take Plant Snapshot

Takes a snapshot of a plant using the configured camera.

**Service:** `plant.take_snapshot`

**Parameters:**
- `entity_id` (Required): The plant entity to take a snapshot of
- `auto_name` (Optional, default: true): Automatically name the snapshot file

**Example:**
```yaml
service: plant.take_snapshot
data:
  entity_id: plant.my_plant
```

### Configure Auto Snapshot

Configure automatic snapshots for a plant at regular intervals.

**Service:** `plant.auto_snapshot`

**Parameters:**
- `entity_id` (Required): The plant entity to configure auto snapshots for
- `interval_minutes` (Optional, default: 60): Interval between snapshots in minutes
- `enabled` (Optional, default: true): Enable or disable auto snapshots

**Example:**
```yaml
service: plant.auto_snapshot
data:
  entity_id: plant.my_plant
  interval_minutes: 30
  enabled: true
```

## How It Works

### Camera Entity Creation

When a plant is configured with a camera entity ID, a `PlantCamera` entity is automatically created. This entity extends Home Assistant's base `Camera` class and provides the following functionality:

1. **Snapshot Capture** - Generates or captures images (in the current implementation, a placeholder image is generated)
2. **Image Storage** - Saves images to a configurable local directory
3. **Plant Integration** - Updates the plant's main image with the latest snapshot

### Image Storage

Images are stored in the directory configured in your plant configuration. By default, this is `/config/www/images/plants/`. Each snapshot is saved with a timestamped filename in the format:

```
[plant_entity_id]_snapshot_[YYYYMMDD_HHMMSS].jpg
```

### Automatic Snapshot Scheduling

When auto snapshots are enabled for a plant, the system will automatically take snapshots at the configured interval. The scheduling is handled through Home Assistant's service infrastructure.

## Technical Implementation

### PlantCamera Class

The `PlantCamera` class in `camera.py` is responsible for:

1. **Initialization** - Setting up the camera with proper naming and unique IDs
2. **Image Capture** - Implementing the `async_take_snapshot` method
3. **Storage Management** - Handling image file creation and storage
4. **Plant Integration** - Updating the plant entity with the latest image

### Camera Services

The camera services in `services.py` provide:

1. **Service Registration** - Registering the `take_snapshot` and `auto_snapshot` services
2. **Service Implementation** - Handling service calls and executing the appropriate actions
3. **Configuration Management** - Storing auto-snapshot settings in plant configuration

### Tent Integration

The tent implementation in `tent.py` supports:

1. **Camera Assignment** - Storing camera entity IDs in tent configuration
2. **Camera Inheritance** - Automatically assigning tent cameras to plants when they are added to a tent

## Limitations and Future Improvements

### Current Limitations

1. **Placeholder Images** - The current implementation generates placeholder images rather than capturing from actual camera devices
2. **Single Camera Support** - Each plant can only have one camera assigned
3. **JPEG Only** - Images are saved in JPEG format only

### Future Improvements

1. **Real Camera Integration** - Integrate with actual camera devices for real image capture
2. **Multiple Camera Support** - Allow plants to have multiple cameras for different angles
3. **Video Recording** - Add support for recording short video clips
4. **Cloud Storage** - Add options for storing images in cloud storage services
5. **Image Analysis** - Integrate with image analysis services for automatic plant health assessment

## Troubleshooting

### Common Issues

1. **Camera Not Found** - Ensure the camera entity ID is correct and the camera is available in Home Assistant
2. **Storage Path Issues** - Verify that the configured storage path exists and is writable
3. **Permission Errors** - Ensure Home Assistant has permission to write to the storage directory

### Logs

Check the Home Assistant logs for any error messages related to the camera integration. Look for entries with the `plant` component and specifically the `PlantCamera` class.

## Example Automations

### Daily Plant Snapshot

```yaml
alias: Daily Plant Snapshot
trigger:
  - platform: time
    at: "09:00:00"
action:
  - service: plant.take_snapshot
    data:
      entity_id: plant.my_plant
```

### Growth Monitoring

```yaml
alias: Growth Monitoring
trigger:
  - platform: time_pattern
    hours: "/6"  # Every 6 hours
action:
  - service: plant.take_snapshot
    data:
      entity_id: plant.my_plant
```

## API Reference

### PlantCamera Methods

- `async_take_snapshot()` - Takes a snapshot and saves it to storage
- `turn_on()` - Turns the camera on
- `turn_off()` - Turns the camera off
- `async_camera_image()` - Returns the latest captured image

### PlantDevice Methods

- `assign_camera(camera_entity_id)` - Assigns a camera to the plant

### Service Definitions

See `services.yaml` for complete service definitions and parameter details.

## Conclusion

The camera integration in Brokkoli Plant Manager provides a flexible way to capture and store images of your plants. Whether you need occasional snapshots or regular monitoring, the system can be configured to meet your needs. With tent-based camera inheritance, managing multiple plants with shared cameras becomes simple and efficient.