"""Button platform voor Overheid Bekendmakingen - Versie 2.0."""
import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import Entity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ManualUpdateButton(ButtonEntity):
    """Button voor handmatige update van bekendmakingen."""

    def __init__(self, hass, name, bekendmakingen_sensor):
        """Initialize the button."""
        self.hass = hass
        self._name = f"{name} Manual Update"
        self._bekendmakingen_sensor = bekendmakingen_sensor
        self._unique_id = f"{bekendmakingen_sensor.unique_id}_manual_update"

    @property
    def name(self):
        """Return the name of the button."""
        return self._name

    @property
    def unique_id(self):
        """Return unique ID."""
        return self._unique_id

    @property
    def device_info(self):
        """Return device info to group with main sensor."""
        return self._bekendmakingen_sensor.device_info

    @property
    def icon(self):
        """Return the icon for the button."""
        return "mdi:refresh"

    @property
    def available(self):
        """Return if button is available."""
        return self._bekendmakingen_sensor.available

    async def async_press(self):
        """Handle the button press."""
        _LOGGER.info(f"Manual update button pressed for {self._name}")
        
        # Trigger manual update
        await self._bekendmakingen_sensor.async_manual_update()
        
        # Fire event for automation triggers
        self.hass.bus.fire("overheid_bekendmakingen_manual_update_pressed", {
            "entity_id": self._bekendmakingen_sensor.entity_id,
            "button_name": self._name
        })


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up button entities."""
    _LOGGER.info("Setting up Overheid Bekendmakingen button entities")
    
    # Get the main sensor from stored data
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        sensor_data = hass.data[DOMAIN][entry.entry_id]
        main_sensor = sensor_data.get('main_sensor')
        config = sensor_data.get('config', {})
        
        if main_sensor:
            name = config.get("name", "Overheid Bekendmakingen")
            
            # Create manual update button
            manual_update_button = ManualUpdateButton(hass, name, main_sensor)
            
            async_add_entities([manual_update_button], update_before_add=False)
            _LOGGER.info("Manual update button toegevoegd")
        else:
            _LOGGER.warning("Kon main sensor niet vinden voor button setup")
    else:
        _LOGGER.warning("Sensor data niet beschikbaar voor button setup")