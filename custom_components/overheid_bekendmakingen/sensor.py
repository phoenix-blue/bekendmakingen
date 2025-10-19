"""Sensor platform voor Overheid Bekendmakingen - Versie 2.0 (Werkende API)."""
import requests
import json
import logging
import asyncio
from datetime import datetime, timedelta
from urllib.parse import urlencode
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    API_BASE_URL,
    MAXIMUM_RECORDS,
    START_RECORD,
    DEFAULT_MUNICIPALITY,
    MUNICIPALITY_COORDINATES,
    get_start_date,
    build_query,
    ATTR_LATEST_TITLE,
    ATTR_LATEST_URL,
    ATTR_LATEST_DATE,
    ATTR_TOTAL_COUNT,
    ATTR_ANNOUNCEMENTS,
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    ATTR_RADIUS,
    ATTR_LAST_UPDATE,
)

_LOGGER = logging.getLogger(__name__)

class BekendmakingenSensor(Entity):
    """Hoofdsensor voor Overheid Bekendmakingen - Werkende API implementatie."""

    def __init__(self, hass, name, latitude, longitude, range_km, interval_hours, municipality=None, unique_id=None, debug=False):
        """Initialize the sensor."""
        self._name = name
        self._state = None
        self._latitude = float(latitude) if latitude else MUNICIPALITY_COORDINATES["lat"]
        self._longitude = float(longitude) if longitude else MUNICIPALITY_COORDINATES["lng"]
        self._range_km = float(range_km) / 1000.0
        self._interval_hours = float(interval_hours)
        self._data = []
        self.hass = hass
        self._unique_id = unique_id
        self._debug = debug
        self._last_update = None
        self._available = True
        self._municipality = municipality if municipality else DEFAULT_MUNICIPALITY
        self._individual_sensors_created = False
        self._async_add_entities = None

        # Create update coordinator with the specified interval
        self.coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self._name}",
            update_method=self._async_update_data,
            update_interval=timedelta(hours=self._interval_hours),
        )

        _LOGGER.info(f"Bekendmakingen Sensor 2.0.1 geinitialiseerd: {self._name}")
        _LOGGER.info(f"Update interval ingesteld op {self._interval_hours} uur")
        _LOGGER.debug(f"Gemeente: {self._municipality}, Coordinaten: {self._latitude}, {self._longitude}")

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return unique ID for this sensor."""
        if self._unique_id:
            return self._unique_id
        return f"{DOMAIN}_{self._municipality.lower().replace('-', '_')}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return len(self._data) if self._data else 0

    @property
    def available(self):
        """Return if entity is available."""
        return self._available

    @property
    def should_poll(self):
        """Return False as we handle updates manually via coordinator."""
        return False

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attributes = {
            ATTR_TOTAL_COUNT: len(self._data),
            ATTR_LATITUDE: self._latitude,
            ATTR_LONGITUDE: self._longitude,
            ATTR_RADIUS: self._range_km * 1000,  # Convert back to meters
            ATTR_LAST_UPDATE: self._last_update,
            "municipality": self._municipality,
            "api_version": "2.0.1"
        }

        if self._data:
            # Sort by date, newest first
            sorted_data = sorted(self._data, key=lambda x: x.get("date", ""), reverse=True)
            latest = sorted_data[0]
            
            attributes[ATTR_LATEST_TITLE] = latest.get("title", "")
            attributes[ATTR_LATEST_URL] = latest.get("url_doc", "")
            attributes[ATTR_LATEST_DATE] = latest.get("date", "")
            attributes[ATTR_ANNOUNCEMENTS] = sorted_data[:10]  # Last 10 for UI

        return attributes

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:file-document-outline"

    @property
    def device_info(self):
        """Return device information to group sensors."""
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": "Overheid Bekendmakingen",
            "manufacturer": "Overheid",
            "model": "Bekendmakingen v2.0",
        }

    async def _async_update_data(self):
        """Fetch data from API via coordinator."""
        try:
            _LOGGER.debug(f"Coordinator updating data for {self._name}")
            await self.hass.async_add_executor_job(self._update_data)
            return self._data
        except Exception as e:
            _LOGGER.error(f"Error updating {self._name}: {e}")
            self._available = False
            raise UpdateFailed(f"Error communicating with API: {e}")

    async def async_update(self):
        """Update the sensor via coordinator."""
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        await super().async_added_to_hass()
        
        # Start the coordinator
        await self.coordinator.async_config_entry_first_refresh()
        
        # Register for manual update events
        self.async_on_remove(
            self.hass.bus.async_listen("overheid_bekendmakingen_manual_update", self._handle_manual_update)
        )
        self.async_on_remove(
            self.hass.bus.async_listen("overheid_bekendmakingen_refresh_all", self._handle_refresh_all)
        )

    def _update_data(self):
        """Fetch data from the API using working implementation."""
        try:
            start_date = get_start_date()
            query = build_query(self._municipality, start_date)
            
            params = {
                'query': query,
                'maximumRecords': MAXIMUM_RECORDS,
                'startRecord': START_RECORD,
                'httpAccept': 'application/json'
            }
            
            url = f"{API_BASE_URL}?{urlencode(params)}"
            _LOGGER.debug(f"API Request URL: {url}")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            _LOGGER.debug(f"API Response keys: {data.keys()}")
            
            # Process the response similar to basgroot implementation
            publications = self._process_response(data)
            
            self._data = publications
            self._last_update = datetime.now().isoformat()
            self._available = True
            
            _LOGGER.info(f"Successfully updated {self._name}: found {len(publications)} announcements")
            
            # Create individual sensors if not done yet and we have data
            if not self._individual_sensors_created and len(publications) > 0 and self._async_add_entities:
                self._create_individual_sensors()
            
        except requests.exceptions.RequestException as e:
            _LOGGER.error(f"Network error fetching data: {e}")
            self._available = False
        except Exception as e:
            _LOGGER.error(f"Error processing data: {e}")
            self._available = False

    def _process_response(self, response_json):
        """Process the API response like basgroot implementation."""
        publications = []
        
        try:
            search_response = response_json.get("searchRetrieveResponse", {})
            record_count = search_response.get("numberOfRecords", 0)
            
            _LOGGER.debug(f"API returned {record_count} records")
            
            if record_count == 0:
                return publications
                
            records = search_response.get("records", {})
            if not records:
                _LOGGER.warning("No records found in response despite record count > 0")
                return publications
                
            # Handle both single record and multiple records
            record_data = records.get("record", [])
            if not isinstance(record_data, list):
                record_data = [record_data]
                
            for record in record_data:
                try:
                    publication = self._extract_publication_data(record)
                    if publication:
                        publications.append(publication)
                except Exception as e:
                    _LOGGER.warning(f"Error processing record: {e}")
                    continue
                    
        except Exception as e:
            _LOGGER.error(f"Error processing response: {e}")
            
        return publications

    def _extract_publication_data(self, record):
        """Extract publication data from a record."""
        try:
            record_data = record.get("recordData", {})
            gzd = record_data.get("gzd", {})
            
            # Get enriched data
            enriched_data = gzd.get("enrichedData", {})
            preferred_url = enriched_data.get("preferredUrl", "").strip()
            
            # Get original data
            original_data = gzd.get("originalData", {})
            meta = original_data.get("meta", {})
            
            # Extract basic info
            owms_kern = meta.get("owmskern", {})
            tp_meta = meta.get("tpmeta", {})
            
            # Get title
            title = self._get_title(meta, owms_kern, tp_meta)
            
            # Get type
            type_info = self._get_type(tp_meta, owms_kern)
            
            # Get date
            date_str = tp_meta.get("datumTijdstipWijzigingWork", "")
            if date_str:
                try:
                    # Parse date - format like "2023-02-10"
                    date_obj = datetime.fromisoformat(date_str.split('T')[0])
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                except:
                    formatted_date = date_str
            else:
                formatted_date = ""
                
            # Get description
            description = owms_kern.get("title", "")
            
            # Create API URL (if possible)
            api_url = self._get_api_url(preferred_url)
            
            # Extract location data
            locations = self._extract_locations(tp_meta)
            
            publication = {
                "title": title,
                "description": description,
                "type": type_info,
                "date": formatted_date,
                "url_doc": preferred_url,
                "url_api": api_url,
                "location": locations
            }
            
            return publication
            
        except Exception as e:
            _LOGGER.warning(f"Error extracting publication data: {e}")
            return None

    def _get_title(self, meta, owms_kern, tp_meta):
        """Extract title from record data."""
        # Try abstract first (like basgroot implementation)
        owms_mantel = meta.get("owmsmantel", {})
        abstract = owms_mantel.get("abstract", "")
        if abstract and isinstance(abstract, str):
            return abstract.strip()
            
        # Fallback to type + activity
        title = self._get_type(tp_meta, owms_kern)
        
        activity = tp_meta.get("activiteit", {})
        if activity and isinstance(activity, dict):
            activity_text = activity.get("$", "")
            if activity_text:
                title += f" {activity_text.strip()}"
        elif isinstance(activity, list) and activity:
            activity_text = activity[0].get("$", "") if isinstance(activity[0], dict) else str(activity[0])
            if activity_text:
                title += f" {activity_text.strip()}"
                
        return title

    def _get_type(self, tp_meta, owms_kern):
        """Extract type from record data."""
        # Check for activity first
        activity = tp_meta.get("activiteit", {})
        if activity:
            if isinstance(activity, list):
                activity = activity[0]
            if isinstance(activity, dict):
                activity_type = activity.get("$", "")
                known_types = ["bouwen", "slopen", "uitweg en inrit", "kappen", 
                              "milieu", "natuur", "reclame", "brandveilig gebruik", 
                              "ruimtelijke ordening"]
                if activity_type in known_types:
                    return activity_type
                    
        # Fallback to owmskern type
        type_info = owms_kern.get("type", "")
        if isinstance(type_info, list):
            type_info = type_info[0]
        if isinstance(type_info, dict):
            type_info = type_info.get("$", "")
            
        return type_info.strip() if type_info else "onbekend"

    def _get_api_url(self, url_doc):
        """Convert document URL to API endpoint like basgroot implementation."""
        try:
            if not url_doc or "zoek.officielebekendmakingen.nl" not in url_doc:
                return "UNAVAILABLE"
                
            # Extract license ID from URL
            # URL: https://zoek.officielebekendmakingen.nl/gmb-2023-56454.html
            start_marker = "https://zoek.officielebekendmakingen.nl/"
            end_marker = ".html"
            
            if url_doc.startswith(start_marker) and url_doc.endswith(end_marker):
                license_id = url_doc[len(start_marker):-len(end_marker)]
                parts = license_id.split("-")
                
                if len(parts) >= 3:
                    # Build API URL
                    # Format: https://repository.overheid.nl/frbr/officielepublicaties/gmb/2023/gmb-2023-56454/1/xml/gmb-2023-56454.xml
                    api_url = (f"https://repository.overheid.nl/frbr/officielepublicaties/"
                              f"{parts[0]}/{parts[1]}/{license_id}/1/xml/{license_id}.xml")
                    return api_url
                    
        except Exception as e:
            _LOGGER.debug(f"Could not build API URL for {url_doc}: {e}")
            
        return "UNAVAILABLE"

    def _extract_locations(self, tp_meta):
        """Extract location coordinates from tp_meta (simplified version)."""
        locations = []
        
        try:
            gebiedsmarkering = tp_meta.get("gebiedsmarkering", [])
            if not isinstance(gebiedsmarkering, list):
                gebiedsmarkering = [gebiedsmarkering]
                
            for markering in gebiedsmarkering:
                if not isinstance(markering, dict):
                    continue
                    
                # Check for Punt with locatiepunt (simple coordinate)
                punt = markering.get("Punt", {})
                if isinstance(punt, dict) and "locatiepunt" in punt:
                    locatiepunt = punt["locatiepunt"]
                    if isinstance(locatiepunt, str) and " " in locatiepunt:
                        locations.append(locatiepunt)
                        
                # Check for Adres with locatiepunt
                adres = markering.get("Adres", {})
                if isinstance(adres, dict) and "locatiepunt" in adres:
                    locatiepunt = adres["locatiepunt"]
                    if isinstance(locatiepunt, str) and " " in locatiepunt:
                        locations.append(locatiepunt)
                        
        except Exception as e:
            _LOGGER.debug(f"Error extracting locations: {e}")
            
        return locations

    def _create_individual_sensors(self):
        """Create individual sensors for announcements."""
        if self._individual_sensors_created:
            return
            
        try:
            from .individual_sensors import BekendmakingIndividualSensor, TypeHistorySensor
            
            # Create individual sensors for announcements
            individual_sensors = []
            for i, announcement in enumerate(self._data[:10]):  # Max 10 individual sensors
                individual_sensor = BekendmakingIndividualSensor(announcement, self, i)
                individual_sensors.append(individual_sensor)
            
            # Create sensors per type with history and latest per type
            type_counts = {}
            for item in self._data:
                item_type = item.get('type', 'onbekend')
                type_counts[item_type] = type_counts.get(item_type, 0) + 1
            
            # Create type sensors for types with more than 1 announcement
            for announcement_type, count in type_counts.items():
                if count > 0:  # Create sensor for all types
                    type_sensor = TypeHistorySensor(self, announcement_type)
                    individual_sensors.append(type_sensor)
                    
                    # TypeHistorySensor already has clickable links now
            
            if individual_sensors and self._async_add_entities:
                self.hass.loop.call_soon_threadsafe(
                    lambda: self.hass.async_create_task(
                        self._async_add_entities(individual_sensors, update_before_add=False)
                    )
                )
                self._individual_sensors_created = True
                _LOGGER.info(f"Created {len(individual_sensors)} individual sensors ({len(type_counts)} type sensors)")
        except Exception as e:
            _LOGGER.error(f"Error creating individual sensors: {e}")

    async def async_manual_update(self):
        """Manually update the sensor (called by button)."""
        _LOGGER.info(f"Manual update triggered for {self._name}")
        await self.async_update()


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensor entities from config entry."""
    _LOGGER.info("Setting up Overheid Bekendmakingen sensor entities")
    
    # Import individual sensors
    from .individual_sensors import BekendmakingIndividualSensor, HistorySensor, TypeFilterSensor
    
    # Get configuration
    config = entry.data
    name = config.get("name", "Overheid Bekendmakingen")
    latitude = config.get("latitude")
    longitude = config.get("longitude")
    radius = config.get("radius", 5000)
    update_interval = config.get("update_interval_hours", 6)
    debug = config.get("debug", False)
    
    # Create main sensor
    main_sensor = BekendmakingenSensor(
        hass=hass,
        name=name,
        latitude=latitude,
        longitude=longitude,
        range_km=radius,
        interval_hours=update_interval,
        municipality=DEFAULT_MUNICIPALITY,  # Always use default municipality
        unique_id=entry.entry_id,
        debug=debug
    )
    
    # Create additional sensors (excluding Range and Interval - now Number entities)
    additional_sensors = [
        HistorySensor(main_sensor),
        TypeFilterSensor(main_sensor)
    ]
    
    # Store async_add_entities for later use
    main_sensor._async_add_entities = async_add_entities
    
    # Add all sensors
    all_sensors = [main_sensor] + additional_sensors
    async_add_entities(all_sensors, update_before_add=True)
    
    # Store sensor reference for other platforms
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    if entry.entry_id not in hass.data[DOMAIN]:
        hass.data[DOMAIN][entry.entry_id] = {}
    
    # Convert entry.data to dict if needed and store references
    entry_dict = hass.data[DOMAIN][entry.entry_id]
    entry_dict['main_sensor'] = main_sensor
    entry_dict['config'] = dict(config)
    
    _LOGGER.info(f"Sensor {name} toegevoegd met unieke ID: {entry.entry_id}")