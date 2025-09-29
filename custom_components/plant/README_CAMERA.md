# Camera Integration for Brokkoli Plant Manager

## Overview

The Brokkoli Plant Manager now includes camera integration that allows you to take snapshots of your plants either on-demand or automatically. This feature also supports tent-based camera inheritance, where cameras assigned to tents are automatically inherited by plants in those tents.

## Features

1. **On-demand snapshots** - Take snapshots of your plants whenever you want
2. **Automatic snapshots** - Configure plants to take snapshots at regular intervals
3. **Tent camera inheritance** - Assign cameras to tents, which are then inherited by plants
4. **Local storage** - Snapshots are stored locally on your Home Assistant instance
5. **Plant image integration** - The latest snapshot becomes the plant's main image

## Services

### Take Plant Snapshot

Takes a snapshot of a plant using the configured camera.

**Service:** `plant.take_snapshot`

**Parameters:**
- `entity_id` (Required): The plant entity to take a snapshot of

### Configure Auto Snapshot

Configure automatic snapshots for a plant at regular intervals.

**Service:** `plant.auto_snapshot`

**Parameters:**
- `entity_id` (Required): The plant entity to configure auto snapshots for
- `interval_minutes` (Optional, default: 60): Interval between snapshots in minutes
- `enabled` (Optional, default: true): Enable or disable auto snapshots

## Tent Camera Assignment

To assign a camera to a tent, include the `camera_entity_id` parameter when creating or updating a tent:

```yaml
service: plant.create_tent
data:
  name: "Grow Tent 1"
  camera_entity_id: "camera.grow_tent_camera"
```

Plants assigned to this tent will automatically inherit the camera.

## Technical Details

### Camera Entity

When a plant is configured with a camera, a `PlantCamera` entity is created that extends Home Assistant's base `Camera` class. This entity handles:

1. Image capture and storage
2. Integration with the plant entity
3. Camera state management (on/off)

### Image Storage

Images are stored in `/config/www/images/plants/` by default. Each snapshot is saved with a timestamped filename.

### Implementation Files

- `camera.py` - Contains the `PlantCamera` class
- `services.py` - Implements the camera services
- `tent.py` - Handles tent camera assignment and inheritance
- `__init__.py` - Includes the `assign_camera` method for plants
- `services.yaml` - Defines the service interfaces
- `const.py` - Contains camera-related constants

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