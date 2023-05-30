import requests
import json
import logging
from datetime import timedelta
from .config_flow import SolarSunsynkConfigFlow
from homeassistant.helpers import device_registry as dr
from homeassistant import config_entries, core
DOMAIN = "solar_sunsynk"
SCAN_INTERVAL = timedelta(seconds=10)

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    return True

async def async_setup_entry(hass, entry):
    return await hass.async_add_executor_job(setup, hass, entry)

def setup(hass: core.HomeAssistant, entry: config_entries.ConfigEntry):
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
    config_entry_id=entry.entry_id,
    identifiers={(DOMAIN, '1.0.0.0')},  # Assuming 'id' is the unique identifier for the device
    name="API",  # Assuming 'name' is the name of the device
    manufacturer="MorneSaunders360",  # Replace with the manufacturer's name
    model="API",  # Replace with the model of the device
    sw_version="1.0.0.4"  # Replace with the software version of the device
    )
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    # Return boolean to indicate that initialization was successful.
    return True

