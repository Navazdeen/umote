"""umote: sources, Living Room tiles and artwork for the umote ESP32 remote."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .coordinator import UmoteCoordinator

PLATFORMS = [Platform.SENSOR, Platform.IMAGE]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type UmoteConfigEntry = ConfigEntry[UmoteCoordinator]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    def _coord() -> UmoteCoordinator:
        return hass.config_entries.async_loaded_entries(DOMAIN)[0].runtime_data

    async def launch(call: ServiceCall) -> None:
        await _coord().async_launch(call.data["source_id"])

    async def name_source(call: ServiceCall) -> None:
        await _coord().async_name_source(call.data["port"], call.data["name"])

    hass.services.async_register(DOMAIN, "launch", launch, vol.Schema({vol.Required("source_id"): cv.string}))
    hass.services.async_register(DOMAIN, "name_source", name_source, vol.Schema(
        {vol.Required("port"): vol.All(vol.Coerce(int), vol.Range(1, 4)), vol.Required("name"): cv.string}))
    return True


async def async_setup_entry(hass: HomeAssistant, entry: UmoteConfigEntry) -> bool:
    coord = UmoteCoordinator(hass, entry)
    await coord.async_load()
    await coord.async_config_entry_first_refresh()
    entry.runtime_data = coord
    entry.async_on_unload(coord.async_track())
    entry.async_on_unload(coord.async_shutdown_tracking)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: UmoteConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
