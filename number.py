"""Number platform voor Overheid Bekendmakingen - Aanpasbare waarden."""
import logging
from homeassistant.components.number import NumberEntity
from homeassistant.const import UnitOfLength, UnitOfTime

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class RangeNumber(NumberEntity):
    """Number entity voor zoekbereik aanpassing."""

    def __init__(self, main_sensor):
        """Initialize the number entity."""
        self._main_sensor = main_sensor
        self._attr_name = "Bekendmakingen Zoekbereik"
        self._attr_unique_id = f"{DOMAIN}_{main_sensor.unique_id}_range_setting"
        self._attr_icon = "mdi:map-marker-radius"
        self._attr_native_min_value = 500
        self._attr_native_max_value = 25000
        self._attr_native_step = 500
        self._attr_native_unit_of_measurement = UnitOfLength.METERS
        self._attr_mode = "slider"

    @property
    def native_value(self):
        """Return current range value in meters."""
        return int(self._main_sensor._range_km * 1000)

    async def async_set_native_value(self, value: float) -> None:
        """Update the range value."""
        new_range_km = value / 1000.0
        self._main_sensor._range_km = new_range_km
        
        _LOGGER.info(f"Range updated to {value}m ({new_range_km}km)")
        
        # Trigger update with new range
        await self._main_sensor.async_update()
        
    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._main_sensor.unique_id)},
            "name": "Overheid Bekendmakingen",
            "manufacturer": "Overheid",
            "model": "Bekendmakingen v2.0",
        }


class IntervalNumber(NumberEntity):
    """Number entity voor update interval aanpassing."""

    def __init__(self, main_sensor):
        """Initialize the number entity."""
        self._main_sensor = main_sensor
        self._attr_name = "Bekendmakingen Update Interval"
        self._attr_unique_id = f"{DOMAIN}_{main_sensor.unique_id}_interval_setting"
        self._attr_icon = "mdi:timer-cog"
        self._attr_native_min_value = 1
        self._attr_native_max_value = 24
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = UnitOfTime.HOURS
        self._attr_mode = "slider"

    @property
    def native_value(self):
        """Return current interval value in hours."""
        return self._main_sensor._interval_hours

    async def async_set_native_value(self, value: float) -> None:
        """Update the interval value."""
        self._main_sensor._interval_hours = value
        _LOGGER.info(f"Update interval changed to {value} hours")
        
    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._main_sensor.unique_id)},
            "name": "Overheid Bekendmakingen",
            "manufacturer": "Overheid", 
            "model": "Bekendmakingen v2.0",
        }


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up number entities from config entry."""
    _LOGGER.info("Setting up Overheid Bekendmakingen number entities")
    
    # Get sensor data 
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        sensor_data = hass.data[DOMAIN][entry.entry_id]
        main_sensor = sensor_data.get('main_sensor')
        
        if main_sensor:
            # Create number entities
            numbers = [
                RangeNumber(main_sensor),
                IntervalNumber(main_sensor)
            ]
            
            async_add_entities(numbers, update_before_add=False)
            _LOGGER.info(f"Added {len(numbers)} number entities")
        else:
            _LOGGER.warning("Geen main sensor gevonden voor number setup")
    else:
        _LOGGER.warning("Sensor data niet beschikbaar voor number setup")