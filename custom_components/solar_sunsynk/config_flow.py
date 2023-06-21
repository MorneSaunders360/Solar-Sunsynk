import voluptuous as vol
from homeassistant import config_entries
from .sunsynkapi import sunsynk_api
from .const import DOMAIN
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
            region = user_input.get("region")
            if not username or not password:
                errors["base"] = "empty_credentials"
            else:
                sunsynk = sunsynk_api(region,username,password, self.hass)
                json_response = await sunsynk.authenticate(username, password)
                if json_response.get('success') == True:
                    valid = True
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
                    vol.Required("region"): vol.In(["Region 1", "Region 2"]),
                }
            ),
            errors=errors,
        )

config_entries.HANDLERS.register(DOMAIN)(SolarSunsynkConfigFlow)




