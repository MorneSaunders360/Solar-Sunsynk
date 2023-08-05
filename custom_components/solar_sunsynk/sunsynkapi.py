
from homeassistant.core import HomeAssistant
from datetime import datetime, timedelta
from .enums import SunsynkApiNames
import requests
import json
from functools import partial
import logging
_LOGGER = logging.getLogger(__name__)
class sunsynk_api:
    def __init__(self, region, username, password,scan_interval, hass: HomeAssistant):
        self.region = region
        self.hass = hass
        self.username = username
        self.password = password
        self.scan_interval = scan_interval
        self.token = None
        self.token_expires = datetime.now()

    async def request(self, method, path, body, autoAuth):
        if autoAuth:
            if not self.token or self.token_expires <= datetime.now():
                responseAuth = await self.authenticate(self.username, self.password)
                self.token = responseAuth["data"]["access_token"]
                # Assuming the token expires in 1 hour
                self.token_expires = datetime.now() + timedelta(hours=1)
            headers = {
                'Content-Type': 'application/json',
                "Authorization": f"Bearer {self.token}"
            }
        else:
            headers = {
                'Content-Type': 'application/json',
            }
            
        if self.region == SunsynkApiNames.Region1:
            host = 'https://pv.inteless.com/'
        elif self.region == SunsynkApiNames.Region2:
            host = 'https://api.sunsynk.net/'
        url = host + path
        #_LOGGER.error("body: %s", body)
        #_LOGGER.error("headers: %s", headers)
        response = await self.hass.async_add_executor_job(
            partial(self._send_request, method, url, headers, body)
        )
        return response

    def _send_request(self, method, url, headers, body):
        try:
            with requests.Session() as s:
                s.headers = headers
                if body:
                    response = s.request(method, url, data=json.dumps(body))
                else:
                    response = s.request(method, url)
            response.raise_for_status()  # Raise an exception if the HTTP request returned an error status
        except requests.exceptions.HTTPError as errh:
            _LOGGER.error(f"HTTP Error: {errh}")
            return None
        except requests.exceptions.ConnectionError as errc:
            _LOGGER.error(f"Error Connecting: {errc}")
            return None
        except requests.exceptions.Timeout as errt:
            _LOGGER.error(f"Timeout Error: {errt}")
            return None
        except requests.exceptions.RequestException as err:
            _LOGGER.error(f"Something Else: {err}")
            return None
        return response.json()

            
    async def get_inverters_data(self,id):
        return await self.request('GET', f'api/v1/plant/{id}/inverters?page=1&limit=10&status=-1&sn=&id={id}&type=-2', None,True)        
    async def get_inverter_data(self,id):
        return await self.request('GET', f'api/v1/inverter/{id}', None,True)        
    async def get_inverter_load_data(self,id):
        return await self.request('GET', f'api/v1/inverter/load/{id}/realtime?sn={id}&lan=en', None,True)        
    async def get_inverter_grid_data(self,id):
        return await self.request('GET', f'api/v1/inverter/grid/{id}/realtime?sn={id}&lan=en', None,True)        
    async def get_inverter_battery_data(self,id):
        return await self.request('GET', f'api/v1/inverter/battery/{id}/realtime?sn={id}&lan=en', None,True)        
    async def get_inverter_input_data(self,id):
        return await self.request('GET', f'api/v1/inverter/{id}/realtime/input', None,True)        
    async def get_inverter_output_data(self,id):
        return await self.request('GET', f'api/v1/inverter/{id}/realtime/output', None,True)        
    # async def get_inverter_load_data(self,id):
    #     now = datetime.today().strftime('%Y-%m-%d')
    #     return await self.request('GET', f'api/v1/inverter/grid/{id}/day?lan=en&date={now}&column=pac', None,True)        
    
    async def get_plant_data(self):
        return await self.request('GET', f'api/v1/plants?page=1&limit=10&name=&status=', None,True)        
    async def get_energy_flow_data(self,id):
        return await self.request('GET', f'api/v1/plant/energy/{id}/flow', None,True)        
    async def get_realtime_data(self,id):
        return await self.request('GET', f'api/v1/plant/{id}/realtime?id={id}', None,True) 
    async def get_all_data(self):
        all_data = {}

        # Get plant data
        try:
            plant_data = await self.get_plant_data()
            if plant_data is None or "data" not in plant_data or "infos" not in plant_data["data"]:
                _LOGGER.error("Unable to fetch or parse plant data")
                return None
        except Exception as e:
            _LOGGER.error(f"Error while getting plant data: {e}")
            return None
            
        # Assuming that plant_data is a JSON object with a key "plants" that contains a list of plants
        # Each plant is assumed to be a JSON object with a key "id" that contains the plant ID
        for plant in plant_data["data"]["infos"]:
            plant_id = plant["id"]
            try:
                inverterdata = await self.get_inverters_data(plant_id)
                if inverterdata is None or "data" not in inverterdata or "infos" not in inverterdata["data"]:
                    _LOGGER.error("Unable to fetch or parse inverter data")
                    continue
            except Exception as e:
                _LOGGER.error(f"Error while getting inverter data: {e}")
                continue
                
            for inverter in inverterdata["data"]["infos"]:
                inverterId = inverter["sn"]
                # Get energy flow data for this plant
                try:
                    inverter_data = await self.get_inverter_data(inverterId)
                    inverter_load_data = await self.get_inverter_load_data(inverterId)
                    inverter_grid_data = await self.get_inverter_grid_data(inverterId)
                    inverter_battery_data = await self.get_inverter_battery_data(inverterId)
                    inverter_input_data = await self.get_inverter_input_data(inverterId)
                    inverter_output_data = await self.get_inverter_output_data(inverterId)
                    inverter_settings = await self.get_settings(inverterId)
                except Exception as e:
                    _LOGGER.error(f"Error while getting inverter related data: {e}")
                    continue
                    
                plant_sn_id = f"sunsynk_{plant_id}_{inverterId}"  
                # Add data to all_data
                all_data[plant_sn_id] = {
                    "inverter_data": inverter_data["data"],
                    "inverter_load_data": inverter_load_data["data"],
                    "inverter_grid_data": inverter_grid_data["data"],
                    "inverter_battery_data": inverter_battery_data["data"],
                    "inverter_input_data": inverter_input_data["data"],
                    "inverter_output_data": inverter_output_data["data"],
                    "inverter_settings_data": inverter_settings["data"],
                }
        return all_data


    async def get_settings(self,sn):
        return await self.request('GET', f'api/v1/common/setting/{sn}/read', None,True)
    async def set_settings(self, sn,setting_data):
        return await self.request('POST', f'api/v1/common/setting/{sn}/set', setting_data,True)
    def authenticate(self, username, password):
        pool_data = {
            "username": username,
            "password": password,
            'grant_type': 'password',
            'client_id': 'csp-web'
        }
        try:
            return self.request('POST', 'oauth/token', pool_data, False)
        except Exception as e:
            _LOGGER.error(f"Error during authentication: {e}")
        return None

            