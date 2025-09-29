# Camera Integration for Brokkoli Plant Manager

The camera integration allows you to take snapshots of your plants either on demand or automatically. These snapshots can be used to visually track the growth and health of your plants over time.

## Features

- Take snapshots of plants on demand via service calls
- Automatic snapshots based on configurable schedules
- Image storage with timestamped filenames
- Integration with plant entities for visual tracking
- Camera assignment inheritance from tents to plants

## Configuration

### Image Storage Path

Images are stored in `www/images/plants/` by default. Each snapshot is saved with a timestamped filename.

You can customize this path in the plant configuration:
1. Go to Configuration → Devices & Services
2. Find your plant configuration entry
3. Click "Configure" 
4. Modify the "Download Path" setting

### Camera Assignment

Cameras can be assigned to tents, which will then be inherited by all plants in that tent:
1. Create or edit a tent
2. Assign a camera entity to the tent
3. All plants in the tent will automatically use that camera

## Services

### Take Snapshot

Takes an immediate snapshot of a plant.

**Service**: `plant.take_snapshot`

**Parameters**:
- `entity_id`: The plant entity to take a snapshot of

### Auto Snapshot

Configures automatic snapshots for a plant.

**Service**: `plant.auto_snapshot`

**Parameters**:
- `entity_id`: The plant entity to configure
- `interval`: Snapshot interval in minutes (1-1440)
- `enabled`: Whether auto snapshots are enabled (true/false)

## Usage

### Manual Snapshots

To take a manual snapshot:
1. Go to Developer Tools → Services
2. Select `plant.take_snapshot`
3. Choose the plant entity
4. Click "Call Service"

### Automatic Snapshots

To configure automatic snapshots:
1. Go to Developer Tools → Services
2. Select `plant.auto_snapshot`
3. Choose the plant entity
4. Set the interval (e.g., 60 for hourly snapshots)
5. Set enabled to `true`
6. Click "Call Service"

### Viewing Snapshots

Snapshots can be viewed in several ways:
1. Plant entity card - Shows the most recent snapshot
2. Media browser - Browse all snapshots by plant
3. Direct file access - Images are stored in your configured image directory

## Troubleshooting

### Permission Issues

If you encounter permission errors:
1. Ensure the configured image storage path is writable
2. Check that Home Assistant has the necessary permissions
3. Consider using a path within the `www` directory

### No Camera Found

If no camera is found:
1. Verify that a camera entity is assigned to the tent or plant
2. Check that the camera entity is available and functioning
3. Restart Home Assistant if necessary

### Image Not Updating

If plant images are not updating:
1. Verify that snapshots are being taken successfully
2. Check the Home Assistant logs for errors
3. Ensure the image storage path is accessible1. Verify that snapshots are being taken successfully
2. Check the Home Assistant logs for errors
3. Ensure the image storage path is accessible