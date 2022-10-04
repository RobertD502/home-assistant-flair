"""Flair Component."""
from __future__ import annotations

from flairaio.exceptions import FlairAuthError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET
from homeassistant.core import HomeAssistant

from .const import DOMAIN, LOGGER, PLATFORMS
from .coordinator import FlairDataUpdateCoordinator
from .util import NoStructuresError, NoUserError, async_validate_api


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Flair from a config entry."""

    coordinator = FlairDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Flair config entry."""

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        del hass.data[DOMAIN][entry.entry_id]
        if not hass.data[DOMAIN]:
            del hass.data[DOMAIN]
    return unload_ok


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old entry."""

    if entry.version == 1:
        LOGGER.warning("The current version of home-assistant-flair requires OAuth2 credentials. Please reauthorize using OAuth2 credentials (NOT OAuth1).")
        entry.async_start_reauth(hass)

    if entry.version == 2:
        LOGGER.info("Migrating Flair config entry to version 2.1")
        # Prior to release 0.1.3, unique_id was not set when a user migrated
        # from OAuth1.0 to 2.0 via reauthentication. In this case, if not present,
        # unique_id needs to be set and entry version set to latest version.
        if not entry.unique_id:
            entry.unique_id = entry.data['client_id']
        entry.version = 2.1

    return True
