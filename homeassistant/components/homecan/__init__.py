"""The HomeCAN integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import (
    CONF_HOST,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_ACCESS_TOKEN,
    CONF_PORT,
    CONF_TIMEOUT,
    CONF_API_KEY,
    CONF_NAME,
    Platform
)

from datetime import timedelta
import logging

from .homecanio import HomeCANio
from .coordinator import HomeCANupdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Supported platforms
PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    # Platform.LIGHT,
    ]


async def async_setup_entry(hass: HomeAssistant, 
                            entry: ConfigEntry) -> bool:
    """Set up HomeCAN from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    host: str = entry.data[CONF_HOST]
    username: str = entry.data[CONF_USERNAME]
    password: str = entry.data[CONF_PASSWORD]

    api = HomeCANio(host, username, password)
    coordinator = HomeCANupdateCoordinator(hass, api)
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

