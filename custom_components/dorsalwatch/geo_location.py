"""Platform for geo_location integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.geo_location import GeolocationEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback, async_get_current_platform
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.unit_system import METRIC_SYSTEM
from homeassistant.helpers import entity_registry as er
from homeassistant.components import recorder
from homeassistant.helpers.entity_platform import EntityPlatform

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Global tracking of entities per config entry
_ENTITY_INSTANCES = {}
_PLATFORM_INSTANCE = None


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the geo_location platform."""
    global _PLATFORM_INSTANCE
    _PLATFORM_INSTANCE = async_get_current_platform()
    
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Initialize entity tracking for this config entry
    _ENTITY_INSTANCES[config_entry.entry_id] = {}

    async def async_update_entities():
        """Update entities based on current data."""
        current_entities = _ENTITY_INSTANCES.get(config_entry.entry_id, {})
        
        if not coordinator.data:
            # Remove all entities if no data
            await _remove_all_entities(hass, config_entry, current_entities)
            return

        current_report_ids = set()
        new_entities = []

        # Get current report IDs and create entities for new ones
        for report in coordinator.data:
            if report.get("coordinate") and report.get("id"):
                report_id = report.get("id")
                current_report_ids.add(report_id)
                
                # Check if this is a new entity
                if report_id not in current_entities:
                    try:
                        coordinate_str = report.get("coordinate", "")
                        if coordinate_str and "," in coordinate_str:
                            lat_str, lon_str = coordinate_str.split(",")
                            lat = float(lat_str.strip())
                            lon = float(lon_str.strip())
                            
                            # Only create entity if coordinates are valid
                            if -90 <= lat <= 90 and -180 <= lon <= 180:
                                entity = DorsalWatchSharkSighting(coordinator, config_entry, report)
                                new_entities.append(entity)
                                current_entities[report_id] = entity
                                _LOGGER.debug(f"Creating new entity for report {report_id}")
                    except (ValueError, AttributeError):
                        _LOGGER.debug(f"Invalid coordinates for report {report_id}: {coordinate_str}")
                        continue

        # Add new entities
        if new_entities:
            async_add_entities(new_entities, update_before_add=True)

        # Remove entities that are no longer in the data
        await _remove_obsolete_entities(hass, config_entry, current_report_ids, current_entities)

    # Set up the initial entities
    await async_update_entities()

    # Register the update function to run on coordinator updates
    @callback
    def coordinator_updated():
        """Handle coordinator update."""
        hass.async_create_task(async_update_entities())

    # Listen for coordinator updates
    coordinator.async_add_listener(coordinator_updated)


async def _remove_obsolete_entities(hass: HomeAssistant, config_entry: ConfigEntry, current_report_ids: set, entity_instances: dict):
    """Remove entities that are no longer in the data."""
    entity_registry = er.async_get(hass)
    entities_to_remove = []
    
    for report_id, entity in list(entity_instances.items()):
        if report_id not in current_report_ids:
            entities_to_remove.append((report_id, entity))
    
    for report_id, entity in entities_to_remove:
        entity_id = f"geo_location.dorsalwatch_report_{report_id}"
        
        try:
            # Method 1: Remove via platform
            if _PLATFORM_INSTANCE and hasattr(_PLATFORM_INSTANCE, 'async_remove_entity'):
                await _PLATFORM_INSTANCE.async_remove_entity(entity.entity_id)
                _LOGGER.debug(f"Removed entity via platform: {entity_id}")
            else:
                # Method 2: Traditional removal
                await entity.async_remove(force_remove=True)
                _LOGGER.debug(f"Removed entity via async_remove: {entity_id}")
            
            # Remove from entity registry
            if entity_registry.async_get(entity_id):
                entity_registry.async_remove(entity_id)
                _LOGGER.debug(f"Removed entity {entity_id} from registry")
            
            # Purge from recorder database if available
            await _purge_entity_from_recorder(hass, entity_id)
            
        except Exception as e:
            _LOGGER.warning(f"Error removing entity {entity_id}: {e}")
        
        # Remove from our tracking
        entity_instances.pop(report_id, None)


async def _remove_all_entities(hass: HomeAssistant, config_entry: ConfigEntry, entity_instances: dict):
    """Remove all entities for this config entry."""
    entity_registry = er.async_get(hass)
    
    for report_id, entity in list(entity_instances.items()):
        entity_id = f"geo_location.dorsalwatch_report_{report_id}"
        
        try:
            # Method 1: Remove via platform
            if _PLATFORM_INSTANCE and hasattr(_PLATFORM_INSTANCE, 'async_remove_entity'):
                await _PLATFORM_INSTANCE.async_remove_entity(entity.entity_id)
                _LOGGER.debug(f"Removed entity via platform: {entity_id}")
            else:
                # Method 2: Traditional removal
                await entity.async_remove(force_remove=True)
                _LOGGER.debug(f"Removed entity via async_remove: {entity_id}")
            
            # Remove from entity registry
            if entity_registry.async_get(entity_id):
                entity_registry.async_remove(entity_id)
                _LOGGER.debug(f"Removed entity {entity_id} from registry")
            
            # Purge from recorder database if available
            await _purge_entity_from_recorder(hass, entity_id)
            
        except Exception as e:
            _LOGGER.warning(f"Error removing entity {entity_id}: {e}")
    
    # Clear all tracking
    entity_instances.clear()


