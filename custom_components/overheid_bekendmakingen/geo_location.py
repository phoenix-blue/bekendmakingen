"""Map integratie voor Overheid Bekendmakingen."""

from homeassistant.components.geo_location import GeolocationEvent
from homeassistant.const import UnitOfLength
from homeassistant.util import dt as dt_util
from datetime import datetime, timedelta
import logging

_LOGGER = logging.getLogger(__name__)

class BekendmakingMapMarker(GeolocationEvent):
    """Map marker voor bekendmakingen."""

    def __init__(self, hass, bekendmaking_data, main_sensor, display_days=7):
        """Initialize the map marker."""
        self._hass = hass
        self._data = bekendmaking_data
        self._main_sensor = main_sensor
        self._display_days = display_days
        
        # Generate unique ID
        self._unique_id = f"bekendmaking_map_{bekendmaking_data.get('identifier', 'unknown')}"
        
        # Use main sensor coordinates with small random offset for visibility
        self._latitude = main_sensor._latitude + (hash(self._unique_id) % 200 - 100) / 100000
        self._longitude = main_sensor._longitude + (hash(self._unique_id) % 200 - 100) / 100000
        
    @property
    def unique_id(self):
        """Return unique ID."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the entity."""
        title = self._data.get('title', 'Bekendmaking')
        return f"📄 {title[:30]}{'...' if len(title) > 30 else ''}"

    @property
    def latitude(self):
        """Return latitude."""
        return self._latitude

    @property
    def longitude(self):
        """Return longitude."""
        return self._longitude

    @property
    def distance(self):
        """Return distance from home."""
        # Calculate distance from main sensor coordinates
        return 0.1  # km (placeholder)

    @property
    def unit_of_measurement(self):
        """Return unit of measurement."""
        return UnitOfLength.KILOMETERS

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        return {
            'title': self._data.get('title', 'Geen titel'),
            'url': self._data.get('url', ''),
            'publication_date': self._data.get('date', 'Onbekend'),
            'source': 'Overheid.nl',
            'type': 'bekendmaking',
            'display_days': self._display_days,
        }

    @property
    def device_info(self):
        """Return device info to group with main sensor."""
        return self._main_sensor.device_info

    def should_display(self):
        """Check if this marker should be displayed based on age."""
        try:
            # For now, always display (would need proper date parsing from API)
            return True
        except:
            return True


async def async_setup_map_markers(hass, main_sensor, display_days=7):
    """Setup map markers for bekendmakingen."""
    markers = []
    
    if not main_sensor._data:
        return markers
    
    for record in main_sensor._data[:10]:  # Limit to 10 markers
        marker = BekendmakingMapMarker(hass, record, main_sensor, display_days)
        if marker.should_display():
            markers.append(marker)
    
    _LOGGER.info(f"Created {len(markers)} map markers for bekendmakingen")
    return markers