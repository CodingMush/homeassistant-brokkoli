"""Entity classes for plant thresholds."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import (
    ATTR_NAME,
    ATTR_UNIT_OF_MEASUREMENT,
    PERCENTAGE,
    STATE_UNKNOWN,
    STATE_UNAVAILABLE,
    UnitOfTemperature,
    LIGHT_LUX,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util.unit_conversion import TemperatureConverter
from homeassistant.helpers.entity import async_generate_entity_id

from .const import (
    ATTR_CONDUCTIVITY,
    ATTR_CURRENT,
    ATTR_DLI,
    ATTR_HUMIDITY,
    ATTR_CO2,
    ATTR_ILLUMINANCE,
    ATTR_LIMITS,
    ATTR_MAX,
    ATTR_MIN,
    ATTR_MOISTURE,
    ATTR_PLANT,
    ATTR_SENSOR,
    ATTR_SENSORS,
    ATTR_TEMPERATURE,
    CONF_MAX_CONDUCTIVITY,
    CONF_MAX_DLI,
    CONF_MAX_HUMIDITY,
    CONF_MAX_CO2,
    CONF_MAX_ILLUMINANCE,
    CONF_MAX_MOISTURE,
    CONF_MAX_TEMPERATURE,
    CONF_MIN_CONDUCTIVITY,
    CONF_MIN_DLI,
    CONF_MIN_HUMIDITY,
    CONF_MIN_CO2,
    CONF_MIN_ILLUMINANCE,
    CONF_MIN_MOISTURE,
    CONF_MIN_TEMPERATURE,
    CONF_MIN_WATER_CONSUMPTION,
    CONF_MAX_WATER_CONSUMPTION,
    CONF_MIN_FERTILIZER_CONSUMPTION,
    CONF_MAX_FERTILIZER_CONSUMPTION,
    CONF_MIN_POWER_CONSUMPTION,
    CONF_MAX_POWER_CONSUMPTION,
    CONF_MIN_PH,
    CONF_MAX_PH,
    DEFAULT_MAX_CONDUCTIVITY,
    DEFAULT_MAX_DLI,
    DEFAULT_MAX_HUMIDITY,
    DEFAULT_MAX_CO2,
    DEFAULT_MAX_ILLUMINANCE,
    DEFAULT_MAX_MOISTURE,
    DEFAULT_MAX_TEMPERATURE,
    DEFAULT_MIN_CONDUCTIVITY,
    DEFAULT_MIN_DLI,
    DEFAULT_MIN_HUMIDITY,
    DEFAULT_MIN_CO2,
    DEFAULT_MIN_ILLUMINANCE,
    DEFAULT_MIN_MOISTURE,
    DEFAULT_MIN_TEMPERATURE,
    DEFAULT_MIN_WATER_CONSUMPTION,
    DEFAULT_MAX_WATER_CONSUMPTION,
    DEFAULT_MIN_FERTILIZER_CONSUMPTION,
    DEFAULT_MAX_FERTILIZER_CONSUMPTION,
    DEFAULT_MIN_POWER_CONSUMPTION,
    DEFAULT_MAX_POWER_CONSUMPTION,
    DEFAULT_MIN_PH,
    DEFAULT_MAX_PH,
    DOMAIN,
    FLOW_PLANT_INFO,
    FLOW_PLANT_LIMITS,
    FLOW_SENSOR_CONDUCTIVITY,
    FLOW_SENSOR_HUMIDITY,
    FLOW_SENSOR_CO2,
    FLOW_SENSOR_ILLUMINANCE,
    FLOW_SENSOR_MOISTURE,
    FLOW_SENSOR_TEMPERATURE,
    ICON_CONDUCTIVITY,
    ICON_DLI,
    ICON_HUMIDITY,
    ICON_CO2,
    ICON_ILLUMINANCE,
    ICON_MOISTURE,
    ICON_TEMPERATURE,
    ICON_WATER_CONSUMPTION,
    ICON_FERTILIZER_CONSUMPTION,
    ICON_POWER_CONSUMPTION,
    ICON_PH,
    READING_CONDUCTIVITY,
    READING_DLI,
    READING_HUMIDITY,
    READING_CO2,
    READING_ILLUMINANCE,
    READING_MOISTURE,
    READING_TEMPERATURE,
    READING_WATER_CONSUMPTION,
    READING_FERTILIZER_CONSUMPTION,
    READING_POWER_CONSUMPTION,
    READING_PH,
    UNIT_CONDUCTIVITY,
    UNIT_PPFD,
)

_LOGGER = logging.getLogger(__name__)


class PlantMinMax(NumberEntity):
    """Parent class for the min/max values."""

    def __init__(
        self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity
    ) -> None:
        """Initialize the Plant component."""
        self._hass = hass
        self._config = config
        self._plant = plantdevice
        self._attr_native_value = 0
        self._attr_state = 0
        self.entity_id = async_generate_entity_id(
            f"{DOMAIN}.{{}}", self._attr_name, hass=hass
        )

    @property
    def not_unit_of_measurement(self) -> str | None:
        """Get unit of measurement from the threshold's sensor."""
        if (
            not hasattr(self, "_attr_native_unit_of_measurement")
            or self._attr_native_unit_of_measurement is None
        ):
            self._attr_native_unit_of_measurement = self._default_unit_of_measurement

        return self._attr_native_unit_of_measurement

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        _LOGGER.debug(
            "Setting value for %s to %s", self.entity_id, value
        )
        self._attr_native_value = value
        self._attr_state = value
        self.async_write_ha_state()

        # Also update the config entry with the new value
        if hasattr(self._config, 'data') and FLOW_PLANT_INFO in self._config.data:
            # Create a copy of the data to modify
            new_data = dict(self._config.data)
            plant_info = dict(new_data.get(FLOW_PLANT_INFO, {}))
            
            # Check if limits exist, if not create them
            if ATTR_LIMITS not in plant_info:
                plant_info[ATTR_LIMITS] = {}
            
            # Update the specific limit value
            plant_info[ATTR_LIMITS][self.limit_key] = value
            
            # Update the plant_info in the data
            new_data[FLOW_PLANT_INFO] = plant_info
            
            # Update the config entry
            self._hass.config_entries.async_update_entry(self._config, data=new_data)
            
            # Update the plant device with the new value
            if hasattr(self._plant, '_plant_info'):
                plant_info = dict(self._plant._plant_info)
                if ATTR_LIMITS not in plant_info:
                    plant_info[ATTR_LIMITS] = {}
                plant_info[ATTR_LIMITS][self.limit_key] = value
                self._plant._plant_info = plant_info

    def state_changed(self, entity_id, from_state, to_state) -> None:
        """Run on every change of the sensors entities."""
        _LOGGER.debug(
            "State change recorded for %s (from %s to %s)",
            entity_id,
            from_state,
            to_state,
        )
        if to_state is None:
            return
        if to_state.state in [STATE_UNKNOWN, STATE_UNAVAILABLE]:
            _LOGGER.debug("New state is unknown, bailing out")
            return

        try:
            state = float(to_state.state)
        except (TypeError, ValueError):
            _LOGGER.debug("New state is not a number, bailing out")
            return

        _LOGGER.debug(
            "Setting %s to %s",
            self._attr_name,
            state,
        )
        self._attr_native_value = state
        self._attr_state = state
        self.async_write_ha_state()


