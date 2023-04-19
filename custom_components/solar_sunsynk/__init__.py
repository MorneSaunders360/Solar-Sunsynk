import logging
import requests
import json
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN

SCAN_INTERVAL = timedelta(seconds=120)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
    """Set up the Solar Sunsynk component."""
    username = entry.data.get('username')
    password = entry.data.get('password')

    # If username and password not present in configuration, try to load from file
    if username is None or password is None:
        try:
            with open("solar_sunsynk_config.json", "r") as f:
                data = json.load(f)
                username = data.get("username")
                password = data.get("password")
        except FileNotFoundError:
            _LOGGER.error("Missing required configuration items %s or %s", 'username', 'password')
            return False

    # Save username and password to file
    data = {"username": username, "password": password}
    with open("solar_sunsynk_config.json", "w") as f:
        json.dump(data, f)

    async def async_update_data():
        urlAuth = "https://solarsunsynk.houselabs.co.za/api/GetToken"  # Replace with your endpoint
        paramsAuth = {"username": username, "password": password}  # Use the username and password from config

        def fetch_data():
            url = "https://pv.inteless.com/api/v1/plants?page=1&limit=10&name=&status="
            responseAuth = requests.get(urlAuth, params=paramsAuth)
            if responseAuth.ok:
                token = responseAuth.text
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(url, headers=headers)
                if response.ok:
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

        await hass.async_add_executor_job(fetch_data)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="solar_sunsynk",
        update_method=async_update_data,
        update_interval
        =SCAN_INTERVAL,
    )

    await coordinator.async_refresh()

    hass.data[DOMAIN] = coordinator

    return True
