"""Latest per type sensors with clickable links and GPS coordinates."""
import logging
from homeassistant.helpers.entity import Entity
from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE

from .const import DOMAIN, get_icon_for_type

_LOGGER = logging.getLogger(__name__)


class LatestByTypeSensor(Entity):
    """Sensor for the latest announcement of a specific type with clickable links."""

    def __init__(self, main_sensor, announcement_type):
        """Initialize the latest by type sensor."""
        self._main_sensor = main_sensor
        self._type = announcement_type
        self._attr_name = f"Laatste {announcement_type.title()}"
        self._attr_unique_id = f"{DOMAIN}_{main_sensor.unique_id}_latest_{announcement_type.replace(' ', '_')}"
        
        # Set icon based on type
        self._attr_icon = get_icon_for_type("", announcement_type)

    @property
    def state(self):
        """Return the date of the latest announcement."""
        latest = self._get_latest_announcement()
        if latest:
            return latest.get('date', 'Onbekend')
        return 'Geen bekendmakingen'

    def _get_latest_announcement(self):
        """Get the latest announcement for this type."""
        if not self._main_sensor._data:
            return None
            
        type_items = []
        for item in self._main_sensor._data:
            if item.get('type', 'onbekend') == self._type:
                type_items.append(item)
        
        if not type_items:
            return None
            
        # Sort by date, newest first
        type_items.sort(key=lambda x: x.get('date', ''), reverse=True)
        return type_items[0]

    @property
    def extra_state_attributes(self):
        """Return attributes with clickable links and GPS coordinates."""
        latest = self._get_latest_announcement()
        
        if not latest:
            return {
                'type': self._type,
                'status': 'Geen bekendmakingen van dit type beschikbaar',
                'last_update': self._main_sensor._last_update,
            }

        title = latest.get('title', 'Onbekend')
        date = latest.get('date', 'Onbekend')
        url = latest.get('url_doc', '')
        description = latest.get('description', 'Geen beschrijving')

        attributes = {
            'type': self._type,
            'titel': title,
            'datum': date,
            'beschrijving': description,
            'document_url': url,
            'last_update': self._main_sensor._last_update,
        }

        # Add clickable HTML links
        if url:
            short_title = title[:60] + ('...' if len(title) > 60 else '')
            attributes['document_link'] = f'<a href="{url}" target="_blank" rel="noopener">📄 {short_title}</a>'
            attributes['plain_link'] = f"📄 {short_title}: {url}"

        # Add GPS coordinates and map links
        locations = latest.get('location', [])
        if locations:
            for location_str in locations:
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
                            
                        # Add GPS attributes
                        attributes[ATTR_LATITUDE] = lat
                        attributes[ATTR_LONGITUDE] = lng
                        attributes['coordinates'] = f"{lat:.6f}, {lng:.6f}"
                        
                        # Add clickable map links
                        maps_url = f"https://www.google.com/maps?q={lat},{lng}"
                        attributes['google_maps_url'] = maps_url
                        attributes['maps_link'] = f'<a href="{maps_url}" target="_blank" rel="noopener">📍 Bekijk op Google Maps</a>'
                        
                        # Add coordinates display
                        attributes['location_display'] = f"📍 {lat:.4f}, {lng:.4f}"
                        break
                except (ValueError, IndexError):
                    continue

        # Create formatted summary with markdown-style links
        summary_lines = [f"**📄 {title}**"]
        if date != 'Onbekend':
            summary_lines.append(f"📅 **Datum:** {date}")
        if description and len(description.strip()) > 0:
            desc_short = description[:200] + ('...' if len(description) > 200 else '')
            summary_lines.append(f"📝 **Beschrijving:** {desc_short}")
        if url:
            summary_lines.append(f"🔗 **Document:** [{url}]({url})")
        if attributes.get('coordinates'):
            maps_url = attributes.get('google_maps_url', '')
            summary_lines.append(f"📍 **Locatie:** [{attributes['coordinates']}]({maps_url})")

        attributes['formatted_summary'] = '\n\n'.join(summary_lines)

        return attributes

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._main_sensor.unique_id)},
            "name": "Overheid Bekendmakingen",
            "manufacturer": "Overheid",
            "model": "Bekendmakingen v2.1",
        }

    @property
    def available(self):
        """Return if entity is available."""
        return self._main_sensor.available