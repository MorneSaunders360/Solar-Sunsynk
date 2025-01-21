"""Config flow for Sunsynk integration."""
from __future__ import annotations

from typing import Any

import aiohttp
from .sunsynkapi import sunsynk_api
import voluptuous as vol
from datetime import timedelta
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME,CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    client = sunsynk_api(data[CONF_USERNAME],data[CONF_PASSWORD],hass)
    try:
        await client.authenticate(data[CONF_USERNAME], data[CONF_PASSWORD])

    except aiohttp.ClientResponseError as e:
        if e.status == 401:
            raise InvalidAuth
        else:
            raise e
    except aiohttp.client_exceptions.ClientConnectorError:
        raise CannotConnect

    else:
        return {"Sunsynk Solar": data[CONF_USERNAME]}


class SunsynkConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sunsynk."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""

        errors = {}
        if user_input:

            try:
                await validate_input(self.hass, user_input)
                # Check if already configured
                existing_entry = await self.async_set_unique_id(user_input[CONF_USERNAME])
                if existing_entry:
                    # Update the existing entry
                    self.hass.config_entries.async_update_entry(existing_entry, data=user_input)
                    return self.async_abort(reason="already_configured")
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"

            return self.async_create_entry(
                    title=user_input["username"], data=user_input
            )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
    async def async_step_reauth(self, data):
        """Perform reauth upon an authentication error."""
        return await self.async_step_user()

class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class CannotConnect(HomeAssistantError):
    """Error to indicate there is a problem connecting."""
