
from homeassistant.core import HomeAssistant
from datetime import datetime, timedelta
import requests
import json
from functools import partial
import logging
_LOGGER = logging.getLogger(__name__)
class sunsynk_api:
    def __init__(self, region, username, password, hass: HomeAssistant):
        self.region = region
        self.hass = hass
        self.username = username
        self.password = password
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
            
        if self.region == 'Region 1':
            host = 'https://pv.inteless.com/'
        elif self.region == 'Region 2':
            host = 'https://api.sunsynk.net/'
        url = host + path
        #_LOGGER.error("body: %s", body)
        #_LOGGER.error("headers: %s", headers)
        response = await self.hass.async_add_executor_job(
            partial(self._send_request, method, url, headers, body)
        )
        return response

    def _send_request(self, method, url, headers, body):
        with requests.Session() as s:
            s.headers = headers
            if body:
                response = s.request(method, url, data=json.dumps(body))
            else:
                response = s.request(method, url)

        return response.json()
            
    async def get_plant_data(self):
        return await self.request('GET', f'api/v1/plants?page=1&limit=10&name=&status=', None,True)        
    async def get_inverters_data(self,id):
        return await self.request('GET', f'api/v1/plant/{id}/inverters?page=1&limit=10&status=-1&sn=&id={id}&type=-2', None,True)        
    async def get_energy_flow_data(self,id):
        return await self.request('GET', f'api/v1/plant/energy/{id}/flow', None,True)        
    async def get_realtime_data(self,id):
        return await self.request('GET', f'api/v1/plant/{id}/realtime?id={id}', None,True)        
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
            return self.request('POST', 'oauth/token', pool_data,False)