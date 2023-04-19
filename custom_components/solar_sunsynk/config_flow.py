import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

DATA_SCHEMA = vol.Schema(
    {
        vol.Required("username"): str,
        vol.Required("password"): str,
    }
)

class SolarSunsynkConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solar Sunsynk."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            await self.async_set_unique_id(user_input["username"])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=user_input["username"], data=user_input)

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

    async def async_step_import(self, import_info):
        """Handle the import."""
        return await self.async_step_user(import_info)

    @callback
    def _abort_if_unique_id_configured(self, updates=None):
        """Abort if a config entry already exists for the entered username."""
        for entry in self._async_current_entries():
            if entry.unique_id == self.unique_id:
                self.hass.config_entries.async_update_entry(entry, data=updates)
                raise config_entries.AbortFlow("already_configured")
