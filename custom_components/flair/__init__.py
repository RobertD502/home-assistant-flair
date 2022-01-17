"""Support for Flair"""
import asyncio
import logging
import voluptuous as vol
from flair import FlairHelper

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET
)
from .const import DOMAIN, PLATFORMS


_LOGGER = logging.getLogger(__name__)


def setup(hass, config):
    """Setup of the component"""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Flair integration from a config entry."""
    client_id = entry.data[CONF_CLIENT_ID]
    client_secret = entry.data[CONF_CLIENT_SECRET]

    _LOGGER.info("Initializing the Flair API")
    flair = await hass.async_add_executor_job(FlairHelper, client_id, client_secret)
    _LOGGER.info("Connected to API")

    hass.data[DOMAIN] = flair

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Flair config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.pop(DOMAIN)
    return unload_ok
