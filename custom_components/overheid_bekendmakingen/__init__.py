import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Overheid Bekendmakingen component."""
    _LOGGER.debug("Setting up Overheid Bekendmakingen component")
    hass.data[DOMAIN] = {}
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Overheid Bekendmakingen from a config entry."""
    _LOGGER.debug("Setting up Overheid Bekendmakingen from config entry: %s", entry.data)
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Setup the sensor platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Overheid Bekendmakingen config entry: %s", entry.entry_id)
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
