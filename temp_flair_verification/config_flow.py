"""Config Flow for Flair integration."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from flairaio.exceptions import FlairAuthError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DEFAULT_NAME, DOMAIN
from .util import NoStructuresError, NoUserError, async_validate_api


DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CLIENT_ID): cv.string,
        vol.Required(CONF_CLIENT_SECRET): cv.string,
    }
)


class FlairConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Flair integration."""

    VERSION = 2.1

    entry: config_entries.ConfigEntry | None

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> FlowResult:
        """Handle re-authentication with Flair."""

        self.entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm re-authentication with Flair."""

        errors: dict[str, str] = {}

        if user_input:
            client_id = user_input[CONF_CLIENT_ID]
            client_secret = user_input[CONF_CLIENT_SECRET]
            try:
                await async_validate_api(self.hass, client_id, client_secret)
            except FlairAuthError:
                errors["base"] = "invalid_auth"
            except ConnectionError:
                errors["base"] = "cannot_connect"
            except NoStructuresError:
                errors["base"] = "no_structures"
            except NoUserError:
                errors["base"] = "no_user"
            else:
                assert self.entry is not None

                if self.entry.version == 1:
                    self.entry.version = 2.1
                    self.entry.unique_id = client_id
                    self.hass.config_entries._async_schedule_save()

                self.hass.config_entries.async_update_entry(
                    self.entry,
                    data={
                        **self.entry.data,
                        CONF_CLIENT_ID: client_id,
                        CONF_CLIENT_SECRET: client_secret,
                    },
                )

                await self.hass.config_entries.async_reload(self.entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_user(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""

        errors: dict[str, str] = {}

        if user_input:
            client_id = user_input[CONF_CLIENT_ID]
            client_secret = user_input[CONF_CLIENT_SECRET]
            try:
                await async_validate_api(self.hass, client_id, client_secret)
            except FlairAuthError:
                errors["base"] = "invalid_auth"
            except ConnectionError:
                errors["base"] = "cannot_connect"
            except NoStructuresError:
                errors["base"] = "no_structures"
            except NoUserError:
                errors["base"] = "no_user"
            else:
                await self.async_set_unique_id(client_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=DEFAULT_NAME,
                    data={CONF_CLIENT_ID: client_id, CONF_CLIENT_SECRET: client_secret},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )
