"""Config flow for Overheid Bekendmakingen integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    NAME,
    CONF_RADIUS,
    DEFAULT_RADIUS,
    CONF_MAP_DISPLAY_DAYS,
    CONF_ARCHIVE_DAYS,
    DEFAULT_MAP_DISPLAY_DAYS,
    DEFAULT_ARCHIVE_DAYS,
)

_LOGGER = logging.getLogger(__name__)

class OverheidBekendmakingenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Overheid Bekendmakingen."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate coordinates if manual input is checked
            manual_coords = user_input.get("manual_coordinates", False)
            if manual_coords:
                if not user_input.get("latitude") or not user_input.get("longitude"):
                    errors["base"] = "invalid_coordinates"
                else:
                    # Additional validation for coordinate ranges
                    try:
                        lat = float(user_input["latitude"])
                        lon = float(user_input["longitude"])
                        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                            errors["base"] = "invalid_coordinates"
                    except (ValueError, TypeError):
                        errors["base"] = "invalid_coordinates"

            if not errors:
                return self.async_create_entry(
                    title=NAME, 
                    data=user_input
                )

        # Get default coordinates from Home Assistant configuration
        latitude = round(self.hass.config.latitude, 5)
        longitude = round(self.hass.config.longitude, 5)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Optional("manual_coordinates", default=False): cv.boolean,
                vol.Optional("latitude", default=latitude): cv.latitude,
                vol.Optional("longitude", default=longitude): cv.longitude,
                vol.Optional(CONF_RADIUS, default=DEFAULT_RADIUS): vol.All(
                    vol.Coerce(int), vol.Range(min=1000, max=50000)
                ),
                vol.Optional("update_interval_hours", default=6): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=24)
                ),
                vol.Optional("debug", default=False): cv.boolean,
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OverheidBekendmakingenOptionsFlow(config_entry)


class OverheidBekendmakingenOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Overheid Bekendmakingen."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_RADIUS, 
                    default=self.config_entry.options.get(CONF_RADIUS, DEFAULT_RADIUS)
                ): vol.All(vol.Coerce(int), vol.Range(min=100, max=10000)),
                vol.Optional(
                    "update_interval_hours", 
                    default=self.config_entry.options.get("update_interval_hours", 12)
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=24)),
                vol.Optional(
                    CONF_MAP_DISPLAY_DAYS,
                    default=self.config_entry.options.get(CONF_MAP_DISPLAY_DAYS, DEFAULT_MAP_DISPLAY_DAYS)
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=365)),
                vol.Optional(
                    CONF_ARCHIVE_DAYS,
                    default=self.config_entry.options.get(CONF_ARCHIVE_DAYS, DEFAULT_ARCHIVE_DAYS)
                ): vol.All(vol.Coerce(int), vol.Range(min=7, max=365)),
                vol.Optional(
                    "debug", 
                    default=self.config_entry.options.get("debug", False)
                ): bool,
            })
        )
