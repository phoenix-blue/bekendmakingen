"""Constanten voor de Overheid Bekendmakingen integratie - Versie 2.0 (Werkende API)."""
from datetime import datetime, timedelta

DOMAIN = "overheid_bekendmakingen"
NAME = "Overheid Bekendmakingen"
VERSION = "2.1.2"  # Force config flow update - clean coordinate-only setup

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
DEFAULT_RADIUS = 5000  # 5km in meters
DEFAULT_UPDATE_INTERVAL = 6  # 6 uur
DEFAULT_SCAN_INTERVAL = 21600  # 6 uur in seconden
DEFAULT_MAP_DISPLAY_DAYS = 7  # dagen
DEFAULT_ARCHIVE_DAYS = 30  # dagen

# API Configuration - Gebaseerd op werkende basgroot implementatie
API_BASE_URL = "https://repository.overheid.nl/sru"
MAXIMUM_RECORDS = 1000
START_RECORD = 1

# Standaard gemeente configuratie (wordt overschreven door gebruiker)
DEFAULT_MUNICIPALITY = "Nederland"
MUNICIPALITY_COORDINATES = {
    "lat": 52.3676,  # Centrum Nederland
    "lng": 4.9041
}

# Date configuration - zoek 6 weken terug voor recente bekendmakingen
LOOKBACK_WEEKS = 6

def get_start_date():
    """Get start date for queries (6 weeks back)."""
    return (datetime.now() - timedelta(weeks=LOOKBACK_WEEKS)).strftime("%Y-%m-%d")

# Query configuratie zoals in werkende implementatie
def build_query(municipality_name, start_date):
    """Build SRU query like working basgroot implementation."""
    return (f"c.product-area==officielepublicaties AND "
            f"dt.modified>={start_date} AND "
            f'dt.creator="{municipality_name}" '
            f"sortBy dt.modified /sort.descending")

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

# Icon mapping based on basgroot implementation + uitgebreid  
# Credit: Gebaseerd op https://github.com/basgroot/bekendmakingen
ICON_MAPPING = {
    "aanvraag": "mdi:file-plus-outline",
    "vergunning": "mdi:file-certificate-outline", 
    "bouwen": "mdi:hammer-wrench",
    "slopen": "mdi:bulldozer", 
    "uitweg en inrit": "mdi:road-variant",
    "kappen": "mdi:tree",
    "milieu": "mdi:leaf-circle-outline",
    "natuur": "mdi:nature-people",
    "reclame": "mdi:billboard",
    "brandveilig gebruik": "mdi:fire-extinguisher",
    "ruimtelijke ordening": "mdi:city-variant-outline",
    "evenement": "mdi:calendar-star",
    "bed & breakfast": "mdi:bed-empty",
    "vakantieverhuur": "mdi:home-variant-outline",
    "boomkap": "mdi:chainsaw",
    "oplaadplaats": "mdi:ev-station",
    "opladen": "mdi:battery-charging-high",
    "laadpaal": "mdi:ev-station",
    "apv vergunning": "mdi:shield-check-outline",
    "parkeervakken": "mdi:parking",
    "tvm": "mdi:traffic-light-outline",
    "verkeer": "mdi:car-multiple",
    # Uitgebreide iconen voor meer bekendmaking types
    "sloop": "mdi:demolish",
    "verbouwing": "mdi:tools",
    "renovatie": "mdi:wrench-outline", 
    "dakkapel": "mdi:home-roof",
    "schuur": "mdi:barn",
    "garage": "mdi:garage-variant",
    "terras": "mdi:table-furniture",
    "zwembad": "mdi:pool",
    "hek": "mdi:gate-arrow-right",
    "schuurtje": "mdi:storage-tank-outline",
    "uitbouw": "mdi:home-plus-outline",
    "aanbouw": "mdi:home-plus",
    "monumentaal": "mdi:bank-outline",
    "bestemmingsplan": "mdi:map-legend",
    "wijziging": "mdi:pencil-outline",
    "bezwaar": "mdi:alert-octagon-outline",
    "intrekking": "mdi:cancel",
    "verlening": "mdi:calendar-plus-outline",
    "horeca": "mdi:silverware-fork-knife",
    "horecabedrijf": "mdi:storefront-outline",
    "café": "mdi:coffee-outline",
    "restaurant": "mdi:silverware-fork-knife",
    "winkel": "mdi:store-outline",
    "detailhandel": "mdi:shopping-outline",
    "kantoor": "mdi:office-building-outline",
    "bedrijf": "mdi:domain",
    "industrie": "mdi:factory",
    "woning": "mdi:home-outline",
    "flat": "mdi:office-building-marker",
    "appartement": "mdi:home-city-outline",
    "onttrekkingsvergunning": "mdi:home-minus",
    "omzettingsvergunning": "mdi:home-switch",
    "kamerverhuur": "mdi:home-account", 
    "water": "mdi:water",
    "boot": "mdi:ferry",
    "default": "mdi:file-document-outline"
}

def get_icon_for_type(title, announcement_type):
    """Get appropriate icon based on announcement type and title with smart detection."""
    title_lower = title.lower() if title else ""
    type_lower = announcement_type.lower() if announcement_type else ""
    combined = f"{title_lower} {type_lower}"
    
    # Prioriteit voor specifieke trefwoorden in titel
    priority_keywords = {
        "aanvraag": "mdi:file-plus-outline",
        "verlenging": "mdi:calendar-plus-outline", 
        "intrekking": "mdi:cancel",
        "wijziging": "mdi:pencil-outline",
        "bezwaar": "mdi:alert-octagon-outline"
    }
    
    for keyword, icon in priority_keywords.items():
        if keyword in combined:
            return icon
    
    # Slimme detectie voor bouwactiviteiten
    if any(word in combined for word in ["dakkapel", "dakraam", "dak"]):
        return ICON_MAPPING["dakkapel"]
    if any(word in combined for word in ["garage", "carport"]):
        return ICON_MAPPING["garage"]  
    if any(word in combined for word in ["uitbouw", "uitbreiding"]):
        return ICON_MAPPING["uitbouw"]
    if any(word in combined for word in ["aanbouw", "bijgebouw"]):
        return ICON_MAPPING["aanbouw"]
    if any(word in combined for word in ["schuur", "schuurtje", "tuinhuis"]):
        return ICON_MAPPING["schuur"]
    if any(word in combined for word in ["zwembad", "jacuzzi", "spa"]):
        return ICON_MAPPING["zwembad"]
    if any(word in combined for word in ["terras", "pergola", "overkapping"]):
        return ICON_MAPPING["terras"]
    
    # Slimme detectie voor bedrijfsactiviteiten  
    if any(word in combined for word in ["horeca", "café", "restaurant", "eetcafé"]):
        return ICON_MAPPING["horeca"]
    if any(word in combined for word in ["winkel", "detailhandel", "verkoop"]):
        return ICON_MAPPING["winkel"]
    if any(word in combined for word in ["kantoor", "praktijk", "bureau"]):
        return ICON_MAPPING["kantoor"]
    
    # Check exacte matches in ICON_MAPPING
    for key, icon in ICON_MAPPING.items():
        if key in type_lower or key in title_lower:
            return icon
    
    return ICON_MAPPING["default"]

