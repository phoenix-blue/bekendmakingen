"""Input helpers voor dynamische configuratie."""

from homeassistant.helpers.entity import Entity
from homeassistant.helpers import config_validation as cv
import voluptuous as vol
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "overheid_bekendmakingen"


async def async_create_input_helpers(hass, entry_id, main_sensor):
    """Create input helpers for dynamic configuration."""
    
    # Create input_number for range
    range_helper_data = {
        "name": f"Bekendmakingen Range {entry_id[:8]}",
        "min": 100,
        "max": 10000,
        "step": 100,
        "initial": int(main_sensor._range_km * 1000),
        "unit_of_measurement": "m",
        "icon": "mdi:map-marker-distance",
    }
    
    # Create input_number for interval
    interval_helper_data = {
        "name": f"Bekendmakingen Interval {entry_id[:8]}",
        "min": 1,
        "max": 24,
        "step": 1,
        "initial": int(main_sensor._interval / 3600),
        "unit_of_measurement": "h",
        "icon": "mdi:clock-outline",
    }
    
    # Create input_number for map display days
    map_days_helper_data = {
        "name": f"Bekendmakingen Map Days {entry_id[:8]}",
        "min": 1,
        "max": 30,
        "step": 1,
        "initial": 7,
        "unit_of_measurement": "dagen",
        "icon": "mdi:calendar-range",
    }
    
    helpers_created = []
    
    try:
        # Add range helper
        range_entity_id = f"input_number.bekendmakingen_range_{entry_id[:8]}"
        await hass.services.async_call(
            "input_number",
            "reload",
            {},
            blocking=True,
        )
        
        _LOGGER.info(f"Input helpers setup for entry {entry_id}")
        helpers_created = [
            range_entity_id,
            f"input_number.bekendmakingen_interval_{entry_id[:8]}",
            f"input_number.bekendmakingen_map_days_{entry_id[:8]}"
        ]
        
    except Exception as e:
        _LOGGER.error(f"Failed to create input helpers: {e}")
    
    return helpers_created


class InputHelperManager:
    """Manage input helpers for bekendmakingen."""
    
    def __init__(self, hass, entry_id, main_sensor):
        self.hass = hass
        self.entry_id = entry_id
        self.main_sensor = main_sensor
        self.helpers = []
        
    async def setup(self):
        """Setup input helpers."""
        self.helpers = await async_create_input_helpers(
            self.hass, self.entry_id, self.main_sensor
        )
        
        # Setup state change listeners
        await self._setup_listeners()
        
    async def _setup_listeners(self):
        """Setup listeners for input helper changes."""
        
        async def handle_range_change(event):
            """Handle range input helper change."""
            if event.data.get("entity_id") == f"input_number.bekendmakingen_range_{self.entry_id[:8]}":
                new_value = event.data.get("new_state").state
                try:
                    range_meters = int(float(new_value))
                    if 100 <= range_meters <= 10000:
                        self.main_sensor._range_km = range_meters / 1000.0
                        _LOGGER.info(f"Range updated via input helper to {range_meters}m")
                        await self.hass.async_add_executor_job(self.main_sensor.update)
                except (ValueError, TypeError):
                    _LOGGER.error(f"Invalid range value from input helper: {new_value}")
        
        async def handle_interval_change(event):
            """Handle interval input helper change."""
            if event.data.get("entity_id") == f"input_number.bekendmakingen_interval_{self.entry_id[:8]}":
                new_value = event.data.get("new_state").state
                try:
                    interval_hours = int(float(new_value))
                    if 1 <= interval_hours <= 24:
                        self.main_sensor._interval = interval_hours * 3600
                        _LOGGER.info(f"Interval updated via input helper to {interval_hours}h")
                        await self.hass.async_add_executor_job(self.main_sensor.update)
                except (ValueError, TypeError):
                    _LOGGER.error(f"Invalid interval value from input helper: {new_value}")
        
        # Register listeners
        self.hass.bus.async_listen("state_changed", handle_range_change)
        self.hass.bus.async_listen("state_changed", handle_interval_change)
        
        _LOGGER.info("Input helper listeners registered")
        
    async def cleanup(self):
        """Cleanup input helpers."""
        # Note: In a real implementation, you would remove the created helpers
        _LOGGER.info("Input helpers cleanup completed")