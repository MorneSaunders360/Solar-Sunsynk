"""Coordinator for Sunsynk integration."""

import logging

import aiohttp
from .sunsynkapi import sunsynk_api
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)


class SunsynkDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, client: sunsynk_api) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=client.scan_interval),
        )
        self.api = client
        self.update_method = self._async_update_data
        self.data: dict[str, dict[str, float]] = {}

    async def _async_update_data(self):
        """Update data via library."""
        try:
            jsondata = await self.api.get_all_data()
            for invertor in jsondata:
                inverterdata: dict[str, any] = {}
                try:
                    _inverter_data = (jsondata[invertor]["inverter_data"],)
                    _inverter_load_data = (jsondata[invertor]["inverter_load_data"],)
                    _inverter_grid_data = (jsondata[invertor]["inverter_grid_data"],)
                    _inverter_battery_data = (
                        jsondata[invertor]["inverter_battery_data"],
                    )
                    _inverter_input_data = (jsondata[invertor]["inverter_input_data"],)
                    _inverter_output_data = (
                        jsondata[invertor]["inverter_output_data"],
                    )
                    _inverter_settings_data = (
                        jsondata[invertor]["inverter_settings_data"],
                    )

                    if _inverter_data[0].get("model") == "":
                        inverterdata.update({"Model": _inverter_data[0].get("model")})
                    else:
                        inverterdata.update({"Model": _inverter_data[0].get("brand")})

                    # Statistics
                    try:
                        _ppv1 = (
                            _inverter_input_data[0].get("pvIV", [{}])[0].get("ppv", 0)
                            if len(_inverter_input_data[0].get("pvIV", [])) > 0
                            else 0
                        )
                        _ppv2 = (
                            _inverter_input_data[0].get("pvIV", [{}])[1].get("ppv", 0)
                            if len(_inverter_input_data[0].get("pvIV", [])) > 1
                            else 0
                        )
                        etoday = float(_inverter_input_data[0].get("etoday", 0))

                        if etoday == 0:
                            Solar_to_Load = 0
                        else:
                            dailyUsed = float(
                                _inverter_load_data[0].get("dailyUsed", 0) or 0
                            )
                            Solar_to_Load = dailyUsed - etoday

                        Grid_to_Load = _inverter_grid_data[0].get("etodayFrom", 0)
                        AverageCap = (
                            sum(
                                float(_inverter_settings_data[0].get(f"cap{i}", 0))
                                for i in range(1, 7)
                            )
                            / 6
                        )
                        inverterdata.update(
                            {
                                "Solar Production": _inverter_input_data[0].get(
                                    "etoday", 0
                                ),
                                "Solar to Battery": _inverter_battery_data[0].get(
                                    "etodayChg", 0
                                ),
                                "Solar to Grid": _inverter_grid_data[0].get(
                                    "etodayTo", 0
                                ),
                                "Solar to Load": Solar_to_Load,
                                "Total Load": _inverter_load_data[0].get(
                                    "dailyUsed", 0
                                ),
                                "Grid to Load": Grid_to_Load,
                                "State of Charge": _inverter_battery_data[0].get(
                                    "soc", 0
                                ),
                                "Charge": _inverter_battery_data[0].get("etodayChg", 0),
                                "Discharge": _inverter_battery_data[0].get(
                                    "etodayDischg", 0
                                ),
                                "Instantaneous Grid I/O Total": _inverter_grid_data[
                                    0
                                ].get("limiterTotalPower", 0),
                                "Instantaneous Generation": _inverter_input_data[0].get(
                                    "pac", 0
                                ),
                                "Instantaneous Battery SOC": _inverter_battery_data[
                                    0
                                ].get("bmsSoc", 0),
                                "Instantaneous Battery I/O": _inverter_battery_data[
                                    0
                                ].get("power", 0),
                                "Instantaneous Load": _inverter_load_data[0].get(
                                    "totalPower", 0
                                ),
                                "Instantaneous PPV1": _ppv1,
                                "Instantaneous PPV2": _ppv2,
                                "Setting - Average State of Charge Capacity": AverageCap,
                            }
                        )
                    except IndexError as index_error:
                        _LOGGER.error(
                            "IndexError for inverter %s while processing statistics: %s. Data: %s",
                            invertor,
                            index_error,
                            jsondata[invertor],
                        )
                        continue
                    except Exception as stats_error:
                        _LOGGER.error(
                            "Unexpected error while processing statistics for inverter %s: %s",
                            invertor,
                            stats_error,
                        )
                        continue

                except KeyError as key_error:
                    _LOGGER.error(
                        "Missing key in data for inverter %s: %s", invertor, key_error
                    )
                    continue

                self.data.update({invertor: inverterdata})

            return self.data
        except aiohttp.client_exceptions.ClientConnectorError as conn_error:
            _LOGGER.error("Connection error while fetching data: %s", conn_error)
            raise UpdateFailed(conn_error) from conn_error
        except aiohttp.ClientResponseError as response_error:
            _LOGGER.error(
                "Client response error while fetching data: %s", response_error
            )
            raise UpdateFailed(response_error) from response_error
        except Exception as general_error:
            _LOGGER.error("Unexpected error during data update: %s", general_error)
            raise UpdateFailed(general_error) from general_error
