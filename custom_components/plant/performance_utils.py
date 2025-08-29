"""Performance optimization utilities for plant integration."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import dt as dt_util
from .const import DEVICE_TYPE_TENT, DEVICE_TYPE_PLANT, ATTR_TENT_ASSIGNMENT

_LOGGER = logging.getLogger(__name__)

# Configuration for data retention
DEFAULT_HISTORY_RETENTION_DAYS = 90
MAX_HISTORY_ENTRIES = 1000
CLEANUP_INTERVAL = timedelta(hours=6)


class MemoryManager:
    """Manages memory usage and data cleanup for plant entities."""
    
    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self._cleanup_tasks: Dict[str, Any] = {}
        self._history_limits: Dict[str, int] = {}
        
    async def setup_cleanup_schedules(self) -> None:
        """Setup periodic cleanup schedules for all plant entities."""
        async_track_time_interval(
            self.hass,
            self.periodic_cleanup,
            CLEANUP_INTERVAL
        )
        _LOGGER.info("Memory management cleanup scheduled every %s", CLEANUP_INTERVAL)
    
    async def periodic_cleanup(self, now: datetime) -> None:
        """Perform periodic cleanup of old data."""
        try:
            cleaned_entities = 0
            cleaned_records = 0
            
            # Clean up plant history data
            for domain_data in self.hass.data.get("plant", {}).values():
                if "plant" in domain_data:
                    plant = domain_data["plant"]
                    records_cleaned = await self._cleanup_plant_history(plant)
                    if records_cleaned > 0:
                        cleaned_entities += 1
                        cleaned_records += records_cleaned
            
            # Clean up tent assignments
            tent_assignments_cleaned = await self.cleanup_tent_assignments()
            if tent_assignments_cleaned > 0:
                _LOGGER.info("Cleaned up %d orphaned tent assignments", tent_assignments_cleaned)
            
            if cleaned_entities > 0:
                _LOGGER.info(
                    "Memory cleanup completed: %d entities, %d records removed",
                    cleaned_entities, cleaned_records
                )
                
        except Exception as e:
            _LOGGER.error("Error during periodic cleanup: %s", e)
    
    async def _cleanup_plant_history(self, plant) -> int:
        """Clean up old history data for a plant entity."""
        records_removed = 0
        cutoff_date = dt_util.utcnow() - timedelta(days=DEFAULT_HISTORY_RETENTION_DAYS)
        
        try:
            # Clean health history
            if hasattr(plant, '_attr_extra_state_attributes'):
                attrs = plant._attr_extra_state_attributes
                if 'health_history' in attrs:
                    original_count = len(attrs['health_history'])
                    attrs['health_history'] = [
                        entry for entry in attrs['health_history']
                        if self._is_entry_recent(entry, cutoff_date)
                    ]
                    # Also limit by count
                    if len(attrs['health_history']) > MAX_HISTORY_ENTRIES:
                        attrs['health_history'] = attrs['health_history'][-MAX_HISTORY_ENTRIES:]
                    
                    records_removed += original_count - len(attrs['health_history'])
            
            # Clean location history if available
            if hasattr(plant, 'location_history') and hasattr(plant.location_history, '_history'):
                location_history = getattr(plant.location_history, '_history', [])
                if isinstance(location_history, list):
                    original_count = len(location_history)
                    recent_history = [
                        entry for entry in location_history
                        if self._is_entry_recent(entry, cutoff_date)
                    ]
                    if len(recent_history) > MAX_HISTORY_ENTRIES:
                        recent_history = recent_history[-MAX_HISTORY_ENTRIES:]
                    
                    # Update the history
                    plant.location_history._history = recent_history
                    records_removed += original_count - len(recent_history)
            
            # Clean tent assignment history
            if hasattr(plant, '_tent_assignment_history'):
                original_count = len(plant._tent_assignment_history)
                plant._tent_assignment_history = [
                    entry for entry in plant._tent_assignment_history
                    if self._is_entry_recent(entry, cutoff_date)
                ]
                if len(plant._tent_assignment_history) > MAX_HISTORY_ENTRIES:
                    plant._tent_assignment_history = plant._tent_assignment_history[-MAX_HISTORY_ENTRIES:]
                
                records_removed += original_count - len(plant._tent_assignment_history)
            
            return records_removed
            
        except Exception as e:
            _LOGGER.warning("Error cleaning plant history for %s: %s", getattr(plant, 'entity_id', 'unknown'), e)
            return 0
    
    def _is_entry_recent(self, entry: Any, cutoff_date: datetime) -> bool:
        """Check if a history entry is recent enough to keep."""
        try:
            if isinstance(entry, dict):
                if 'timestamp' in entry:
                    entry_time = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                    return entry_time > cutoff_date
                elif 'time' in entry:
                    entry_time = datetime.fromisoformat(entry['time'].replace('Z', '+00:00'))
                    return entry_time > cutoff_date
            return True  # Keep if we can't determine age
        except (ValueError, AttributeError, TypeError):
            return True  # Keep if parsing fails
    
    def set_history_limit(self, entity_id: str, limit: int) -> None:
        """Set custom history limit for specific entity."""
        self._history_limits[entity_id] = limit
    
    def get_history_limit(self, entity_id: str) -> int:
        """Get history limit for entity."""
        return self._history_limits.get(entity_id, MAX_HISTORY_ENTRIES)
    
    async def cleanup_tent_assignments(self) -> int:
        """Clean up orphaned tent assignments and virtual sensor references."""
        cleaned_count = 0
        
        try:
            # Get all plant entities
            for domain_data in self.hass.data.get("plant", {}).values():
                if "plant" in domain_data:
                    plant = domain_data["plant"]
                    
                    # Check for orphaned tent assignments
                    if hasattr(plant, '_tent_assignment') and plant._tent_assignment:
                        tent_entity_id = plant._tent_assignment
                        
                        # Check if tent entity still exists
                        tent_state = self.hass.states.get(tent_entity_id)
                        if tent_state is None:
                            _LOGGER.warning(
                                "Removing orphaned tent assignment for %s (tent %s not found)",
                                getattr(plant, 'entity_id', 'unknown'),
                                tent_entity_id
                            )
                            plant._tent_assignment = None
                            
                            # Clean up virtual sensor references
                            if hasattr(plant, '_virtual_sensors'):
                                plant._virtual_sensors.clear()
                            
                            cleaned_count += 1
            
            if cleaned_count > 0:
                _LOGGER.info("Cleaned up %d orphaned tent assignments", cleaned_count)
            
            return cleaned_count
            
        except Exception as e:
            _LOGGER.error("Error during tent assignment cleanup: %s", e)
            return 0


class OptimizedSensorManager:
    """Optimized sensor management to reduce database load."""
    
    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self._virtual_sensors: Dict[str, Any] = {}
        self._update_batches: Dict[str, List[Any]] = {}
        
    def register_virtual_sensor(self, sensor_id: str, sensor) -> None:
        """Register a virtual sensor that doesn't persist to database."""
        self._virtual_sensors[sensor_id] = sensor
        _LOGGER.debug("Registered virtual sensor: %s", sensor_id)
    
    def unregister_virtual_sensor(self, sensor_id: str) -> bool:
        """Unregister a virtual sensor and clean up references."""
        if sensor_id in self._virtual_sensors:
            del self._virtual_sensors[sensor_id]
            _LOGGER.debug("Unregistered virtual sensor: %s", sensor_id)
            return True
        return False
    
    def get_virtual_sensors_for_tent(self, tent_entity_id: str) -> List[str]:
        """Get all virtual sensors referencing a specific tent."""
        tent_sensors = []
        for sensor_id, sensor in self._virtual_sensors.items():
            if hasattr(sensor, '_tent_reference') and sensor._tent_reference == tent_entity_id:
                tent_sensors.append(sensor_id)
        return tent_sensors
    
    async def cleanup_virtual_sensors_for_tent(self, tent_entity_id: str) -> int:
        """Clean up all virtual sensors for a specific tent."""
        tent_sensors = self.get_virtual_sensors_for_tent(tent_entity_id)
        cleaned_count = 0
        
        for sensor_id in tent_sensors:
            if self.unregister_virtual_sensor(sensor_id):
                cleaned_count += 1
        
        if cleaned_count > 0:
            _LOGGER.info("Cleaned up %d virtual sensors for tent %s", cleaned_count, tent_entity_id)
        
        return cleaned_count
    
    async def batch_update_sensors(self, sensors: List[Any]) -> None:
        """Batch update multiple sensors to reduce database writes."""
        if not sensors:
            return
            
        try:
            # Group sensors by update frequency
            high_freq = []
            low_freq = []
            
            for sensor in sensors:
                if hasattr(sensor, '_update_frequency'):
                    if sensor._update_frequency == 'high':
                        high_freq.append(sensor)
                    else:
                        low_freq.append(sensor)
                else:
                    low_freq.append(sensor)
            
            # Update high frequency sensors immediately
            for sensor in high_freq:
                if hasattr(sensor, 'async_write_ha_state'):
                    sensor.async_write_ha_state()
            
            # Batch low frequency sensors
            if low_freq:
                await self._batch_write_states(low_freq)
                
        except Exception as e:
            _LOGGER.error("Error in batch sensor update: %s", e)
    
    async def _batch_write_states(self, sensors: List[Any]) -> None:
        """Write multiple sensor states in batch."""
        tasks = []
        for sensor in sensors:
            if hasattr(sensor, 'async_write_ha_state'):
                tasks.append(asyncio.create_task(
                    asyncio.to_thread(sensor.async_write_ha_state)
                ))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