async def _purge_entity_from_recorder(hass: HomeAssistant, entity_id: str):
    """Purge entity data from the recorder database using the service call."""
    try:
        # Use the same service call that works manually
        await hass.services.async_call(
            "recorder",
            "purge_entities",
            {
                "keep_days": 0,
                "entity_id": [entity_id]
            }
        )
        _LOGGER.debug(f"Called recorder.purge_entities for {entity_id}")
    except Exception as e:
        _LOGGER.debug(f"Could not purge recorder data for {entity_id}: {e}")


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload geo_location entities."""
    # Clean up all entities and tracking when integration is unloaded
    current_entities = _ENTITY_INSTANCES.get(config_entry.entry_id, {})
    await _remove_all_entities(hass, config_entry, current_entities)
    _ENTITY_INSTANCES.pop(config_entry.entry_id, None)
    return True


class DorsalWatchSharkSighting(CoordinatorEntity, GeolocationEvent):
    """Geo location entity for individual shark sightings."""

    def __init__(self, coordinator, config_entry, report_data):
        """Initialize the geo location entity."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._report_data = report_data
        
        # Create unique identifier and entity ID based on report ID
        report_id = report_data.get("id")
        self._attr_unique_id = f"{config_entry.entry_id}_sighting_{report_id}"
        self._attr_source = DOMAIN  # Required for GeolocationEvent
        
        # Set entity ID to use report ID
        self.entity_id = f"geo_location.dorsalwatch_report_{report_id}"
        
        # Create a friendly name
        location = report_data.get("location", "Unknown Location")
        shark_type = report_data.get("typeOfShark", "Unknown")
        encounter_type = report_data.get("typeOfEncounter", "Sighting")
        
        if shark_type and shark_type != "Unknown":
            self._attr_name = f"{shark_type} {location}"
        else:
            self._attr_name = f"Shark {encounter_type} {location}"
        
        # Parse and store coordinates
        coordinate_str = report_data.get("coordinate", "")
        if coordinate_str and "," in coordinate_str:
            try:
                lat_str, lon_str = coordinate_str.split(",")
                self._latitude = float(lat_str.strip())
                self._longitude = float(lon_str.strip())
            except (ValueError, AttributeError):
                self._latitude = None
                self._longitude = None
        else:
            self._latitude = None
            self._longitude = None

        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"DorsalWatch {config_entry.data['country']}",
            "manufacturer": "DorsalWatch",
            "model": "Shark Sightings",
        }

    @property
    def latitude(self) -> float | None:
        """Return latitude."""
        return self._latitude

    @property
    def longitude(self) -> float | None:
        """Return longitude."""
        return self._longitude

    @property
    def distance(self) -> float | None:
        """Return distance from home in km."""
        if not self.hass.config.latitude or not self.hass.config.longitude:
            return None
        if not self._latitude or not self._longitude:
            return None
            
        # Calculate distance from home coordinates
        from math import radians, cos, sin, asin, sqrt
        
        home_lat = radians(self.hass.config.latitude)
        home_lon = radians(self.hass.config.longitude)
        sighting_lat = radians(self._latitude)
        sighting_lon = radians(self._longitude)
        
        # Haversine formula
        dlat = sighting_lat - home_lat
        dlon = sighting_lon - home_lon
        a = sin(dlat/2)**2 + cos(home_lat) * cos(sighting_lat) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        
        return round(c * r, 1)

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        if self.hass.config.units is METRIC_SYSTEM:
            return "km"
        return "mi"

    @property
    def icon(self) -> str:
        """Return the icon for the geo location."""
        encounter_type = self._report_data.get("typeOfEncounter", "").lower()
        
        if "tag" in encounter_type:
            return "mdi:shark-fin"
        elif "aerial" in encounter_type or "drone" in encounter_type:
            return "mdi:shark"
        else:
            return "mdi:shark"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        # Find current report data from coordinator (in case it was updated)
        current_report = None
        if self.coordinator.data:
            for report in self.coordinator.data:
                if report.get("id") == self._report_data.get("id"):
                    current_report = report
                    break
        
        if not current_report:
            current_report = self._report_data
        
        attributes = {}
        
        # Add important report fields as attributes
        for key, value in current_report.items():
            if key not in ["coordinate"]:  # Skip coordinate as it's already used for position
                # Convert keys to lowercase with underscores for consistency
                attr_key = key.lower().replace(' ', '_').replace('-', '_')
                attributes[attr_key] = value
        
        # Add some computed attributes
        attributes["country"] = self._config_entry.data["country"]
        if self._config_entry.data.get("state"):
            attributes["configured_state"] = self._config_entry.data["state"]
        
        # Add coordinate string for reference
        attributes["coordinates"] = current_report.get("coordinate")
            
        return attributes

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Check if this entity's report ID is still in the current data
        if self.coordinator.data:
            current_report_ids = {report.get("id") for report in self.coordinator.data if report.get("id")}
            report_id = self._report_data.get("id")
            if report_id not in current_report_ids:
                return False
        
        return (
            self.coordinator.last_update_success and 
            self._latitude is not None and 
            self._longitude is not None
        )