class PlantMaxMoisture(PlantMinMax):
    """Entity class for max moisture threshold"""

    def __init__(
        self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity
    ) -> None:
        """Initialize the component."""
        self._attr_name = f"{plantdevice.name} {ATTR_MAX} {READING_MOISTURE}"
        # Fix: Use ATTR_LIMITS instead of FLOW_PLANT_LIMITS
        limits = config.data.get(FLOW_PLANT_INFO, {}).get(ATTR_LIMITS, {})
        self._attr_native_value = limits.get(
            CONF_MAX_MOISTURE, DEFAULT_MAX_MOISTURE
        )
        self._attr_unique_id = f"{config.entry_id}-max-moisture"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_native_max_value = 100
        self._attr_native_min_value = 0
        self._attr_native_step = 1

        super().__init__(hass, config, plantdevice)

    @property
    def device_class(self):
        return f"{SensorDeviceClass.HUMIDITY} threshold"
        # return f"{SensorDeviceClass.MOISTURE} threshold" #FIXME

    limit_key = CONF_MAX_MOISTURE
    default_value = DEFAULT_MAX_MOISTURE


class PlantMinMoisture(PlantMinMax):
    """Entity class for min moisture threshold"""

    def __init__(
        self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity
    ) -> None:
        """Initialize the Plant component."""
        self._attr_name = f"{plantdevice.name} {ATTR_MIN} {READING_MOISTURE}"
        # Fix: Use ATTR_LIMITS instead of FLOW_PLANT_LIMITS
        limits = config.data.get(FLOW_PLANT_INFO, {}).get(ATTR_LIMITS, {})
        self._attr_native_value = limits.get(
            CONF_MIN_MOISTURE, DEFAULT_MIN_MOISTURE
        )
        self._attr_unique_id = f"{config.entry_id}-min-moisture"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_native_max_value = 100
        self._attr_native_min_value = 0
        self._attr_native_step = 1

        super().__init__(hass, config, plantdevice)

    @property
    def device_class(self):
        return f"{SensorDeviceClass.HUMIDITY} threshold"
        # return f"{SensorDeviceClass.MOISTURE} threshold" #FIXME

    limit_key = CONF_MIN_MOISTURE
    default_value = DEFAULT_MIN_MOISTURE


