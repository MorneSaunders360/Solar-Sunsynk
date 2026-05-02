"""Sunsynk Switch entities."""
from dataclasses import dataclass
from typing import List

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SunsynkDataUpdateCoordinator
from .helpers import SunsynkSettingsMixin, sunsynk_device_info


@dataclass
class _SwitchDesc:
    key: str
    name: str
    group: str
    on_value: str = "true"
    off_value: str = "false"
    enabled_default: bool = True


SOLAR_SETTINGS = "System Mode"
BATTERY_SETTINGS = "Battery Settings"
BASIC_SETTINGS = "Basic Settings"
AUXILIARY_LOAD_SETTINGS = "Auxiliary Load Settings"
ADVANCED_SETTINGS = "Advanced Settings"
GRID_SETTINGS = "Grid Settings"


_SWITCH_DESCRIPTIONS: List[_SwitchDesc] = [
    *[_SwitchDesc(f"time{i}on", f"Grid Charge Time {i}", SOLAR_SETTINGS) for i in range(1, 7)],
    *[_SwitchDesc(f"genTime{i}on", f"Gen Charge Time {i}", SOLAR_SETTINGS) for i in range(1, 7)],
    _SwitchDesc("mondayOn", "Monday", SOLAR_SETTINGS),
    _SwitchDesc("tuesdayOn", "Tuesday", SOLAR_SETTINGS),
    _SwitchDesc("wednesdayOn", "Wednesday", SOLAR_SETTINGS),
    _SwitchDesc("thursdayOn", "Thursday", SOLAR_SETTINGS),
    _SwitchDesc("fridayOn", "Friday", SOLAR_SETTINGS),
    _SwitchDesc("saturdayOn", "Saturday", SOLAR_SETTINGS),
    _SwitchDesc("sundayOn", "Sunday", SOLAR_SETTINGS),
    _SwitchDesc("batteryOn", "Battery Enabled", BATTERY_SETTINGS, "1", "0"),
    _SwitchDesc("sdChargeOn", "Grid Charge", BATTERY_SETTINGS, "1", "0"),
    _SwitchDesc("genChargeOn", "Generator Charge", BATTERY_SETTINGS, "1", "0"),
    _SwitchDesc("gridSignal", "Grid Signal", BATTERY_SETTINGS, "1", "0"),
    _SwitchDesc("genSignal", "Generator Signal", BATTERY_SETTINGS, "1", "0"),
    _SwitchDesc("generatorForcedStart", "Generator Forced Start", BATTERY_SETTINGS, "1", "0"),
    _SwitchDesc("bmsErrStop", "BMS Error Stop", BATTERY_SETTINGS, "1", "0"),
    _SwitchDesc("signalIslandModeEnable", "Signal Island Mode", BATTERY_SETTINGS, "1", "0"),
    _SwitchDesc("lowPowerMode", "Low Power Mode", BATTERY_SETTINGS, "1", "0"),
    _SwitchDesc("disableFloatCharge", "Disable Float Charge", BATTERY_SETTINGS, "1", "0"),
    _SwitchDesc("timeSync", "Time Sync", BASIC_SETTINGS, "1", "0"),
    _SwitchDesc("beep", "Beeper", BASIC_SETTINGS, "1", "0"),
    _SwitchDesc("ampm", "AM/PM", BASIC_SETTINGS, "1", "0"),
    _SwitchDesc("autoDim", "Auto Dim", BASIC_SETTINGS, "1", "0"),
    _SwitchDesc("lockOutChange", "Lock Out All Changes", BASIC_SETTINGS, "1", "0"),
    _SwitchDesc("genPeakShaving", "Generator Peak Shaving", AUXILIARY_LOAD_SETTINGS, "1", "0"),
    _SwitchDesc("genConnectGrid", "Generator Connect to Grid", AUXILIARY_LOAD_SETTINGS, "1", "0"),
    _SwitchDesc("acCoupleOnLoadSideEnable", "AC Couple on Load Side", AUXILIARY_LOAD_SETTINGS, "1", "0"),
    _SwitchDesc("acCoupleOnGridSideEnable", "AC Couple on Grid Side", AUXILIARY_LOAD_SETTINGS, "1", "0"),
    _SwitchDesc("parallel", "Parallel", ADVANCED_SETTINGS, "1", "0"),
    _SwitchDesc("gridSideINVMeter2", "Grid Side INV Meter2", ADVANCED_SETTINGS, "1", "0"),
    _SwitchDesc("exMeterCtSwitch", "External Meter for CT", ADVANCED_SETTINGS, "1", "0"),
    _SwitchDesc("mpptMulti", "MPPT Multi-Point Scanning", ADVANCED_SETTINGS, "1", "0"),
    _SwitchDesc("pv1SelfCheck", "PV1 Self Check", ADVANCED_SETTINGS, "1", "0"),
    _SwitchDesc("pv2SelfCheck", "PV2 Self Check", ADVANCED_SETTINGS, "1", "0"),
    _SwitchDesc("gridPeakShaving", "Grid Peak Shaving", GRID_SETTINGS, "1", "0"),
    _SwitchDesc("gridAlwaysOn", "Grid Always On", GRID_SETTINGS, "1", "0"),
    _SwitchDesc("micExportGridOff", "Micro Inverter Export Grid Off", GRID_SETTINGS, "1", "0"),
    _SwitchDesc("remoteLock", "Remote Lock", GRID_SETTINGS, "1", "0", False),
    _SwitchDesc("atsEnable", "ATS Enable", GRID_SETTINGS, "1", "0", False),
    _SwitchDesc("atsSwitch", "ATS Switch", GRID_SETTINGS, "1", "0", False),
    _SwitchDesc("drmEnable", "DRM Enable", GRID_SETTINGS, "1", "0", False),
    _SwitchDesc("isletProtect", "Islet Protect", GRID_SETTINGS, "1", "0", False),
    _SwitchDesc("solar1WindInputEnable", "DC1 Wind Turbine", GRID_SETTINGS, "1", "0", False),
    _SwitchDesc("solar2WindInputEnable", "DC2 Wind Turbine", GRID_SETTINGS, "1", "0", False),
    _SwitchDesc("solar3WindInputEn", "DC3 Wind Turbine", GRID_SETTINGS, "1", "0", False),
    _SwitchDesc("genToLoad", "Generator to Load", GRID_SETTINGS, "1", "0", False),
]


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator: SunsynkDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for serial in coordinator.data:
        for desc in _SWITCH_DESCRIPTIONS:
            entities.append(SunsynkSwitch(coordinator, entry, serial, desc))
    async_add_entities(entities)


