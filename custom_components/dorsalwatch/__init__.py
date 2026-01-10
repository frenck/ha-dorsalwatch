"""The DorsalWatch integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .api import DorsalWatchAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.GEO_LOCATION]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up DorsalWatch from a config entry."""
    api = DorsalWatchAPI(
        country=entry.data["country"],
        state=entry.data.get("state"),
        public_key=entry.data["public_key"],
        page_size=entry.data.get("page_size", 12),
        time_range=entry.data.get("time_range", 0),
    )

    coordinator = DorsalWatchCoordinator(hass, api)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class DorsalWatchCoordinator(DataUpdateCoordinator):
    """DorsalWatch data update coordinator."""

    def __init__(self, hass: HomeAssistant, api: DorsalWatchAPI) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self):
        """Fetch data from DorsalWatch API."""
        return await self.hass.async_add_executor_job(self.api.get_reports)