class PlantMaxTemperature(PlantMinMax):
    """Entity class for max temperature threshold"""

    def __init__(self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity) -> None:
        # Erst die Basisklasse initialisieren
        super().__init__(hass, config, plantdevice)
        
        # Dann können wir auf self._hass zugreifen
        self._attr_name = f"{plantdevice.name} {ATTR_MAX} {READING_TEMPERATURE}"
        # Fix: Use ATTR_LIMITS instead of FLOW_PLANT_LIMITS
        limits = config.data.get(FLOW_PLANT_INFO, {}).get(ATTR_LIMITS, {})
        self._attr_native_value = limits.get(
            CONF_MAX_TEMPERATURE, DEFAULT_MAX_TEMPERATURE
        )
        self._attr_unique_id = f"{config.entry_id}-max-temperature"
        self.entity_id = async_generate_entity_id(
            f"{DOMAIN}.{{}}", f"{plantdevice.name}_max_temperature", hass=hass
        )
        self._attr_native_unit_of_measurement = self._hass.config.units.temperature_unit
        self._attr_native_max_value = 100
        self._attr_native_min_value = 0
        self._attr_native_step = 1
        self._attr_icon = ICON_TEMPERATURE

    @property
    def device_class(self):
        return f"{SensorDeviceClass.TEMPERATURE} threshold"

    @property
    def not_unit_of_measurement(self) -> str | None:
        """Get unit of measurement from the temperature meter"""
        if (
            not hasattr(self, "_attr_unit_of_measurement")
            or self._attr_native_unit_of_measurement is None
        ):
            self._attr_native_unit_of_measurement = self._default_unit_of_measurement

        if self._plant.sensor_temperature:
            if not self._plant.sensor_temperature.unit_of_measurement:
                return self._attr_native_unit_of_measurement
            if (
                self._attr_native_unit_of_measurement
                != self._plant.sensor_temperature.unit_of_measurement
            ):
                self._attr_native_unit_of_measurement = (
                    self._plant.sensor_temperature.unit_of_measurement
                )

        return self._attr_native_unit_of_measurement

    def state_attributes_changed(self, old_attributes, new_attributes):
        """Calculate C or F"""
        if new_attributes.get(ATTR_UNIT_OF_MEASUREMENT) is None:
            return
        if old_attributes.get(ATTR_UNIT_OF_MEASUREMENT) is None:
            return
        if new_attributes.get(ATTR_UNIT_OF_MEASUREMENT) == old_attributes.get(
            ATTR_UNIT_OF_MEASUREMENT
        ):
            return
        new_state = self._attr_state
        if (
            old_attributes.get(ATTR_UNIT_OF_MEASUREMENT) == "°F"
            and new_attributes.get(ATTR_UNIT_OF_MEASUREMENT) == "°C"
        ):
            new_state = round(
                TemperatureConverter.convert(
                    temperature=float(self.state),
                    from_unit=UnitOfTemperature.FAHRENHEIT,
                    to_unit=UnitOfTemperature.CELSIUS,
                )
            )
            _LOGGER.debug(
                "Changing from F to C measurement is %s new is %s",
                self.state,
                new_state,
            )

        if (
            old_attributes.get(ATTR_UNIT_OF_MEASUREMENT) == "°C"
            and new_attributes.get(ATTR_UNIT_OF_MEASUREMENT) == "°F"
        ):
            new_state = round(
                TemperatureConverter.convert(
                    temperature=float(self.state),
                    from_unit=UnitOfTemperature.CELSIUS,
                    to_unit=UnitOfTemperature.FAHRENHEIT,
                )
            )
            _LOGGER.debug(
                "Changing from C to F measurement is %s new is %s",
                self.state,
                new_state,
            )

        self._hass.states.set(self.entity_id, new_state, new_attributes)

    limit_key = CONF_MAX_TEMPERATURE
    default_value = DEFAULT_MAX_TEMPERATURE


