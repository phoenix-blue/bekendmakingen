import requests
import xml.etree.ElementTree as ET
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "overheid_bekendmakingen"

class BekendmakingenSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, hass, name, latitude, longitude, range_km, interval_hours, unique_id=None, debug=False):
        self._name = name
        self._state = None
        self._latitude = latitude
        self._longitude = longitude
        self._range_km = range_km  # Range in kilometers
        self._interval = interval_hours * 3600  # Convert hours to seconds
        self._data = []
        self.hass = hass
        self._unique_id = unique_id  # Add unique ID for the entity
        self._debug = debug  # Add debug option

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the title of the latest announcement."""
        if self._data:
            return self._data[0]['title']  # Latest announcement
        return "No announcements"

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        if self._data:
            return {
                'records': self._data,  # Full details of the records
                'latitude': self._latitude,
                'longitude': self._longitude,
                'range_km': self._range_km,
                'latest_title': self._data[0]['title'],  # Latest title
                'latest_url': self._data[0]['url'],  # Latest URL
            }
        return {
            'latitude': self._latitude,
            'longitude': self._longitude,
            'range_km': self._range_km,
        }

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def device_class(self):
        """Return the class of this device."""
        return "timestamp"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return None

    def update(self):
        """Fetch new data for the sensor."""
        url = f'https://repository.overheid.nl/sru?query=c.product-area=="lokalebekendmakingen" AND w.locatiepunt within/etrs89 "{self._latitude} {self._longitude} {self._range_km}"'
        if self._debug:
            _LOGGER.debug(f'Fetching data from {url}')

        try:
            response = requests.get(url)
            if self._debug:
                _LOGGER.debug(f'Response status code: {response.status_code}')
            if response.status_code == 200:
                new_data = self.parse_response(response.content)
                
                if new_data and new_data != self._data:
                    self._data = new_data
                    self.hass.bus.fire("bekendmakingen_update", {
                        "latest_title": new_data[0]['title'],
                        "latest_url": new_data[0]['url']
                    })
            else:
                _LOGGER.error(f'Error fetching data: {response.status_code}')
        except Exception as e:
            _LOGGER.error(f'Failed to fetch data: {e}')

    def parse_response(self, xml_data):
        """Parse the XML response and return unique records."""
        records = []
        tree = ET.fromstring(xml_data)
        sru_records = tree.findall('.//sru:record', namespaces={'sru': 'http://docs.oasis-open.org/ns/search-ws/sruResponse'})
        seen = set()

        for record in sru_records:
            identifier = record.find('.//dcterms:identifier', namespaces={'dcterms': 'http://purl.org/dc/terms/'}).text
            if identifier not in seen:
                title = record.find('.//dcterms:title', namespaces={'dcterms': 'http://purl.org/dc/terms/'}).text
                url = record.find('.//gzd:url', namespaces={'gzd': 'http://standaarden.overheid.nl/sru'}).text
                records.append({'title': title, 'url': url})
                seen.add(identifier)

        return records


class LatestTitleSensor(Entity):
    """Sensor for the latest title of announcements."""

    def __init__(self, hass, name, bekendmakingen_sensor):
        self._name = name
        self._state = None
        self.bekendmakingen_sensor = bekendmakingen_sensor

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self.bekendmakingen_sensor.extra_state_attributes.get('latest_title', 'No announcements')

    def update(self):
        """Update the sensor."""
        self.bekendmakingen_sensor.update()


class LatestUrlSensor(Entity):
    """Sensor for the latest URL of announcements."""

    def __init__(self, hass, name, bekendmakingen_sensor):
        self._name = name
        self._state = None
        self.bekendmakingen_sensor = bekendmakingen_sensor

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self.bekendmakingen_sensor.extra_state_attributes.get('latest_url', 'No URL')

    def update(self):
        """Update the sensor."""
        self.bekendmakingen_sensor.update()


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Bekendmakingen sensor platform from a config entry."""
    name = entry.data.get("name", "Overheid bekendmakingen")
    latitude = entry.data.get("latitude", hass.config.latitude)
    longitude = entry.data.get("longitude", hass.config.longitude)
    range_km = entry.data.get("range_km", 0.5)  # Range in kilometers
    interval = entry.data.get("update_interval_hours", 12) * 3600  # Convert to seconds
    debug = entry.data.get("debug", False)  # Get the debug option

    unique_id = entry.entry_id  # Use the entry ID as unique ID

    # Create the main sensor for announcements
    sensor = BekendmakingenSensor(hass, name, latitude, longitude, range_km, interval, unique_id, debug)

    # Create sensors for the latest title and URL
    latest_title_sensor = LatestTitleSensor(hass, f"{name} Latest Title", sensor)
    latest_url_sensor = LatestUrlSensor(hass, f"{name} Latest URL", sensor)

    # Add the sensors
    async_add_entities([sensor, latest_title_sensor, latest_url_sensor], update_before_add=True)

    # Register the device
    device_registry = await async_get_device_registry(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, unique_id)},
        name=name,
        manufacturer="Overheid",
        model="Bekendmakingen Sensor",
    )

    # Create a service for manual refresh
    async def handle_manual_refresh(call):
        sensor.update()

    hass.services.async_register(DOMAIN, "manual_refresh", handle_manual_refresh)
device_registry = await async_get_device_registry(hass)
