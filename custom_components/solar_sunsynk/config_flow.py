import logging
import requests
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

DOMAIN = "solar_sunsynk"

_LOGGER = logging.getLogger(__name__)

class SolarSunsynkConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        # Check if a configuration entry already exists. If so, abort the current flow.
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors = {}
        if user_input is not None:
            username = user_input.get("username")
            password = user_input.get("password")
            if not username or not password:
                errors["base"] = "empty_credentials"
            else:
                valid = await self._validate_credentials(username, password)
                if valid:
                    return self.async_create_entry(title="Solar Sunsynk", data=user_input)
                else:
                    errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("username"): str,
                    vol.Required("password"): str,
                }
            ),
            errors=errors,
        )


    async def _validate_credentials(self, username, password):
        def check_credentials():
            validAuth = False
            try:
                headers = {
                    'Content-type': 'application/json',
                    'Accept': 'application/json'
                }

                payload = {
                    "username": username,
                    "password": password,
                    "grant_type": "password",
                    "client_id": "csp-web"
                }

                urlAuth = "https://pv.inteless.com/oauth/token"
                responseAuth = requests.post(urlAuth, json=payload, headers=headers)
                json_response = responseAuth.json()
                if json_response.get('success') == True:
                    validAuth = True
                return validAuth
            except Exception as e:
                return validAuth

        return await self.hass.async_add_executor_job(check_credentials)

config_entries.HANDLERS.register(DOMAIN)(SolarSunsynkConfigFlow)




