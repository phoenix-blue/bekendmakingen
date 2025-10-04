"""Constanten voor de Overheid Bekendmakingen integratie."""

DOMAIN = "overheid_bekendmakingen"
NAME = "Overheid Bekendmakingen"
VERSION = "2024.10.04.4"

# Configuratie sleutels
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude" 
CONF_RADIUS = "radius"
CONF_MANUAL_COORDINATES = "manual_coordinates"
CONF_UPDATE_INTERVAL = "update_interval_hours"
CONF_DEBUG = "debug"
CONF_MAP_DISPLAY_DAYS = "map_display_days"
CONF_ARCHIVE_DAYS = "archive_days"

# Standaard waarden
DEFAULT_RADIUS = 1000  # meters
DEFAULT_UPDATE_INTERVAL = 12  # uur
DEFAULT_SCAN_INTERVAL = 3600  # 1 uur in seconden
DEFAULT_MAP_DISPLAY_DAYS = 7  # dagen
DEFAULT_ARCHIVE_DAYS = 30  # dagen

# API endpoints - Officiële Bekendmakingen Nederlandse overheid
BASE_URL = "https://repository.overheid.nl/sru"
API_ENDPOINT = f"{BASE_URL}/Search"

# Update intervallen
MIN_TIME_BETWEEN_UPDATES = 1800  # 30 minuten

# Sensor eigenschappen
ATTR_LATEST_TITLE = "laatste_titel"
ATTR_LATEST_URL = "laatste_url"
ATTR_LATEST_DATE = "laatste_datum"
ATTR_TOTAL_COUNT = "aantal_bekendmakingen"
ATTR_ANNOUNCEMENTS = "bekendmakingen"
ATTR_LATITUDE = "breedtegraad"
ATTR_LONGITUDE = "lengtegraad"  
ATTR_RADIUS = "radius_meters"
ATTR_LAST_UPDATE = "laatst_bijgewerkt"

# Map/kaart eigenschappen voor het tonen van balletjes
MAP_ZOOM_LEVEL = 13
MAP_ICON = "mdi:file-document-outline"
MAP_COLOR = "#ff6600"  # Oranje voor Nederlandse overheid

