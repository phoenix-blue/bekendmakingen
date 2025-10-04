import requests
import xml.etree.ElementTree as ET
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from homeassistant.components.input_number import InputNumberEntity
from homeassistant.components.input_text import InputTextEntity
import logging
import asyncio
from urllib.parse import urlencode
from datetime import datetime, timedelta
import json

from .const import (
    DOMAIN,
    API_ENDPOINT,
    CONF_RADIUS,
    DEFAULT_RADIUS,
    CONF_MAP_DISPLAY_DAYS,
    CONF_ARCHIVE_DAYS,
    DEFAULT_MAP_DISPLAY_DAYS,
    DEFAULT_ARCHIVE_DAYS,
)

_LOGGER = logging.getLogger(__name__)

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
        base_attrs = {
            'latitude': self._latitude,
            'longitude': self._longitude,
            'range_km': self._range_km,
            'radius_meters': int(self._range_km * 1000),  # Toon ook in meters
            'update_interval_hours': self._interval / 3600,
            'debug_mode': self._debug,
        }
        
        if self._data:
            base_attrs.update({
                'records': self._data,  # Volledige details van de records
                'total_records': len(self._data),
                'latest_title': self._data[0]['title'],
                'latest_url': self._data[0]['url'],
            })
        
        return base_attrs

    def get_recent_records(self, days=1):
        """Get records from the last X days."""
        if not self._data:
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent = []
        
        for record in self._data:
            # Try to parse date from record if available
            try:
                # This would need to be implemented based on actual data structure
                recent.append(record)
            except:
                # For now, return all records as we don't have date parsing yet
                recent.append(record)
                
        return recent[:10]  # Limit to 10 most recent
    
    def get_archive_records(self, days=30):
        """Get all records from the archive."""
        if not self._data:
            return []
        return self._data  # For now return all data

    @property
    def unique_id(self):
        """Retourneer het unieke ID van de sensor."""
        return self._unique_id

    @property
    def device_info(self):
        """Return device info to group sensors under one device."""
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": "Overheid Bekendmakingen",
            "manufacturer": "Overheid.nl",
            "model": "Lokale Bekendmakingen Sensor",
            "sw_version": "2024.10.04.3",
        }

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
        # Probeer eerst de lokale bekendmakingen API
        urls_to_try = [
            # Officiële lokale bekendmakingen SRU API
            self._build_sru_url(),
            # Fallback naar algemene bekendmakingen
            self._build_fallback_url()
        ]
        
        for url in urls_to_try:
            _LOGGER.debug(f'Gegevens ophalen van {url}')
            
            try:
                response = requests.get(url, timeout=15)
                _LOGGER.debug(f'Response status code: {response.status_code}')
                
                if response.status_code == 200:
                    new_data = self.parse_response(response.content)
                    if new_data:  # Als we data hebben gevonden, stop met proberen
                        if new_data != self._data:
                            self._data = new_data
                            self.hass.bus.fire("bekendmakingen_update", {
                                "latest_title": new_data[0]['title'],
                                "latest_url": new_data[0]['url']
                            })
                        return
                else:
                    _LOGGER.debug(f'URL {url} gaf status {response.status_code}')
                    
            except requests.exceptions.RequestException as e:
                _LOGGER.debug(f'Fout bij ophalen van {url}: {e}')
                continue
        
        # Als alle URLs falen
        _LOGGER.error('Alle URLs faalden bij het ophalen van gegevens')
    
    def _build_sru_url(self):
        """Bouw SRU URL voor lokale bekendmakingen."""
        query_params = {
            'version': '1.2',
            'operation': 'searchRetrieve',
            'recordSchema': 'gzd', 
            'query': 'c.product-area=="lokalebekendmakingen"',
            'maximumRecords': '20',
            'startRecord': '1'
        }
        return f"https://repository.overheid.nl/sru?{urlencode(query_params)}"
    
    def _build_fallback_url(self):
        """Bouw fallback URL voor algemene bekendmakingen.""" 
        query_params = {
            'version': '1.2',
            'operation': 'searchRetrieve',
            'recordSchema': 'gzd',
            'query': 'dcterms.type=="bekendmaking"',
            'maximumRecords': '10',
            'startRecord': '1'
        }
        return f"https://repository.overheid.nl/sru?{urlencode(query_params)}"

    def parse_response(self, xml_data):
        """Parse de XML-response en retourneer unieke records."""
        records = []
        try:
            tree = ET.fromstring(xml_data)
            
            # Correcte namespaces voor SRU response van overheid.nl
            ns = {
                'sru': 'http://docs.oasis-open.org/ns/search-ws/sruResponse',
                'gzd': 'http://standaarden.overheid.nl/sru',
                'dcterms': 'http://purl.org/dc/terms/',
                'overheidwetgeving': 'http://standaarden.overheid.nl/wetgeving/'
            }
            
            # Debug: log de XML structuur
            if self._debug:
                _LOGGER.debug(f"XML Response: {xml_data[:1000]}...")  # Eerste 1000 chars
            
            # Zoek naar records in de SRU response
            sru_records = tree.findall('.//sru:record', ns)
            _LOGGER.debug(f"Gevonden {len(sru_records)} SRU records")
            
            seen = set()
            
            for record in sru_records:
                try:
                    # Zoek recordData binnen elke record
                    record_data = record.find('sru:recordData', ns)
                    if record_data is not None:
                        # Zoek naar gzd element
                        gzd = record_data.find('gzd:gzd', ns)
                        if gzd is not None:
                            # Haal titel en identifier op
                            title_elem = gzd.find('.//dcterms:title', ns)
                            identifier_elem = gzd.find('.//dcterms:identifier', ns)
                            
                            if title_elem is not None and identifier_elem is not None:
                                title = title_elem.text
                                identifier = identifier_elem.text
                                
                                if identifier and identifier not in seen:
                                    # Maak een echte URL van de identifier
                                    bekendmaking_url = f"https://repository.overheid.nl/frbr/officielepublicaties/{identifier}/"
                                    
                                    records.append({
                                        'title': title or 'Geen titel',
                                        'url': bekendmaking_url
                                    })
                                    seen.add(identifier)
                                    
                except Exception as e:
                    _LOGGER.debug(f"Fout bij verwerken van individuele record: {e}")
                    continue

            _LOGGER.debug(f"Totaal {len(records)} unieke records gevonden")
            
        except ET.ParseError as e:
            _LOGGER.error(f'Fout bij het parsen van XML: {e}')
        except Exception as e:
            _LOGGER.error(f'Onverwachte fout bij parsen: {e}')
            
        return records