class PlantMinTemperature(PlantMinMax):
    """Entity class for min temperature threshold"""

    def __init__(self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity) -> None:
        # Erst die Basisklasse initialisieren
        super().__init__(hass, config, plantdevice)
        
        # Dann können wir auf self._hass zugreifen
        self._attr_name = f"{plantdevice.name} {ATTR_MIN} {READING_TEMPERATURE}"
        # Fix: Use ATTR_LIMITS instead of FLOW_PLANT_LIMITS
        limits = config.data.get(FLOW_PLANT_INFO, {}).get(ATTR_LIMITS, {})
        self._attr_native_value = limits.get(
            CONF_MIN_TEMPERATURE, DEFAULT_MIN_TEMPERATURE
        )
        self._attr_unique_id = f"{config.entry_id}-min-temperature"
        self.entity_id = async_generate_entity_id(
            f"{DOMAIN}.{{}}", f"{plantdevice.name}_min_temperature", hass=hass
        )
        self._attr_native_unit_of_measurement = self._hass.config.units.temperature_unit
        self._attr_native_max_value = 50
        self._attr_native_min_value = -50
        self._attr_native_step = 1
        self._attr_icon = ICON_TEMPERATURE

    @property
    def device_class(self):
        return f"{SensorDeviceClass.TEMPERATURE} threshold"

    @property
    def not_unit_of_measurement(self) -> str | None:
        if (
            not hasattr(self, "_attr_native_unit_of_measurement")
            or self._attr_native_unit_of_measurement is None
        ):
            self._attr_native_unit_of_measurement = self._default_unit_of_measurement

        if self._plant.sensor_temperature:
            if not self._plant.sensor_temperature.unit_of_measurement:
                return self._attr_native_unit_of_measurement
            if (
                self._attr_native_unit_of_measurement
                != self._plant.sensor_temperature.unit_of_measurement
            ):
                self._attr_native_unit_of_measurement = (
                    self._plant.sensor_temperature.unit_of_measurement
                )

        return self._attr_native_unit_of_measurement

    def state_attributes_changed(self, old_attributes, new_attributes):
        """Calculate C or F"""
        if new_attributes.get(ATTR_UNIT_OF_MEASUREMENT) is None:
            return
        if old_attributes.get(ATTR_UNIT_OF_MEASUREMENT) is None:
            return
        if new_attributes.get(ATTR_UNIT_OF_MEASUREMENT) == old_attributes.get(
            ATTR_UNIT_OF_MEASUREMENT
        ):
            return
        new_state = self._attr_state
        if (
            old_attributes.get(ATTR_UNIT_OF_MEASUREMENT) == "°F"
            and new_attributes.get(ATTR_UNIT_OF_MEASUREMENT) == "°C"
        ):
            new_state = round(
                TemperatureConverter.convert(
                    temperature=float(self.state),
                    from_unit=UnitOfTemperature.FAHRENHEIT,
                    to_unit=UnitOfTemperature.CELSIUS,
                )
            )
            _LOGGER.debug(
                "Changing from F to C measurement is %s new is %s",
                self.state,
                new_state,
            )

        if (
            old_attributes.get(ATTR_UNIT_OF_MEASUREMENT) == "°C"
            and new_attributes.get(ATTR_UNIT_OF_MEASUREMENT) == "°F"
        ):
            new_state = round(
                TemperatureConverter.convert(
                    temperature=float(self.state),
                    from_unit=UnitOfTemperature.CELSIUS,
                    to_unit=UnitOfTemperature.FAHRENHEIT,
                )
            )
            _LOGGER.debug(
                "Changing from C to F measurement is %s new is %s",
                self.state,
                new_state,
            )

        self._hass.states.set(self.entity_id, new_state, new_attributes)

    limit_key = CONF_MIN_TEMPERATURE
    default_value = DEFAULT_MIN_TEMPERATURE


