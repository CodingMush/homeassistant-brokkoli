# Installation Parameters

This document describes the various configuration parameters available for the Brokkoli Plant Manager integration.

## Configuration Options

### General Settings

- **Temperature Unit**: Choose between Celsius (°C) and Fahrenheit (°F) for temperature readings
- **Illuminance Unit**: Choose between Lux and PPFD (μmol/s⋅m²) for light measurements
- **Aggregation Method**: Select how sensor data is aggregated (mean, median, min, max)
- **Normalization Window**: Set the number of days for sensor data normalization (default: 7 days)
- **Normalization Percentile**: Set the percentile for normalization calculations (default: 95)

### Plant Limits

Default limits for various plant parameters:
- **Temperature**: 10-40°C (50-104°F)
- **Soil Moisture**: 20-60%
- **Soil Conductivity**: 500-3000 μS/cm
- **Illuminance**: 0-100000 lux
- **Air Humidity**: 20-60%
- **Air CO2**: 60-60 ppm (Note: This appears to be a configuration error)
- **DLI**: 2-30 mol/d⋅m²

### Consumption Settings

- **Water Consumption**: 0.1-2.0 L per day
- **Fertilizer Consumption**: 0.1-2.0 mL per day
- **Power Consumption**: 0.1-5.0 kWh per day
- **Default kWh Price**: 0.3684 € per kWh

### Image Storage

- **Image Storage**: Plant images are stored in the `www/images/plants/` directory by default
- **Download Path**: Customizable path for image storage (relative to Home Assistant configuration directory)

### Advanced Settings

- **Check Days**: Number of days to consider for problem detection (default: 3)
- **pH Range**: 5.5-7.5 (adjustable)
- **Default Pot Size**: 0.4 liters
- **Default Water Capacity**: 50% (adjustable)

## Service Configuration

The integration provides several services for plant management:
- `plant.create_plant`: Create a new plant entity
- `plant.remove_plant`: Remove a plant entity
- `plant.replace_sensor`: Replace a sensor associated with a plant
- `plant.move_to_area`: Move a plant to a different area
- `plant.export_plants`: Export plant data to a file
- `plant.import_plants`: Import plant data from a file
- `plant.clone_plant`: Create a clone of an existing plant
- `plant.add_image`: Add an image to a plant's gallery
- `plant.add_watering`: Add a manual watering entry
- `plant.add_conductivity`: Add a manual conductivity reading
- `plant.add_ph`: Add a manual pH reading
- `plant.change_position`: Change a plant's position in a tent
- `plant.take_snapshot`: Take a snapshot of a plant (camera integration)
- `plant.auto_snapshot`: Configure automatic snapshots for a plant (camera integration)

## Tent Configuration

- **Tent Creation**: Create and manage growing tents
- **Camera Assignment**: Assign cameras to tents (inherited by plants)
- **Plant Organization**: Group plants by tent for easier management

## Cycle Management

- **Cycle Creation**: Create growing cycles for tracking plant development
- **Growth Phase Tracking**: Track plants through different growth phases
- **Problem Detection**: Automatic detection of plant health issues

## Data Sources

The integration supports multiple data sources:
- **OpenPlantbook**: Fetch plant information from the OpenPlantbook database
- **Manual Entry**: Manually configure plant parameters
- **Default Values**: Use system defaults for common plants

## Integration with Other Systems

- **Sensor Integration**: Works with various Home Assistant sensor platforms
- **Notification System**: Can trigger notifications based on plant conditions
- **Automation Support**: Fully compatible with Home Assistant automation system
- **Camera Integration**: Supports camera entities for visual plant monitoring