class LatestTitleSensor(Entity):
    """Sensor voor de laatste titel van bekendmakingen."""

    def __init__(self, hass, name, bekendmakingen_sensor):
        self._name = name
        self._state = None
        self.bekendmakingen_sensor = bekendmakingen_sensor
        self._unique_id = f"{bekendmakingen_sensor.unique_id}_latest_title"

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def device_info(self):
        """Return device info to group with main sensor."""
        return self.bekendmakingen_sensor.device_info

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
        self._unique_id = f"{bekendmakingen_sensor.unique_id}_latest_url"

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def device_info(self):
        """Return device info to group with main sensor."""
        return self.bekendmakingen_sensor.device_info

    @property
    def state(self):
        return self.bekendmakingen_sensor.extra_state_attributes.get('latest_url', 'Geen URL')

    def update(self):
        """Werk de sensor bij."""
        self.bekendmakingen_sensor.update()


class RecentBekendmakingenSensor(Entity):
    """Sensor voor recente bekendmakingen (laatste 24 uur)."""

    def __init__(self, hass, name, bekendmakingen_sensor):
        self._name = name
        self._state = None
        self.bekendmakingen_sensor = bekendmakingen_sensor
        self._unique_id = f"{bekendmakingen_sensor.unique_id}_recent"

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def device_info(self):
        """Return device info to group with main sensor."""
        return self.bekendmakingen_sensor.device_info

    @property
    def state(self):
        recent_records = self.bekendmakingen_sensor.get_recent_records(1)
        return len(recent_records)

    @property
    def extra_state_attributes(self):
        """Return recent records as attributes."""
        recent_records = self.bekendmakingen_sensor.get_recent_records(1)
        return {
            'records': recent_records,
            'count': len(recent_records),
            'last_update': datetime.now().isoformat(),
            'display_text': self._format_records_text(recent_records)
        }

    def _format_records_text(self, records):
        """Format records as readable text."""
        if not records:
            return "Geen recente bekendmakingen"
        
        text_lines = ["📋 Recente Bekendmakingen (24u):"]
        for i, record in enumerate(records[:5], 1):
            text_lines.append(f"{i}. {record.get('title', 'Geen titel')}")
        
        if len(records) > 5:
            text_lines.append(f"... en {len(records) - 5} meer")
            
        return "\n".join(text_lines)

    def update(self):
        """Werk de sensor bij."""
        self.bekendmakingen_sensor.update()


