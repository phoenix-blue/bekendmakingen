"""Geo Location platform voor Overheid Bekendmakingen - Kaartweergave."""

from __future__ import annotations

import asyncio
import logging
from typing import Iterable

from homeassistant.components.geo_location import GeolocationEvent
from homeassistant.util import slugify

from .const import DOMAIN, DEFAULT_MUNICIPALITY, MAP_COLOR, get_icon_for_type

_LOGGER = logging.getLogger(__name__)

_MAX_OBJECT_ID_LEN = 64
_PERIODIC_UPDATE_INTERVAL = 30  # seconden


async def async_setup_entry(hass, entry, async_add_entities):
	"""Set up geo location entities from config entry."""
	_LOGGER.info("🗺️ Setting up Overheid Bekendmakingen geo location entities")

	max_wait = 60
	waited = 0

	while waited < max_wait:
		if (
			DOMAIN in hass.data
			and entry.entry_id in hass.data[DOMAIN]
			and "main_sensor" in hass.data[DOMAIN][entry.entry_id]
		):
			main_sensor = hass.data[DOMAIN][entry.entry_id].get("main_sensor")
			if main_sensor and getattr(main_sensor, "_name", None):
				break

		await asyncio.sleep(2)
		waited += 2

	if (
		DOMAIN not in hass.data
		or entry.entry_id not in hass.data[DOMAIN]
		or "main_sensor" not in hass.data[DOMAIN][entry.entry_id]
	):
		_LOGGER.error(
			"Timeout: Sensor data niet beschikbaar na %s seconden wachten", max_wait
		)
		return False

	sensor_data = hass.data[DOMAIN][entry.entry_id]
	main_sensor = sensor_data.get("main_sensor")

	if not main_sensor or not getattr(main_sensor, "_name", None):
		_LOGGER.error(
			"Main sensor niet geldig voor geo location setup. main_sensor=%s",
			main_sensor,
		)
		if main_sensor:
			_LOGGER.error(
				"main_sensor attributes: entity_id=%s, name=%s",
				getattr(main_sensor, "entity_id", None),
				getattr(main_sensor, "_name", None),
			)
		return False

	_LOGGER.info(
		"✅ Main sensor gevonden voor geo location: %s",
		getattr(main_sensor, "_name", "Unknown"),
	)

	manager = BekendmakingenGeoManager(hass, entry, async_add_entities, main_sensor)
	await manager.async_start()

	hass.data[DOMAIN][entry.entry_id]["geo_manager"] = manager
	_LOGGER.info("Geo location manager succesvol gestart")
	return True


class BekendmakingenGeoManager:
	"""Manager voor geo location entiteiten."""

	def __init__(self, hass, entry, async_add_entities, main_sensor):
		self._hass = hass
		self._entry = entry
		self._async_add_entities = async_add_entities
		self._main_sensor = main_sensor
		self._entities: dict[str, BekendmakingenGeoEntity] = {}
		self._periodic_task: asyncio.Task | None = None

	async def async_start(self) -> None:
		"""Start monitoring van de hoofdsensor."""
		try:
			_LOGGER.debug(
				"Starting geo location manager voor %s",
				getattr(self._main_sensor, "_name", "onbekend"),
			)

			await self._update_geo_entities()

			async def periodic_update() -> None:
				while True:
					await asyncio.sleep(_PERIODIC_UPDATE_INTERVAL)
					await self._update_geo_entities()

			self._periodic_task = self._hass.loop.create_task(periodic_update())

		except Exception as err:  # pragma: no cover - safeguard
			_LOGGER.error("Fout bij starten geo location manager: %s", err)
			raise

	async def async_stop(self) -> None:
		"""Stop monitoring en ruim geo entiteiten op."""
		if self._periodic_task:
			self._periodic_task.cancel()
			self._periodic_task = None

		for entity in list(self._entities.values()):
			await entity.async_remove()
		self._entities.clear()

	async def _update_geo_entities(self) -> None:
		"""Werk geo entiteiten bij op basis van sensor data."""
		if not self._main_sensor.available:
			_LOGGER.debug("Main sensor niet beschikbaar, sla geo update over")
			return

		announcements = getattr(self._main_sensor, "_data", []) or []
		_LOGGER.debug("Bijwerken van %s geo aankondigingen", len(announcements))

		current_entity_ids: set[str] = set()

		for announcement in announcements:
			locations = announcement.get("location", []) or []
			if not locations:
				fallback_lat = float(self._hass.config.latitude)
				fallback_lng = float(self._hass.config.longitude)
				locations = [f"{fallback_lat} {fallback_lng}"]

			for index, location in enumerate(locations):
				try:
					latitude, longitude = self._parse_coordinates(location)
				except ValueError:
					_LOGGER.debug("Ongeldige locatie '%s' overgeslagen", location)
					continue

				base_id = self._get_announcement_id(announcement)
				entity_key = f"{base_id}_{index}" if len(locations) > 1 else base_id
				current_entity_ids.add(entity_key)

				object_id = self._build_object_id(entity_key)
				unique_id = f"{self._entry.entry_id}_{entity_key}"

				if entity_key not in self._entities:
					entity = BekendmakingenGeoEntity(
						object_id,
						unique_id,
						announcement,
						latitude,
						longitude,
						self._main_sensor,
					)
					self._entities[entity_key] = entity
					_LOGGER.debug(
						"Toevoegen geo entity %s op (%s, %s)",
						entity.entity_id,
						latitude,
						longitude,
					)
					self._async_add_entities([entity])
				else:
					self._entities[entity_key].update_announcement(
						announcement, latitude, longitude
					)

		stale_entities = set(self._entities.keys()) - current_entity_ids
		for entity_key in stale_entities:
			entity = self._entities.pop(entity_key)
			await entity.async_remove()

	def _parse_coordinates(self, location: str) -> tuple[float, float]:
		coords = location.strip().split()
		if len(coords) < 2:
			raise ValueError("Onvoldoende coördinaten")

		coord1, coord2 = float(coords[0]), float(coords[1])

		if 50 <= coord1 <= 54 and 3 <= coord2 <= 8:
			return coord1, coord2
		if 50 <= coord2 <= 54 and 3 <= coord1 <= 8:
			return coord2, coord1

		_LOGGER.debug("Valt buiten NL-bereik (%s), gebruik HA coördinaten", location)
		return float(self._hass.config.latitude), float(self._hass.config.longitude)

	def _get_announcement_id(self, announcement: dict) -> str:
		title = announcement.get("title", "unknown")
		date = announcement.get("date", "")
		return slugify(f"{title}_{date}")[:50]

	def _build_object_id(self, suffix: str) -> str:
		slug = slugify(f"{DOMAIN}_{suffix}")
		if len(slug) > _MAX_OBJECT_ID_LEN:
			slug = slug[:_MAX_OBJECT_ID_LEN]
		return slug