class PlantMaxIlluminance(PlantMinMax):
    """Entity class for max illuminance threshold"""

    def __init__(
        self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity
    ) -> None:
        """Initialize the component."""
        self._attr_name = f"{plantdevice.name} {ATTR_MAX} {READING_ILLUMINANCE}"
        # Fix: Use ATTR_LIMITS instead of FLOW_PLANT_LIMITS
        limits = config.data.get(FLOW_PLANT_INFO, {}).get(ATTR_LIMITS, {})
        self._attr_native_value = limits.get(
            CONF_MAX_ILLUMINANCE, DEFAULT_MAX_ILLUMINANCE
        )
        self._attr_unique_id = f"{config.entry_id}-max-illuminance"
        self._attr_native_unit_of_measurement = LIGHT_LUX
        self._attr_native_max_value = 200000
        self._attr_native_min_value = 0
        self._attr_native_step = 500
        
        super().__init__(hass, config, plantdevice)

    @property
    def device_class(self):
        return f"{SensorDeviceClass.ILLUMINANCE} threshold"

    limit_key = CONF_MAX_ILLUMINANCE
    default_value = DEFAULT_MAX_ILLUMINANCE


class PlantMinIlluminance(PlantMinMax):
    """Entity class for min illuminance threshold"""

    def __init__(
        self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity
    ) -> None:
        """Initialize the component."""
        self._attr_name = f"{plantdevice.name} {ATTR_MIN} {READING_ILLUMINANCE}"
        # Fix: Use ATTR_LIMITS instead of FLOW_PLANT_LIMITS
        limits = config.data.get(FLOW_PLANT_INFO, {}).get(ATTR_LIMITS, {})
        self._attr_native_value = limits.get(
            CONF_MIN_ILLUMINANCE, DEFAULT_MIN_ILLUMINANCE
        )
        self._attr_unique_id = f"{config.entry_id}-min-illuminance"
        self._attr_native_unit_of_measurement = LIGHT_LUX
        self._attr_native_max_value = 200000
        self._attr_native_min_value = 0
        self._attr_native_step = 500
        
        super().__init__(hass, config, plantdevice)

    @property
    def device_class(self):
        return f"{SensorDeviceClass.ILLUMINANCE} threshold"

    limit_key = CONF_MIN_ILLUMINANCE
    default_value = DEFAULT_MIN_ILLUMINANCE


