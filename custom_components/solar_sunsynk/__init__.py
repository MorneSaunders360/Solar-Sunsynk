import requests
import json
from datetime import timedelta

DOMAIN = "solar_sunsynk"
SCAN_INTERVAL = timedelta(seconds=120)

def setup(hass, config):
    username = config[DOMAIN].get('username')
    password = config[DOMAIN].get('password')

    if username is None or password is None:
        _LOGGER.error("Missing required configuration items %s or %s", 'username', 'password')
        return False

    def update_states(now=None):
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
                response_code = response.status_code
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
