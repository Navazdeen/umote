"""image.umote_artwork: the Cast artwork, shrunk to 212x76 baseline JPEG."""
from __future__ import annotations

import logging

from homeassistant.components.image import ImageEntity
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util import dt as dt_util

from .artwork import shrink
from .const import TV_CAST

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities) -> None:
    async_add_entities([ArtworkImage(hass)])


class ArtworkImage(ImageEntity):
    _attr_unique_id = "umote_artwork"
    _attr_name = "umote artwork"
    _attr_content_type = "image/jpeg"
    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(hass)
        self.entity_id = "image.umote_artwork"
        self._bytes: bytes | None = None
        self._source: str | None = None

    @property
    def available(self) -> bool:
        return self._bytes is not None

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(async_track_state_change_event(self.hass, [TV_CAST], self._on_cast))
        await self._refresh()

    @callback
    def _on_cast(self, _event: Event) -> None:
        self.hass.async_create_task(self._refresh())

    async def _refresh(self) -> None:
        st = self.hass.states.get(TV_CAST)
        picture = st.attributes.get("entity_picture") if st and st.state not in ("off", "unavailable") else None
        if picture == self._source:
            return
        self._source = picture
        data = await self._fetch() if picture else None
        self._bytes = await self.hass.async_add_executor_job(shrink, data) if data else None
        self._attr_image_last_updated = dt_util.utcnow()
        self.async_write_ha_state()

    async def _fetch(self) -> bytes | None:
        component = self.hass.data.get("media_player")
        entity = component.get_entity(TV_CAST) if component else None
        if entity is None:
            return None
        try:
            data, _ctype = await entity.async_get_media_image()
        except Exception as err:  # noqa: BLE001 - artwork is best effort
            _LOGGER.debug("artwork fetch failed: %s", err)
            return None
        return data

    async def async_image(self) -> bytes | None:
        return self._bytes
