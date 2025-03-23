"""Coordinator for Sunsynk integration."""

import itertools
import logging
import statistics
from collections import deque, defaultdict
from statistics import mean

import aiohttp

from .enums import SunsynkNames
from .sunsynkapi import sunsynk_api
import datetime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)

# Default number of seconds to wait between updates. The default is used until we have processed enough updates to
# predict when the next dataset should be available on the Sunsynk servers.
DEFAULT_UPDATE_INTERVAL = 60

# The number of seconds to offset the predicted update intervals by. This adds a small margin of safety to prevent
# updates being attempted too early.
UPDATE_INTERVAL_OFFSET = 10


class SunsynkDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, client: sunsynk_api) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=datetime.timedelta(seconds=DEFAULT_UPDATE_INTERVAL),
        )
        self.api = client
        self.update_method = self.update_inverter_data

        self._updated_at_histories = defaultdict(lambda: deque(maxlen=3))

    async def update_inverter_data(self) -> dict:
        """Update inverter data from the Sunsynk API.

        Returns:
            dict: Dictionary containing inverter data with plant and inverter serial numbers as keys.
                Each plant contains data points like solar production, battery state, etc.

        Raises:
            UpdateFailed: If there is a connection error, client response error or other error
                while fetching or processing the data.
        """
        data = {}
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
                inverter_data = plant_sn_id_data["inverter_data"]
                inverter_settings_data = plant_sn_id_data["inverter_settings_data"]
                inverter_load_data = plant_sn_id_data["inverter_load_data"]
                inverter_grid_data = plant_sn_id_data["inverter_grid_data"]
                inverter_battery_data = plant_sn_id_data["inverter_battery_data"]
                inverter_input_data = plant_sn_id_data["inverter_input_data"]

                self._record_updated_at(plant_sn_id, inverter_data["updateAt"])

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
                    "Model": inverter_data.get("model")
                    or inverter_data.get("brand", ""),
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

                data[plant_sn_id] = sunsynk_data

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

        return data

    def _record_updated_at(self, plant_sn_id: str, updated_at: str) -> None:
        """Record the timestamp of the most recent dataset that is available for this inverter and ignore.

        Args:
            plant_sn_id (str): The plant/inverter serial number ID
            updated_at (str): ISO format timestamp string of when data was last updated (i.e. `updateAt`)

        Note:
            Maintains a history of updateAt timestamps for each inverter to help predict
            optimal polling intervals. Skips duplicate timestamps and logs warnings for
            early update attempts.
        """
        updated_at_ts = int(datetime.datetime.fromisoformat(updated_at).timestamp())
        inverter_update_history = self._updated_at_histories[plant_sn_id]

        if updated_at_ts in inverter_update_history:
            if len(inverter_update_history) > 1:
                # This is a predicted update that occurred too early - issue a warnign
                most_recent_update = datetime.datetime.fromtimestamp(
                    self._updated_at_histories[plant_sn_id][-1], tz=datetime.UTC
                )
                _LOGGER.warning(
                    f"Early update attempt detected for {plant_sn_id}! Most recent update was at {most_recent_update}"
                )

            # Skip duplicate update timestamps
            return

        inverter_update_history.append(updated_at_ts)

    def _calc_avg_update_interval(self) -> int:
        """Calculate the average interval between data updates across all inverters.

        Returns:
            int: The average update interval in seconds. Returns DEFAULT_UPDATE_INTERVAL if
                 insufficient history exists to calculate an average.

        The method:
        1. Calculates average update intervals for each inverter based on timestamp history
        2. Takes the mean across all inverter averages to get the plant-wide interval
        3. Returns DEFAULT_UPDATE_INTERVAL if not enough history exists
        """
        avg_update_intervals = []

        for plant_sn_id, update_history in self._updated_at_histories.items():
            _LOGGER.debug(
                f"Update history timestamps for {plant_sn_id} is {', '.join(str(uh) for uh in update_history)}"
            )

            if (num_updates := len(update_history)) < 2:
                # Need at least two entries to calculate the interval between them
                continue

            # Find the number of seconds between each update
            update_intervals = [
                update_history[i + 1] - update_history[i]
                for i in range(num_updates - 1)
            ]

            # Calculate the average update interval for this inverter
            avg_update_interval = statistics.mean(update_intervals)

            _LOGGER.debug(
                f"Average update interval for {plant_sn_id} is {avg_update_interval} seconds"
            )
            avg_update_intervals.append(avg_update_interval)

        if not avg_update_intervals:
            # Update history is not yet sufficient for making predictions - use default
            return DEFAULT_UPDATE_INTERVAL

        # Calculate the average of all inverter update intervals for this plan
        plant_avg = statistics.mean(avg_update_intervals)
        _LOGGER.debug(f"Average update interval for this plant is {plant_avg} seconds")

        return plant_avg

    @callback
    def _schedule_refresh(self) -> None:
        """Schedule the next data refresh based on update history.

        This method calculates when the next data update should be available based on
        historical update patterns. It determines the optimal polling interval by:
        1. Calculating average time between updates across all inverters
        2. Using this to predict when next dataset should be available
        3. Setting the update_interval to align with predicted availability

        If insufficient history exists, falls back to DEFAULT_UPDATE_INTERVAL.
        """
        avg_update_interval = self._calc_avg_update_interval()
        if avg_update_interval == DEFAULT_UPDATE_INTERVAL:
            _LOGGER.debug(
                f"Checking for updated plant data in {DEFAULT_UPDATE_INTERVAL} seconds..."
            )
            self.update_interval = datetime.timedelta(seconds=DEFAULT_UPDATE_INTERVAL)
            return super()._schedule_refresh()

        most_recent_update_ts = sorted(
            itertools.chain.from_iterable(self._updated_at_histories.values())
        )[-1]

        most_recent_update = datetime.datetime.fromtimestamp(
            most_recent_update_ts, tz=datetime.UTC
        )
        _LOGGER.debug(f"Most recent update was at {most_recent_update}")

        expect_next_update_at = most_recent_update + datetime.timedelta(
            seconds=avg_update_interval
        )
        _LOGGER.debug(f"Expecting next update at {expect_next_update_at}")

        now_ts = datetime.datetime.now(datetime.UTC).timestamp()
        seconds_to_next_update = max(
            DEFAULT_UPDATE_INTERVAL,
            int(expect_next_update_at.timestamp() - now_ts) + UPDATE_INTERVAL_OFFSET,
        )

        self.update_interval = datetime.timedelta(seconds=seconds_to_next_update)

        return super()._schedule_refresh()
