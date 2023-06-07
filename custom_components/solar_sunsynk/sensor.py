from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.components.sensor import SensorEntity
from functools import partial
from datetime import timedelta
import aiohttp
import async_timeout
import json
import logging
import time
import re
from datetime import datetime
# Constants
DOMAIN = "solar_sunsynk"
_LOGGER = logging.getLogger(__name__)
DEVICE_INFO = {
    "identifiers": {(DOMAIN, "solar_sunsynk")},
    "name": "Solar Sunsynk",
    "manufacturer": "MorneSaunders360",
    "model": "Sunsynk API",
    "sw_version": "1.0.12",
}
UPDATE_INTERVAL = 10
async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensors from config entry."""
    session = aiohttp.ClientSession()
    # Create the data update coordinator
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="sensor",
        update_method=partial(fetch_data, session, config_entry),
        update_interval=timedelta(seconds=UPDATE_INTERVAL),
    )
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    # Create device registry
    device_registry = hass.helpers.device_registry.async_get(hass)
    device = device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        **DEVICE_INFO,
    )
    
    # Create sensor entities and add them
    entities = []
    for result_key in coordinator.data.keys():
        entity = SolarSunSynkSensor(coordinator, result_key,device, coordinator.data.get("id"))
        entities.append(entity)
    
    async_add_entities(entities)


class SolarSunSynkSensor(SensorEntity):
    """Representation of a sensor entity for Solar Sunsynk data."""

    def __init__(self, coordinator, result_key, device, id):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.result_key = result_key
        self.device = device
        self.id = id

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes of the sensor."""
        attributes = {}
        if self.result_key == "income" and 'currency' in self.coordinator.data:
            attributes['currency_code'] = self.coordinator.data['currency']
        return attributes

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, "solar_sunsynk")},
            "name": self.device.name,
            "manufacturer": self.device.manufacturer,
            "model": self.device.model,
            "sw_version": self.device.sw_version,
            "via_device": (DOMAIN, self.device.id),
        }

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"sunsynk_{self.result_key}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"sunsynk_{self.id}_{self.result_key}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self.result_key]
    

    @property
    def unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        attributes = self.extra_state_attributes
        if self.result_key == "income":
            return attributes.get('currency_code') or "Currency"
        elif self.result_key in ["pvPower", "battPower", "gridOrMeterPower", "loadOrEpsPower", "genPower", "minPower", "pac", "etoday", "etotal", "emonth", "eyear", "totalPower"]:
            return "kWh"
        elif self.result_key == "soc" or self.result_key == "efficiency":
            return "%"
        elif self.result_key == "pac":
            return "W"
        else:
            return None

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        if self.result_key == "income":
            return "monetary"
        elif self.result_key == "soc":
            return "battery"
        elif self.result_key in ["pvPower", "battPower", "gridOrMeterPower", "loadOrEpsPower", "genPower", "minPower", "pac", "etoday", "etotal", "emonth", "eyear", "totalPower"]:
            return "power"
        elif self.result_key in ["pvTo", "toLoad", "toGrid", "toBat", "batTo", "gridTo", "genTo", "minTo", "existsGen", "existsMin", "genOn", "microOn", "existsMeter", "bmsCommFaultFlag", "existThinkPower"]:
            return "switch"
        else:
            return None


    @property
    def state_class(self):
        """Return the state class of the sensor."""
        if self.result_key in ["pvPower", "battPower", "gridOrMeterPower", "loadOrEpsPower", "genPower", "minPower", "soc", "pac", "efficiency", "etoday", "etotal", "emonth", "eyear", "income", "totalPower"]:
            return "measurement"
        else:
            return None

    async def async_update(self):
        """Update the sensor."""
        await self.coordinator.async_request_refresh()

async def get_token(session, USERNAME, PASSWORD, API_URL):
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
    try:
        async with session.post(API_URL+"oauth/token", json=payload, headers=headers) as resp:
            responseAuth = await resp.json()
        token = responseAuth["data"]["access_token"]
        expires_in = responseAuth["data"]["expires_in"]
        expiration_time = time.time() + expires_in
        return token, expiration_time
    except Exception as e:
        _LOGGER.error("Failed to get token: %s", e)
        return None, None

async def fetch_data(session, config_entry):
    USERNAME = config_entry.data["username"]
    PASSWORD = config_entry.data["password"]
    region = config_entry.data["region"]
    if region == "Region 1":
        API_URL = "https://pv.inteless.com/"
    elif region == "Region 2":
        API_URL = "https://api.sunsynk.net/"
    token, expiration_time = await get_token(session, USERNAME, PASSWORD, API_URL)
    if time.time() > expiration_time:
        token, expiration_time = await get_token(session, USERNAME, PASSWORD, API_URL)
    headers = {"Authorization": f"Bearer {token}"}
    # Fetch plant data
    async with session.get(f"{API_URL}api/v1/plants?page=1&limit=10&name=&status=", headers=headers) as resp:
        data = await resp.json()
        if resp.status != 200:
            raise UpdateFailed(f"Request failed: {data}")
        infos = data["data"]["infos"]
    
    # Combine all the plant data into a single dictionary
    combined_data = {}
    for info in infos:
        id = info["id"]
        # Format dates
        if "updateAt" in info:
            updateAt_object = datetime.strptime(info["updateAt"], "%Y-%m-%dT%H:%M:%SZ")
            info["updateAt"] = updateAt_object.strftime("%Y/%m/%d %H:%M")
        if "createAt" in info:
            createAt_object = datetime.strptime(info["createAt"], "%Y-%m-%dT%H:%M:%S.%f%z")
            info["createAt"] = createAt_object.strftime("%Y/%m/%d %H:%M")

        info = {k: str(v)[:255] for k, v in info.items() if v is not None and k not in ["plantPermission", "custCode", "meterCode", "masterId", "type", "status"]}
        combined_data.update(info)

        # Fetch additional data for each plant
        # Fetch energy flow data
        async with session.get(f"{API_URL}api/v1/plant/energy/{id}/flow", headers=headers) as resp:
            energy_flow_data = await resp.json()
            energy_flow_data = {k: str(v)[:255] for k, v in energy_flow_data["data"].items() if v is not None and k not in ["plantPermission", "custCode", "meterCode", "masterId", "type", "status"]}
            combined_data.update(energy_flow_data)

        # Fetch realtime data
        async with session.get(f"{API_URL}api/v1/plant/{id}/realtime?id={id}", headers=headers) as resp:
            realtime_data = await resp.json()
            # Format dates
            if "updateAt" in realtime_data["data"]:
                updateAt_object = datetime.strptime(realtime_data["data"]["updateAt"], "%Y-%m-%dT%H:%M:%SZ")
                realtime_data["data"]["updateAt"] = updateAt_object.strftime("%Y/%m/%d %H:%M")

            realtime_data = {
                k: v["code"] if k == "currency" else str(v)[:255] 
                for k, v in realtime_data["data"].items() 
                if v is not None and k not in ["plantPermission", "custCode", "meterCode", "masterId", "type", "status"]
            }
            combined_data.update(realtime_data)
    return combined_data

