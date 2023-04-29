import requests
import json
import logging
from datetime import timedelta
from .config_flow import SolarSunsynkConfigFlow

DOMAIN = "solar_sunsynk"
SCAN_INTERVAL = timedelta(seconds=120)

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    return True

async def async_setup_entry(hass, entry):
    username = entry.data["username"]
    password = entry.data["password"]
    def update_states(now=None):
        headers = {
        'Content-type':'application/json', 
        'Accept':'application/json'
        }

        payload = {
        "username": username,
        "password": password,
        "grant_type":"password",
        "client_id":"csp-web"
        }

        urlAuth = "https://pv.inteless.com/oauth/token"  # Replace with your endpoint
        url = "https://pv.inteless.com/api/v1/plants?page=1&limit=10&name=&status="

        responseAuth = requests.post(urlAuth, json=payload, headers=headers).json()
        token = responseAuth["data"]["access_token"]
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
                hass.states.set(entity_idthumb, info["thumbUrl"])
                
                for keyinfo, valueInfo in info.items():
                    if keyinfo == 'plantPermission' or valueInfo is None:
                        continue
                    # Define the entity ID as "solar_sunsynk.<key>"
                    entity_idinfo = f"sensor.solar_sunsynk_{keyinfo}"
                    # Set the state for the entity
                    hass.states.set(entity_idinfo, valueInfo)
                        
                
                id = info["id"]
                url = f"https://pv.inteless.com/api/v1/plant/energy/{id}/flow"
                response = requests.get(url, headers=headers)
                result = json.loads(response.content)

                # Set Home Assistant sensor entities for all data in the result
                for key, value in result["data"].items():
                    if value is None:
                        continue
                    # Check if the key is numeric
                    entity_id = f"sensor.solar_sunsynk_{key}"
                    # Set the state for the entity
                    hass.states.set(entity_id, value)
                
                url = f"https://pv.inteless.com/api/v1/plant/{id}/realtime?id={id}"
                response = requests.get(url, headers=headers)
                result = json.loads(response.content)

                # Set Home Assistant sensor entities for all data in the result
                for key, value in result["data"].items():
                    if value is None:
                        continue
                    # Check if the key is numeric
                    entity_id = f"sensor.solar_sunsynk_{key}"
                    # Set the state for the entity
                    hass.states.set(entity_id, value)
                    
                    
    # Call your existing setup function with the username and password directly
    return await hass.async_add_executor_job(setup, hass, username, password)

def setup(hass, username, password):
    if username is None or password is None:
        return False

    def update_states(now=None):
        headers = {
        'Content-type':'application/json', 
        'Accept':'application/json'
        }

        payload = {
        "username": username,
        "password": password,
        "grant_type":"password",
        "client_id":"csp-web"
        }

        urlAuth = "https://pv.inteless.com/oauth/token"  # Replace with your endpoint
        url = "https://pv.inteless.com/api/v1/plants?page=1&limit=10&name=&status="

        responseAuth = requests.post(urlAuth, json=payload, headers=headers).json()
        token = responseAuth["data"]["access_token"]
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
                hass.states.set(entity_idthumb, info["thumbUrl"])
                
                for keyinfo, valueInfo in info.items():
                    if keyinfo == 'plantPermission' or valueInfo is None:
                        continue
                    # Define the entity ID as "solar_sunsynk.<key>"
                    entity_idinfo = f"sensor.solar_sunsynk_{keyinfo}"
                    # Set the state for the entity
                    hass.states.set(entity_idinfo, valueInfo)
                        
                
                id = info["id"]
                url = f"https://pv.inteless.com/api/v1/plant/energy/{id}/flow"
                response = requests.get(url, headers=headers)
                result = json.loads(response.content)

                # Set Home Assistant sensor entities for all data in the result
                for key, value in result["data"].items():
                    if value is None:
                        continue
                    # Check if the key is numeric
                    entity_id = f"sensor.solar_sunsynk_{key}"
                    # Set the state for the entity
                    hass.states.set(entity_id, value)
                
                url = f"https://pv.inteless.com/api/v1/plant/{id}/realtime?id={id}"
                response = requests.get(url, headers=headers)
                result = json.loads(response.content)

                # Set Home Assistant sensor entities for all data in the result
                for key, value in result["data"].items():
                    if value is None:
                        continue
                    # Check if the key is numeric
                    entity_id = f"sensor.solar_sunsynk_{key}"
                    # Set the state for the entity
                    hass.states.set(entity_id, value)
                    
                    
    # Schedule the update_states function to run every 2 minutes
    hass.helpers.event.async_track_time_interval(update_states, SCAN_INTERVAL)

    # Return boolean to indicate that initialization was successful.
    return True
