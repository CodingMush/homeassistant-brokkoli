"""Meter entities for the plant integration"""

from __future__ import annotations

from datetime import datetime, timedelta
import logging
import random
from statistics import quantiles
from typing import Any

from homeassistant.components.integration.const import METHOD_TRAPEZOIDAL
from homeassistant.components.integration.sensor import IntegrationSensor
from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.components.utility_meter.const import DAILY
from homeassistant.components.utility_meter.sensor import UtilityMeterSensor
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ICON,
    ATTR_NAME,
    ATTR_UNIT_OF_MEASUREMENT,
    LIGHT_LUX,
    PERCENTAGE,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    STATE_OK,
    STATE_PROBLEM,
    UnitOfConductivity,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfPower,
    Platform,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import (
    Entity,
    EntityCategory,
    async_generate_entity_id,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event, async_call_later
from homeassistant.util import dt as dt_util
from homeassistant.components.recorder import history, get_instance

from . import SETUP_DUMMY_SENSORS
from .const import (
    ATTR_CONDUCTIVITY,
    ATTR_DLI,
    ATTR_MOISTURE,
    ATTR_PLANT,
    ATTR_SENSORS,
    ATTR_PH,
    DATA_UPDATED,
    DEFAULT_LUX_TO_PPFD,
    DOMAIN,
    DOMAIN_SENSOR,
    FLOW_PLANT_INFO,
    FLOW_SENSOR_CONDUCTIVITY,
    FLOW_SENSOR_HUMIDITY,
    FLOW_SENSOR_CO2,
    FLOW_SENSOR_ILLUMINANCE,
    FLOW_SENSOR_MOISTURE,
    FLOW_SENSOR_TEMPERATURE,
    FLOW_SENSOR_POWER_CONSUMPTION,
    FLOW_SENSOR_PH,
    ICON_CONDUCTIVITY,
    ICON_DLI,
    ICON_HUMIDITY,
    ICON_CO2,
    ICON_ILLUMINANCE,
    ICON_MOISTURE,
    ICON_PPFD,
    ICON_TEMPERATURE,
    ICON_POWER_CONSUMPTION,
    ICON_PH,
    READING_CONDUCTIVITY,
    READING_DLI,
    READING_HUMIDITY,
    READING_CO2,
    READING_ILLUMINANCE,
    READING_MOISTURE,
    READING_PPFD,
    READING_TEMPERATURE,
    READING_POWER_CONSUMPTION,
    READING_PH,
    UNIT_CONDUCTIVITY,
    UNIT_DLI,
    UNIT_PPFD,
    DEVICE_TYPE_CYCLE,
    DEFAULT_AGGREGATIONS,
    ATTR_IS_NEW_PLANT,
    ATTR_NORMALIZE_MOISTURE,
    ATTR_NORMALIZE_WINDOW,
    ATTR_NORMALIZE_PERCENTILE,
    DEFAULT_NORMALIZE_WINDOW,
    DEFAULT_NORMALIZE_PERCENTILE,
    ICON_WATER_CONSUMPTION,
    UNIT_VOLUME,
    READING_MOISTURE_CONSUMPTION,
    READING_FERTILIZER_CONSUMPTION,
    ICON_FERTILIZER_CONSUMPTION,
    ATTR_KWH_PRICE,
    DEFAULT_KWH_PRICE,
    READING_ENERGY_COST,
    ICON_ENERGY_COST,
    DEVICE_CLASS_PH,  # Importiere unsere eigene Device Class
)
from .sensor_config import get_sensor_config, round_sensor_value, format_sensor_value

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up Plant Sensors from a config entry."""
    plant = hass.data[DOMAIN][entry.entry_id][ATTR_PLANT]

    # Erstelle die Standard-Sensoren für Plants
    if plant.device_type != DEVICE_TYPE_CYCLE:
        # Standard Sensoren erstellen
        pcurb = PlantCurrentIlluminance(hass, entry, plant)
        pcurc = PlantCurrentConductivity(hass, entry, plant)
        pcurm = PlantCurrentMoisture(hass, entry, plant)
        pcurt = PlantCurrentTemperature(hass, entry, plant)
        pcurh = PlantCurrentHumidity(hass, entry, plant)
        pcurCO2 = PlantCurrentCO2(hass, entry, plant)
        pcurph = PlantCurrentPh(hass, entry, plant)  # Neuer pH Sensor

        plant_sensors = [
            pcurb,
            pcurc,
            pcurm,
            pcurt,
            pcurh,
            pcurph,
            pcurCO2,
        ]  # pH Sensor hinzugefügt

        # Erst die Entities zu HA hinzufügen
        async_add_entities(plant_sensors)
        hass.data[DOMAIN][entry.entry_id][ATTR_SENSORS] = plant_sensors

        # Dann die Sensoren der Plant hinzufügen
        plant.add_sensors(
            temperature=pcurt,
            moisture=pcurm,
            conductivity=pcurc,
            illuminance=pcurb,
            humidity=pcurh,
            CO2=pcurCO2,
            power_consumption=None,  # Wird später gesetzt
            ph=pcurph,  # pH Sensor hinzugefügt
        )

        # Jetzt erst die externen Sensoren zuweisen
        if entry.data[FLOW_PLANT_INFO].get(FLOW_SENSOR_ILLUMINANCE):
            pcurb.replace_external_sensor(
                entry.data[FLOW_PLANT_INFO][FLOW_SENSOR_ILLUMINANCE]
            )
        if entry.data[FLOW_PLANT_INFO].get(FLOW_SENSOR_CONDUCTIVITY):
            pcurc.replace_external_sensor(
                entry.data[FLOW_PLANT_INFO][FLOW_SENSOR_CONDUCTIVITY]
            )
        if entry.data[FLOW_PLANT_INFO].get(FLOW_SENSOR_MOISTURE):
            pcurm.replace_external_sensor(
                entry.data[FLOW_PLANT_INFO][FLOW_SENSOR_MOISTURE]
            )
        if entry.data[FLOW_PLANT_INFO].get(FLOW_SENSOR_TEMPERATURE):
            pcurt.replace_external_sensor(
                entry.data[FLOW_PLANT_INFO][FLOW_SENSOR_TEMPERATURE]
            )
        if entry.data[FLOW_PLANT_INFO].get(FLOW_SENSOR_HUMIDITY):
            pcurh.replace_external_sensor(
                entry.data[FLOW_PLANT_INFO][FLOW_SENSOR_HUMIDITY]
            )
        if entry.data[FLOW_PLANT_INFO].get(FLOW_SENSOR_CO2):
            pcurCO2.replace_external_sensor(
                entry.data[FLOW_PLANT_INFO][FLOW_SENSOR_CO2]
            )
        if entry.data[FLOW_PLANT_INFO].get(FLOW_SENSOR_PH):  # pH Sensor zuweisen
            pcurph.replace_external_sensor(entry.data[FLOW_PLANT_INFO][FLOW_SENSOR_PH])

        # PPFD und DLI für Plants
        pcurppfd = PlantCurrentPpfd(hass, entry, plant)
        async_add_entities([pcurppfd])

        pintegral = PlantTotalLightIntegral(hass, entry, pcurppfd, plant)
        async_add_entities([pintegral], update_before_add=True)

        # Consumption Sensoren erstellen
        moisture_consumption = None
        total_water_consumption = None  # Initialisiere Total Water
        fertilizer_consumption = None
        total_fertilizer_consumption = None  # Initialisiere Total Fertilizer

        if plant.sensor_moisture:
            moisture_consumption = PlantCurrentMoistureConsumption(
                hass,
                entry,
                plant,
            )
            async_add_entities([moisture_consumption])

            # Total Water Consumption hinzufügen
            total_water_consumption = PlantTotalWaterConsumption(
                hass,
                entry,
                plant,
            )
            async_add_entities([total_water_consumption])

        if plant.sensor_conductivity:
            fertilizer_consumption = PlantCurrentFertilizerConsumption(
                hass,
                entry,
                plant,
            )
            async_add_entities([fertilizer_consumption])

            # Total Fertilizer Consumption hinzufügen
            total_fertilizer_consumption = PlantTotalFertilizerConsumption(
                hass,
                entry,
                plant,
            )
            async_add_entities([total_fertilizer_consumption])

        # Jetzt können wir add_calculations aufrufen
        plant.add_calculations(
            pcurppfd, pintegral, moisture_consumption, fertilizer_consumption
        )
        # Füge die Total Consumption Sensoren hinzu
        plant.total_water_consumption = total_water_consumption
        plant.total_fertilizer_consumption = total_fertilizer_consumption

        pdli = PlantDailyLightIntegral(hass, entry, pintegral, plant)
        async_add_entities(new_entities=[pdli], update_before_add=True)

        plant.add_dli(dli=pdli)

        # Füge zuerst den Total Power Consumption Sensor hinzu
        if plant.device_type != DEVICE_TYPE_CYCLE:
            total_power_consumption = PlantTotalPowerConsumption(hass, entry, plant)
            async_add_entities([total_power_consumption])

            # Weise den externen Sensor zu
            if entry.data[FLOW_PLANT_INFO].get(FLOW_SENSOR_POWER_CONSUMPTION):
                total_power_consumption.replace_external_sensor(
                    entry.data[FLOW_PLANT_INFO][FLOW_SENSOR_POWER_CONSUMPTION]
                )

            # Dann erst den Current Power Consumption Sensor erstellen
            pcurp = PlantCurrentPowerConsumption(hass, entry, plant)
            async_add_entities([pcurp])

            # Jetzt können wir beide Sensoren der Plant hinzufügen
            plant.add_power_consumption_sensors(
                current=pcurp, total=total_power_consumption
            )
    if plant.device_type == DEVICE_TYPE_CYCLE:
        cycle_sensors = {}

        # Basis-Sensoren
        base_sensor_types = [
            "temperature",
            "moisture",
            "conductivity",
            "illuminance",
            "humidity",
            "ph",
            "CO2",
        ]
        for sensor_type in base_sensor_types:
            cycle_sensors[sensor_type] = CycleMedianSensor(
                hass, entry, plant, sensor_type
            )

        # Berechnete Sensoren
        calculated_sensor_types = [
            "ppfd",
            "dli",
            "total_integral",
            "moisture_consumption",
            "total_water_consumption",  # Füge Total Water hinzu
            "fertilizer_consumption",
            "total_fertilizer_consumption",  # Füge Total Fertilizer hinzu
            "power_consumption",
            "total_power_consumption",  # Füge Total Power hinzu
        ]
        for sensor_type in calculated_sensor_types:
            cycle_sensors[sensor_type] = CycleMedianSensor(
                hass, entry, plant, sensor_type
            )

        # Füge alle Sensoren zu Home Assistant hinzu
        async_add_entities(cycle_sensors.values())

        # Füge die Sensoren der Plant hinzu
        plant.add_sensors(
            temperature=cycle_sensors["temperature"],
            moisture=cycle_sensors["moisture"],
            conductivity=cycle_sensors["conductivity"],
            illuminance=cycle_sensors["illuminance"],
            humidity=cycle_sensors["humidity"],
            CO2=cycle_sensors["CO2"],
            power_consumption=cycle_sensors["power_consumption"],
            ph=cycle_sensors["ph"],
        )

        # Füge die berechneten Sensoren hinzu
        plant.add_calculations(
            ppfd=cycle_sensors["ppfd"],
            total_integral=cycle_sensors["total_integral"],
            moisture_consumption=cycle_sensors["moisture_consumption"],
            fertilizer_consumption=cycle_sensors["fertilizer_consumption"],
        )
        plant.add_dli(dli=cycle_sensors["dli"])

        # Total Consumption Sensoren
        plant.total_water_consumption = cycle_sensors["total_water_consumption"]
        plant.total_fertilizer_consumption = cycle_sensors[
            "total_fertilizer_consumption"
        ]

        # Power Consumption Sensoren
        plant.add_power_consumption_sensors(
            current=cycle_sensors["power_consumption"],
            total=cycle_sensors["total_power_consumption"],
        )

    # Füge Energiekosten-Sensor hinzu
    energy_cost = PlantEnergyCost(hass, entry, plant)
    plant.energy_cost = energy_cost
    async_add_entities([energy_cost])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return True


class PlantCurrentStatus(RestoreSensor):
    """Base device for plants"""

    def __init__(
        self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity, sensor_type: str = None
    ) -> None:
        """Initialize the Plant component."""
        super().__init__()
        self._hass = hass
        self._config = config
        self._default_state = 0
        self._plant = plantdevice
        self._sensor_type = sensor_type
        
        # Get sensor configuration
        if sensor_type:
            sensor_config = get_sensor_config(sensor_type)
            if sensor_config:
                self._attr_icon = sensor_config.get("icon", getattr(self, "_attr_icon", None))
                self._attr_native_unit_of_measurement = sensor_config.get("unit", getattr(self, "_attr_native_unit_of_measurement", None))
        
        # Only set entity_id if name is already defined
        if hasattr(self, "_attr_name") and self._attr_name:
            self.entity_id = async_generate_entity_id(
                f"{DOMAIN}.{{}}", self.name, current_ids={}
            )
        if not self._attr_native_value or self._attr_native_value == STATE_UNKNOWN:
            self._attr_native_value = self._default_state

    @property
    def state_class(self):
        """Return the state class."""
        return (
            self._attr_state_class
            if hasattr(self, "_attr_state_class")
            else SensorStateClass.MEASUREMENT
        )

    @property
    def device_class(self):
        """Return the device class."""
        return self._attr_device_class if hasattr(self, "_attr_device_class") else None

    @property
    def device_info(self) -> dict:
        """Device info for devices"""
        return {
            "identifiers": {(DOMAIN, self._plant.unique_id)},
        }

    @property
    def extra_state_attributes(self) -> dict:
        if hasattr(self, "_external_sensor") and self._external_sensor:
            attributes = {
                "external_sensor": self.external_sensor,
            }
            return attributes
        return {}

    @property
    def external_sensor(self) -> str:
        """The external sensor we are tracking"""
        return getattr(self, "_external_sensor", None)

    def replace_external_sensor(self, new_sensor: str | None) -> None:
        """Modify the external sensor"""
        _LOGGER.info("Setting %s external sensor to %s", self.entity_id, new_sensor)
        self._external_sensor = new_sensor
        async_track_state_change_event(
            self._hass,
            [self._external_sensor],
            self._state_changed_event,
        )

        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()

        # We do not restore the state for these.
        # They are read from the external sensor anyway
        self._attr_native_value = None
        if state:
            if "external_sensor" in state.attributes:
                self.replace_external_sensor(state.attributes["external_sensor"])

        async_dispatcher_connect(
            self._hass, DATA_UPDATED, self._schedule_immediate_update
        )

    @callback
    def _schedule_immediate_update(self):
        """Schedule an immediate update."""
        self.async_schedule_update_ha_state(True)

    @callback
    def _state_changed_event(self, event):
        """Sensor state change event."""
        self.state_changed(event.data.get("entity_id"), event.data.get("new_state"))

    @callback
    def state_changed(self, entity_id, new_state):
        """Run on every update to allow for changes from the GUI and service call"""
        if not self.hass.states.get(self.entity_id):
            return
        if entity_id == self.entity_id:
            current_attrs = self.hass.states.get(self.entity_id).attributes
            if current_attrs.get("external_sensor") != self.external_sensor:
                self.replace_external_sensor(current_attrs.get("external_sensor"))

            if (
                ATTR_ICON in new_state.attributes
                and self.icon != new_state.attributes[ATTR_ICON]
            ):
                self._attr_icon = new_state.attributes[ATTR_ICON]

        if (
            self.external_sensor
            and new_state
            and new_state.state != STATE_UNKNOWN
            and new_state.state != STATE_UNAVAILABLE
        ):
            try:
                # Convert the value to a float for processing
                value = float(new_state.state)
                
                # Apply precision handling based on sensor type
                if self._sensor_type:
                    # Use calculation precision for internal processing
                    self._attr_native_value = round_sensor_value(value, self._sensor_type, "calculation")
                else:
                    self._attr_native_value = value
                    
                if ATTR_UNIT_OF_MEASUREMENT in new_state.attributes:
                    self._attr_native_unit_of_measurement = new_state.attributes[
                        ATTR_UNIT_OF_MEASUREMENT
                    ]
            except (ValueError, TypeError):
                self._attr_native_value = self._default_state
        else:
            self._attr_native_value = self._default_state

    async def async_update(self) -> None:
        """Set state and unit to the parent sensor state and unit"""
        if hasattr(self, "_external_sensor") and self._external_sensor:
            try:
                state = self._hass.states.get(self._external_sensor)
                if state:
                    value = float(state.state)
                    
                    # Apply precision handling based on sensor type
                    if self._sensor_type:
                        # Use calculation precision for internal processing
                        self._attr_native_value = round_sensor_value(value, self._sensor_type, "calculation")
                    else:
                        self._attr_native_value = value
                        
                    if ATTR_UNIT_OF_MEASUREMENT in state.attributes:
                        self._attr_native_unit_of_measurement = state.attributes[
                            ATTR_UNIT_OF_MEASUREMENT
                        ]
            except AttributeError:
                _LOGGER.debug(
                    "Unknown external sensor for %s: %s, setting to default: %s",
                    self.entity_id,
                    self._external_sensor,
                    self._default_state,
                )
                self._attr_native_value = self._default_state
            except ValueError:
                _LOGGER.debug(
                    "Unknown external value for %s: %s = %s, setting to default: %s",
                    self.entity_id,
                    self._external_sensor,
                    self._hass.states.get(self._external_sensor).state,
                    self._default_state,
                )
                self._attr_native_value = self._default_state
        else:
            _LOGGER.debug(
                "External sensor not set for %s, setting to default: %s",
                self.entity_id,
                self._default_state,
            )
            self._attr_native_value = self._default_state
            return


class PlantCurrentMoisture(PlantCurrentStatus):
    """Entity class for the current moisture meter"""

    def __init__(
        self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity
    ) -> None:
        """Initialize the sensor"""
        self._attr_name = f"{plantdevice.name} {READING_MOISTURE}"
        self._attr_unique_id = f"{config.entry_id}-current-moisture"
        self._attr_has_entity_name = False
        self._external_sensor = config.data[FLOW_PLANT_INFO].get(FLOW_SENSOR_MOISTURE)

        self._raw_value = None  # Initialisiere _raw_value
        self._normalize_factor = None  # Initialisiere normalize_factor
        super().__init__(hass, config, plantdevice, "moisture")

        self._normalize = config.data[FLOW_PLANT_INFO].get(
            ATTR_NORMALIZE_MOISTURE, False
        )
        self._normalize_window = config.data[FLOW_PLANT_INFO].get(
            ATTR_NORMALIZE_WINDOW, DEFAULT_NORMALIZE_WINDOW
        )
        self._normalize_percentile = config.data[FLOW_PLANT_INFO].get(
            ATTR_NORMALIZE_PERCENTILE, DEFAULT_NORMALIZE_PERCENTILE
        )
        self._max_moisture = None
        self._last_normalize_update = None

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()

        # Initialisiere Normalisierung beim Start
        if self._normalize:
            self._last_normalize_update = None  # Force update
            await self._update_normalization()

            # Wenn es eine Neuerstellung ist, aktualisiere sofort
            if self._config.data[FLOW_PLANT_INFO].get(ATTR_IS_NEW_PLANT, False):
                _LOGGER.debug("New plant created, updating normalization immediately")
                await self._update_normalization()

    async def _update_normalization(self) -> None:
        """Update the normalization max value"""
        if not self._normalize or not self._external_sensor:
            return

        now = dt_util.utcnow()

        # Aktualisiere nur alle 5 Minuten, außer bei None (Erststart/Neuerstellung)
        if (
            self._last_normalize_update is not None
            and now - self._last_normalize_update < timedelta(minutes=5)
        ):
            return

        # Hole historische Daten
        start_time = now - timedelta(days=self._normalize_window)

        # Korrigierter Aufruf der history API mit dem richtigen Executor
        recorder = get_instance(self._hass)
        history_list = await recorder.async_add_executor_job(
            history.state_changes_during_period,
            self._hass,
            start_time,
            now,
            self._external_sensor,
        )

        if not history_list or self._external_sensor not in history_list:
            return

        # Extrahiere numerische Werte
        values = []
        for state in history_list[self._external_sensor]:
            try:
                if state.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE):
                    values.append(float(state.state))
            except (ValueError, TypeError):
                continue

        if values:
            # Berechne das Perzentil
            percentile_index = int(len(values) * self._normalize_percentile / 100)
            sorted_values = sorted(values)
            self._max_moisture = sorted_values[percentile_index]
            self._normalize_factor = (
                100 / self._max_moisture
            )  # Exakter Wert für Berechnungen
            self._last_normalize_update = now
            _LOGGER.debug(
                "Updated moisture normalization: max=%s, factor=%s (from %s values)",
                self._max_moisture,
                round(self._normalize_factor, 2),  # Gerundeter Wert nur für Log
                len(values),
            )

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional sensor attributes."""
        attributes = super().extra_state_attributes or {}

        if self._normalize:
            attributes.update(
                {
                    "moisture_normalization": {
                        "enabled": True,
                        "window_days": self._normalize_window,
                        "percentile": self._normalize_percentile,
                        "current_max": self._max_moisture,
                        "raw_value": self._raw_value
                        if hasattr(self, "_raw_value")
                        else None,
                    }
                }
            )

        return attributes

    async def async_update(self) -> None:
        """Update the sensor."""
        await super().async_update()

        # Speichere den Rohwert vor der Normalisierung
        if self._attr_native_value is not None:
            self._raw_value = self._attr_native_value

        # Aktualisiere Normalisierung
        await self._update_normalization()

        # Normalisiere den Wert wenn nötig
        if (
            self._normalize
            and self._max_moisture
            and self._attr_native_value is not None
        ):
            try:
                normalized = min(
                    100, (float(self._attr_native_value) / self._max_moisture) * 100
                )
                self._attr_native_value = round(normalized, 1)
            except (ValueError, TypeError):
                pass

    @property
    def device_class(self) -> str:
        """Device class"""
        return ATTR_MOISTURE


class PlantCurrentTemperature(PlantCurrentStatus):
    """Entity class for the current temperature meter"""

    def __init__(
        self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity
    ) -> None:
        """Initialize the sensor"""
        self._attr_name = f"{plantdevice.name} {READING_TEMPERATURE}"
        self._attr_unique_id = f"{config.entry_id}-current-temperature"
        self._attr_has_entity_name = False
        self._external_sensor = config.data[FLOW_PLANT_INFO].get(
            FLOW_SENSOR_TEMPERATURE
        )
        super().__init__(hass, config, plantdevice, "temperature")

    @property
    def device_class(self) -> str:
        """Device class"""
        return SensorDeviceClass.TEMPERATURE


class PlantCurrentIlluminance(PlantCurrentStatus):
    """Entity class for the current illuminance meter"""

    def __init__(
        self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity
    ) -> None:
        """Initialize the sensor"""
        self._attr_name = f"{plantdevice.name} {READING_ILLUMINANCE}"
        self._attr_unique_id = f"{config.entry_id}-current-illuminance"
        self._attr_has_entity_name = False
        self._external_sensor = config.data[FLOW_PLANT_INFO].get(
            FLOW_SENSOR_ILLUMINANCE
        )
        super().__init__(hass, config, plantdevice, "illuminance")

    @property
    def device_class(self) -> str:
        """Device class"""
        return SensorDeviceClass.ILLUMINANCE


class PlantCurrentHumidity(PlantCurrentStatus):
    """Entity class for the current humidity meter"""

    def __init__(
        self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity
    ) -> None:
        """Initialize the sensor"""
        self._attr_name = f"{plantdevice.name} {READING_HUMIDITY}"
        self._attr_unique_id = f"{config.entry_id}-current-humidity"
        self._attr_has_entity_name = False
        self._external_sensor = config.data[FLOW_PLANT_INFO].get(FLOW_SENSOR_HUMIDITY)
        super().__init__(hass, config, plantdevice, "humidity")

    @property
    def device_class(self) -> str:
        """Device class"""
        return SensorDeviceClass.HUMIDITY


class PlantCurrentCO2(PlantCurrentStatus):
    """Entity class for the current CO2 meter"""

    def __init__(
        self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity
    ) -> None:
        """Initialize the sensor"""
        self._attr_name = f"{plantdevice.name} {READING_PPFD}"
        self._attr_unique_id = f"{config.entry_id}-current-ppfd"
        self._attr_has_entity_name = False
        self._plant = plantdevice
        self._external_sensor = self._plant.sensor_illuminance.entity_id
        self._follow_unit = False
        super().__init__(hass, config, plantdevice, "ppfd")
        self.entity_id = async_generate_entity_id(
            f"{DOMAIN_SENSOR}.{{}}", self.name, current_ids={}
        )

        # Setze Wert bei Neuerstellung zurück
        if config.data[FLOW_PLANT_INFO].get(ATTR_IS_NEW_PLANT, False):
            self._attr_native_value = None

    @property
    def device_class(self) -> str:
        """Device class"""
        return None

    async def async_update(self) -> None:
        """Run on every update to allow for changes from the GUI and service call"""
        if not self.hass.states.get(self.entity_id):
            return
        if self.external_sensor != self._plant.sensor_illuminance.entity_id:
            self.replace_external_sensor(self._plant.sensor_illuminance.entity_id)
        if self.external_sensor:
            external_sensor = self.hass.states.get(self.external_sensor)
            if external_sensor:
                self._attr_native_value = self.ppfd(external_sensor.state)
            else:
                self._attr_native_value = None
        else:
            self._attr_native_value = None

    @callback
    def state_changed(self, entity_id: str, new_state: str) -> None:
        """Run on every update to allow for changes from the GUI and service call"""
        if not self.hass.states.get(self.entity_id):
            return
        if self._external_sensor != self._plant.sensor_illuminance.entity_id:
            self.replace_external_sensor(self._plant.sensor_illuminance.entity_id)
        if self.external_sensor:
            external_sensor = self.hass.states.get(self.external_sensor)
            if external_sensor:
                self._attr_native_value = self.ppfd(external_sensor.state)
            else:
                self._attr_native_value = None
        else:
            self._attr_native_value = None


class PlantTotalLightIntegral(IntegrationSensor):
    """Entity class to calculate PPFD from LX"""

    def __init__(
        self,
        hass: HomeAssistant,
        config: ConfigEntry,
        illuminance_ppfd_sensor: Entity,
        plantdevice: Entity,
    ) -> None:
        """Initialize the sensor"""
        self._config = config  # Speichere config für späteren Zugriff
        super().__init__(
            hass,
            integration_method=METHOD_TRAPEZOIDAL,
            name=f"{plantdevice.name} Total {READING_PPFD} Integral",
            round_digits=2,
            source_entity=illuminance_ppfd_sensor.entity_id,
            unique_id=f"{config.entry_id}-ppfd-integral",
            unit_prefix=None,
            unit_time=UnitOfTime.SECONDS,
            max_sub_interval=None,
        )
        self._attr_has_entity_name = False
        self._unit_of_measurement = UNIT_PPFD  # Benutze PPFD Einheit statt DLI
        self._attr_native_unit_of_measurement = UNIT_PPFD  # Setze auch native unit
        self._attr_icon = ICON_DLI
        self.entity_id = async_generate_entity_id(
            f"{DOMAIN_SENSOR}.{{}}", self.name, current_ids={}
        )
        self._plant = plantdevice
        self._attr_native_value = 0  # Starte immer bei 0

        # Setze Wert bei Neuerstellung zurück
        if config.data[FLOW_PLANT_INFO].get(ATTR_IS_NEW_PLANT, False):
            self._attr_native_value = 0
            self._state = 0  # Wichtig für IntegrationSensor

    @property
    def entity_category(self) -> str:
        """The entity category"""
        return EntityCategory.DIAGNOSTIC

    @property
    def device_info(self) -> dict:
        """Device info for devices"""
        return {
            "identifiers": {(DOMAIN, self._plant.unique_id)},
        }

    @property
    def entity_registry_visible_default(self) -> str:
        return False

    def _unit(self, source_unit: str) -> str:
        """Override unit"""
        return UNIT_PPFD  # Benutze immer PPFD als Einheit

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()

        # Bei einer neuen Plant nicht den alten State wiederherstellen
        if self._config.data[FLOW_PLANT_INFO].get(ATTR_IS_NEW_PLANT, False):
            self._attr_native_value = 0
            self._state = 0  # Wichtig für IntegrationSensor


class PlantDailyLightIntegral(RestoreSensor):
    """Entity class to calculate Daily Light Integral from PPDF"""

    def __init__(
        self,
        hass: HomeAssistant,
        config: ConfigEntry,
        illuminance_integration_sensor: Entity,
        plantdevice: Entity,
    ) -> None:
        """Initialize the sensor"""
        self._hass = hass
        self._config = config
        self._plant = plantdevice
        self._attr_name = f"{plantdevice.name} {READING_DLI}"
        self._attr_unique_id = f"{config.entry_id}-dli"
        self._attr_native_unit_of_measurement = UNIT_DLI
        self._attr_icon = ICON_DLI
        self._source_entity = illuminance_integration_sensor.entity_id
        self._history = []
        self._last_update = None
        self._attr_native_value = 0  # Starte immer bei 0
        self._last_value = None  # Initialisiere _last_value

        # Bei Neuerstellung explizit auf 0 setzen
        if config.data[FLOW_PLANT_INFO].get(ATTR_IS_NEW_PLANT, False):
            self._attr_native_value = 0
            self._history = []

        self.entity_id = async_generate_entity_id(
            f"{DOMAIN_SENSOR}.{{}}", self.name, current_ids={}
        )

    @property
    def device_class(self) -> str:
        return ATTR_DLI

    @property
    def device_info(self) -> dict:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._plant.unique_id)},
        }

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional sensor attributes."""
        return {"last_update": self._last_update, "source_entity": self._source_entity}

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()

        # Restore previous state
        last_state = await self.async_get_last_state()
        if last_state and last_state.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            try:
                if not self._config.data[FLOW_PLANT_INFO].get(ATTR_IS_NEW_PLANT, False):
                    self._attr_native_value = float(last_state.state)
                    if last_state.attributes.get("last_update"):
                        self._last_update = last_state.attributes["last_update"]

            except ValueError:
                self._attr_native_value = 0  # Fallback to 0

    async def async_update(self) -> None:
        """Update the sensor's state."""
        source_state = self._hass.states.get(self._source_entity)

        if source_state and source_state.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            new_value = source_state.state

            # Update the sensor state only if the new value is different from the last value
            if new_value != self._last_value:
                self._last_value = new_value

                # Calculate the DLI value based on the new value and the time difference
                if self._last_update:
                    time_diff = (datetime.now() - self._last_update).total_seconds()
                    dli_value = float(new_value) * time_diff
                    self._history.append(dli_value)

                self._last_update = datetime.now()

                # Sum up the DLI values in the history to get the total DLI
                self._attr_native_value = sum(self._history)

                # Optionally, you can clear the history if you want to reset the DLI for each update
                # self._history = []

        else:
            self._attr_native_value = 0  # Set to 0 if the source entity is unavailable or unknown


