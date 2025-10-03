import requests
import xml.etree.ElementTree as ET
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
import logging
import asyncio

_LOGGER = logging.getLogger(__name__)

DOMAIN = "overheid_bekendmakingen"

class BekendmakingenSensor(Entity):
    """Weergave van een sensor."""

    def __init__(self, hass, name, latitude, longitude, range_km, interval_hours, unique_id=None, debug=False):
        self._name = name
        self._state = None
        self._latitude = float(latitude)
        self._longitude = float(longitude)
        self._range_km = float(range_km)  # Bereik in kilometers (geen limiet)
        self._interval = float(interval_hours) * 3600  # Converteer uren naar seconden
        self._data = []
        self.hass = hass
        self._unique_id = unique_id  # Voeg unieke ID toe voor de entiteit
        self._debug = debug  # Voeg debugoptie toe

        _LOGGER.debug(f"Sensor geinitialiseerd: {self._name}, Latitude: {self._latitude}, Longitude: {self._longitude}, Range: {self._range_km}km")

    @property
    def name(self):
        """Retourneer de naam van de sensor."""
        return self._name

    @property
    def state(self):
        """Retourneer de titel van de laatste bekendmaking."""
        if self._data:
            _LOGGER.debug(f"Laatste status data: {self._data[0]['title']}")
            return self._data[0]['title']  # Laatste bekendmaking
        return "Geen bekendmakingen"

    @property
    def extra_state_attributes(self):
        """Retourneer extra state-attributen."""
        if self._data:
            return {
                'records': self._data,  # Volledige details van de records
                'latitude': self._latitude,
                'longitude': self._longitude,
                'range_km': self._range_km,
                'latest_title': self._data[0]['title'],  # Laatste titel
                'latest_url': self._data[0]['url'],  # Laatste URL
            }
        return {
            'latitude': self._latitude,
            'longitude': self._longitude,
            'range_km': self._range_km,
        }

    @property
    def unique_id(self):
        """Retourneer het unieke ID van de sensor."""
        return self._unique_id

    @property
    def device_class(self):
        """Retourneer de klasse van dit apparaat."""
        return "timestamp"

    @property
    def unit_of_measurement(self):
        """Retourneer de meeteenheid."""
        return None
    def update(self):
        """Haalt nieuwe gegevens op voor de sensor."""
        url = f'https://repository.overheid.nl/frbr/lokalebekendmakingen/a400441bb3d36cd1c9f88d0ea4f448ab/1/metadata/metadata.xml'

        # Log de URL die wordt opgevraagd
        _LOGGER.debug(f'Gegevens ophalen van {url}')

        try:
            response = requests.get(url, timeout=10)

            # Log de statuscode van de response
            _LOGGER.debug(f'Response status code: {response.status_code}')

            # Log de inhoud van de response voor debugging
            _LOGGER.debug(f'Response content: {response.content}')

            if response.status_code == 200:
                new_data = self.parse_response(response.content)

                if new_data and new_data != self._data:
                    self._data = new_data
                    self.hass.bus.fire("bekendmakingen_update", {
                        "latest_title": new_data[0]['title'],
                        "latest_url": new_data[0]['url']
                    })
            else:
                _LOGGER.error(f'Fout bij het ophalen van gegevens: {response.status_code}')
        except requests.exceptions.RequestException as e:
            _LOGGER.error(f'Gegevens ophalen mislukt: {e}')

    def parse_response(self, xml_data):
        """Parse de XML-response en retourneer unieke records."""
        records = []
        try:
            tree = ET.fromstring(xml_data)
            ns = {'overheidbm': 'http://standaarden.overheid.nl/bm/terms/', 'dcterms': 'http://purl.org/dc/terms/'}
            sru_records = tree.findall('.//overheidbm:bekendmakingdocument', namespaces=ns)
            seen = set()

            for record in sru_records:
                identifier = record.find('.//dcterms:identifier', namespaces=ns).text
                if identifier not in seen:
                    title = record.find('.//dcterms:title', namespaces=ns).text
                    url = identifier  # Gebruik de identifier als de URL
                    records.append({'title': title, 'url': url})
                    seen.add(identifier)

            _LOGGER.debug(f"Gepresenteerde records: {records}")
        except ET.ParseError as e:
            _LOGGER.error(f'Fout bij het parsen van XML: {e}')
        return records


class LatestTitleSensor(Entity):
    """Sensor voor de laatste titel van bekendmakingen."""

    def __init__(self, hass, name, bekendmakingen_sensor):
        self._name = name
        self._state = None
        self.bekendmakingen_sensor = bekendmakingen_sensor

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self.bekendmakingen_sensor.extra_state_attributes.get('latest_title', 'Geen bekendmakingen')

    def update(self):
        """Werk de sensor bij."""
        self.bekendmakingen_sensor.update()


class LatestUrlSensor(Entity):
    """Sensor voor de laatste URL van bekendmakingen."""

    def __init__(self, hass, name, bekendmakingen_sensor):
        self._name = name
        self._state = None
        self.bekendmakingen_sensor = bekendmakingen_sensor

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self.bekendmakingen_sensor.extra_state_attributes.get('latest_url', 'Geen URL')

    def update(self):
        """Werk de sensor bij."""
        self.bekendmakingen_sensor.update()


async def async_setup_entry(hass, entry, async_add_entities):
    """Stel het Bekendmakingen sensor platform in vanuit een config entry."""
    name = entry.data.get("name", "Overheid bekendmakingen")
    latitude = entry.data.get("latitude", hass.config.latitude)
    longitude = entry.data.get("longitude", hass.config.longitude)
    range_km = entry.data.get("range_km", 3.0)  # Standaardbereik in kilometers is nu 3
    interval = entry.data.get("update_interval_hours", 12) * 3600  # Omrekenen naar seconden
    debug = entry.data.get("debug", False)  # Krijg de debugoptie

    unique_id = entry.entry_id  # Gebruik de entry ID als uniek ID

    _LOGGER.debug(f"Sensors instellen voor {name} op {latitude}, {longitude}, bereik {range_km}km")

    # Maak de hoofd sensor aan voor bekendmakingen
    sensor = BekendmakingenSensor(hass, name, latitude, longitude, range_km, interval, unique_id, debug)

    # Maak sensoren aan voor de laatste titel en URL
    latest_title_sensor = LatestTitleSensor(hass, f"{name} Latest Title", sensor)
    latest_url_sensor = LatestUrlSensor(hass, f"{name} Latest URL", sensor)

    # Voeg de sensoren toe
    async_add_entities([sensor, latest_title_sensor, latest_url_sensor], update_before_add=True)

    # Registreer het apparaat
    await register_device(hass, entry, name, unique_id)

    # Maak een service aan voor handmatige verversing
    async def handle_manual_refresh(call):
        _LOGGER.debug("Handmatige verversing service aangeroepen")
        await hass.async_add_executor_job(sensor.update)

    hass.services.async_register(DOMAIN, "manual_refresh", handle_manual_refresh)


async def register_device(hass, entry, name, unique_id):
    """Registreer het apparaat in het apparaatregister."""
    device_registry = async_get_device_registry(hass)  # Verwijder await hier
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, unique_id)},
        name=name,
        manufacturer="Overheid",
        model="Bekendmakingen Sensor",
    )
