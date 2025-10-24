"""Individual sensors for each bekendmaking."""
import logging
from textwrap import shorten
from homeassistant.helpers.entity import Entity
from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE
from .const import DOMAIN, get_icon_for_type

_LOGGER = logging.getLogger(__name__)

class BekendmakingIndividualSensor(Entity):
    """Individual sensor for a single bekendmaking."""

    def __init__(self, announcement_data, main_sensor, index):
        """Initialize the individual sensor."""
        self._announcement = announcement_data
        self._main_sensor = main_sensor
        self._index = index
        self._attr_available = True
        
        # Create unique ID and name with better formatting
        title = (announcement_data.get('title') or 'Onbekend').strip()
    # Create a cleaner name that prioritizes the announcement text in the UI
    self._attr_name = shorten(title, width=80, placeholder="...")
        self._attr_unique_id = f"{DOMAIN}_{main_sensor.unique_id}_{index}"
        
        _LOGGER.debug(f"Created individual sensor: {self._attr_name}")

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._announcement.get('type', 'onbekend')

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return get_icon_for_type(
            self._announcement.get('title', ''), 
            self._announcement.get('type', '')
        )

    @property
    def extra_state_attributes(self):
        """Return the state attributes with better formatting."""
        title = self._announcement.get('title', 'Onbekend')
        description = self._announcement.get('description', '')
        date = self._announcement.get('date', '')
        url = self._announcement.get('url_doc', '')
        
        attributes = {
            'titel': title,
            'beschrijving': description,
            'type': self._announcement.get('type', ''),
            'datum': date,
            'document_url': url,
            'api_url': self._announcement.get('url_api', ''),
            'index': self._index + 1,
        }
        
        # Add formatted summary
        summary = f"📄 {title}"
        if date:
            summary += f"\n📅 Datum: {date}"
        if description:
            summary += f"\n📝 {description[:100]}"
            if len(description) > 100:
                summary += "..."
        if url:
            summary += f"\n🔗 Document: {url}"
        
        attributes['samenvatting'] = summary
        
        # Add location if available
        locations = self._announcement.get('location', [])
        if locations and len(locations) > 0:
            try:
                # Parse first location coordinate
                coords = locations[0].split()
                if len(coords) >= 2:
                    coord1, coord2 = float(coords[0]), float(coords[1])
                    
                    # Determine lat/lng like in geo_location.py
                    if 50 <= coord1 <= 54 and 3 <= coord2 <= 8:
                        lat, lng = coord1, coord2
                    elif 50 <= coord2 <= 54 and 3 <= coord1 <= 8:
                        lat, lng = coord2, coord1
                    else:
                        lat = lng = None
                    
                    if lat and lng:
                        attributes[ATTR_LATITUDE] = lat
                        attributes[ATTR_LONGITUDE] = lng
                        attributes['locatie'] = f"📍 {lat:.4f}, {lng:.4f}"
            except (ValueError, IndexError):
                pass
        
        # Add quick link text for easy copy-paste
        if url:
            attributes['link_tekst'] = f"Bekijk document: {url}"
                
        return attributes

    @property
    def device_info(self):
        """Return device information to group sensors."""
        return {
            "identifiers": {(DOMAIN, self._main_sensor.unique_id)},
            "name": "Overheid Bekendmakingen",
            "manufacturer": "Overheid",
            "model": "Bekendmakingen v2.0",
        }


class HistorySensor(Entity):
    """Sensor showing history/last received time."""
    
    def __init__(self, main_sensor):
        """Initialize the history sensor."""
        self._main_sensor = main_sensor
        self._attr_name = "Bekendmakingen Laatste Update"
        self._attr_unique_id = f"{DOMAIN}_{main_sensor.unique_id}_history"
        self._attr_icon = "mdi:clock-outline"
        
    @property
    def state(self):
        """Return last update time."""
        return self._main_sensor._last_update
        
    @property
    def extra_state_attributes(self):
        """Return attributes."""
        return {
            'total_count': len(self._main_sensor._data) if self._main_sensor._data else 0,
            'update_interval_hours': self._main_sensor._interval_hours,
            'last_successful_update': self._main_sensor._last_update,
        }
        
    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._main_sensor.unique_id)},
            "name": "Overheid Bekendmakingen",
            "manufacturer": "Overheid", 
            "model": "Bekendmakingen v2.0",
        }


