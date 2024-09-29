import logging
import xml.etree.ElementTree as ET
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Overheid Bekendmakingen component."""
    _LOGGER.debug("Setting up Overheid Bekendmakingen component")
    
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
        _LOGGER.debug(f"{DOMAIN} not found in hass.data, initializing.")
    else:
        _LOGGER.debug(f"{DOMAIN} already in hass.data, skipping initialization.")
    
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Overheid Bekendmakingen from a config entry."""
    _LOGGER.debug(f"Setting up Overheid Bekendmakingen from config entry: {entry.data}")

    # Controleren of de entry al bestaat
    if entry.entry_id in hass.data.get(DOMAIN, {}):
        _LOGGER.warning(f"Config entry {entry.entry_id} already set up!")
        return False

    # Config entry opslaan
    hass.data[DOMAIN][entry.entry_id] = entry.data
    _LOGGER.debug(f"Stored entry data: {hass.data[DOMAIN][entry.entry_id]}")
    
    try:
        # Forward de setup naar het sensorplatform
        _LOGGER.debug("Forwarding entry setup to sensor platform.")
        await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
        _LOGGER.debug("Sensor platform setup completed.")
        
    except Exception as e:
        _LOGGER.error(f"Error setting up sensor platform: {e}")
        return False

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry and remove associated sensors."""
    _LOGGER.debug(f"Unloading Overheid Bekendmakingen config entry: {entry.entry_id}")

    try:
        # Forward de unload naar het sensorplatform
        _LOGGER.debug("Forwarding entry unload to sensor platform.")
        await hass.config_entries.async_forward_entry_unload(entry, "sensor")
        _LOGGER.debug("Sensor platform unload completed.")
    except Exception as e:
        _LOGGER.error(f"Error unloading sensor platform: {e}")
        return False

    # Verwijder de opgeslagen config entry data
    if entry.entry_id in hass.data[DOMAIN]:
        _LOGGER.debug(f"Removing entry data for {entry.entry_id} from hass.data.")
        hass.data[DOMAIN].pop(entry.entry_id)
    else:
        _LOGGER.warning(f"Entry {entry.entry_id} not found in hass.data, cannot remove.")
    
    return True
