"""Flair Component."""
from __future__ import annotations

import importlib
import sys

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_CLIENT_ID
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.service import async_register_admin_service
from homeassistant.loader import async_get_integration

from .const import DOMAIN, LOGGER, PLATFORMS
from .coordinator import FlairDataUpdateCoordinator
from .util import NoStructuresError, NoUserError, async_validate_api


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Flair from a config entry."""

    coordinator = FlairDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _register_reload_code(hass)

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
        # unique_id needs to be set and entry version set to the latest version.

        hass.config_entries.async_update_entry(
            entry,
            unique_id=entry.data[CONF_CLIENT_ID],
            version=2.1
        )

    return True

async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: dr.DeviceEntry
) -> bool:
    """Remove a config entry from a device."""
    return True


def _forget_code(hass: HomeAssistant, package: str, domain: str) -> None:
    """Drop a package's modules so the next setup imports them from disk again.

    Home Assistant keeps its own copy of each imported integration module
    (hass.data["components"], keyed "<domain>" and "<domain>.<platform>") next
    to Python's sys.modules; both have to go.
    """
    for cache, root in (
        (sys.modules, package),
        (hass.data.get("components", {}), domain),
        (hass.data.get("missing_platforms", {}), domain),
    ):
        for name in [n for n in cache if n == root or n.startswith(root + ".")]:
            del cache[name]
    importlib.invalidate_caches()  # a file added since the last import may not be found


@callback
def _register_reload_code(hass: HomeAssistant) -> None:
    """Dev: flair.reload_code loads the Python files from disk without a restart."""

    async def _reload_code(call: ServiceCall) -> None:
        # Disabled and ignored entries are never set up, so they are not ours to reload.
        entries = hass.config_entries.async_entries(
            DOMAIN, include_ignore=False, include_disabled=False
        )
        for entry in entries:
            if not await hass.config_entries.async_unload(entry.entry_id):
                raise HomeAssistantError(
                    f"{DOMAIN} did not unload; restart Home Assistant instead"
                )
        _forget_code(hass, __name__, DOMAIN)
        try:
            await hass.async_add_import_executor_job(_import_code, __name__)
        except Exception as err:
            # This handler stays registered, so the action works again once the code is fixed.
            raise HomeAssistantError(
                f"{DOMAIN} is unloaded: the new code did not load ({err}). "
                f"Fix it and call {DOMAIN}.reload_code again"
            ) from err
        failed = [
            e.title
            for e in entries
            if not await hass.config_entries.async_setup(e.entry_id)
        ]
        if failed:
            raise HomeAssistantError(
                f"{DOMAIN} did not set up again for {failed}; see the log"
            )

    async_register_admin_service(hass, DOMAIN, "reload_code", _reload_code)
