"""Geo Location platform voor Overheid Bekendmakingen - Kaartweergave."""
import logging
from homeassistant.components.geo_location import GeolocationEvent
from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util.unit_system import METRIC_SYSTEM
from homeassistant.util import slugify

from .const import (
    DOMAIN,
    DEFAULT_MUNICIPALITY,
    get_icon_for_type,
    MAP_COLOR,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up geo location entities from config entry."""
    _LOGGER.info("Setting up Overheid Bekendmakingen geo location entities")
    
    # Wait for sensor to be set up first
    import asyncio
    max_wait = 30  # seconds
    waited = 0
    
    while waited < max_wait:
        if (DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN] and 
            'main_sensor' in hass.data[DOMAIN][entry.entry_id]):
            break
        await asyncio.sleep(1)
        waited += 1
    
    # Get sensor data 
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        sensor_data = hass.data[DOMAIN][entry.entry_id]
        main_sensor = sensor_data.get('main_sensor')
        
        if main_sensor and hasattr(main_sensor, 'entity_id') and main_sensor.entity_id:
            # Create geo location manager
            manager = BekendmakingenGeoManager(hass, entry, async_add_entities, main_sensor)
            await manager.async_start()
            
            # Store manager for cleanup
            hass.data[DOMAIN][entry.entry_id]['geo_manager'] = manager
            _LOGGER.info("Geo location manager gestart")
        else:
            _LOGGER.warning(f"Geen main sensor gevonden voor geo location setup. main_sensor: {main_sensor}")
            if main_sensor:
                _LOGGER.warning(f"main_sensor attributes: entity_id={getattr(main_sensor, 'entity_id', 'MISSING')}")
    else:
        _LOGGER.warning("Sensor data niet beschikbaar na wachten")

class BekendmakingenGeoManager:
    """Manager for geo location entities."""
    
    def __init__(self, hass, entry, async_add_entities, main_sensor):
        """Initialize the manager."""
        self._hass = hass
        self._entry = entry
        self._async_add_entities = async_add_entities
        self._main_sensor = main_sensor
        self._entities = {}
        self._unsub_state_change = None
        
    async def async_start(self):
        """Start monitoring the main sensor."""
        # Track state changes of the main sensor
        self._unsub_state_change = async_track_state_change_event(
            self._hass, 
            [self._main_sensor.entity_id],
            self._sensor_state_changed
        )
        
        # Initial update
        await self._update_geo_entities()
        
    async def async_stop(self):
        """Stop monitoring and cleanup."""
        if self._unsub_state_change:
            self._unsub_state_change()
            
        # Remove all geo entities
        for entity in list(self._entities.values()):
            await entity.async_remove()
        self._entities.clear()
        
    async def _sensor_state_changed(self, event):
        """Handle sensor state change event."""
        await self._update_geo_entities()
        
    async def _update_geo_entities(self):
        """Update geo location entities based on sensor data."""
        if not self._main_sensor.available:
            return
            
        announcements = self._main_sensor._data or []
        current_entity_ids = set()
        
        for announcement in announcements:
            # Only show announcements with location data
            locations = announcement.get("location", [])
            if not locations:
                # Use Home Assistant location as fallback
                locations = [f"{self.hass.config.latitude} {self.hass.config.longitude}"]
                
            for i, location_str in enumerate(locations):
                try:
                    # Parse coordinates - format should be "lng lat" or "lat lng"
                    coords = location_str.strip().split()
                    if len(coords) >= 2:
                        coord1, coord2 = float(coords[0]), float(coords[1])
                        
                        # Determine which is lat/lng based on ranges
                        # Netherlands: lat ~51-53, lng ~3-7
                        if 50 <= coord1 <= 54 and 3 <= coord2 <= 8:
                            lat, lng = coord1, coord2
                        elif 50 <= coord2 <= 54 and 3 <= coord1 <= 8:
                            lat, lng = coord2, coord1
                        else:
                            # Use Home Assistant location if outside Netherlands
                            _LOGGER.warning(f"Invalid coordinates {location_str}, using HA location")
                            lat = float(self.hass.config.latitude)
                            lng = float(self.hass.config.longitude)
                    else:
                        continue
                    
                    # Create unique entity ID
                    announcement_id = self._get_announcement_id(announcement)
                    entity_id = f"{announcement_id}_{i}" if len(locations) > 1 else announcement_id
                    current_entity_ids.add(entity_id)
                    
                    # Create or update entity
                    if entity_id not in self._entities:
                        entity = BekendmakingenGeoEntity(
                            entity_id, announcement, lat, lng, self._main_sensor
                        )
                        self._entities[entity_id] = entity
                        self._async_add_entities([entity])
                    else:
                        # Update existing entity
                        self._entities[entity_id].update_announcement(announcement, lat, lng)
                        
                except (ValueError, IndexError) as e:
                    _LOGGER.debug(f"Invalid location format: {location_str}, error: {e}")
                    continue
                    
        # Remove entities that are no longer in the data
        entities_to_remove = set(self._entities.keys()) - current_entity_ids
        for entity_id in entities_to_remove:
            entity = self._entities.pop(entity_id)
            await entity.async_remove()
            
    def _get_announcement_id(self, announcement):
        """Generate a unique ID for an announcement."""
        title = announcement.get("title", "unknown")
        date = announcement.get("date", "")
        return slugify(f"{title}_{date}")[:50]  # Limit length

class BekendmakingenGeoEntity(GeolocationEvent):
    """Geo location entity for a bekendmaking."""
    
    def __init__(self, entity_id, announcement, latitude, longitude, main_sensor):
        """Initialize the entity."""
        super().__init__()
        self._entity_id = f"{DOMAIN}.{entity_id}"
        self._announcement = announcement
        self._latitude = latitude
        self._longitude = longitude
        self._main_sensor = main_sensor
        self._attr_should_poll = False
        
        # Set icon immediately based on announcement type
        title = announcement.get("title", "")
        announcement_type = announcement.get("type", "")
        self._attr_icon = get_icon_for_type(title, announcement_type)
        
    @property
    def entity_id(self):
        """Return entity ID."""
        return self._entity_id
        
    @property
    def name(self):
        """Return the name of the entity."""
        title = self._announcement.get("title", "Bekendmaking")
        return title[:50]  # Limit length for map display
        
    @property
    def latitude(self):
        """Return latitude."""
        return self._latitude
        
    @property
    def longitude(self):
        """Return longitude."""
        return self._longitude
        
    @property
    def source(self):
        """Return source of the event."""
        return DOMAIN
        
    @property
    def distance(self):
        """Return distance from home."""
        # Calculate distance from main sensor coordinates
        home_lat = self._main_sensor._latitude
        home_lng = self._main_sensor._longitude
        
        from math import radians, cos, sin, asin, sqrt
        
        def haversine(lon1, lat1, lon2, lat2):
            """Calculate the great circle distance between two points."""
            # Convert decimal degrees to radians
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            
            # Haversine formula
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            
            # Radius of earth in kilometers
            r = 6371
            return c * r
            
        return haversine(home_lng, home_lat, self._longitude, self._latitude)
        
    @property
    def unit_of_measurement(self):
        """Return unit of measurement."""
        return "km"
        
    @property
    def icon(self):
        """Return icon based on announcement type."""
        title = self._announcement.get("title", "")
        announcement_type = self._announcement.get("type", "")
        return get_icon_for_type(title, announcement_type)
        
    @property 
    def entity_picture(self):
        """Return entity picture for map display."""
        # Return None to use icon instead of picture
        return None
        
    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        # Get the icon for this announcement type
        title = self._announcement.get("title", "")
        announcement_type = self._announcement.get("type", "")
        icon = get_icon_for_type(title, announcement_type)
        
        attrs = {
            "type": self._announcement.get("type", ""),
            "date": self._announcement.get("date", ""),
            "description": self._announcement.get("description", ""),
            "url_doc": self._announcement.get("url_doc", ""),
            "municipality": DEFAULT_MUNICIPALITY,
            "source_info": "Gebaseerd op https://github.com/basgroot/bekendmakingen implementatie",
            "api_source": "repository.overheid.nl via SRU protocol",
            "color": MAP_COLOR,
            "icon": icon,
            "entity_picture": f"/local/mdi:{icon.replace('mdi:', '')}.svg",
            "friendly_name_template": f"{icon} {{{{ state_attr('friendly_name') }}}}"
        }
        
        # Add API URL if available
        api_url = self._announcement.get("url_api")
        if api_url and api_url != "UNAVAILABLE":
            attrs["url_api"] = api_url
            
        return attrs
        
    def update_announcement(self, announcement, latitude, longitude):
        """Update the announcement data."""
        self._announcement = announcement
        self._latitude = latitude
        self._longitude = longitude
        
        # Update icon based on new announcement type
        title = announcement.get("title", "")
        announcement_type = announcement.get("type", "")
        self._attr_icon = get_icon_for_type(title, announcement_type)
        
        self.async_schedule_update_ha_state()