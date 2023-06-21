from homeassistant import config_entries, core
import logging
from .const import SetSolarSettingsSchema,DOMAIN
from .sunsynkapi import sunsynk_api
import json
_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    return True

async def async_setup_entry(hass, entry):
    return await hass.async_add_executor_job(setup, hass, entry)

def setup(hass: core.HomeAssistant, entry: config_entries.ConfigEntry):

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    USERNAME = entry.data["username"]
    PASSWORD = entry.data["password"]
    region = entry.data["region"]
    sunsynk = sunsynk_api(region,USERNAME,PASSWORD, hass)

    async def async_set_solar_settings(call):
        sn = call.data.get("sn")
        new_dict = {}
        new_dict["sn"] = sn
        for key in call.data.keys():
            new_dict[key] = call.data[key]
        # Prepare the payload
        response = await sunsynk.set_settings(sn, new_dict)
        if response.get('success') == True:
            # Request successful
            return True
        else:
            # Request failed
            return False

    hass.services.async_register(
        DOMAIN, "set_solar_settings", async_set_solar_settings, SetSolarSettingsSchema
    )

    # Return boolean to indicate that initialization was successful.
    return True
