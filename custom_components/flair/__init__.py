"""Support for Flair"""
import asyncio
import logging
import voluptuous as vol
from flair import FlairHelper

import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET
)
from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)


def setup(hass, config):
    """Setup of the component"""
    return True


async def async_setup_entry(hass, config_entry):
    """Set up Flair integration from a config entry."""
    client_id = config_entry.data.get(CONF_CLIENT_ID)
    client_secret = config_entry.data.get(CONF_CLIENT_SECRET)

    _LOGGER.info("Initializing the Flair API")
    flair = await hass.async_add_executor_job(FlairHelper, client_id, client_secret)
    _LOGGER.info("Connected to API")

    hass.data[DOMAIN] = flair

    hass.async_add_job(
        hass.config_entries.async_forward_entry_setup(config_entry, "sensor")
    )

    hass.async_add_job(
        hass.config_entries.async_forward_entry_setup(config_entry, "fan")
    )

    hass.async_add_job(
        hass.config_entries.async_forward_entry_setup(config_entry, "climate")
    )

    return True