class IntervalSensor(Entity):
    """Sensor showing update interval."""
    
    def __init__(self, main_sensor):
        """Initialize the interval sensor."""
        self._main_sensor = main_sensor
        self._attr_name = "Bekendmakingen Update Interval"
        self._attr_unique_id = f"{DOMAIN}_{main_sensor.unique_id}_interval"
        self._attr_icon = "mdi:timer-outline"
        self._attr_unit_of_measurement = "uur"
        
    @property
    def state(self):
        """Return update interval."""
        return self._main_sensor._interval_hours
        
    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._main_sensor.unique_id)},
            "name": "Overheid Bekendmakingen",
            "manufacturer": "Overheid",
            "model": "Bekendmakingen v2.0",
        }


class RangeSensor(Entity):
    """Sensor showing search range."""
    
    def __init__(self, main_sensor):
        """Initialize the range sensor."""
        self._main_sensor = main_sensor
        self._attr_name = "Bekendmakingen Zoekbereik" 
        self._attr_unique_id = f"{DOMAIN}_{main_sensor.unique_id}_range"
        self._attr_icon = "mdi:map-marker-radius-outline"
        self._attr_unit_of_measurement = "m"
        
    @property
    def state(self):
        """Return search range in meters."""
        return int(self._main_sensor._range_km * 1000)
        
    @property
    def extra_state_attributes(self):
        """Return attributes."""
        return {
            'range_km': self._main_sensor._range_km,
            'center_latitude': self._main_sensor._latitude,
            'center_longitude': self._main_sensor._longitude,
        }
        
    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._main_sensor.unique_id)},
            "name": "Overheid Bekendmakingen",
            "manufacturer": "Overheid",
            "model": "Bekendmakingen v2.0",
        }


class TypeFilterSensor(Entity):
    """Sensor showing type breakdown."""
    
    def __init__(self, main_sensor):
        """Initialize the type filter sensor."""
        self._main_sensor = main_sensor
        self._attr_name = "Bekendmakingen per Type"
        self._attr_unique_id = f"{DOMAIN}_{main_sensor.unique_id}_types"
        self._attr_icon = "mdi:filter-variant"
        
    @property
    def state(self):
        """Return number of unique types."""
        if not self._main_sensor._data:
            return 0
        types = set()
        for item in self._main_sensor._data:
            types.add(item.get('type', 'onbekend'))
        return len(types)
        
    @property
    def extra_state_attributes(self):
        """Return type breakdown."""
        if not self._main_sensor._data:
            return {}
            
        type_counts = {}
        for item in self._main_sensor._data:
            item_type = item.get('type', 'onbekend')
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
            
        return {
            'type_breakdown': type_counts,
            'total_types': len(type_counts),
        }
        
    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._main_sensor.unique_id)},
            "name": "Overheid Bekendmakingen",
            "manufacturer": "Overheid",
            "model": "Bekendmakingen v2.0",
        }


