import requests
import json
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

DOMAIN = "solar_sunsynk"
SCAN_INTERVAL = timedelta(seconds=120)

async def async_setup(hass: HomeAssistant, config: dict):
    return True
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    username = entry.data.get('username')
    password = entry.data.get('password')

    async def update_states(now=None):
        urlAuth = "https://solarsunsynk.houselabs.co.za/api/GetToken"  # Replace with your endpoint
        paramsAuth = {"username": username, "password": password}  # Use the username and password from config
        url = "https://pv.inteless.com/api/v1/plants?page=1&limit=10&name=&status="

        responseAuth = requests.get(urlAuth, params=paramsAuth)
        if responseAuth.ok:
            token = responseAuth.text
            headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(url, headers=headers)

        if not response.ok:
            hass.states.set("solar_sunsynk.error", "Failed")
        else:
            data = json.loads(response.content)["data"]
            infos = data["infos"]
            for info in infos:
                # Define the entity ID as "solar_sunsynk.thumb"
                entity_idthumb = "solar_sunsynk.thumb"
                # Set the state for the entity
                hass.states.async_set(entity_idthumb, info["thumbUrl"])
                
                for keyinfo, valueInfo in info.items():
                    if keyinfo == 'plantPermission' or valueInfo is None:
                        continue
                    # Define the entity ID as "solar_sunsynk.<key>"
                    entity_idinfo = f"solar_sunsynk.{keyinfo}"
                    # Set the state for the entity
                    hass.states.async_set(entity_idinfo, valueInfo)
                        
                
                id = info["id"]
                url = f"https://pv.inteless.com/api/v1/plant/energy/{id}/flow"
                response = requests.get(url, headers=headers)
                response_code = response.status_code
                result = json.loads(response.content)

                # Set Home Assistant sensor entities for all data in the result
                for key, value in result["data"].items():
                    if value is None:
                        continue
                    # Check if the key is numeric
                    entity_id = f"solar_sunsynk.{key}"
                    # Set the state for the entity
                    hass.states.async_set(entity_id, value)

    # Schedule the update_states function to run every 2 minutes
    hass.helpers.event.async_track_time_interval(update_states, SCAN_INTERVAL)

    # Return boolean to indicate that initialization was successful.
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    # Remove entities that belong to the integration
    await asyncio.gather(
        *[hass.config_entries.async_forward_entry_unload(entry, domain) for domain in ["sensor"]]
    )

    return True
