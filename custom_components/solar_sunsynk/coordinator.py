"""Coordinator for Sunsynk integration."""
import logging

import aiohttp
from .sunsynkapi import sunsynk_api

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL

_LOGGER: logging.Logger = logging.getLogger(__package__)


class SunsynkDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, client: sunsynk_api) -> None:
        """Initialize."""
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self.api = client
        self.update_method = self._async_update_data
        self.data: dict[str, dict[str, float]] = {}

    async def _async_update_data(self):
        """Update data via library."""
        try:
            jsondata = await self.api.get_all_data()
            for invertor in jsondata:
                inverterdata: dict[str, any] = {}
                
                _inverter_data = jsondata[invertor]["inverter_data"],
                _inverter_load_data = jsondata[invertor]["inverter_load_data"],
                _inverter_grid_data = jsondata[invertor]["inverter_grid_data"],
                _inverter_battery_data = jsondata[invertor]["inverter_battery_data"],
                _inverter_input_data = jsondata[invertor]["inverter_input_data"],
                _inverter_output_data = jsondata[invertor]["inverter_output_data"],
                _inverter_settings_data = jsondata[invertor]["inverter_settings_data"],
                inverterdata.update({"Model": _inverter_data[0].get("model")})
                # statistics
                _ppv1 = _inverter_input_data[0].get("pvIV",{})[0].get("ppv",0)
                _ppv2 = _inverter_input_data[0].get("pvIV",{})[1].get("ppv",0)
                etoday = float(_inverter_input_data[0].get("etoday",0))
                if etoday == 0:
                    Solar_to_Load = 0
                else:
                    dailyUsed = float(_inverter_load_data[0].get("dailyUsed",0))
                    Solar_to_Load = dailyUsed - etoday
                Grid_to_Load = _inverter_grid_data[0].get("etodayFrom",0)
                AverageCap = ((float(_inverter_settings_data[0].get("cap1")) + float(_inverter_settings_data[0].get("cap2"))+float(_inverter_settings_data[0].get("cap3"))+float(_inverter_settings_data[0].get("cap4"))+float(_inverter_settings_data[0].get("cap5"))+float(_inverter_settings_data[0].get("cap6")))/6)
                inverterdata.update({"Solar Production": _inverter_input_data[0].get("etoday", 0)})
                inverterdata.update({"Solar to Battery":  _inverter_battery_data[0].get("etodayChg", 0)})
                inverterdata.update({"Solar to Grid": _inverter_grid_data[0].get("etodayTo", 0)})
                inverterdata.update({"Solar to Load": Solar_to_Load})
                inverterdata.update({"Total Load": _inverter_load_data[0].get("dailyUsed",0)})
                inverterdata.update({"Grid to Load": Grid_to_Load})
                #inverterdata.update({"Grid to Battery": _stats.get("EGridCharge")})
                inverterdata.update({"State of Charge": _inverter_battery_data[0].get("soc", 0)})
                inverterdata.update({"Charge": _inverter_battery_data[0].get("etodayChg", 0)})
                inverterdata.update({"Discharge": _inverter_battery_data[0].get("etodayDischg", 0)})
                inverterdata.update({"Instantaneous Grid I/O L1": _inverter_grid_data[0].get("vip",{})[0].get("power", 0)})
                inverterdata.update({"Instantaneous Grid I/O Total": _inverter_grid_data[0].get("vip",{})[0].get("power", 0)})
                inverterdata.update({"Instantaneous Generation": _inverter_input_data[0].get("pac", 0)})
                inverterdata.update({"Instantaneous Battery SOC": _inverter_battery_data[0].get("bmsSoc", 0)})
                inverterdata.update({"Instantaneous Battery I/O": _inverter_battery_data[0].get("power", 0)})
                inverterdata.update({"Instantaneous Load": _inverter_load_data[0].get("vip",{})[0].get("power", 0)})
                inverterdata.update({"Instantaneous PPV1": _ppv1})
                inverterdata.update({"Instantaneous PPV2": _ppv2})
                inverterdata.update({"Setting - Average State of Charge Capacity": AverageCap})
                self.data.update({invertor: inverterdata})


            return self.data
        except (
            aiohttp.client_exceptions.ClientConnectorError,
            aiohttp.ClientResponseError,
        ) as error:
            raise UpdateFailed(error) from error
