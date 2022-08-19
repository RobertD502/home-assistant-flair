""" Utilities for Flair Integration """
from __future__ import annotations



import async_timeout
from flairaio import FlairClient
from flairaio.exceptions import FlairAuthError
from flairaio.model import Structure, User

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import LOGGER, FLAIR_ERRORS, TIMEOUT

async def async_validate_api(hass: HomeAssistant, client_id: str, client_secret: str) -> bool:
    """ Get data from API. """
    client = FlairClient(
        client_id,
        client_secret,
        session=async_get_clientsession(hass),
        timeout=TIMEOUT,
    )

    try:
        async with async_timeout.timeout(TIMEOUT):
            users_query = await client.get_users()
            structures_query = await client.get_structures()
    except FlairAuthError as err:
        LOGGER.error(f'Could not authenticate on Flair servers: {err}')
        raise FlairAuthError from err
    except FLAIR_ERRORS as err:
        LOGGER.error(f'Failed to get information from Flair servers: {err}')
        raise ConnectionError from err

    users: dict[str, User] = users_query.users
    structures: dict[str, Structure] = structures_query.structures
    if not users:
        LOGGER.error("Could not retrieve any users from Flair servers")
        raise NoUserError
    if not structures:
        LOGGER.error('Could not retrieve any structures from Flair servers')
        raise NoStructuresError
    return True


class NoUserError(Exception):
    """ No User from Flair API. """

class NoStructuresError(Exception):
    """ No Litter Boxes from PurrSong API. """
