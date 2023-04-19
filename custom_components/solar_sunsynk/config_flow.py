import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.setup(title=DOMAIN, data=user_input)

        schema = vol.Schema({
            vol.Required('username'): str,
            vol.Required('password'): str,
        })

        return self.async_show_form(step_id='user', data_schema=schema)