class ArchiefBekendmakingenSensor(Entity):
    """Sensor voor archief bekendmakingen."""

    def __init__(self, hass, name, bekendmakingen_sensor):
        self._name = name
        self._state = None
        self.bekendmakingen_sensor = bekendmakingen_sensor
        self._unique_id = f"{bekendmakingen_sensor.unique_id}_archive"

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def device_info(self):
        """Return device info to group with main sensor."""
        return self.bekendmakingen_sensor.device_info

    @property
    def state(self):
        archive_records = self.bekendmakingen_sensor.get_archive_records(30)
        return len(archive_records)

    @property
    def extra_state_attributes(self):
        """Return archive records as attributes."""
        archive_records = self.bekendmakingen_sensor.get_archive_records(30)
        return {
            'records': archive_records,
            'count': len(archive_records),
            'last_update': datetime.now().isoformat(),
            'display_text': self._format_archive_text(archive_records)
        }

    def _format_archive_text(self, records):
        """Format archive records as readable text."""
        if not records:
            return "Geen gearchiveerde bekendmakingen"
        
        text_lines = ["📚 Archief Bekendmakingen:"]
        for i, record in enumerate(records[:10], 1):
            text_lines.append(f"{i}. {record.get('title', 'Geen titel')}")
        
        if len(records) > 10:
            text_lines.append(f"... en {len(records) - 10} meer (totaal: {len(records)})")
            
        return "\n".join(text_lines)

    def update(self):
        """Werk de sensor bij."""
        self.bekendmakingen_sensor.update()


class RangeConfigSensor(Entity):
    """Sensor om de range dynamisch aan te passen."""

    def __init__(self, hass, name, bekendmakingen_sensor):
        self._name = name
        self._state = None
        self.bekendmakingen_sensor = bekendmakingen_sensor
        self._unique_id = f"{bekendmakingen_sensor.unique_id}_range_config"
        self.hass = hass

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def device_info(self):
        """Return device info to group with main sensor."""
        return self.bekendmakingen_sensor.device_info

    @property
    def state(self):
        return int(self.bekendmakingen_sensor._range_km * 1000)  # Return in meters

    @property
    def extra_state_attributes(self):
        """Return range configuration attributes."""
        return {
            'range_meters': int(self.bekendmakingen_sensor._range_km * 1000),
            'range_km': self.bekendmakingen_sensor._range_km,
            'min_range': 100,
            'max_range': 10000,
            'step': 100,
            'unit_of_measurement': 'm'
        }

    async def async_set_value(self, value):
        """Set new range value."""
        try:
            range_meters = int(value)
            if 100 <= range_meters <= 10000:
                self.bekendmakingen_sensor._range_km = range_meters / 1000.0
                _LOGGER.info(f"Range aangepast naar {range_meters}m ({self.bekendmakingen_sensor._range_km}km)")
                await self.hass.async_add_executor_job(self.bekendmakingen_sensor.update)
        except (ValueError, TypeError):
            _LOGGER.error(f"Ongeldige range waarde: {value}")

    def update(self):
        """Werk de sensor bij."""
        pass  # This sensor doesn't need updating from the main sensor


class IntervalConfigSensor(Entity):
    """Sensor om de scan interval dynamisch aan te passen."""

    def __init__(self, hass, name, bekendmakingen_sensor):
        self._name = name
        self._state = None
        self.bekendmakingen_sensor = bekendmakingen_sensor
        self._unique_id = f"{bekendmakingen_sensor.unique_id}_interval_config"
        self.hass = hass

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def device_info(self):
        """Return device info to group with main sensor."""
        return self.bekendmakingen_sensor.device_info

    @property
    def state(self):
        return int(self.bekendmakingen_sensor._interval / 3600)  # Return in hours

    @property
    def extra_state_attributes(self):
        """Return interval configuration attributes."""
        return {
            'interval_hours': self.bekendmakingen_sensor._interval / 3600,
            'interval_seconds': self.bekendmakingen_sensor._interval,
            'min_hours': 1,
            'max_hours': 24,
            'step': 1,
            'unit_of_measurement': 'h'
        }

    async def async_set_value(self, value):
        """Set new interval value."""
        try:
            interval_hours = int(value)
            if 1 <= interval_hours <= 24:
                self.bekendmakingen_sensor._interval = interval_hours * 3600
                _LOGGER.info(f"Scan interval aangepast naar {interval_hours}h")
                await self.hass.async_add_executor_job(self.bekendmakingen_sensor.update)
        except (ValueError, TypeError):
            _LOGGER.error(f"Ongeldige interval waarde: {value}")

    def update(self):
        """Werk de sensor bij."""
        pass  # This sensor doesn't need updating from the main sensor


