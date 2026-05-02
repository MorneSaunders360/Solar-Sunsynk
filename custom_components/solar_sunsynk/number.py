"""Sunsynk Number entities."""
from dataclasses import dataclass
from typing import List

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import (
    EntityCategory,
    PERCENTAGE,
    UnitOfElectricPotential,
    UnitOfPower,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SunsynkDataUpdateCoordinator
from .helpers import SunsynkSettingsMixin, sunsynk_device_info


@dataclass
class _NumberDesc:
    key: str
    name: str
    group: str
    min_value: float
    max_value: float
    step: float = 1.0
    unit: str | None = None
    enabled_default: bool = True


SOLAR_SETTINGS = "System Mode"
BATTERY_SETTINGS = "Battery Settings"
AUXILIARY_LOAD_SETTINGS = "Auxiliary Load Settings"
ADVANCED_SETTINGS = "Advanced Settings"
GRID_SETTINGS = "Grid Settings"


_SLOT_NUMBERS: List[_NumberDesc] = [
    *[
        _NumberDesc(f"cap{i}", f"Slot {i} Battery SOC", SOLAR_SETTINGS, 0, 100, 1, PERCENTAGE)
        for i in range(1, 7)
    ],
    *[
        _NumberDesc(
            f"sellTime{i}Pac",
            f"Slot {i} Power",
            SOLAR_SETTINGS,
            0,
            15000,
            100,
            UnitOfPower.WATT,
        )
        for i in range(1, 7)
    ],
    *[
        _NumberDesc(
            f"sellTime{i}Volt",
            f"Slot {i} Min Voltage",
            SOLAR_SETTINGS,
            40,
            65,
            0.1,
            UnitOfElectricPotential.VOLT,
        )
        for i in range(1, 7)
    ],
]

_SYSTEM_NUMBERS: List[_NumberDesc] = [
    _NumberDesc("pvMaxLimit", "PV Max Limit", SOLAR_SETTINGS, 0, 15000, 100, UnitOfPower.WATT),
    _NumberDesc("zeroExportPower", "Zero Export Power", SOLAR_SETTINGS, 0, 15000, 10, UnitOfPower.WATT),
]

_BATTERY_NUMBERS: List[_NumberDesc] = [
    _NumberDesc("batteryCap", "Capacity", BATTERY_SETTINGS, 0, 9999, 1, "Ah"),
    _NumberDesc("batteryMaxCurrentCharge", "Charge Current", BATTERY_SETTINGS, 0, 275, 1, "A"),
    _NumberDesc("batteryMaxCurrentDischarge", "Discharge Current", BATTERY_SETTINGS, 0, 275, 1, "A"),
    _NumberDesc("batteryEmptyV", "Empty Voltage", BATTERY_SETTINGS, 41, 63, 0.1, UnitOfElectricPotential.VOLT),
    _NumberDesc("batteryImpedance", "Impedance", BATTERY_SETTINGS, 0, 100, 1),
    _NumberDesc("batteryEfficiency", "Efficiency", BATTERY_SETTINGS, 0, 100, 1, PERCENTAGE),
    _NumberDesc("batteryShutdownCap", "Shutdown SOC", BATTERY_SETTINGS, 0, 100, 1, PERCENTAGE),
    _NumberDesc("batteryLowCap", "Low SOC", BATTERY_SETTINGS, 0, 100, 1, PERCENTAGE),
    _NumberDesc("batteryRestartCap", "Restart SOC", BATTERY_SETTINGS, 0, 100, 1, PERCENTAGE),
    _NumberDesc("batteryShutdownVolt", "Shutdown Voltage", BATTERY_SETTINGS, 41, 63, 0.1, UnitOfElectricPotential.VOLT),
    _NumberDesc("batteryLowVolt", "Low Voltage", BATTERY_SETTINGS, 41, 63, 0.1, UnitOfElectricPotential.VOLT),
    _NumberDesc("batteryRestartVolt", "Restart Voltage", BATTERY_SETTINGS, 41, 63, 0.1, UnitOfElectricPotential.VOLT),
    _NumberDesc("floatVolt", "Float Voltage", BATTERY_SETTINGS, 41, 63, 0.1, UnitOfElectricPotential.VOLT),
    _NumberDesc("lithiumMode", "Lithium Protocol", BATTERY_SETTINGS, 0, 20, 1),
    _NumberDesc("sdStartCap", "Grid Start SOC", BATTERY_SETTINGS, 0, 100, 1, PERCENTAGE),
    _NumberDesc("sdBatteryCurrent", "Grid Charge Current", BATTERY_SETTINGS, 0, 275, 1, "A"),
    _NumberDesc("generatorStartCap", "Generator Start SOC", BATTERY_SETTINGS, 0, 100, 1, PERCENTAGE),
    _NumberDesc("generatorStartVolt", "Generator Start Voltage", BATTERY_SETTINGS, 0, 65, 0.1, UnitOfElectricPotential.VOLT),
    _NumberDesc("generatorBatteryCurrent", "Generator Charge Current", BATTERY_SETTINGS, 0, 275, 1, "A"),
    _NumberDesc("equChargeCycle", "Equalization Charge Cycle", BATTERY_SETTINGS, 0, 365, 1),
    _NumberDesc("equChargeTime", "Equalization Charge Time", BATTERY_SETTINGS, 0, 24, 1, "h"),
    _NumberDesc("absorptionVolt", "Absorption Voltage", BATTERY_SETTINGS, 41, 63, 0.1, UnitOfElectricPotential.VOLT),
    _NumberDesc("equVoltCharge", "Equalization Charge Voltage", BATTERY_SETTINGS, 41, 63, 0.1, UnitOfElectricPotential.VOLT),
    _NumberDesc("tempco", "Temperature Compensation", BATTERY_SETTINGS, 0, 20, 1),
    _NumberDesc("sdStartVolt", "Grid Start Voltage", BATTERY_SETTINGS, 0, 65, 0.1, UnitOfElectricPotential.VOLT),
    _NumberDesc("lowNoiseMode", "Low Noise Mode", BATTERY_SETTINGS, 0, 10000, 100),
]

_AUXILIARY_LOAD_NUMBERS: List[_NumberDesc] = [
    _NumberDesc("genMinSolar", "Generator Minimum Solar", AUXILIARY_LOAD_SETTINGS, 0, 30000, 100, UnitOfPower.WATT),
    _NumberDesc("genOffCap", "Generator Off SOC", AUXILIARY_LOAD_SETTINGS, 0, 100, 1, PERCENTAGE),
    _NumberDesc("genOnCap", "Generator On SOC", AUXILIARY_LOAD_SETTINGS, 0, 100, 1, PERCENTAGE),
    _NumberDesc("genOffVolt", "Generator Off Voltage", AUXILIARY_LOAD_SETTINGS, 0, 65, 0.1, UnitOfElectricPotential.VOLT),
    _NumberDesc("genOnVolt", "Generator On Voltage", AUXILIARY_LOAD_SETTINGS, 0, 65, 0.1, UnitOfElectricPotential.VOLT),
    _NumberDesc("acCoupleFreqUpper", "AC Couple Upper Frequency", AUXILIARY_LOAD_SETTINGS, 45, 65, 0.1, "Hz"),
    _NumberDesc("genPeakPower", "Generator Peak Shaving Power", AUXILIARY_LOAD_SETTINGS, 500, 30000, 100, UnitOfPower.WATT),
]

_ADVANCED_NUMBERS: List[_NumberDesc] = [
    _NumberDesc("modbusSn", "Modbus SN", ADVANCED_SETTINGS, 0, 16, 1),
    _NumberDesc("externalCtRatio", "CT Ratio", ADVANCED_SETTINGS, 0, 10000, 1),
    _NumberDesc("solarMaxSellPower", "Max Solar Power", ADVANCED_SETTINGS, 0, 30000, 100, UnitOfPower.WATT),
]

_GRID_NUMBERS: List[_NumberDesc] = [
    _NumberDesc("gridPeakPower", "Grid Peak Shaving Power", GRID_SETTINGS, 0, 65000, 100, UnitOfPower.WATT),
    _NumberDesc("backupDelay", "Backup Delay", GRID_SETTINGS, 0, 600, 1, "s"),
    _NumberDesc("acOutputPowerLimit", "AC Output Power Limit", GRID_SETTINGS, 0, 8000, 1, UnitOfPower.WATT),
    *[
        _NumberDesc(f"volt{i}", f"Voltage Curve {i}", GRID_SETTINGS, -10000, 10000, 0.1, UnitOfElectricPotential.VOLT, False)
        for i in range(1, 13)
    ],
    *[
        _NumberDesc(f"current{i}", f"Current Curve {i}", GRID_SETTINGS, -10000, 10000, 0.1, "A", False)
        for i in range(1, 13)
    ],
]

ALL_NUMBERS = (
    _SLOT_NUMBERS
    + _SYSTEM_NUMBERS
    + _BATTERY_NUMBERS
    + _AUXILIARY_LOAD_NUMBERS
    + _ADVANCED_NUMBERS
    + _GRID_NUMBERS
)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator: SunsynkDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for serial in coordinator.data:
        for desc in ALL_NUMBERS:
            entities.append(SunsynkNumber(coordinator, entry, serial, desc))
    async_add_entities(entities)


class SunsynkNumber(SunsynkSettingsMixin, CoordinatorEntity, NumberEntity):
    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        coordinator: SunsynkDataUpdateCoordinator,
        config,
        serial: str,
        desc: _NumberDesc,
    ):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._config = config
        self._serial = serial
        self._sn: str = coordinator.data[serial]["inverter_sn"]
        self._desc = desc
        self._attr_name = desc.name
        self._attr_unique_id = f"{config.entry_id}_{serial}_{desc.key}"
        self._attr_native_min_value = desc.min_value
        self._attr_native_max_value = desc.max_value
        self._attr_native_step = desc.step
        self._attr_native_unit_of_measurement = desc.unit
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_entity_registry_enabled_default = desc.enabled_default
        self._attr_device_info = sunsynk_device_info(coordinator, serial)

    @property
    def native_value(self) -> float:
        optimistic = self._get_optimistic()
        if optimistic is not None:
            return optimistic
        val = self.coordinator.data[self._serial].get("settings", {}).get(self._desc.key)
        try:
            return float(val) if val is not None else 0.0
        except (ValueError, TypeError):
            return 0.0

    async def async_set_native_value(self, value: float) -> None:
        self._set_optimistic(value)
        await self._send_update({self._desc.key: _format_number(value)})


def _format_number(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.3f}".rstrip("0").rstrip(".")
