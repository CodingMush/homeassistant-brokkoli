"""Configuration and migration utilities for tent sensor optimization."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_registry import async_get as async_get_registry
from homeassistant.helpers.storage import Store

from .const import DOMAIN, FLOW_PLANT_INFO, FLOW_TENT_ENTITY, FLOW_INHERIT_TENT_SENSORS

_LOGGER = logging.getLogger(__name__)

# Configuration constants
OPTIMIZATION_CONFIG_VERSION = 1
OPTIMIZATION_STORAGE_KEY = f"{DOMAIN}_optimization_config"

# Default optimization levels
OPTIMIZATION_LEVELS = {
    "disabled": {
        "use_virtual_sensors": False,
        "enable_database_exclusion": False,
        "cleanup_orphaned_sensors": False,
        "description": "No optimization applied"
    },
    "basic": {
        "use_virtual_sensors": True,
        "enable_database_exclusion": True,
        "cleanup_orphaned_sensors": False,
        "description": "Basic virtual sensor optimization"
    },
    "aggressive": {
        "use_virtual_sensors": True,
        "enable_database_exclusion": True,
        "cleanup_orphaned_sensors": True,
        "auto_migrate_existing": True,
        "description": "Full optimization with automatic migration"
    },
    "custom": {
        "description": "User-defined optimization settings"
    }
}


class OptimizationConfig:
    """Manage optimization configuration and database exclusion settings."""
    
    def __init__(self, hass: HomeAssistant):
        """Initialize optimization configuration."""
        self.hass = hass
        self._store = Store(hass, OPTIMIZATION_CONFIG_VERSION, OPTIMIZATION_STORAGE_KEY)
        self._config = None
        
    async def async_load(self) -> Dict[str, Any]:
        """Load optimization configuration."""
        if self._config is None:
            stored_config = await self._store.async_load() or {}
            
            # Apply defaults
            self._config = {
                "optimization_level": stored_config.get("optimization_level", "basic"),
                "settings": stored_config.get("settings", OPTIMIZATION_LEVELS["basic"].copy()),
                "migration_status": stored_config.get("migration_status", {}),
                "recording_exclusions": stored_config.get("recording_exclusions", []),
                "last_updated": stored_config.get("last_updated"),
            }
            
            # Ensure settings have all required keys
            level = self._config["optimization_level"]
            if level in OPTIMIZATION_LEVELS:
                default_settings = OPTIMIZATION_LEVELS[level].copy()
                self._config["settings"] = {**default_settings, **self._config["settings"]}
        
        return self._config
    
    async def async_save(self) -> None:
        """Save optimization configuration."""
        if self._config:
            self._config["last_updated"] = datetime.now().isoformat()
            await self._store.async_save(self._config)
    
    async def set_optimization_level(self, level: str, custom_settings: Optional[Dict] = None) -> bool:\n        \"\"\"Set optimization level and update configuration.\"\"\"\n        config = await self.async_load()\n        \n        if level not in OPTIMIZATION_LEVELS and level != \"custom\":\n            _LOGGER.error(f\"Invalid optimization level: {level}\")\n            return False\n        \n        config[\"optimization_level\"] = level\n        \n        if level == \"custom\" and custom_settings:\n            config[\"settings\"] = custom_settings\n        elif level in OPTIMIZATION_LEVELS:\n            config[\"settings\"] = OPTIMIZATION_LEVELS[level].copy()\n        \n        await self.async_save()\n        _LOGGER.info(f\"Optimization level set to: {level}\")\n        return True\n    \n    async def get_recording_exclusions(self) -> List[str]:\n        \"\"\"Get list of entity patterns to exclude from database recording.\"\"\"\n        config = await self.async_load()\n        return config.get(\"recording_exclusions\", [])\n    \n    async def add_recording_exclusion(self, pattern: str) -> None:\n        \"\"\"Add entity pattern to recording exclusions.\"\"\"\n        config = await self.async_load()\n        exclusions = config.setdefault(\"recording_exclusions\", [])\n        \n        if pattern not in exclusions:\n            exclusions.append(pattern)\n            await self.async_save()\n            _LOGGER.info(f\"Added recording exclusion pattern: {pattern}\")\n    \n    async def remove_recording_exclusion(self, pattern: str) -> None:\n        \"\"\"Remove entity pattern from recording exclusions.\"\"\"\n        config = await self.async_load()\n        exclusions = config.get(\"recording_exclusions\", [])\n        \n        if pattern in exclusions:\n            exclusions.remove(pattern)\n            await self.async_save()\n            _LOGGER.info(f\"Removed recording exclusion pattern: {pattern}\")\n    \n    async def is_entity_excluded_from_recording(self, entity_id: str) -> bool:\n        \"\"\"Check if entity should be excluded from database recording.\"\"\"\n        exclusions = await self.get_recording_exclusions()\n        \n        for pattern in exclusions:\n            if self._matches_pattern(entity_id, pattern):\n                return True\n        \n        # Check if entity is a virtual sensor\n        if \"_virtual\" in entity_id:\n            return True\n        \n        return False\n    \n    def _matches_pattern(self, entity_id: str, pattern: str) -> bool:\n        \"\"\"Check if entity ID matches exclusion pattern.\"\"\"\n        import fnmatch\n        return fnmatch.fnmatch(entity_id, pattern)\n    \n    async def get_settings(self) -> Dict[str, Any]:\n        \"\"\"Get current optimization settings.\"\"\"\n        config = await self.async_load()\n        return config.get(\"settings\", {})\n    \n    async def update_migration_status(self, migration_type: str, status: Dict[str, Any]) -> None:\n        \"\"\"Update migration status for a specific migration type.\"\"\"\n        config = await self.async_load()\n        migration_status = config.setdefault(\"migration_status\", {})\n        migration_status[migration_type] = {\n            **status,\n            \"timestamp\": datetime.now().isoformat()\n        }\n        await self.async_save()


class OptimizationMigrator:\n    \"\"\"Handle migration of existing installations to optimization.\"\"\"\n    \n    def __init__(self, hass: HomeAssistant, config_manager: OptimizationConfig):\n        \"\"\"Initialize migration manager.\"\"\"\n        self.hass = hass\n        self.config_manager = config_manager\n    \n    async def migrate_existing_installation(self) -> Dict[str, Any]:\n        \"\"\"Migrate existing installation to use optimization.\"\"\"\n        _LOGGER.info(\"Starting migration of existing installation\")\n        \n        migration_results = {\n            \"started_at\": datetime.now().isoformat(),\n            \"plants_analyzed\": 0,\n            \"plants_migrated\": 0,\n            \"tents_found\": 0,\n            \"virtual_sensors_created\": 0,\n            \"real_sensors_removed\": 0,\n            \"errors\": [],\n            \"completed\": False\n        }\n        \n        try:\n            # Find all plant entries\n            plant_entries = [\n                entry for entry in self.hass.config_entries.async_entries(DOMAIN)\n                if FLOW_PLANT_INFO in entry.data and not entry.data.get(\"is_tent\", False)\n            ]\n            \n            migration_results[\"plants_analyzed\"] = len(plant_entries)\n            \n            # Find tent entries\n            tent_entries = [\n                entry for entry in self.hass.config_entries.async_entries(DOMAIN)\n                if entry.data.get(\"is_tent\", False)\n            ]\n            \n            migration_results[\"tents_found\"] = len(tent_entries)\n            \n            # Migrate each plant\n            for plant_entry in plant_entries:\n                try:\n                    plant_result = await self._migrate_plant_entry(plant_entry)\n                    \n                    if plant_result[\"migrated\"]:\n                        migration_results[\"plants_migrated\"] += 1\n                        migration_results[\"virtual_sensors_created\"] += plant_result.get(\"virtual_sensors_created\", 0)\n                        migration_results[\"real_sensors_removed\"] += plant_result.get(\"real_sensors_removed\", 0)\n                \n                except Exception as e:\n                    error_msg = f\"Failed to migrate plant {plant_entry.entry_id}: {str(e)}\"\n                    migration_results[\"errors\"].append(error_msg)\n                    _LOGGER.error(error_msg)\n            \n            # Setup default recording exclusions\n            await self._setup_default_recording_exclusions()\n            \n            migration_results[\"completed\"] = True\n            migration_results[\"completed_at\"] = datetime.now().isoformat()\n            \n            # Update migration status\n            await self.config_manager.update_migration_status(\"initial_migration\", migration_results)\n            \n        except Exception as e:\n            error_msg = f\"Migration failed: {str(e)}\"\n            migration_results[\"errors\"].append(error_msg)\n            _LOGGER.error(error_msg)\n        \n        _LOGGER.info(f\"Migration completed: {migration_results}\")\n        return migration_results\n    \n    async def _migrate_plant_entry(self, plant_entry: ConfigEntry) -> Dict[str, Any]:\n        \"\"\"Migrate a single plant entry.\"\"\"\n        plant_info = plant_entry.data.get(FLOW_PLANT_INFO, {})\n        \n        migration_result = {\n            \"plant_entry_id\": plant_entry.entry_id,\n            \"migrated\": False,\n            \"virtual_sensors_created\": 0,\n            \"real_sensors_removed\": 0,\n            \"reason\": \"No migration needed\"\n        }\n        \n        # Check if plant has any tent-inheritable sensors configured\n        inheritable_sensors = [\n            \"temperature_sensor\", \"humidity_sensor\", \"co2_sensor\",\n            \"illuminance_sensor\", \"conductivity_sensor\", \"ph_sensor\"\n        ]\n        \n        has_external_sensors = any(\n            plant_info.get(sensor) for sensor in inheritable_sensors\n        )\n        \n        if not has_external_sensors:\n            migration_result[\"reason\"] = \"No external sensors configured\"\n            return migration_result\n        \n        # Try to find a suitable tent for this plant\n        suitable_tent = await self._find_suitable_tent_for_plant(plant_entry)\n        \n        if not suitable_tent:\n            migration_result[\"reason\"] = \"No suitable tent found\"\n            return migration_result\n        \n        # Migrate plant to tent inheritance\n        try:\n            await self._assign_plant_to_tent(plant_entry, suitable_tent)\n            \n            migration_result[\"migrated\"] = True\n            migration_result[\"tent_assigned\"] = suitable_tent\n            migration_result[\"virtual_sensors_created\"] = len([\n                sensor for sensor in inheritable_sensors \n                if plant_info.get(sensor)\n            ])\n            migration_result[\"reason\"] = \"Successfully migrated to tent inheritance\"\n            \n        except Exception as e:\n            migration_result[\"reason\"] = f\"Migration failed: {str(e)}\"\n            raise\n        \n        return migration_result\n    \n    async def _find_suitable_tent_for_plant(self, plant_entry: ConfigEntry) -> Optional[str]:\n        \"\"\"Find a suitable tent for plant migration.\"\"\"\n        plant_info = plant_entry.data.get(FLOW_PLANT_INFO, {})\n        \n        # Get all tent entries\n        tent_entries = [\n            entry for entry in self.hass.config_entries.async_entries(DOMAIN)\n            if entry.data.get(\"is_tent\", False)\n        ]\n        \n        if not tent_entries:\n            return None\n        \n        # For now, use the first available tent\n        # In a more sophisticated implementation, we could match based on\n        # sensor compatibility, location, or other criteria\n        return tent_entries[0].entry_id\n    \n    async def _assign_plant_to_tent(self, plant_entry: ConfigEntry, tent_entry_id: str) -> None:\n        \"\"\"Assign plant to tent for sensor inheritance.\"\"\"\n        plant_data = dict(plant_entry.data)\n        plant_info = dict(plant_data.get(FLOW_PLANT_INFO, {}))\n        \n        # Set tent assignment\n        plant_info[FLOW_TENT_ENTITY] = tent_entry_id\n        plant_info[FLOW_INHERIT_TENT_SENSORS] = True\n        \n        plant_data[FLOW_PLANT_INFO] = plant_info\n        \n        # Update config entry\n        self.hass.config_entries.async_update_entry(plant_entry, data=plant_data)\n        \n        # Trigger reload to apply changes\n        await self.hass.config_entries.async_reload(plant_entry.entry_id)\n    \n    async def _setup_default_recording_exclusions(self) -> None:\n        \"\"\"Setup default database recording exclusions for virtual sensors.\"\"\"\n        default_exclusions = [\n            f\"sensor.*_virtual\",  # All virtual sensors\n            f\"sensor.*_{DOMAIN}_*_virtual\",  # Domain-specific virtual sensors\n        ]\n        \n        for pattern in default_exclusions:\n            await self.config_manager.add_recording_exclusion(pattern)\n    \n    async def rollback_migration(self, migration_id: str) -> Dict[str, Any]:\n        \"\"\"Rollback a previous migration.\"\"\"\n        _LOGGER.info(f\"Starting rollback of migration: {migration_id}\")\n        \n        rollback_results = {\n            \"migration_id\": migration_id,\n            \"started_at\": datetime.now().isoformat(),\n            \"plants_processed\": 0,\n            \"plants_rolled_back\": 0,\n            \"errors\": [],\n            \"completed\": False\n        }\n        \n        try:\n            # Find plants with tent assignments\n            plant_entries = [\n                entry for entry in self.hass.config_entries.async_entries(DOMAIN)\n                if (FLOW_PLANT_INFO in entry.data and \n                    entry.data.get(FLOW_PLANT_INFO, {}).get(FLOW_TENT_ENTITY))\n            ]\n            \n            rollback_results[\"plants_processed\"] = len(plant_entries)\n            \n            for plant_entry in plant_entries:\n                try:\n                    await self._rollback_plant_entry(plant_entry)\n                    rollback_results[\"plants_rolled_back\"] += 1\n                except Exception as e:\n                    error_msg = f\"Failed to rollback plant {plant_entry.entry_id}: {str(e)}\"\n                    rollback_results[\"errors\"].append(error_msg)\n                    _LOGGER.error(error_msg)\n            \n            rollback_results[\"completed\"] = True\n            rollback_results[\"completed_at\"] = datetime.now().isoformat()\n            \n        except Exception as e:\n            error_msg = f\"Rollback failed: {str(e)}\"\n            rollback_results[\"errors\"].append(error_msg)\n            _LOGGER.error(error_msg)\n        \n        return rollback_results\n    \n    async def _rollback_plant_entry(self, plant_entry: ConfigEntry) -> None:\n        \"\"\"Rollback a single plant entry from tent inheritance.\"\"\"\n        plant_data = dict(plant_entry.data)\n        plant_info = dict(plant_data.get(FLOW_PLANT_INFO, {}))\n        \n        # Remove tent assignment\n        plant_info.pop(FLOW_TENT_ENTITY, None)\n        plant_info.pop(FLOW_INHERIT_TENT_SENSORS, None)\n        \n        plant_data[FLOW_PLANT_INFO] = plant_info\n        \n        # Update config entry\n        self.hass.config_entries.async_update_entry(plant_entry, data=plant_data)\n        \n        # Trigger reload to apply changes\n        await self.hass.config_entries.async_reload(plant_entry.entry_id)


# Global instances\n_optimization_config: Optional[OptimizationConfig] = None\n_optimization_migrator: Optional[OptimizationMigrator] = None\n\ndef get_optimization_config(hass: HomeAssistant) -> OptimizationConfig:\n    \"\"\"Get or create the global optimization configuration.\"\"\"\n    global _optimization_config\n    if _optimization_config is None:\n        _optimization_config = OptimizationConfig(hass)\n    return _optimization_config\n\ndef get_optimization_migrator(hass: HomeAssistant) -> OptimizationMigrator:\n    \"\"\"Get or create the global optimization migrator.\"\"\"\n    global _optimization_migrator\n    if _optimization_migrator is None:\n        config_manager = get_optimization_config(hass)\n        _optimization_migrator = OptimizationMigrator(hass, config_manager)\n    return _optimization_migrator