class TypeHistorySensor(Entity):
    """Individual sensor for each announcement type with history."""
    
    def __init__(self, main_sensor, announcement_type):
        """Initialize the type history sensor."""
        self._main_sensor = main_sensor
        self._type = announcement_type
        self._attr_name = f"Bekendmakingen {announcement_type.title()}"
        self._attr_unique_id = f"{DOMAIN}_{main_sensor.unique_id}_type_{announcement_type.replace(' ', '_')}"
        
        # Set icon based on type
        from .const import get_icon_for_type
        self._attr_icon = get_icon_for_type("", announcement_type)
        
    @property
    def state(self):
        """Return count of this type."""
        if not self._main_sensor._data:
            return 0
            
        count = 0
        for item in self._main_sensor._data:
            if item.get('type', 'onbekend') == self._type:
                count += 1
        return count
        
    @property
    def extra_state_attributes(self):
        """Return latest announcement for this type with clickable links and GPS."""
        if not self._main_sensor._data:
            return {
                'type': self._type,
                'count': 0,
                'latest_announcement': 'Geen bekendmakingen beschikbaar',
                'last_update': self._main_sensor._last_update,
            }
            
        type_items = []
        for item in self._main_sensor._data:
            if item.get('type', 'onbekend') == self._type:
                type_items.append(item)
        
        # Sort by date, newest first
        type_items.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        if not type_items:
            return {
                'type': self._type,
                'count': 0,
                'latest_announcement': 'Geen bekendmakingen van dit type',
                'last_update': self._main_sensor._last_update,
            }
            
        # Get latest announcement
        latest = type_items[0]
        title = latest.get('title', 'Onbekend')
        date = latest.get('date', 'Onbekend')
        url = latest.get('url_doc', '')
        description = latest.get('description', 'Geen beschrijving')
        
        attributes = {
            'type': self._type,
            'count': len(type_items),
            'last_update': self._main_sensor._last_update,
            
            # Latest announcement data
            'titel': title,
            'datum': date,
            'beschrijving': description,
            'document_url': url,
        }
        
        # Add clickable HTML link
        if url:
            # Create HTML link that should be clickable in some HA contexts
            short_title = title[:50] + ('...' if len(title) > 50 else '')
            attributes['document_link_html'] = f'<a href="{url}" target="_blank">{short_title}</a>'
            attributes['document_link_markdown'] = f'[{short_title}]({url})'
            
        # Add GPS coordinates if available
        locations = latest.get('location', [])
        if locations:
            for i, location_str in enumerate(locations):
                try:
                    coords = location_str.strip().split()
                    if len(coords) >= 2:
                        coord1, coord2 = float(coords[0]), float(coords[1])
                        
                        # Determine lat/lng - Netherlands ranges
                        if 50 <= coord1 <= 54 and 3 <= coord2 <= 8:
                            lat, lng = coord1, coord2
                        elif 50 <= coord2 <= 54 and 3 <= coord1 <= 8:
                            lat, lng = coord2, coord1
                        else:
                            continue
                            
                        attributes['latitude'] = lat
                        attributes['longitude'] = lng
                        attributes['gps_coordinates'] = f"{lat:.6f}, {lng:.6f}"
                        
                        # Add Google Maps link
                        maps_url = f"https://www.google.com/maps?q={lat},{lng}"
                        attributes['google_maps_url'] = maps_url
                        attributes['google_maps_link'] = f'<a href="{maps_url}" target="_blank">📍 Bekijk op kaart ({lat:.4f}, {lng:.4f})</a>'
                        break
                except (ValueError, IndexError):
                    continue
        
        # Create formatted display text with emojis
        display_lines = [f"📄 **{title}**"]
        if date != 'Onbekend':
            display_lines.append(f"📅 {date}")
        if description and len(description.strip()) > 0:
            desc_short = description[:150] + ('...' if len(description) > 150 else '')
            display_lines.append(f"📝 {desc_short}")
        if url:
            display_lines.append(f"🔗 [Document bekijken]({url})")
        if attributes.get('gps_coordinates'):
            display_lines.append(f"📍 {attributes['gps_coordinates']}")
            
        attributes['formatted_display'] = '\n'.join(display_lines)
        
        # Add recent history count
        if len(type_items) > 1:
            attributes['historical_count'] = len(type_items) - 1
            attributes['total_in_period'] = len(type_items)
            
        return attributes
        
    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._main_sensor.unique_id)},
            "name": "Overheid Bekendmakingen",
            "manufacturer": "Overheid",
            "model": "Bekendmakingen v2.0",
        }