class PlantMaxDli(PlantMinMax):
    """Entity class for max illuminance threshold"""

    def __init__(self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity) -> None:
        self._attr_name = f"{plantdevice.name} {ATTR_MAX} {READING_DLI}"
        # Fix: Use ATTR_LIMITS instead of FLOW_PLANT_LIMITS
        limits = config.data.get(FLOW_PLANT_INFO, {}).get(ATTR_LIMITS, {})
        self._attr_native_value = limits.get(
            CONF_MAX_DLI, DEFAULT_MAX_DLI
        )
        self._attr_unique_id = f"{config.entry_id}-max-dli"
        self._attr_native_unit_of_measurement = UNIT_PPFD
        self._attr_native_max_value = 100
        self._attr_native_min_value = 0
        self._attr_native_step = 1
        
        super().__init__(hass, config, plantdevice)

    @property
    def device_class(self):
        return f"{SensorDeviceClass.ILLUMINANCE} threshold"

    limit_key = CONF_MAX_DLI
    default_value = DEFAULT_MAX_DLI


class PlantMinDli(PlantMinMax):
    """Entity class for min illuminance threshold"""

    def __init__(self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity) -> None:
        self._attr_name = f"{plantdevice.name} {ATTR_MIN} {READING_DLI}"
        # Fix: Use ATTR_LIMITS instead of FLOW_PLANT_LIMITS
        limits = config.data.get(FLOW_PLANT_INFO, {}).get(ATTR_LIMITS, {})
        self._attr_native_value = limits.get(
            CONF_MIN_DLI, DEFAULT_MIN_DLI
        )
        self._attr_unique_id = f"{config.entry_id}-min-dli"
        self._attr_native_unit_of_measurement = UNIT_PPFD
        self._attr_native_max_value = 100
        self._attr_native_min_value = 0
        self._attr_native_step = 1
        
        super().__init__(hass, config, plantdevice)

    @property
    def device_class(self):
        return SensorDeviceClass.ILLUMINANCE

    limit_key = CONF_MIN_DLI
    default_value = DEFAULT_MIN_DLI


class PlantMaxConductivity(PlantMinMax):
    """Entity class for max conductivity threshold"""

    def __init__(self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity) -> None:
        self._attr_name = f"{plantdevice.name} {ATTR_MAX} {READING_CONDUCTIVITY}"
        # Fix: Use ATTR_LIMITS instead of FLOW_PLANT_LIMITS
        limits = config.data.get(FLOW_PLANT_INFO, {}).get(ATTR_LIMITS, {})
        self._attr_native_value = limits.get(
            CONF_MAX_CONDUCTIVITY, DEFAULT_MAX_CONDUCTIVITY
        )
        self._attr_unique_id = f"{config.entry_id}-max-conductivity"
        self._attr_native_unit_of_measurement = UNIT_CONDUCTIVITY
        self._attr_native_max_value = 3000
        self._attr_native_min_value = 0
        self._attr_native_step = 50
        
        super().__init__(hass, config, plantdevice)

    @property
    def device_class(self):
        return f"{ATTR_CONDUCTIVITY} threshold"

    limit_key = CONF_MAX_CONDUCTIVITY
    default_value = DEFAULT_MAX_CONDUCTIVITY


class PlantMinConductivity(PlantMinMax):
    """Entity class for min conductivity threshold"""

    def __init__(self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity) -> None:
        self._attr_name = f"{plantdevice.name} {ATTR_MIN} {READING_CONDUCTIVITY}"
        # Fix: Use ATTR_LIMITS instead of FLOW_PLANT_LIMITS
        limits = config.data.get(FLOW_PLANT_INFO, {}).get(ATTR_LIMITS, {})
        self._attr_native_value = limits.get(
            CONF_MIN_CONDUCTIVITY, DEFAULT_MIN_CONDUCTIVITY
        )
        self._attr_unique_id = f"{config.entry_id}-min-conductivity"
        self._attr_native_unit_of_measurement = UNIT_CONDUCTIVITY
        self._attr_native_max_value = 3000
        self._attr_native_min_value = 0
        self._attr_native_step = 50
        
        super().__init__(hass, config, plantdevice)

    @property
    def device_class(self):
        return f"{ATTR_CONDUCTIVITY} threshold"

    limit_key = CONF_MIN_CONDUCTIVITY
    default_value = DEFAULT_MIN_CONDUCTIVITY


