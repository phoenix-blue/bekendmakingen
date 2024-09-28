import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from .const import DOMAIN

class OverheidBekendmakingenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Overheid bekendmakingen."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        # Get the default coordinates from Home Assistant and round them.
        latitude = round(self.hass.config.latitude, 5)
        longitude = round(self.hass.config.longitude, 5)

        if user_input is not None:
            # Validate if manual input is checked.
            if user_input["manual_coordinates"]:
                if not user_input["latitude"] or not user_input["longitude"]:
                    errors["base"] = "invalid_coordinates"

            return self.async_create_entry(title="Overheid bekendmakingen", data=user_input)

        # Show the configuration form.
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Optional("manual_coordinates", default=False): cv.boolean,
                vol.Optional("latitude", default=latitude): cv.latitude,
                vol.Optional("longitude", default=longitude): cv.longitude,
                vol.Optional("range_km", default=0.5): vol.Coerce(float),  # Range in kilometers
                vol.Optional("update_interval_hours", default=12): vol.Coerce(int),  # Update interval in hours
                vol.Optional("debug", default=False): cv.boolean,  # Add the debug option
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OverheidBekendmakingenOptionsFlow(config_entry)


class OverheidBekendmakingenOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Overheid bekendmakingen."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("range_km", default=self.config_entry.options.get("range_km", 0.5)): float,
                vol.Optional("update_interval_hours", default=self.config_entry.options.get("update_interval_hours", 12)): int,
                vol.Optional("debug", default=self.config_entry.options.get("debug", False)): bool,  # Add the debug option
            })
        )

