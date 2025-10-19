import logging
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
    """Set up Overheid Bekendmakingen from a config entry - Versie 2.0."""
    _LOGGER.info(f"Setting up Overheid Bekendmakingen 2.0 from config entry: {entry.entry_id}")
    
    # Store the config entry data as a mutable dict
    hass.data[DOMAIN][entry.entry_id] = dict(entry.data)
    _LOGGER.debug(f"Stored entry data: {hass.data[DOMAIN][entry.entry_id]}")

    try:
        # Forward the setup to platforms (added geo_location for map display)
        _LOGGER.debug("Forwarding entry setup to platforms.")
        await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "button", "number", "geo_location"])
        _LOGGER.debug("Platforms setup completed.")
        
        # Register services voor versie 2.0
        await _register_services(hass)
        
    except Exception as e:
        _LOGGER.error(f"Error setting up sensor platform: {e}")
        return False

    return True

async def _register_services(hass: HomeAssistant):
    """Register services voor handmatige updates en configuratie."""
    
    async def handle_manual_update(call):
        """Handle manual update service call."""
        entity_id = call.data.get("entity_id")
        force = call.data.get("force", False)
        
        _LOGGER.info(f"Manual update service called for {entity_id}, force={force}")
        
        # Vuur een event dat de sensor kan oppikken
        hass.bus.async_fire("overheid_bekendmakingen_manual_update", {
            "entity_id": entity_id,
            "force": force
        })
        
    async def handle_refresh_all(call):
        """Handle refresh all sensors service call."""
        clear_cache = call.data.get("clear_cache", False)
        
        _LOGGER.info(f"Refresh all service called, clear_cache={clear_cache}")
        
        # Vuur een event voor alle sensors
        hass.bus.async_fire("overheid_bekendmakingen_refresh_all", {
            "clear_cache": clear_cache
        })
    
    # Registreer de services
    hass.services.async_register(DOMAIN, "manual_update", handle_manual_update)
    hass.services.async_register(DOMAIN, "refresh_all", handle_refresh_all)
    
    _LOGGER.info("Overheid Bekendmakingen 2.0 services geregistreerd")

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug(f"Unloading Overheid Bekendmakingen config entry: {entry.entry_id}")

    try:
        # Forward the unload to platforms
        _LOGGER.debug("Forwarding entry unload to platforms.")
        unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor", "button", "number", "geo_location"])
        _LOGGER.debug("Platforms unload completed.")
        
        # Stop geo manager if exists
        if entry.entry_id in hass.data[DOMAIN]:
            geo_manager = hass.data[DOMAIN][entry.entry_id].get('geo_manager')
            if geo_manager:
                await geo_manager.async_stop()
        return unload_ok
    except Exception as e:
        _LOGGER.error(f"Error unloading platforms: {e}")
        return False

    # Remove the stored config entry data
    if entry.entry_id in hass.data[DOMAIN]:
        _LOGGER.debug(f"Removing entry data for {entry.entry_id} from hass.data.")
        hass.data[DOMAIN].pop(entry.entry_id)
    else:
        _LOGGER.warning(f"Entry {entry.entry_id} not found in hass.data, cannot remove.")
    
    return True
