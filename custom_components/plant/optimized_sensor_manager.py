"""Optimized sensor manager for reduced database load."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Set
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    FLOW_TENT_ENTITY,
    FLOW_INHERIT_TENT_SENSORS,
    FLOW_PLANT_INFO,
    DEVICE_TYPE_CYCLE,
)
from .virtual_sensors import VirtualPlantSensor, get_tent_sensor_proxy
from .tent_sensor_manager import TentSensorManager
from .entity_registry_optimizer import get_entity_registry_optimizer

_LOGGER = logging.getLogger(__name__)


class OptimizedSensorManager:
    """
    Optimized sensor manager that reduces database load through:
    - Virtual sensors for tent-inherited environmental data
    - Conditional entity creation based on necessity
    - Proxy-based sensor value access
    - Elimination of redundant sensor entities
    """
    
    def __init__(self, hass: HomeAssistant):
        """Initialize optimized sensor manager."""
        self.hass = hass
        self.tent_proxy = get_tent_sensor_proxy(hass)
        self.base_manager = TentSensorManager(hass)
        self.registry_optimizer = get_entity_registry_optimizer(hass)
        
        # Track which sensors should be created vs virtualized
        self._virtual_sensor_types = {
            "temperature", "humidity", "co2", "illuminance", "conductivity", "ph"
        }
        self._required_sensor_types = {
            "moisture"  # Moisture is plant-specific, always create
        }
        self._derived_sensor_types = {
            "ppfd", "dli", "light_integral"  # Always create as they're calculated
        }
    
    async def setup_optimized_sensors(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        plant,
        async_add_entities: AddEntitiesCallback
    ) -> Dict[str, any]:
        """
        Set up optimized sensor configuration with minimal database impact.
        
        Returns:
            Dictionary mapping sensor types to sensor entities/proxies
        """
        plant_info = entry.data.get(FLOW_PLANT_INFO, {})
        tent_entry_id = plant_info.get(FLOW_TENT_ENTITY)
        inherit_tent_sensors = plant_info.get(FLOW_INHERIT_TENT_SENSORS, True)
        
        sensor_entities = {}
        entities_to_add = []
        
        # 1. Handle environmental sensors (virtual if tent-inherited)
        environmental_sensors = await self._setup_environmental_sensors(
            hass, entry, plant, tent_entry_id, inherit_tent_sensors
        )
        sensor_entities.update(environmental_sensors["entities"])
        entities_to_add.extend(environmental_sensors["to_add"])
        
        # 2. Always create plant-specific sensors (moisture)
        plant_specific = await self._setup_plant_specific_sensors(hass, entry, plant)
        sensor_entities.update(plant_specific["entities"])
        entities_to_add.extend(plant_specific["to_add"])
        
        # 3. Create derived/calculated sensors (PPFD, DLI, etc.)
        derived_sensors = await self._setup_derived_sensors(hass, entry, plant)
        sensor_entities.update(derived_sensors["entities"])
        entities_to_add.extend(derived_sensors["to_add"])
        
        # 4. Setup consumption sensors only if base sensors exist
        consumption_sensors = await self._setup_consumption_sensors(
            hass, entry, plant, sensor_entities
        )
        sensor_entities.update(consumption_sensors["entities"])
        entities_to_add.extend(consumption_sensors["to_add"])
        
        # Add all entities to Home Assistant
        if entities_to_add:
            async_add_entities(entities_to_add)
        
        # Register with plant device
        await self._register_sensors_with_plant(plant, sensor_entities)
        
        _LOGGER.info(
            f"Optimized sensor setup for {plant.name}: "
            f"{len(entities_to_add)} entities created, "
            f"{len(sensor_entities) - len(entities_to_add)} virtual/proxy sensors"
        )
        
        return sensor_entities
    
    async def _setup_environmental_sensors(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        plant,
        tent_entry_id: Optional[str],
        inherit_tent_sensors: bool
    ) -> Dict[str, any]:
        """Set up environmental sensors with virtualization for tent inheritance."""
        entities = {}
        to_add = []
        
        # Get resolved sensor configuration
        resolved_sensors = await self.base_manager.resolve_plant_sensors(
            plant_config={
                f"{sensor_type}_sensor": entry.data.get(FLOW_PLANT_INFO, {}).get(f"{sensor_type}_sensor")
                for sensor_type in self._virtual_sensor_types
            },
            tent_entry_id=tent_entry_id,
            inherit_sensors=inherit_tent_sensors
        )
        
        for sensor_type in self._virtual_sensor_types:
            external_sensor = resolved_sensors.get(sensor_type)
            plant_override = entry.data.get(FLOW_PLANT_INFO, {}).get(f"{sensor_type}_sensor")
            
            # Determine if we should create virtual sensor or real entity
            if external_sensor and not plant_override and tent_entry_id and inherit_tent_sensors:
                # Use virtual sensor for tent-inherited sensors
                virtual_sensor = VirtualPlantSensor(
                    hass=hass,
                    plant_device=plant,
                    sensor_type=sensor_type,
                    external_sensor_id=external_sensor,
                    unique_id_suffix="_virtual"
                )
                entities[sensor_type] = virtual_sensor
                to_add.append(virtual_sensor)
                
                _LOGGER.debug(f"Created virtual {sensor_type} sensor for {plant.name}")
                
            elif external_sensor:
                # Create real sensor for plant-specific overrides
                real_sensor = await self._create_real_sensor(hass, entry, plant, sensor_type)
                if real_sensor:
                    real_sensor.replace_external_sensor(external_sensor)
                    entities[sensor_type] = real_sensor
                    to_add.append(real_sensor)
                    
                    _LOGGER.debug(f"Created real {sensor_type} sensor for {plant.name}")
            else:
                # Create sensor without external reference
                real_sensor = await self._create_real_sensor(hass, entry, plant, sensor_type)
                if real_sensor:
                    entities[sensor_type] = real_sensor
                    to_add.append(real_sensor)
        
        return {"entities": entities, "to_add": to_add}
    
    async def _setup_plant_specific_sensors(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        plant
    ) -> Dict[str, any]:
        """Set up sensors that are always plant-specific (moisture, etc.)."""
        entities = {}
        to_add = []
        
        # Moisture sensor is always plant-specific
        moisture_sensor = await self._create_real_sensor(hass, entry, plant, "moisture")
        if moisture_sensor:
            # Apply external sensor if configured
            external_moisture = entry.data.get(FLOW_PLANT_INFO, {}).get("moisture_sensor")
            if external_moisture:
                moisture_sensor.replace_external_sensor(external_moisture)
            
            entities["moisture"] = moisture_sensor
            to_add.append(moisture_sensor)
        
        return {"entities": entities, "to_add": to_add}
    
    async def _setup_derived_sensors(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        plant
    ) -> Dict[str, any]:
        """Set up derived/calculated sensors (PPFD, DLI, etc.)."""
        from .sensor import PlantCurrentPpfd, PlantTotalLightIntegral, PlantDailyLightIntegral
        
        entities = {}
        to_add = []
        
        # PPFD sensor (calculated from illuminance)
        ppfd_sensor = PlantCurrentPpfd(hass, entry, plant)
        entities["ppfd"] = ppfd_sensor
        to_add.append(ppfd_sensor)
        
        # Light integral sensor
        integral_sensor = PlantTotalLightIntegral(hass, entry, ppfd_sensor, plant)
        entities["light_integral"] = integral_sensor
        to_add.append(integral_sensor)
        
        # DLI sensor
        dli_sensor = PlantDailyLightIntegral(hass, entry, integral_sensor, plant)
        entities["dli"] = dli_sensor
        to_add.append(dli_sensor)
        
        return {"entities": entities, "to_add": to_add}
    
    async def _setup_consumption_sensors(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        plant,
        existing_sensors: Dict[str, any]
    ) -> Dict[str, any]:
        """Set up consumption sensors only if base sensors exist."""
        from .sensor import (
            PlantCurrentMoistureConsumption, PlantTotalWaterConsumption,
            PlantCurrentFertilizerConsumption, PlantTotalFertilizerConsumption,
            PlantCurrentPowerConsumption, PlantTotalPowerConsumption,
            PlantEnergyCost
        )
        
        entities = {}
        to_add = []
        
        # Water consumption (only if moisture sensor exists)
        if "moisture" in existing_sensors:
            moisture_consumption = PlantCurrentMoistureConsumption(hass, entry, plant)
            total_water = PlantTotalWaterConsumption(hass, entry, plant)
            
            entities["moisture_consumption"] = moisture_consumption
            entities["total_water_consumption"] = total_water
            to_add.extend([moisture_consumption, total_water])
        
        # Fertilizer consumption (only if conductivity sensor exists)
        if "conductivity" in existing_sensors:
            fertilizer_consumption = PlantCurrentFertilizerConsumption(hass, entry, plant)
            total_fertilizer = PlantTotalFertilizerConsumption(hass, entry, plant)
            
            entities["fertilizer_consumption"] = fertilizer_consumption
            entities["total_fertilizer_consumption"] = total_fertilizer
            to_add.extend([fertilizer_consumption, total_fertilizer])
        
        # Power consumption sensors
        total_power = PlantTotalPowerConsumption(hass, entry, plant)
        current_power = PlantCurrentPowerConsumption(hass, entry, plant)
        
        # Apply external power sensor if configured
        external_power = entry.data.get(FLOW_PLANT_INFO, {}).get("power_consumption_sensor")
        if external_power:
            total_power.replace_external_sensor(external_power)
        
        entities["total_power_consumption"] = total_power
        entities["current_power_consumption"] = current_power
        to_add.extend([total_power, current_power])
        
        # Energy cost sensor
        energy_cost = PlantEnergyCost(hass, entry, plant)
        entities["energy_cost"] = energy_cost
        to_add.append(energy_cost)
        
        return {"entities": entities, "to_add": to_add}
    
    async def _create_real_sensor(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        plant,
        sensor_type: str
    ):
        """Create a real sensor entity for the specified type."""
        from .sensor import (
            PlantCurrentTemperature, PlantCurrentHumidity, PlantCurrentCO2,
            PlantCurrentIlluminance, PlantCurrentConductivity, PlantCurrentPh,
            PlantCurrentMoisture
        )
        
        sensor_classes = {
            "temperature": PlantCurrentTemperature,
            "humidity": PlantCurrentHumidity,
            "co2": PlantCurrentCO2,
            "illuminance": PlantCurrentIlluminance,
            "conductivity": PlantCurrentConductivity,
            "ph": PlantCurrentPh,
            "moisture": PlantCurrentMoisture,
        }
        
        sensor_class = sensor_classes.get(sensor_type)
        if sensor_class:
            return sensor_class(hass, entry, plant)
        
        _LOGGER.warning(f"Unknown sensor type: {sensor_type}")
        return None
    
    async def _register_sensors_with_plant(self, plant, sensor_entities: Dict[str, any]) -> None:
        """Register sensors with the plant device."""
        # Register main sensors
        plant.add_sensors(
            temperature=sensor_entities.get("temperature"),
            humidity=sensor_entities.get("humidity"),
            moisture=sensor_entities.get("moisture"),
            conductivity=sensor_entities.get("conductivity"),
            illuminance=sensor_entities.get("illuminance"),
            CO2=sensor_entities.get("co2"),
            ph=sensor_entities.get("ph"),
            power_consumption=sensor_entities.get("current_power_consumption"),
        )
        
        # Register calculated sensors
        if all(key in sensor_entities for key in ["ppfd", "light_integral"]):
            plant.add_calculations(
                sensor_entities["ppfd"],
                sensor_entities["light_integral"],
                sensor_entities.get("moisture_consumption"),
                sensor_entities.get("fertilizer_consumption")
            )
        
        # Register DLI
        if "dli" in sensor_entities:
            plant.add_dli(sensor_entities["dli"])
        
        # Register consumption sensors
        if "total_water_consumption" in sensor_entities:
            plant.total_water_consumption = sensor_entities["total_water_consumption"]
        if "total_fertilizer_consumption" in sensor_entities:
            plant.total_fertilizer_consumption = sensor_entities["total_fertilizer_consumption"]
        
        # Register power consumption
        if all(key in sensor_entities for key in ["current_power_consumption", "total_power_consumption"]):
            plant.add_power_consumption_sensors(
                current=sensor_entities["current_power_consumption"],
                total=sensor_entities["total_power_consumption"]
            )
        
        # Register energy cost
        if "energy_cost" in sensor_entities:
            plant.energy_cost = sensor_entities["energy_cost"]
    
    async def handle_tent_assignment_change(
        self,
        plant_entry_id: str,
        new_tent_id: Optional[str],
        inherit_sensors: bool = True
    ) -> None:
        """Handle changes in tent assignment with optimized sensor updates and cleanup."""
        # Get plant entry
        plant_entry = None
        for entry in self.hass.config_entries.async_entries(DOMAIN):
            if entry.entry_id == plant_entry_id:
                plant_entry = entry
                break
        
        if not plant_entry:
            _LOGGER.error(f"Plant entry {plant_entry_id} not found")
            return
        
        # Get current tent assignment
        plant_info = plant_entry.data.get(FLOW_PLANT_INFO, {})
        old_tent_id = plant_info.get(FLOW_TENT_ENTITY)
        
        # Update plant configuration
        plant_data = dict(plant_entry.data)
        plant_info = dict(plant_data.get(FLOW_PLANT_INFO, {}))
        
        plant_info[FLOW_TENT_ENTITY] = new_tent_id
        plant_info[FLOW_INHERIT_TENT_SENSORS] = inherit_sensors
        
        plant_data[FLOW_PLANT_INFO] = plant_info
        
        # Update config entry
        self.hass.config_entries.async_update_entry(plant_entry, data=plant_data)
        
        # Handle entity registry optimization and cleanup
        transition_results = await self.registry_optimizer.handle_tent_assignment_change(
            plant_entry_id, old_tent_id, new_tent_id, inherit_sensors
        )
        
        # For virtual sensors, update their external sensor references
        if new_tent_id and inherit_sensors:
            await self._update_virtual_sensors_for_tent_change(
                plant_entry_id, old_tent_id, new_tent_id
            )
        
        _LOGGER.info(
            f"Updated tent assignment for plant {plant_entry_id}: {old_tent_id} -> {new_tent_id}. "
            f"Transition results: {transition_results}"
        )
    
    async def _update_virtual_sensors_for_tent_change(
        self,
        plant_entry_id: str,
        old_tent_id: Optional[str],
        new_tent_id: str
    ) -> None:
        """Update virtual sensor references when tent assignment changes."""
        # Get new tent sensor configuration
        new_tent_sensors = await self.base_manager.get_tent_sensor_config(new_tent_id)
        
        # Find virtual sensors for this plant and update them
        entity_registry = self.hass.helpers.entity_registry.async_get(self.hass)
        
        for entity_id, entity_entry in entity_registry.entities.items():
            if (entity_entry.config_entry_id == plant_entry_id and 
                entity_id.endswith("_virtual")):
                
                # Get the sensor entity
                sensor_entity = self.hass.data.get("entity_components", {}).get("sensor", {}).get(entity_id)
                
                if isinstance(sensor_entity, VirtualPlantSensor):
                    # Determine sensor type from entity
                    sensor_type = sensor_entity._sensor_type
                    new_external_sensor = new_tent_sensors.get(sensor_type)
                    
                    # Update virtual sensor reference
                    sensor_entity.update_external_sensor(new_external_sensor)
                    
                    _LOGGER.debug(f"Updated virtual {sensor_type} sensor for tent change")
    
    def get_optimization_stats(self) -> Dict[str, any]:
        """Get statistics about optimization effectiveness."""
        return {
            "virtual_sensor_types": list(self._virtual_sensor_types),
            "required_sensor_types": list(self._required_sensor_types),
            "derived_sensor_types": list(self._derived_sensor_types),
            "tent_proxy_info": self.tent_proxy.get_tent_info("all") if hasattr(self.tent_proxy, 'get_tent_info') else {},
        }
    
    async def cleanup_orphaned_sensors(self) -> Dict[str, int]:
        """Clean up orphaned virtual sensors and optimize entity registry."""
        _LOGGER.info("Starting optimization cleanup process")
        
        # Clean up orphaned virtual sensors
        cleanup_stats = await self.registry_optimizer.cleanup_orphaned_virtual_sensors()
        
        # Add optimization statistics
        optimization_summary = {
            "cleanup_completed": True,
            "timestamp": datetime.now().isoformat(),
            **cleanup_stats
        }
        
        _LOGGER.info(f"Optimization cleanup completed: {optimization_summary}")
        return optimization_summary
    
    async def optimize_plant_entities(self, plant_entry_id: str) -> Dict[str, any]:
        """Optimize entities for a specific plant."""
        return await self.registry_optimizer.optimize_entity_lifecycle(plant_entry_id)
    
    async def get_transition_history(self, plant_entry_id: Optional[str] = None) -> Dict:
        """Get transition history for monitoring and debugging."""
        return await self.registry_optimizer.get_transition_history(plant_entry_id)
    
    async def validate_optimization_health(self) -> Dict[str, any]:
        """Validate the health of the optimization system."""
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "tent_proxy_status": "healthy",
            "virtual_sensors_count": 0,
            "orphaned_sensors": 0,
            "optimization_active": True,
            "issues": [],
        }
        
        try:
            # Check tent proxy health
            if not hasattr(self.tent_proxy, 'get_tent_info'):
                health_report["tent_proxy_status"] = "degraded"
                health_report["issues"].append("Tent proxy missing methods")
            
            # Count virtual sensors
            from homeassistant.helpers.entity_registry import async_get as async_get_registry
            entity_registry = async_get_registry(self.hass)
            
            virtual_entities = [
                entity for entity in entity_registry.entities.values()
                if (entity.platform == DOMAIN and 
                    entity.unique_id and 
                    "_virtual" in entity.unique_id)
            ]
            health_report["virtual_sensors_count"] = len(virtual_entities)
            
            # Quick orphan check
            orphaned_count = 0
            for entity in virtual_entities[:10]:  # Sample check
                plant_entry = None
                for entry in self.hass.config_entries.async_entries(DOMAIN):
                    if entry.entry_id == entity.config_entry_id:
                        plant_entry = entry
                        break
                
                if not plant_entry:
                    orphaned_count += 1
            
            health_report["orphaned_sensors"] = orphaned_count
            
            if orphaned_count > 0:
                health_report["issues"].append(f"Found {orphaned_count} potentially orphaned sensors")
            
        except Exception as e:
            health_report["optimization_active"] = False
            health_report["issues"].append(f"Health check error: {str(e)}")
            _LOGGER.error(f"Optimization health check failed: {e}")
        
        return health_report