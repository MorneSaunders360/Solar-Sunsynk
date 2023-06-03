from homeassistant import config_entries, core
DOMAIN = "solar_sunsynk"
async def async_setup(hass, config):
    return True

async def async_setup_entry(hass, entry):
    return await hass.async_add_executor_job(setup, hass, entry)

def setup(hass: core.HomeAssistant, entry: config_entries.ConfigEntry):

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    # Return boolean to indicate that initialization was successful.
    return True