class PlantCurrentMoistureConsumption(RestoreSensor):
    """Sensor to track water consumption based on moisture drop."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: ConfigEntry,
        plant_device: Entity,
    ) -> None:
        """Initialize the sensor."""
        self._hass = hass
        self._config = config
        self._plant = plant_device
        self._attr_name = f"{plant_device.name} {READING_MOISTURE_CONSUMPTION}"
        self._attr_unique_id = f"{config.entry_id}-moisture-consumption"
        self._history = []
        self._last_update = None
        self._attr_native_value = 0  # Starte immer bei 0

        # Get sensor configuration
        sensor_config = get_sensor_config("moisture_consumption")
        if sensor_config:
            self._attr_icon = sensor_config.get("icon")
            self._attr_native_unit_of_measurement = sensor_config.get("unit")

        # Bei Neuerstellung explizit auf 0 setzen
        if config.data[FLOW_PLANT_INFO].get(ATTR_IS_NEW_PLANT, False):
            self._attr_native_value = 0
            self._history = []

    async def async_added_to_hass(self) -> None:
        """Handle being added to Home Assistant."""
        await super().async_added_to_hass()

        if (last_state := await self.async_get_last_state()) is None:
            return

        try:
            self._attr_native_value = float(last_state.state)
            self._last_update = last_state.attributes["last_update"]
        except (TypeError, ValueError):
            self._attr_native_value = 0

        # Track source entity changes
        async_track_state_change_event(
            self._hass,
            [self._source_entity],
            self._state_changed_event,
        )

    @callback
    def _state_changed_event(self, event):
        """Handle source entity state changes."""
        if self._config.data[FLOW_PLANT_INFO].get(ATTR_IS_NEW_PLANT, False):
            return  # Bei neuer Plant keine Änderungen verarbeiten

        new_state = event.data.get("new_state")
        if not new_state or new_state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            return

        try:
            current_value = float(new_state.state)
            current_time = dt_util.utcnow()

            # Add to history
            self._history.append((current_time, current_value))

            # Entferne Einträge älter als 24 Stunden
            cutoff_time = current_time - timedelta(hours=24)
            self._history = [(t, v) for t, v in self._history if t >= cutoff_time]

            # Berechne Konsum basierend auf historischen Werten
            if self._last_update is not None and self._last_value is not None:
                delta_time = (current_time - self._last_update).total_seconds() / 3600  # Zeit in Stunden
                delta_value = self._last_value - current_value  # Verbrauch pro Stunde

                # Konsum nur aktualisieren, wenn Werte gültig sind
                if delta_value > 0:
                    self._attr_native_value += delta_value * delta_time

            # Aktualisiere letzte Zeit und Wert
            self._last_update = current_time
            self._last_value = current_value

        except (ValueError, TypeError):
            return


class PlantCurrentPowerConsumption(RestoreSensor):
    """Power consumption sensor for a plant."""

    def __init__(
        self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity
    ) -> None:
        """Initialize the sensor."""
        super().__init__()
        self._hass = hass
        self._config = config
        self._plant = plantdevice
        self._attr_name = f"{plantdevice.name} {READING_POWER_CONSUMPTION}"
        self._attr_unique_id = f"{config.entry_id}-current-power-consumption"
        self._attr_has_entity_name = False
        self._last_value = None
        self._last_time = None
        self._attr_native_value = 0  # Starte immer bei 0

        # Get sensor configuration
        sensor_config = get_sensor_config("power_consumption")
        if sensor_config:
            self._attr_icon = sensor_config.get("icon")
            self._attr_native_unit_of_measurement = sensor_config.get("unit")
            self._attr_device_class = sensor_config.get("device_class", SensorDeviceClass.POWER)

        self._attr_state_class = (
            SensorStateClass.MEASUREMENT
        )  # MEASUREMENT statt TOTAL_INCREASING

        # Bei Neuerstellung explizit auf 0 setzen
        if config.data[FLOW_PLANT_INFO].get(ATTR_IS_NEW_PLANT, False):
            self._attr_native_value = 0
            self._last_value = None
            self._last_time = None

    @property
    def device_info(self) -> dict:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._plant.unique_id)},
        }

    @property
    def should_poll(self) -> bool:
        """Return True as we want to poll for updates."""
        return True

    async def async_update(self) -> None:
        """Update the sensor."""
        if not self._plant.total_power_consumption:
            return

        try:
            state = self._hass.states.get(self._plant.total_power_consumption.entity_id)
            if not state or state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
                return

            current_value = float(state.state)
            current_time = dt_util.utcnow()

            # Berechne aktuelle Leistung in Watt
            if self._last_value is not None and self._last_time is not None:
                time_diff = (current_time - self._last_time).total_seconds()
                if time_diff > 0:
                    # Umrechnung von kWh/s in Watt
                    power = (
                        (current_value - self._last_value) * 3600 * 1000
                    ) / time_diff
                    self._attr_native_value = max(
                        0, round(power, 0)
                    )  # Keine Nachkommastellen

            # Speichere aktuelle Werte für nächste Berechnung
            self._last_value = current_value
            self._last_time = current_time

        except (TypeError, ValueError):
            pass

    @property
    def external_sensor(self) -> str:
        """The external sensor we are tracking"""
        return self._external_sensor

    def replace_external_sensor(self, new_sensor: str | None) -> None:
        """Modify the external sensor."""
        _LOGGER.info("Setting %s external sensor to %s", self.entity_id, new_sensor)
        self._external_sensor = new_sensor
        if new_sensor:
            async_track_state_change_event(
                self._hass,
                [self._external_sensor],
                self._state_changed_event,
            )
        self.async_write_ha_state()

    @property
    def should_poll(self) -> bool:
        """Return True as we want to poll for updates."""
        return True

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()

        # Restore previous state
        last_state = await self.async_get_last_state()
        if last_state and last_state.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            try:
                if not self._config.data[FLOW_PLANT_INFO].get(ATTR_IS_NEW_PLANT, False):
                    self._attr_native_value = float(last_state.state)
            except (TypeError, ValueError):
                self._attr_native_value = 0

    async def async_update(self) -> None:
        """Update the sensor."""
        if self._external_sensor:
            external_state = self.hass.states.get(self._external_sensor)
            if external_state and external_state.state not in (
                STATE_UNKNOWN,
                STATE_UNAVAILABLE,
            ):
                try:
                    current_value = float(external_state.state)

                    # Berechne nur die Differenz seit dem letzten Wert
                    if self._last_value is not None:
                        if current_value > self._last_value:  # Nur positive Änderungen
                            increase = current_value - self._last_value
                            self._attr_native_value += round(
                                increase, 3
                            )  # 3 Nachkommastellen statt 2

                    # Speichere aktuellen Wert für nächste Berechnung
                    self._last_value = current_value
                    self.async_write_ha_state()

                except (TypeError, ValueError):
                    pass
        else:
            self._attr_native_value = 0
            self.async_write_ha_state()


class PlantCurrentFertilizerConsumption(RestoreSensor):
    """Sensor to track fertilizer consumption based on conductivity drop."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: ConfigEntry,
        plant_device: Entity,
    ) -> None:
        """Initialize the sensor."""
        self._hass = hass
        self._config = config
        self._plant = plant_device
        self._attr_name = f"{plant_device.name} {READING_FERTILIZER_CONSUMPTION}"
        self._attr_unique_id = f"{config.entry_id}-fertilizer-consumption"
        self._history = []
        self._last_update = None
        self._attr_native_value = 0  # Starte immer bei 0
        self._last_value = None  # Initialisiere _last_value

        # Get sensor configuration
        sensor_config = get_sensor_config("fertilizer_consumption")
        if sensor_config:
            self._attr_icon = sensor_config.get("icon")
            self._attr_native_unit_of_measurement = sensor_config.get("unit")

        # Bei Neuerstellung explizit auf 0 setzen
        if config.data[FLOW_PLANT_INFO].get(ATTR_IS_NEW_PLANT, False):
            self._attr_native_value = 0
            self._history = []

    @property
    def device_info(self) -> dict:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._plant.unique_id)},
        }

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional sensor attributes."""
        return {
            "last_update": self._last_update,
        }

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()

        # Restore previous state
        last_state = await self.async_get_last_state()
        if last_state and last_state.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            try:
                if not self._config.data[FLOW_PLANT_INFO].get(ATTR_IS_NEW_PLANT, False):
                    self._attr_native_value = float(last_state.state)
            except (TypeError, ValueError):
                self._attr_native_value = 0

        # Track conductivity sensor changes
        async_track_state_change_event(
            self._hass,
            [self._plant.sensor_conductivity.entity_id],
            self._state_changed_event,
        )

    @callback
    def _state_changed_event(self, event):
        """Handle conductivity sensor state changes."""
        if self._config.data[FLOW_PLANT_INFO].get(ATTR_IS_NEW_PLANT, False):
            return  # Bei neuer Plant keine Änderungen verarbeiten

        new_state = event.data.get("new_state")
        if not new_state or new_state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            return

        try:
            current_value = float(new_state.state)

            # Berechne nur die Differenz seit dem letzten Wert
            if self._last_value is not None:
                if current_value > self._last_value:  # Nur positive Änderungen
                    increase = current_value - self._last_value
                    self._attr_native_value += round(
                        increase, 3
                    )  # 3 Nachkommastellen statt 2

            # Speichere aktuellen Wert für nächste Berechnung
            self._last_value = current_value
            self.async_write_ha_state()

        except (TypeError, ValueError):
            pass


class PlantTotalWaterConsumption(RestoreSensor):
    """Sensor to track total water consumption."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: ConfigEntry,
        plant_device: Entity,
    ) -> None:
        """Initialize the sensor."""
        self._hass = hass
        self._config = config
        self._plant = plant_device
        self._attr_name = f"{plant_device.name} Total {READING_WATER_CONSUMPTION}"
        self._attr_unique_id = f"{config.entry_id}-total-water-consumption"
        self._attr_native_unit_of_measurement = UNIT_WATER
        self._attr_icon = ICON_WATER_CONSUMPTION
        self._attr_entity_category = (
            EntityCategory.DIAGNOSTIC
        )  # Füge Entity-Kategorie hinzu
        self._history = []
        self._last_update = None
        self._attr_native_value = 0  # Starte immer bei 0
        self._last_water_usage = 0  # Initialisiere _last_water_usage

        # Bei Neuerstellung explizit auf 0 setzen
        if config.data[FLOW_PLANT_INFO].get(ATTR_IS_NEW_PLANT, False):
            self._attr_native_value = 0
            self._history = []

    @property
    def entity_category(self) -> str:
        """The entity category"""
        return EntityCategory.DIAGNOSTIC

    @property
    def device_info(self) -> dict:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._plant.unique_id)},
        }

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional sensor attributes."""
        return {
            "last_update": self._last_update,
        }

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()

        # Restore previous state
        last_state = await self.async_get_last_state()
        if last_state and last_state.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            try:
                if not self._config.data[FLOW_PLANT_INFO].get(ATTR_IS_NEW_PLANT, False):
                    self._attr_native_value = float(last_state.state)
            except (TypeError, ValueError):
                self._attr_native_value = 0

        # Track water sensor changes
        async_track_state_change_event(
            self._hass,
            [self._plant.sensor_water_usage.entity_id],
            self._state_changed_event,
        )

    @callback
    def _state_changed_event(self, event):
        """Handle water sensor state changes."""
        if self._config.data[FLOW_PLANT_INFO].get(ATTR_IS_NEW_PLANT, False):
            return  # Bei neuer Plant keine Änderungen verarbeiten

        new_state = event.data.get("new_state")
        if not new_state or new_state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            return

        try:
            current_value = float(new_state.state)
            current_time = dt_util.utcnow()

            # Entferne Einträge älter als 24 Stunden
            cutoff_time = current_time - timedelta(hours=24)
            self._history = [(t, v) for t, v in self._history if t >= cutoff_time]

            # Berechne nur die Differenz seit dem letzten Wert
            if self._last_water_usage is not None:
                if current_value > self._last_water_usage:  # Nur positive Änderungen
                    increase = current_value - self._last_water_usage
                    self._attr_native_value += round(
                        increase, 3
                    )  # 3 Nachkommastellen statt 2

            # Speichere aktuellen Wert für nächste Berechnung
            self._last_water_usage = current_value
            self.async_write_ha_state()

        except Exception:
            # Ensure no crash on service call
            self.async_write_ha_state()


class PlantTotalFertilizerConsumption(RestoreSensor):
    """Sensor to track total fertilizer consumption."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: ConfigEntry,
        plant_device: Entity,
    ) -> None:
        """Initialize the sensor."""
        self._hass = hass
        self._config = config
        self._plant = plant_device
        self._attr_name = f"{plant_device.name} Total {READING_FERTILIZER_CONSUMPTION}"
        self._attr_unique_id = f"{config.entry_id}-total-fertilizer-consumption"
        self._attr_native_unit_of_measurement = UNIT_CONDUCTIVITY
        self._attr_icon = ICON_FERTILIZER_CONSUMPTION
        self._attr_entity_category = (
            EntityCategory.DIAGNOSTIC
        )  # Füge Entity-Kategorie hinzu
        self._history = []
        self._last_update = None
        self._attr_native_value = 0  # Starte immer bei 0
        self._last_value = None  # Initialisiere _last_value

        # Bei Neuerstellung explizit auf 0 setzen
        if config.data[FLOW_PLANT_INFO].get(ATTR_IS_NEW_PLANT, False):
            self._attr_native_value = 0
            self._history = []

    @property
    def entity_category(self) -> str:
        """The entity category"""
        return EntityCategory.DIAGNOSTIC

    @property
    def device_info(self) -> dict:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._plant.unique_id)},
        }

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional sensor attributes."""
        return {
            "last_update": self._last_update,
        }

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()

        # Restore previous state
        last_state = await self.async_get_last_state()
        if last_state and last_state.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            try:
                if not self._config.data[FLOW_PLANT_INFO].get(ATTR_IS_NEW_PLANT, False):
                    self._attr_native_value = float(last_state.state)
            except (TypeError, ValueError):
                self._attr_native_value = 0

        # Track conductivity sensor changes
        async_track_state_change_event(
            self._hass,
            [self._plant.sensor_conductivity.entity_id],
            self._state_changed_event,
        )

    @callback
    def _state_changed_event(self, event):
        """Handle conductivity sensor state changes."""
        if self._config.data[FLOW_PLANT_INFO].get(ATTR_IS_NEW_PLANT, False):
            return  # Bei neuer Plant keine Änderungen verarbeiten

        new_state = event.data.get("new_state")
        if not new_state or new_state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            return

        try:
            current_time = dt_util.utcnow()
            current_value = float(new_state.state)

            # Entferne Einträge älter als 24 Stunden
            cutoff_time = current_time - timedelta(hours=24)
            self._history = [(t, v) for t, v in self._history if t >= cutoff_time]

            # Berechne nur die Differenz seit dem letzten Wert
            if self._last_value is not None:
                if current_value > self._last_value:  # Nur positive Änderungen
                    increase = current_value - self._last_value
                    self._attr_native_value += round(
                        increase, 3
                    )  # 3 Nachkommastellen statt 2

            # Speichere aktuellen Wert für nächste Berechnung
            self._last_value = current_value
            self.async_write_ha_state()

        except (TypeError, ValueError):
            pass


class PlantEnergyCost(RestoreSensor):
    """Sensor für die Energiekosten."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: ConfigEntry,
        plant_device: Entity,
    ) -> None:
        """Initialize the sensor."""
        super().__init__()
        self._hass = hass
        self._config = config
        self._plant = plant_device
        self._attr_unique_id = f"{config.entry_id}_energy_cost"
        self.entity_id = async_generate_entity_id(
            "sensor.{}", f"{plant_device.name}_energy_cost", hass=hass
        )
        self._attr_name = f"{plant_device.name} {READING_ENERGY_COST}"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

        # Get sensor configuration
        sensor_config = get_sensor_config("energy_cost")
        if sensor_config:
            self._attr_icon = sensor_config.get("icon")
            self._attr_native_unit_of_measurement = sensor_config.get("unit")

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()

        state = await self.async_get_last_state()
        if state:
            try:
                self._attr_native_value = float(state.state)
            except (TypeError, ValueError):
                self._attr_native_value = 0.0

    async def async_update(self) -> None:
        """Update the sensor."""
        if not self._plant.total_power_consumption:
            self._attr_native_value = 0.0
            return

        try:
            total_power = float(self._plant.total_power_consumption.state)
            self._attr_native_value = round(total_power * self._plant.kwh_price, 2)
        except (TypeError, ValueError):
            self._attr_native_value = 0.0


class PlantCurrentPh(PlantCurrentStatus):
    """Entity class for the current pH meter"""

    def __init__(
        self, hass: HomeAssistant, config: ConfigEntry, plantdevice: Entity
    ) -> None:
        """Initialize the sensor"""
        self._attr_name = f"{plantdevice.name} {READING_PH}"
        self._attr_unique_id = f"{config.entry_id}-current-ph"
        self._attr_has_entity_name = False
        self._external_sensor = config.data[FLOW_PLANT_INFO].get(FLOW_SENSOR_PH)
        self._default_state = 7.0  # Neutraler pH-Wert als Default
        super().__init__(hass, config, plantdevice, "ph")

    @property
    def device_class(self) -> str:
        """Device class"""
        return DEVICE_CLASS_PH  # Verwende unsere eigene Device Class

    async def set_manual_value(self, value: float) -> None:
        """Set a manual pH measurement (0-14)."""
        try:
            if value is None:
                return
            # clamp plausible pH range
            if value < 0:
                value = 0
            if value > 14:
                value = 14
            self._attr_native_value = float(value)
            self.async_write_ha_state()
        except (TypeError, ValueError):
            return