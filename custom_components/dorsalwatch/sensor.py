"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Create sensors
    entities = [
        DorsalWatchReportCountSensor(coordinator, config_entry),
        DorsalWatchLatestReportSensor(coordinator, config_entry),
    ]

    async_add_entities(entities, update_before_add=True)


class DorsalWatchSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for DorsalWatch sensors."""

    def __init__(self, coordinator, config_entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"DorsalWatch {config_entry.data['country']}",
            "manufacturer": "DorsalWatch",
            "model": "API Integration",
        }


class DorsalWatchReportCountSensor(DorsalWatchSensorBase):
    """Sensor for current reports with all report data as attributes."""

    def __init__(self, coordinator, config_entry):
        """Initialize the sensor."""
        super().__init__(coordinator, config_entry)
        self._attr_name = f"DorsalWatch {config_entry.data['country']} Current Reports"
        self._attr_unique_id = f"{config_entry.entry_id}_current_reports"
        self._attr_icon = "mdi:shark"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data:
            return len(self.coordinator.data)
        return 0

    @property
    def extra_state_attributes(self):
        """Return additional state attributes with all reports data."""
        if not self.coordinator.data:
            return {}

        attributes = {
            "country": self._config_entry.data["country"],
            "state": self._config_entry.data.get("state"),
            "reports": self.coordinator.data  # Include all reports as attribute
        }
        
        return attributes


class DorsalWatchLatestReportSensor(DorsalWatchSensorBase):
    """Sensor for the latest report."""

    def __init__(self, coordinator, config_entry):
        """Initialize the sensor."""
        super().__init__(coordinator, config_entry)
        self._attr_name = f"DorsalWatch {config_entry.data['country']} Latest Report"
        self._attr_unique_id = f"{config_entry.entry_id}_latest_report"
        self._attr_icon = "mdi:shark-fin"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data:
            return len(self.coordinator.data)
        return 0

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and len(self.coordinator.data) > 0:
            latest_report = self.coordinator.data[0]
            return latest_report.get("formattedReportTime", "Unknown")
        return "No reports"

    @property
    def extra_state_attributes(self):
        """Return additional state attributes."""
        if not self.coordinator.data or len(self.coordinator.data) == 0:
            return {}

        latest_report = self.coordinator.data[0]
        
        # Extract common fields that might be in the report
        attributes = {}
        
        # Add all report fields as attributes
        for key, value in latest_report.items():
            # Convert keys to lowercase with underscores for consistency
            attr_key = key.lower().replace(' ', '_').replace('-', '_')
            attributes[attr_key] = value

        return attributes