async def async_setup_entry(hass, entry, async_add_entities):
    """Stel het Bekendmakingen sensor platform in vanuit een config entry."""
    # Gebruik options als beschikbaar, anders data als fallback
    config = entry.options or entry.data
    
    name = entry.data.get("name", "Overheid bekendmakingen")
    latitude = entry.data.get("latitude", hass.config.latitude)
    longitude = entry.data.get("longitude", hass.config.longitude)
    
    # Fix: Converteer radius van meters naar kilometers en gebruik options
    radius_meters = config.get(CONF_RADIUS, DEFAULT_RADIUS)
    range_km = radius_meters / 1000.0  # Converteer meters naar kilometers
    
    interval_hours = config.get("update_interval_hours", 12)
    interval = interval_hours * 3600  # Converteer uren naar seconden
    debug = config.get("debug", False)

    unique_id = entry.entry_id  # Gebruik de entry ID als uniek ID

    _LOGGER.debug(f"Sensors instellen voor {name} op {latitude}, {longitude}, bereik {range_km}km (radius: {radius_meters}m)")

    # Maak de hoofd sensor aan voor bekendmakingen
    sensor = BekendmakingenSensor(hass, name, latitude, longitude, range_km, interval, unique_id, debug)

    # Maak sensoren aan voor de laatste titel en URL
    latest_title_sensor = LatestTitleSensor(hass, f"{name} Latest Title", sensor)
    latest_url_sensor = LatestUrlSensor(hass, f"{name} Latest URL", sensor)
    
    # Maak nieuwe sensoren aan
    recent_sensor = RecentBekendmakingenSensor(hass, f"{name} Recent (24h)", sensor)
    archive_sensor = ArchiefBekendmakingenSensor(hass, f"{name} Archive", sensor)
    range_config_sensor = RangeConfigSensor(hass, f"{name} Range Config", sensor)
    interval_config_sensor = IntervalConfigSensor(hass, f"{name} Interval Config", sensor)

    # Voeg alle sensoren toe
    all_sensors = [
        sensor,
        latest_title_sensor, 
        latest_url_sensor,
        recent_sensor,
        archive_sensor,
        range_config_sensor,
        interval_config_sensor
    ]
    async_add_entities(all_sensors, update_before_add=True)

    # Registreer het apparaat
    await register_device(hass, entry, name, unique_id)

    # Setup options update listener
    async def async_options_updated(hass, entry):
        """Handle options update."""
        _LOGGER.debug("Configuratie opties bijgewerkt - sensor wordt ververst")
        # Trigger sensor update met nieuwe instellingen
        config = entry.options or entry.data
        new_radius_meters = config.get(CONF_RADIUS, DEFAULT_RADIUS)
        new_range_km = new_radius_meters / 1000.0
        new_interval_hours = config.get("update_interval_hours", 12)
        new_debug = config.get("debug", False)
        
        # Update sensor configuratie
        sensor._range_km = new_range_km
        sensor._interval = new_interval_hours * 3600
        sensor._debug = new_debug
        
        # Force update
        await hass.async_add_executor_job(sensor.update)

    entry.async_on_unload(entry.add_update_listener(async_options_updated))

    # Registreer services
    async def handle_manual_refresh(call):
        _LOGGER.debug("Handmatige verversing service aangeroepen")
        await hass.async_add_executor_job(sensor.update)

    async def handle_set_range(call):
        """Handle set range service call."""
        range_meters = call.data.get("range_meters")
        if range_meters:
            await range_config_sensor.async_set_value(range_meters)
            _LOGGER.info(f"Range aangepast via service naar {range_meters}m")

    async def handle_set_interval(call):
        """Handle set interval service call."""
        interval_hours = call.data.get("interval_hours")
        if interval_hours:
            await interval_config_sensor.async_set_value(interval_hours)
            _LOGGER.info(f"Interval aangepast via service naar {interval_hours}h")

    # Registreer alle services
    hass.services.async_register(DOMAIN, "manual_refresh", handle_manual_refresh)
    hass.services.async_register(DOMAIN, "set_range", handle_set_range)
    hass.services.async_register(DOMAIN, "set_interval", handle_set_interval)


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