def _is_truthy(val) -> bool:
    return val is True or str(val).lower() in {"true", "1", "on", "yes"}


class SunsynkSwitch(SunsynkSettingsMixin, CoordinatorEntity, SwitchEntity):
    def __init__(
        self,
        coordinator: SunsynkDataUpdateCoordinator,
        config,
        serial: str,
        desc: _SwitchDesc,
    ):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._config = config
        self._serial = serial
        self._sn: str = coordinator.data[serial]["inverter_sn"]
        self._desc = desc
        self._attr_name = desc.name
        self._attr_unique_id = f"{config.entry_id}_{serial}_{desc.key}"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_entity_registry_enabled_default = desc.enabled_default
        self._attr_device_info = sunsynk_device_info(coordinator, serial)

    @property
    def is_on(self) -> bool:
        optimistic = self._get_optimistic()
        if optimistic is not None:
            return optimistic
        val = self.coordinator.data[self._serial].get("settings", {}).get(self._desc.key, False)
        return _is_truthy(val)

    async def async_turn_on(self, **kwargs) -> None:
        self._set_optimistic(True)
        await self._send_update({self._desc.key: self._desc.on_value})

    async def async_turn_off(self, **kwargs) -> None:
        self._set_optimistic(False)
        await self._send_update({self._desc.key: self._desc.off_value})
