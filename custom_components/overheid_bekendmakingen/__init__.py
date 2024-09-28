DOMAIN = "overheid_bekendmakingen"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Overheid Bekendmakingen from a config entry."""
    try:
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = entry.data

        # Add sensor or other entity
        await hass.config_entries.async_forward_entry_setup(entry, "sensor")
        return True
    except Exception as e:
        # Log the error for debugging
        hass.logger.error(f"Error setting up entry for {DOMAIN}: {e}")
        return False
