from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from functools import partial
from datetime import timedelta,datetime
import logging
from .sunsynkapi import sunsynk_api
from .const import UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_get_coordinator(hass, config_entry):
    """Set up the DataUpdateCoordinator."""
    USERNAME = config_entry.data["username"]
    PASSWORD = config_entry.data["password"]
    region = config_entry.data["region"]
    sunsynk = sunsynk_api(region,USERNAME,PASSWORD, hass)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Sunsynk",
        update_method=partial(fetch_data, sunsynk),
        update_interval=timedelta(seconds=UPDATE_INTERVAL),
    )
    return coordinator

async def fetch_data(sunsynk):

    # Fetch plant data
    data = await sunsynk.get_plant_data()
    infos = data["data"]["infos"]
    
    # Combine all the plant data into a single dictionary
    combined_data = {}
    for info in infos:
        id = info["id"]
        inverter_data = await sunsynk.get_inverters_data(id)
        # Extract "sn" values from the inverter data
        inverters_sn = inverter_data["data"]["infos"][0]["sn"] if inverter_data["data"]["infos"] else None
        # Add the "sn" values to the combined_data
        combined_data[f"inverters_{id}_sn"] = inverters_sn
        setting_data = await sunsynk.get_settings(inverters_sn)
        # Extract settings from the data
        for setting_key, setting_value in setting_data["data"].items():
            # Format the setting key to include the inverter serial number
            combined_key = f"settings_{inverters_sn}_{setting_key}"
            # Add the setting to the combined_data
            combined_data[combined_key] = str(setting_value)[:255]  # Ensure the value is a string and not exceeding 255 characters

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
        energy_flow_data = await sunsynk.get_energy_flow_data(id)
        energy_flow_data = {k: str(v)[:255] for k, v in energy_flow_data["data"].items() if v is not None and k not in ["plantPermission", "custCode", "meterCode", "masterId", "type", "status"]}
        combined_data.update(energy_flow_data)

        # Fetch realtime data
        realtime_data = await sunsynk.get_realtime_data(id)
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

