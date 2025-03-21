"""Coordinator for Sunsynk integration."""

import logging
from statistics import mean

import aiohttp

from .enums import SunsynkNames
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
            all_data = await self.api.get_all_data()
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

        for plant_sn_id, plant_sn_id_data in all_data.items():
            try:
                inverter_settings_data = plant_sn_id_data["inverter_settings_data"]
                inverter_load_data = plant_sn_id_data["inverter_load_data"]
                inverter_grid_data = plant_sn_id_data["inverter_grid_data"]
                inverter_battery_data = plant_sn_id_data["inverter_battery_data"]
                inverter_input_data = plant_sn_id_data["inverter_input_data"]

                # Statistics
                solar_to_load = float(inverter_input_data.get("etoday", 0))
                if solar_to_load:
                    solar_to_load = (
                        float(inverter_load_data.get("dailyUsed", 0)) - solar_to_load
                    )

                average_cap = mean(
                    float(inverter_settings_data.get(f"cap{i}", 0)) for i in range(1, 7)
                )

                pvIV = inverter_input_data.get("pvIV", [{}, {}])

                sunsynk_data = {
                    "Model": plant_sn_id_data["inverter_data"].get("model")
                    or plant_sn_id_data["inverter_data"].get("brand", ""),
                    SunsynkNames.SolarProduction.value: inverter_input_data.get(
                        "etoday", 0
                    ),
                    SunsynkNames.SolarToBattery.value: inverter_battery_data.get(
                        "etodayChg", 0
                    ),
                    SunsynkNames.SolarToGrid.value: inverter_grid_data.get(
                        "etodayTo", 0
                    ),
                    SunsynkNames.SolarToLoad.value: solar_to_load,
                    SunsynkNames.TotalLoad.value: inverter_load_data.get(
                        "dailyUsed", 0
                    ),
                    SunsynkNames.GridToLoad.value: inverter_grid_data.get(
                        "etodayFrom", 0
                    ),
                    SunsynkNames.StateOfCharge.value: inverter_battery_data.get(
                        "soc", 0
                    ),
                    SunsynkNames.Charge.value: inverter_battery_data.get(
                        "etodayChg", 0
                    ),
                    SunsynkNames.Discharge.value: inverter_battery_data.get(
                        "etodayDischg", 0
                    ),
                    SunsynkNames.GridIOTotal.value: inverter_grid_data.get(
                        "limiterTotalPower", 0
                    ),
                    SunsynkNames.GridPowerTotal.value: inverter_grid_data.get("pac", 0),
                    SunsynkNames.Generation.value: inverter_input_data.get("pac", 0),
                    SunsynkNames.BatterySOC.value: inverter_battery_data.get(
                        "bmsSoc", 0
                    ),
                    SunsynkNames.BatteryIO.value: inverter_battery_data.get("power", 0),
                    SunsynkNames.Load.value: inverter_load_data.get("totalPower", 0),
                    SunsynkNames.PPV1.value: pvIV[0].get("ppv", 0),
                    SunsynkNames.PPV2.value: pvIV[1].get("ppv", 0),
                    SunsynkNames.SettingAverageCap.value: average_cap,
                }

                # Update data dictionary
                if plant_sn_id not in self.data:
                    self.data[plant_sn_id] = {}

                self.data[plant_sn_id].update(sunsynk_data)

            except IndexError as index_error:
                _LOGGER.error(
                    "IndexError for inverter %s while processing statistics: %s. Data: %s",
                    plant_sn_id,
                    index_error,
                    plant_sn_id_data,
                )
                continue

            except Exception as stats_error:
                _LOGGER.error(
                    "Unexpected error while processing statistics for inverter %s: %s",
                    plant_sn_id,
                    stats_error,
                )
                continue

            except KeyError as key_error:
                _LOGGER.error(
                    "Missing key in data for inverter %s: %s",
                    plant_sn_id,
                    key_error,
                )
                continue

        return self.data
