from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.components.sensor import SensorEntity
from functools import partial
from datetime import timedelta
import aiohttp
import async_timeout
import json
import logging
# Constants
_LOGGER = logging.getLogger(__name__)
UPDATE_INTERVAL = 10
AUTH_URL = "https://pv.inteless.com/oauth/token"
API_URL = "https://pv.inteless.com/api/v1/plants?page=1&limit=10&name=&status="
async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensors from config entry."""
    session = aiohttp.ClientSession()
    USERNAME = config_entry.data["username"]
    PASSWORD = config_entry.data["password"]
    # Perform authentication and get access token
    headers = {
        'Content-type':'application/json', 
        'Accept':'application/json'
    }
    payload = {
        "username": USERNAME,
        "password": PASSWORD,
        "grant_type":"password",
        "client_id":"csp-web"
    }
    async with session.post(AUTH_URL, json=payload, headers=headers) as resp:
        responseAuth = await resp.json()
    token = responseAuth["data"]["access_token"]

    # Create the data update coordinator
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="sensor",
        update_method=partial(fetch_data, session, token),
        update_interval=timedelta(seconds=UPDATE_INTERVAL),
    )
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    # Create sensor entities and add them
    async_add_entities(SolarSunSynkSensor(coordinator, result_key) for result_key in coordinator.data.keys())

class SolarSunSynkSensor(SensorEntity):
    """Representation of a sensor entity for Solar Sunsynk data."""
    def __init__(self, coordinator, result_key):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.result_key = result_key

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"solar_sunsynk_2{self.result_key}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.result_key

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self.result_key]

    async def async_update(self):
        """Update the sensor."""
        await self.coordinator.async_request_refresh()

async def fetch_data(session, token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # Fetch plant data
    async with async_timeout.timeout(10):
        async with session.get(API_URL, headers=headers) as resp:
            data = await resp.json()
            if resp.status != 200:
                raise UpdateFailed(f"Request failed: {data}")
            infos = data["data"]["infos"]
    
    # Combine all the plant data into a single dictionary
    combined_data = {}
    for info in infos:
        id = info["id"]
        info = {k: str(v)[:255] for k, v in info.items() if v is not None}
        combined_data.update(info)

        # Fetch additional data for each plant
        async with async_timeout.timeout(10):
            # Fetch energy flow data
            async with session.get(f"https://pv.inteless.com/api/v1/plant/energy/{id}/flow", headers=headers) as resp:
                energy_flow_data = await resp.json()
                energy_flow_data = {k: str(v)[:255] for k, v in energy_flow_data["data"].items() if v is not None}
                combined_data.update(energy_flow_data)

            # Fetch realtime data
            async with session.get(f"https://pv.inteless.com/api/v1/plant/{id}/realtime?id={id}", headers=headers) as resp:
                realtime_data = await resp.json()
                realtime_data = {k: str(v)[:255] for k, v in realtime_data["data"].items() if v is not None}
                combined_data.update(realtime_data)

    return combined_data
