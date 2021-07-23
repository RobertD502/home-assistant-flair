"""Config flow of our component"""
import logging
import voluptuous as vol
from flair.flair_helper import FlairHelper
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET
)
from .const import DOMAIN
_LOGGER = logging.getLogger(__name__)

class FlairConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle our config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize Flair configuration flow"""
        self.schema = vol.Schema({
            vol.Required(CONF_CLIENT_ID): str,
            vol.Required(CONF_CLIENT_SECRET): str
        })

        self._client_id = None
        self._client_secret = None

    async def async_step_user(self, user_input=None):
        """Handle a flow start."""

        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        if not user_input:
            return self._show_form()

        self._client_id = user_input[CONF_CLIENT_ID]
        self._client_secret = user_input[CONF_CLIENT_SECRET]

        return await self._async_flair_login()


    async def _async_flair_login(self):

        errors = {}

        try:
            client = await self.hass.async_add_executor_job(FlairHelper, self._client_id, self._client_secret)
            await self.hass.async_add_executor_job(client.discover_rooms)

        except Exception:
            _LOGGER.error("Unable to connect to Flair: Failed to Log In")
            errors = {"base": "auth_error"}

        if errors:
            return self._show_form(errors=errors)

        return await self._async_create_entry()

    async def _async_create_entry(self):
        """Create the config entry."""
        config_data = {
            CONF_CLIENT_ID: self._client_id,
            CONF_CLIENT_SECRET: self._client_secret,
        }

        return self.async_create_entry(title='Flair', data=config_data)

    @callback
    def _show_form(self, errors=None):
        """Show the form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=self.schema,
            errors=errors if errors else {},
        )