class BekendmakingenGeoEntity(GeolocationEvent):
	"""Geo location entity voor een bekendmaking."""

	def __init__(
		self,
		object_id: str,
		unique_id: str,
		announcement: dict,
		latitude: float,
		longitude: float,
		main_sensor,
	) -> None:
		super().__init__()
		self.entity_id = f"geo_location.{object_id}"
		self._attr_unique_id = unique_id
		self._announcement = announcement
		self._latitude = latitude
		self._longitude = longitude
		self._main_sensor = main_sensor
		self._attr_should_poll = False
		self._attr_name = announcement.get("title", "Bekendmaking")[:50]
		self._attr_icon = get_icon_for_type(
			announcement.get("title", ""),
			announcement.get("type", ""),
		)

	@property
	def name(self) -> str:
		return self._attr_name

	@property
	def latitude(self) -> float:
		return self._latitude

	@property
	def longitude(self) -> float:
		return self._longitude

	@property
	def source(self) -> str:
		return DOMAIN

	@property
	def distance(self) -> float:
		home_lat = self._main_sensor._latitude
		home_lng = self._main_sensor._longitude

		from math import asin, cos, radians, sin, sqrt

		lon1, lat1, lon2, lat2 = map(
			radians, [home_lng, home_lat, self._longitude, self._latitude]
		)
		dlon = lon2 - lon1
		dlat = lat2 - lat1
		a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
		c = 2 * asin(sqrt(a))
		radius_km = 6371
		return c * radius_km

	@property
	def unit_of_measurement(self) -> str:
		return "km"

	@property
	def entity_picture(self) -> None:
		return None

	@property
	def state_attributes(self) -> dict:
		attrs = super().state_attributes or {}
		announcement_type = (self._announcement.get("type", "") or "").lower()

		if "bouw" in announcement_type or "sloop" in announcement_type:
			attrs["icon_color"] = "#FF6B6B"
		elif "milieu" in announcement_type or "water" in announcement_type:
			attrs["icon_color"] = "#4ECDC4"
		elif "vergunning" in announcement_type:
			attrs["icon_color"] = "#45B7D1"
		elif "ruimtelijke ordening" in announcement_type:
			attrs["icon_color"] = "#96CEB4"
		elif "faillissement" in announcement_type:
			attrs["icon_color"] = "#FECA57"
		else:
			attrs["icon_color"] = "#6C5CE7"

		return attrs

	@property
	def extra_state_attributes(self) -> dict:
		title = self._announcement.get("title", "")
		announcement_type = self._announcement.get("type", "")
		icon = get_icon_for_type(title, announcement_type)

		attrs = {
			"type": announcement_type,
			"date": self._announcement.get("date", ""),
			"description": self._announcement.get("description", ""),
			"url_doc": self._announcement.get("url_doc", ""),
			"municipality": DEFAULT_MUNICIPALITY,
			"source_info": "Gebaseerd op https://github.com/basgroot/bekendmakingen implementatie",
			"api_source": "repository.overheid.nl via SRU protocol",
			"color": MAP_COLOR,
			"icon": icon,
			"entity_picture": f"/local/mdi:{icon.replace('mdi:', '')}.svg",
		}

		api_url = self._announcement.get("url_api")
		if api_url and api_url != "UNAVAILABLE":
			attrs["url_api"] = api_url

		return attrs

	def update_announcement(
		self, announcement: dict, latitude: float, longitude: float
	) -> None:
		self._announcement = announcement
		self._latitude = latitude
		self._longitude = longitude
		self._attr_name = announcement.get("title", "Bekendmaking")[:50]
		self._attr_icon = get_icon_for_type(
			announcement.get("title", ""),
			announcement.get("type", ""),
		)
		self.async_schedule_update_ha_state()
