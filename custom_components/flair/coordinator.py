"""DataUpdateCoordinator for the Flair integration."""
from __future__ import annotations

from datetime import timedelta

from flairaio import FlairClient
from flairaio.exceptions import FlairAuthError, FlairError
from flairaio.model import FlairData


from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, LOGGER, TIMEOUT


class FlairDataUpdateCoordinator(DataUpdateCoordinator):
    """Flair Data Update Coordinator."""

    data: FlairData

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the Flair coordinator."""

        self.client = FlairClient(
            entry.data[CONF_CLIENT_ID],
            entry.data[CONF_CLIENT_SECRET],
            session=async_get_clientsession(hass),
            timeout=TIMEOUT,
        )
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> FlairData:
        """Fetch data from Flair."""

        try:
            data = await self.client.get_flair_data()
        except FlairAuthError as error:
            raise ConfigEntryAuthFailed(error) from error
        except FlairError as error:
            raise UpdateFailed(error) from error
        if not data.structures:
            raise UpdateFailed("No Structures found")
        return data