class PlantMaxHumidity(PlantMinMax):
    """Entity class for max humidity threshold"""

    def __init__(self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity) -> None:
        self._attr_name = f"{plantdevice.name} {ATTR_MAX} {READING_HUMIDITY}"
        # Fix: Use ATTR_LIMITS instead of FLOW_PLANT_LIMITS
        limits = config.data.get(FLOW_PLANT_INFO, {}).get(ATTR_LIMITS, {})
        self._attr_native_value = limits.get(
            CONF_MAX_HUMIDITY, DEFAULT_MAX_HUMIDITY
        )
        self._attr_unique_id = f"{config.entry_id}-max-humidity"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_native_max_value = 100
        self._attr_native_min_value = 0
        self._attr_native_step = 1
        
        super().__init__(hass, config, plantdevice)

    @property
    def device_class(self):
        return f"{SensorDeviceClass.HUMIDITY} threshold"

    limit_key = CONF_MAX_HUMIDITY
    default_value = DEFAULT_MAX_HUMIDITY


class PlantMinHumidity(PlantMinMax):
    """Entity class for min conductivity threshold"""

    def __init__(self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity) -> None:
        self._attr_name = f"{plantdevice.name} {ATTR_MIN} {READING_HUMIDITY}"
        # Fix: Use ATTR_LIMITS instead of FLOW_PLANT_LIMITS
        limits = config.data.get(FLOW_PLANT_INFO, {}).get(ATTR_LIMITS, {})
        self._attr_native_value = limits.get(
            CONF_MIN_HUMIDITY, DEFAULT_MIN_HUMIDITY
        )
        self._attr_unique_id = f"{config.entry_id}-min-humidity"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_native_max_value = 100
        self._attr_native_min_value = 0
        self._attr_native_step = 1
        
        super().__init__(hass, config, plantdevice)

    @property
    def device_class(self):
        return f"{SensorDeviceClass.HUMIDITY} threshold"

    limit_key = CONF_MIN_HUMIDITY
    default_value = DEFAULT_MIN_HUMIDITY


class PlantMaxCo2(PlantMinMax):
    """Entity class for max CO2 threshold"""

    def __init__(self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity) -> None:
        self._attr_name = f"{plantdevice.name} {ATTR_MAX} {READING_CO2}"
        # Fix: Use ATTR_LIMITS instead of FLOW_PLANT_LIMITS
        limits = config.data.get(FLOW_PLANT_INFO, {}).get(ATTR_LIMITS, {})
        self._attr_native_value = limits.get(
            CONF_MAX_CO2, DEFAULT_MAX_CO2
        )
        self._attr_unique_id = f"{config.entry_id}-max-co2"
        self._attr_native_unit_of_measurement = "ppm"
        self._attr_native_max_value = 2000
        self._attr_native_min_value = 0
        self._attr_native_step = 10
        
        super().__init__(hass, config, plantdevice)

    @property
    def device_class(self):
        return f"{SensorDeviceClass.CO2} threshold"

    limit_key = CONF_MAX_CO2
    default_value = DEFAULT_MAX_CO2


class PlantMinCo2(PlantMinMax):
    """Entity class for min CO2 threshold"""

    def __init__(self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity) -> None:
        self._attr_name = f"{plantdevice.name} {ATTR_MIN} {READING_CO2}"
        # Fix: Use ATTR_LIMITS instead of FLOW_PLANT_LIMITS
        limits = config.data.get(FLOW_PLANT_INFO, {}).get(ATTR_LIMITS, {})
        self._attr_native_value = limits.get(
            CONF_MIN_CO2, DEFAULT_MIN_CO2
        )
        self._attr_unique_id = f"{config.entry_id}-min-co2"
        self._attr_native_unit_of_measurement = "ppm"
        self._attr_native_max_value = 2000
        self._attr_native_min_value = 0
        self._attr_native_step = 10
        
        super().__init__(hass, config, plantdevice)

    @property
    def device_class(self):
        return f"{SensorDeviceClass.CO2} threshold"

    limit_key = CONF_MIN_CO2
    default_value = DEFAULT_MIN_CO2