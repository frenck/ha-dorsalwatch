"""Config flow for DorsalWatch integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    CONF_COUNTRY,
    CONF_STATE,
    CONF_PUBLIC_KEY,
    CONF_PAGE_SIZE,
    CONF_TIME_RANGE,
    DEFAULT_COUNTRY,
    DEFAULT_PAGE_SIZE,
    DEFAULT_TIME_RANGE,
    COUNTRIES
)

from .api import DorsalWatchAPI

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for DorsalWatch."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await self._validate_input(user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"DorsalWatch {user_input[CONF_COUNTRY]}", data=user_input
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_COUNTRY, default=DEFAULT_COUNTRY): vol.In(COUNTRIES),
                vol.Required(CONF_PUBLIC_KEY): str,
                vol.Optional(CONF_STATE): str,
                vol.Optional(CONF_PAGE_SIZE, default=DEFAULT_PAGE_SIZE): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=100)
                ),
                vol.Optional(CONF_TIME_RANGE, default=DEFAULT_TIME_RANGE): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=365)
                ),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def _validate_input(self, data: dict[str, Any]) -> None:
        """Validate the user input allows us to connect."""
        api = DorsalWatchAPI(
            country=data[CONF_COUNTRY],
            state=data.get(CONF_STATE),
            public_key=data[CONF_PUBLIC_KEY],
            page_size=data.get(CONF_PAGE_SIZE, DEFAULT_PAGE_SIZE),
            time_range=data.get(CONF_TIME_RANGE, DEFAULT_TIME_RANGE),
        )

        # Test the API connection
        try:
            await self.hass.async_add_executor_job(api.get_reports)
        except Exception as exc:
            _LOGGER.error("Cannot connect to DorsalWatch API: %s", exc)
            raise CannotConnect from exc


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""