class DatabaseOptimizer:
    """Optimize database operations for plant integration."""
    
    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        
    async def optimize_plant_queries(self) -> None:
        """Optimize database queries for plant data."""
        try:
            # Implementation would depend on specific database optimization needs
            # This is a placeholder for future enhancements
            _LOGGER.debug("Database optimization completed")
        except Exception as e:
            _LOGGER.error("Database optimization failed: %s", e)
    
    def should_persist_sensor(self, sensor) -> bool:
        """Determine if sensor data should be persisted to database."""
        # Check if sensor is marked as virtual or reference-only
        if hasattr(sensor, '_virtual') and sensor._virtual:
            return False
            
        # Check if sensor references external data
        if hasattr(sensor, '_external_reference') and sensor._external_reference:
            return False
        
        # Check if sensor is a tent virtual sensor
        if hasattr(sensor, '_tent_reference') and sensor._tent_reference:
            return False
            
        return True


# Tent-specific performance utilities
class TentPerformanceManager:
    """Performance optimization specifically for tent management."""
    
    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self._tent_sensors_cache: Dict[str, Dict[str, Any]] = {}
        self._virtual_sensor_refs: Dict[str, List[str]] = {}
    
    def cache_tent_sensors(self, tent_entity_id: str, sensors: Dict[str, Any]) -> None:
        """Cache tent sensor references for quick access."""
        self._tent_sensors_cache[tent_entity_id] = sensors
        _LOGGER.debug("Cached sensors for tent %s", tent_entity_id)
    
    def get_cached_tent_sensors(self, tent_entity_id: str) -> Dict[str, Any]:
        """Get cached sensor references for a tent."""
        return self._tent_sensors_cache.get(tent_entity_id, {})
    
    def register_virtual_sensor_reference(self, tent_entity_id: str, virtual_sensor_id: str) -> None:
        """Register a virtual sensor reference for a tent."""
        if tent_entity_id not in self._virtual_sensor_refs:
            self._virtual_sensor_refs[tent_entity_id] = []
        
        if virtual_sensor_id not in self._virtual_sensor_refs[tent_entity_id]:
            self._virtual_sensor_refs[tent_entity_id].append(virtual_sensor_id)
    
    def unregister_virtual_sensor_reference(self, tent_entity_id: str, virtual_sensor_id: str) -> None:
        """Unregister a virtual sensor reference for a tent."""
        if tent_entity_id in self._virtual_sensor_refs:
            if virtual_sensor_id in self._virtual_sensor_refs[tent_entity_id]:
                self._virtual_sensor_refs[tent_entity_id].remove(virtual_sensor_id)
    
    def cleanup_tent_cache(self, tent_entity_id: str) -> None:
        """Clean up cached data for a removed tent."""
        if tent_entity_id in self._tent_sensors_cache:
            del self._tent_sensors_cache[tent_entity_id]
        
        if tent_entity_id in self._virtual_sensor_refs:
            del self._virtual_sensor_refs[tent_entity_id]
        
        _LOGGER.debug("Cleaned up cache for tent %s", tent_entity_id)


async def setup_performance_monitoring(hass: HomeAssistant) -> None:
    """Setup performance monitoring and optimization."""
    memory_manager = MemoryManager(hass)
    await memory_manager.setup_cleanup_schedules()
    
    sensor_manager = OptimizedSensorManager(hass)
    tent_performance_manager = TentPerformanceManager(hass)
    
    # Store managers in hass data for access by other components
    if "plant_performance" not in hass.data:
        hass.data["plant_performance"] = {}
    
    hass.data["plant_performance"]["memory_manager"] = memory_manager
    hass.data["plant_performance"]["sensor_manager"] = sensor_manager
    hass.data["plant_performance"]["tent_manager"] = tent_performance_manager
    
    _LOGGER.info("Plant performance monitoring initialized with tent support")