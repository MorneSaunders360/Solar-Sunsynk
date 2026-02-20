"""Coordinator for Sunsynk integration."""

import itertools
import logging
import statistics
from collections import deque, defaultdict
from statistics import mean

import aiohttp
from typing import Any, Dict, List
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

        

        def _to_float(val: Any) -> float:
            try:
                if val is None:
                    return 0.0
                if isinstance(val, (int, float)):
                    return float(val)
                s: str = str(val).strip()
                if s in {"--", ""}:
                    return 0.0
                return float(s)
            except Exception:
                return 0.0

        for plant_sn_id, plant_sn_id_data in all_data.items():
            try:
                inverter_data: Dict[str, Any] = plant_sn_id_data["inverter_data"] or {}
                inverter_settings_data: Dict[str, Any] = plant_sn_id_data["inverter_settings_data"] or {}
                inverter_load_data: Dict[str, Any] = plant_sn_id_data["inverter_load_data"] or {}
                inverter_grid_data: Dict[str, Any] = plant_sn_id_data["inverter_grid_data"] or {}
                inverter_battery_data: Dict[str, Any] = plant_sn_id_data["inverter_battery_data"] or {}
                inverter_input_data: Dict[str, Any] = plant_sn_id_data["inverter_input_data"] or {}
                inverter_output_data: Dict[str, Any] = plant_sn_id_data["inverter_output_data"] or {}
                energy_flow_data: Dict[str, Any] = plant_sn_id_data.get("energy_flow_data") or {}

                self._record_updated_at(plant_sn_id, inverter_data["updateAt"])

                etoday_val: float = _to_float(inverter_input_data.get("etoday"))
                total_load_val: float = _to_float(inverter_load_data.get("dailyUsed"))
                solar_to_load: float = total_load_val - etoday_val if etoday_val > 0.0 else 0.0

                caps_values: List[float] = []
                for i in range(1, 7):
                    key: str = f"cap{i}"
                    if key in inverter_settings_data:
                        caps_values.append(_to_float(inverter_settings_data.get(key)))
                average_cap: float = (sum(caps_values) / len(caps_values)) if caps_values else 0.0

                pvIV_raw: Any = inverter_input_data.get("pvIV")
                pvIV_list: List[Dict[str, Any]] = pvIV_raw if isinstance(pvIV_raw, list) else []
                pvIV_padded: List[Dict[str, Any]] = pvIV_list + [{}, {}, {}, {}]
                ppv1: float = _to_float(pvIV_padded[0].get("ppv"))
                ppv2: float = _to_float(pvIV_padded[1].get("ppv"))
                ppv3: float = _to_float(pvIV_padded[2].get("ppv"))
                ppv4: float = _to_float(pvIV_padded[3].get("ppv"))
                ipv1: float = _to_float(pvIV_padded[0].get("ipv"))
                ipv2: float = _to_float(pvIV_padded[1].get("ipv"))
                ipv3: float = _to_float(pvIV_padded[2].get("ipv"))
                ipv4: float = _to_float(pvIV_padded[3].get("ipv"))
                vpv1: float = _to_float(pvIV_padded[0].get("vpv"))
                vpv2: float = _to_float(pvIV_padded[1].get("vpv"))
                vpv3: float = _to_float(pvIV_padded[2].get("vpv"))
                vpv4: float = _to_float(pvIV_padded[3].get("vpv"))
                pv_current: float = ipv1 + ipv2 + ipv3 + ipv4

                load_vip_raw: Any = inverter_load_data.get("vip")
                load_vip: List[Dict[str, Any]] = load_vip_raw if isinstance(load_vip_raw, list) else [{}]
                load_volt: float = _to_float(load_vip[0].get("volt") if load_vip else 0)
                load_power: float = _to_float(inverter_load_data.get("totalPower"))
                load_current: float = (load_power / load_volt) if load_volt != 0 else 0.0

                grid_vip_raw: Any = inverter_grid_data.get("vip")
                grid_vip: List[Dict[str, Any]] = grid_vip_raw if isinstance(grid_vip_raw, list) else [{}]
                grid_volt: float = _to_float(grid_vip[0].get("volt") if grid_vip else 0)
                grid_power: float = _to_float(inverter_grid_data.get("pac"))
                grid_current: float = (grid_power / grid_volt) if grid_volt != 0 else 0.0
                grid_fac: float = _to_float(inverter_grid_data.get("fac"))

                output_vip_raw: Any = inverter_output_data.get("vip")
                output_vip: List[Dict[str, Any]] = output_vip_raw if isinstance(output_vip_raw, list) else []
                output_vip_padded: List[Dict[str, Any]] = output_vip + [{}, {}, {}]
                output_volt: float = _to_float(output_vip_padded[0].get("volt"))
                output_current: float = (
                    _to_float(output_vip_padded[0].get("current"))
                    + _to_float(output_vip_padded[1].get("current"))
                    + _to_float(output_vip_padded[2].get("current"))
                )

                bat_etotal_chg: float = _to_float(inverter_battery_data.get("etotalChg"))
                bat_etotal_dischg: float = _to_float(inverter_battery_data.get("etotalDischg"))
                bat_efficiency: float = (
                    round(100 - (bat_etotal_chg - bat_etotal_dischg) / bat_etotal_dischg * 100)
                    if bat_etotal_dischg > 0 else 0.0
                )

                gateway_vo: Dict[str, Any] = inverter_data.get("gatewayVO") or {}

                sunsynk_data: Dict[str, Any] = {
                    "Model": inverter_data.get("model") or inverter_data.get("brand", ""),
                    # --- Existing sensors ---
                    SunsynkNames.SolarProduction.value: etoday_val,
                    SunsynkNames.SolarToBattery.value: _to_float(inverter_battery_data.get("etodayChg")),
                    SunsynkNames.SolarToGrid.value: _to_float(inverter_grid_data.get("etodayTo")),
                    SunsynkNames.SolarToLoad.value: solar_to_load,
                    SunsynkNames.TotalLoad.value: total_load_val,
                    SunsynkNames.GridToLoad.value: _to_float(inverter_grid_data.get("etodayFrom")),
                    SunsynkNames.StateOfCharge.value: _to_float(inverter_battery_data.get("soc")),
                    SunsynkNames.Charge.value: _to_float(inverter_battery_data.get("etodayChg")),
                    SunsynkNames.Discharge.value: _to_float(inverter_battery_data.get("etodayDischg")),
                    SunsynkNames.GridIOTotal.value: _to_float(inverter_grid_data.get("limiterTotalPower")),
                    SunsynkNames.GridPowerTotal.value: grid_power,
                    SunsynkNames.Generation.value: _to_float(inverter_input_data.get("pac")),
                    SunsynkNames.BatterySOC.value: _to_float(inverter_battery_data.get("bmsSoc")),
                    SunsynkNames.BatteryIO.value: _to_float(inverter_battery_data.get("power")),
                    SunsynkNames.Load.value: load_power,
                    SunsynkNames.PPV1.value: ppv1,
                    SunsynkNames.PPV2.value: ppv2,
                    SunsynkNames.SettingAverageCap.value: average_cap,
                    # --- PV strings 3 & 4 + all voltages/currents ---
                    SunsynkNames.PPV3.value: ppv3,
                    SunsynkNames.PPV4.value: ppv4,
                    SunsynkNames.IPV1.value: ipv1,
                    SunsynkNames.IPV2.value: ipv2,
                    SunsynkNames.IPV3.value: ipv3,
                    SunsynkNames.IPV4.value: ipv4,
                    SunsynkNames.VPV1.value: vpv1,
                    SunsynkNames.VPV2.value: vpv2,
                    SunsynkNames.VPV3.value: vpv3,
                    SunsynkNames.VPV4.value: vpv4,
                    SunsynkNames.PVCurrent.value: pv_current,
                    SunsynkNames.PVEtotal.value: _to_float(inverter_input_data.get("etotal")),
                    # --- Load ---
                    SunsynkNames.LoadTotalUsed.value: _to_float(inverter_load_data.get("totalUsed")),
                    SunsynkNames.LoadVolt.value: load_volt,
                    SunsynkNames.LoadUpsPower.value: _to_float(inverter_load_data.get("upsPowerTotal")),
                    SunsynkNames.LoadFac.value: _to_float(inverter_load_data.get("loadFac")),
                    SunsynkNames.LoadCurrent.value: load_current,
                    # --- Battery extended ---
                    SunsynkNames.BatteryTemp.value: _to_float(inverter_battery_data.get("temp")),
                    SunsynkNames.BatteryVoltage.value: _to_float(inverter_battery_data.get("voltage")),
                    SunsynkNames.BatteryChargeVolt.value: _to_float(inverter_battery_data.get("chargeVolt")),
                    SunsynkNames.BatteryStatus.value: _to_float(inverter_battery_data.get("status")),
                    SunsynkNames.BatteryChargeCurrentLimit.value: _to_float(inverter_battery_data.get("chargeCurrentLimit")),
                    SunsynkNames.BatteryDischargeCurrentLimit.value: _to_float(inverter_battery_data.get("dischargeCurrentLimit")),
                    SunsynkNames.BatteryCapacity.value: _to_float(inverter_battery_data.get("correctCap")),
                    SunsynkNames.BatteryCurrent.value: _to_float(inverter_battery_data.get("current")),
                    SunsynkNames.BatteryEtotalChg.value: bat_etotal_chg,
                    SunsynkNames.BatteryEtotalDischg.value: bat_etotal_dischg,
                    SunsynkNames.BatteryEfficiency.value: bat_efficiency,
                    # --- Grid extended ---
                    SunsynkNames.GridTotalIn.value: _to_float(inverter_grid_data.get("etotalFrom")),
                    SunsynkNames.GridTotalOut.value: _to_float(inverter_grid_data.get("etotalTo")),
                    SunsynkNames.GridFac.value: grid_fac,
                    SunsynkNames.GridStatus.value: _to_float(inverter_grid_data.get("status")),
                    SunsynkNames.GridPF.value: _to_float(inverter_grid_data.get("pf")),
                    SunsynkNames.GridVolt.value: grid_volt,
                    SunsynkNames.GridCurrent.value: grid_current,
                    # --- Output (already fetched, now used) ---
                    SunsynkNames.OutputPowerAux.value: _to_float(inverter_output_data.get("poweraux")),
                    SunsynkNames.OutputEtotal.value: _to_float(inverter_output_data.get("etotal")),
                    SunsynkNames.OutputEtoday.value: _to_float(inverter_output_data.get("etoday")),
                    SunsynkNames.OutputPAC.value: _to_float(inverter_output_data.get("pac")),
                    SunsynkNames.OutputPInv.value: _to_float(inverter_output_data.get("pInv")),
                    SunsynkNames.OutputFac.value: _to_float(inverter_output_data.get("fac")),
                    SunsynkNames.OutputVolt.value: output_volt,
                    SunsynkNames.OutputCurrent.value: output_current,
                    # --- Energy flow ---
                    SunsynkNames.FlowBatterySOC.value: _to_float(energy_flow_data.get("soc")),
                    SunsynkNames.FlowLoadPower.value: _to_float(energy_flow_data.get("loadOrEpsPower")),
                    SunsynkNames.FlowPVPower.value: _to_float(energy_flow_data.get("pvPower")),
                    SunsynkNames.FlowBatteryPower.value: _to_float(energy_flow_data.get("battPower")),
                    SunsynkNames.FlowGridPower.value: _to_float(energy_flow_data.get("gridOrMeterPower")),
                    SunsynkNames.FlowGenPower.value: _to_float(energy_flow_data.get("genPower")),
                    SunsynkNames.FlowMinPower.value: _to_float(energy_flow_data.get("minPower")),
                    SunsynkNames.FlowHeatPumpPower.value: _to_float(energy_flow_data.get("heatPumpPower")),
                    SunsynkNames.FlowSmartLoadPower.value: _to_float(energy_flow_data.get("smartLoadPower")),
                    SunsynkNames.FlowHomeLoadPower.value: _to_float(energy_flow_data.get("homeLoadPower")),
                    # --- Inverter status ---
                    SunsynkNames.InverterStatus.value: _to_float(inverter_data.get("status")),
                    SunsynkNames.GatewayStatus.value: _to_float(gateway_vo.get("status")),
                }

                data[plant_sn_id] = sunsynk_data

            except KeyError as key_error:
                _LOGGER.error(
                    "Missing key in data for inverter %s: %s",
                    plant_sn_id,
                    key_error,
                )
                continue
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
