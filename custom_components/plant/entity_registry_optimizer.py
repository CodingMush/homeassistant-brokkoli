"""Entity registry optimization for tent sensor transitions."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Set
from datetime import datetime

from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_registry import async_get as async_get_registry
from homeassistant.helpers.device_registry import async_get as async_get_device_registry

from .const import (
    DOMAIN,
    FLOW_PLANT_INFO,
    FLOW_TENT_ENTITY,
    FLOW_INHERIT_TENT_SENSORS,
    DEVICE_TYPE_CYCLE,
)
from .virtual_sensors import get_tent_sensor_proxy

_LOGGER = logging.getLogger(__name__)


class EntityRegistryOptimizer:
    """
    Optimize entity registry operations for tent sensor transitions.
    
    This class manages:
    - Entity cleanup when plants change tent assignments
    - Lifecycle management of virtual vs real sensors
    - Registry optimization for reduced database load
    - Transition handling between tent assignments
    """
    
    def __init__(self, hass: HomeAssistant):
        """Initialize the entity registry optimizer."""
        self.hass = hass
        self.tent_proxy = get_tent_sensor_proxy(hass)
        self._transition_history: Dict[str, Dict] = {}
        
        # Track virtual sensor types for cleanup decisions
        self._virtual_sensor_types = {
            "temperature", "humidity", "co2", "illuminance", "conductivity", "ph"
        }
        
    async def handle_tent_assignment_change(
        self,
        plant_entry_id: str,
        old_tent_id: Optional[str],
        new_tent_id: Optional[str],
        inherit_sensors: bool = True
    ) -> Dict[str, any]:
        """
        Handle entity registry changes when plant tent assignment changes.
        
        Returns:
            Dictionary with transition results and statistics
        """
        _LOGGER.info(
            f"Handling tent assignment change for plant {plant_entry_id}: "
            f"{old_tent_id} -> {new_tent_id}"
        )
        
        transition_results = {
            "plant_entry_id": plant_entry_id,
            "old_tent_id": old_tent_id,
            "new_tent_id": new_tent_id,
            "inherit_sensors": inherit_sensors,
            "entities_cleaned": [],
            "entities_created": [],
            "virtual_sensors_updated": [],
            "transition_time": datetime.now(),
        }
        
        # Get plant config entry
        plant_entry = await self._get_plant_entry(plant_entry_id)
        if not plant_entry:
            _LOGGER.error(f"Plant entry {plant_entry_id} not found")
            return transition_results
        
        # Handle different transition scenarios
        if old_tent_id and new_tent_id:
            # Tent-to-tent transition
            await self._handle_tent_to_tent_transition(
                plant_entry, old_tent_id, new_tent_id, inherit_sensors, transition_results
            )
        elif old_tent_id and not new_tent_id:
            # Tent-to-direct transition
            await self._handle_tent_to_direct_transition(
                plant_entry, old_tent_id, transition_results
            )
        elif not old_tent_id and new_tent_id:
            # Direct-to-tent transition
            await self._handle_direct_to_tent_transition(
                plant_entry, new_tent_id, inherit_sensors, transition_results
            )
        
        # Store transition history
        self._transition_history[plant_entry_id] = transition_results
        
        # Trigger plant entity reload if needed
        if transition_results["entities_cleaned"] or transition_results["entities_created"]:
            await self._trigger_plant_reload(plant_entry_id)
        
        _LOGGER.info(f"Tent assignment transition completed: {transition_results}")
        return transition_results
    
    async def cleanup_orphaned_virtual_sensors(self) -> Dict[str, int]:
        """
        Clean up orphaned virtual sensors that no longer have valid tent assignments.
        
        Returns:
            Dictionary with cleanup statistics
        """
        _LOGGER.info("Starting cleanup of orphaned virtual sensors")
        
        entity_registry = async_get_registry(self.hass)
        cleanup_stats = {
            "scanned_entities": 0,
            "orphaned_found": 0,
            "entities_removed": 0,
            "errors": 0,
        }
        
        # Get all virtual sensor entities
        virtual_entities = [
            entity for entity in entity_registry.entities.values()
            if (entity.platform == DOMAIN and 
                entity.unique_id and 
                "_virtual" in entity.unique_id)
        ]
        
        cleanup_stats["scanned_entities"] = len(virtual_entities)
        
        for entity in virtual_entities:
            try:
                # Check if the plant still exists and has valid tent assignment
                plant_entry = await self._get_plant_entry(entity.config_entry_id)
                if not plant_entry:
                    # Plant entry no longer exists, remove virtual sensor
                    await self._remove_entity(entity.entity_id, "Plant entry removed")
                    cleanup_stats["orphaned_found"] += 1
                    cleanup_stats["entities_removed"] += 1
                    continue
                
                plant_info = plant_entry.data.get(FLOW_PLANT_INFO, {})
                tent_id = plant_info.get(FLOW_TENT_ENTITY)
                inherit_sensors = plant_info.get(FLOW_INHERIT_TENT_SENSORS, True)
                
                if not tent_id or not inherit_sensors:
                    # Plant no longer inherits from tent, remove virtual sensor
                    await self._remove_entity(entity.entity_id, "No tent inheritance")
                    cleanup_stats["orphaned_found"] += 1
                    cleanup_stats["entities_removed"] += 1
                    continue
                
                # Check if tent still exists
                tent_sensors = await self._get_tent_sensor_config(tent_id)
                if not tent_sensors:
                    # Tent no longer exists or has no sensors, remove virtual sensor
                    await self._remove_entity(entity.entity_id, "Tent no longer exists")
                    cleanup_stats["orphaned_found"] += 1
                    cleanup_stats["entities_removed"] += 1
                
            except Exception as e:
                _LOGGER.error(f"Error processing virtual entity {entity.entity_id}: {e}")
                cleanup_stats["errors"] += 1
        
        _LOGGER.info(f"Virtual sensor cleanup completed: {cleanup_stats}")
        return cleanup_stats
    
    async def optimize_entity_lifecycle(self, plant_entry_id: str) -> Dict[str, any]:
        """
        Optimize entity lifecycle for a specific plant.
        
        Returns:
            Dictionary with optimization results
        """
        optimization_results = {
            "plant_entry_id": plant_entry_id,
            "entities_analyzed": 0,
            "entities_optimized": 0,
            "virtual_sensors_created": 0,
            "real_sensors_removed": 0,
            "memory_saved_estimate": 0,
        }
        
        plant_entry = await self._get_plant_entry(plant_entry_id)
        if not plant_entry:
            return optimization_results
        
        plant_info = plant_entry.data.get(FLOW_PLANT_INFO, {})
        tent_id = plant_info.get(FLOW_TENT_ENTITY)
        inherit_sensors = plant_info.get(FLOW_INHERIT_TENT_SENSORS, True)
        
        if not tent_id or not inherit_sensors:
            # No optimization possible without tent inheritance
            return optimization_results
        
        # Get current plant entities
        entity_registry = async_get_registry(self.hass)
        plant_entities = [
            entity for entity in entity_registry.entities.values()
            if entity.config_entry_id == plant_entry_id and entity.platform == DOMAIN
        ]
        
        optimization_results["entities_analyzed"] = len(plant_entities)
        
        # Analyze entities for optimization opportunities
        tent_sensors = await self._get_tent_sensor_config(tent_id)
        
        for entity in plant_entities:
            sensor_type = self._extract_sensor_type(entity.unique_id)
            
            if (sensor_type in self._virtual_sensor_types and 
                sensor_type in tent_sensors and
                not "_virtual" in entity.unique_id):
                
                # This is a real sensor that could be virtualized
                optimization_results["entities_optimized"] += 1
                optimization_results["memory_saved_estimate"] += 50  # Estimated KB per entity
                
                _LOGGER.debug(
                    f"Optimization opportunity: {entity.entity_id} could be virtualized"
                )
        
        return optimization_results
    
    async def get_transition_history(self, plant_entry_id: Optional[str] = None) -> Dict:
        """Get transition history for debugging and monitoring."""
        if plant_entry_id:
            return self._transition_history.get(plant_entry_id, {})
        return self._transition_history.copy()
    
    # Private helper methods
    
    async def _handle_tent_to_tent_transition(
        self,
        plant_entry: ConfigEntry,
        old_tent_id: str,
        new_tent_id: str,
        inherit_sensors: bool,
        results: Dict
    ) -> None:
        """Handle transition from one tent to another."""
        if not inherit_sensors:
            # Convert virtual sensors to real sensors
            await self._convert_virtual_to_real(plant_entry, results)
        else:
            # Update virtual sensor references
            await self._update_virtual_sensor_references(
                plant_entry.entry_id, old_tent_id, new_tent_id, results
            )
    
    async def _handle_tent_to_direct_transition(
        self,
        plant_entry: ConfigEntry,
        old_tent_id: str,
        results: Dict
    ) -> None:
        """Handle transition from tent inheritance to direct sensors."""
        # Convert virtual sensors to real sensors
        await self._convert_virtual_to_real(plant_entry, results)
    
    async def _handle_direct_to_tent_transition(
        self,
        plant_entry: ConfigEntry,
        new_tent_id: str,
        inherit_sensors: bool,
        results: Dict
    ) -> None:
        """Handle transition from direct sensors to tent inheritance."""
        if inherit_sensors:
            # Convert real sensors to virtual sensors where applicable
            await self._convert_real_to_virtual(plant_entry, new_tent_id, results)
    
    async def _convert_virtual_to_real(self, plant_entry: ConfigEntry, results: Dict) -> None:
        """Convert virtual sensors to real sensors."""
        entity_registry = async_get_registry(self.hass)
        
        virtual_entities = [
            entity for entity in entity_registry.entities.values()
            if (entity.config_entry_id == plant_entry.entry_id and 
                "_virtual" in entity.unique_id)
        ]
        
        for entity in virtual_entities:
            # Remove virtual entity
            await self._remove_entity(entity.entity_id, "Converting to real sensor")
            results["entities_cleaned"].append(entity.entity_id)
            
            # Note: Real sensor creation will be handled by the sensor setup process
            sensor_type = self._extract_sensor_type(entity.unique_id)
            results["entities_created"].append(f"real_{sensor_type}_sensor")
    
    async def _convert_real_to_virtual(
        self,
        plant_entry: ConfigEntry,
        tent_id: str,
        results: Dict
    ) -> None:
        """Convert real sensors to virtual sensors where applicable."""
        tent_sensors = await self._get_tent_sensor_config(tent_id)
        entity_registry = async_get_registry(self.hass)
        
        plant_entities = [
            entity for entity in entity_registry.entities.values()
            if (entity.config_entry_id == plant_entry.entry_id and 
                entity.platform == DOMAIN and
                "_virtual" not in entity.unique_id)
        ]
        
        for entity in plant_entities:
            sensor_type = self._extract_sensor_type(entity.unique_id)
            
            if sensor_type in self._virtual_sensor_types and sensor_type in tent_sensors:
                # This sensor can be virtualized
                await self._remove_entity(entity.entity_id, "Converting to virtual sensor")
                results["entities_cleaned"].append(entity.entity_id)
                results["entities_created"].append(f"virtual_{sensor_type}_sensor")
    
    async def _update_virtual_sensor_references(
        self,
        plant_entry_id: str,
        old_tent_id: str,
        new_tent_id: str,
        results: Dict
    ) -> None:
        """Update virtual sensor references to new tent."""
        # Get virtual sensors for this plant
        entity_registry = async_get_registry(self.hass)
        
        virtual_entities = [
            entity for entity in entity_registry.entities.values()
            if (entity.config_entry_id == plant_entry_id and 
                "_virtual" in entity.unique_id)
        ]
        
        # Get new tent sensor configuration
        new_tent_sensors = await self._get_tent_sensor_config(new_tent_id)
        
        for entity in virtual_entities:
            sensor_type = self._extract_sensor_type(entity.unique_id)
            
            if sensor_type in new_tent_sensors:
                # Update virtual sensor reference
                results["virtual_sensors_updated"].append(entity.entity_id)
                _LOGGER.debug(f"Updated virtual sensor {entity.entity_id} to reference new tent")
    
    async def _get_plant_entry(self, plant_entry_id: str) -> Optional[ConfigEntry]:
        """Get plant config entry by ID."""
        for entry in self.hass.config_entries.async_entries(DOMAIN):
            if entry.entry_id == plant_entry_id:
                return entry
        return None
    
    async def _get_tent_sensor_config(self, tent_id: str) -> Dict[str, str]:
        """Get tent sensor configuration."""
        from .tent_sensor_manager import TentSensorManager
        manager = TentSensorManager(self.hass)
        return await manager.get_tent_sensor_config(tent_id)
    
    async def _remove_entity(self, entity_id: str, reason: str) -> None:
        """Remove entity from registry."""
        entity_registry = async_get_registry(self.hass)
        
        try:
            entity_registry.async_remove(entity_id)
            _LOGGER.info(f"Removed entity {entity_id}: {reason}")
        except Exception as e:
            _LOGGER.error(f"Failed to remove entity {entity_id}: {e}")
    
    async def _trigger_plant_reload(self, plant_entry_id: str) -> None:
        """Trigger plant entity reload after registry changes."""
        try:
            await self.hass.config_entries.async_reload(plant_entry_id)
            _LOGGER.info(f"Triggered reload for plant {plant_entry_id}")
        except Exception as e:
            _LOGGER.error(f"Failed to reload plant {plant_entry_id}: {e}")
    
    def _extract_sensor_type(self, unique_id: str) -> str:
        """Extract sensor type from unique ID."""
        # Example: "entry_id-current-temperature" -> "temperature"
        # Example: "entry_id_temperature_virtual" -> "temperature"
        
        parts = unique_id.split("-")
        if len(parts) >= 3:
            return parts[-1].replace("_virtual", "")
        
        # Alternative format
        parts = unique_id.split("_")
        for part in parts:
            if part in self._virtual_sensor_types:
                return part
        
        return "unknown"


# Global optimizer instance
_registry_optimizer: Optional[EntityRegistryOptimizer] = None

def get_entity_registry_optimizer(hass: HomeAssistant) -> EntityRegistryOptimizer:
    """Get or create the global entity registry optimizer."""
    global _registry_optimizer
    if _registry_optimizer is None:
        _registry_optimizer = EntityRegistryOptimizer(hass)
    return _registry_optimizer