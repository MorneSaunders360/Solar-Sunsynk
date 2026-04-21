"""Sunsynk Number entities."""
from dataclasses import dataclass
from typing import List

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import PERCENTAGE, UnitOfElectricPotential, UnitOfPower
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SunsynkDataUpdateCoordinator
from .helpers import SunsynkSettingsMixin, sunsynk_device_info


@dataclass
class _NumberDesc:
    key: str
    name: str
    min_value: float
    max_value: float
    step: float = 1.0
    unit: str | None = None


_SLOT_NUMBERS: List[_NumberDesc] = [
    *[_NumberDesc(f"cap{i}", f"Cap {i} (SOC %)", 0, 100, 1, PERCENTAGE) for i in range(1, 7)],
    *[_NumberDesc(f"sellTime{i}Pac", f"Sell Time {i} Power", 0, 15000, 100, UnitOfPower.WATT) for i in range(1, 7)],
    *[_NumberDesc(f"sellTime{i}Volt", f"Sell Time {i} Min Voltage", 40, 65, 1, UnitOfElectricPotential.VOLT) for i in range(1, 7)],
]

_SYSTEM_NUMBERS: List[_NumberDesc] = [
    _NumberDesc("pvMaxLimit", "PV Max Limit", 0, 15000, 100, UnitOfPower.WATT),
    _NumberDesc("zeroExportPower", "Zero Export Power", 0, 15000, 10, UnitOfPower.WATT),
    _NumberDesc("solarMaxSellPower", "Solar Max Sell Power", 0, 15000, 100, UnitOfPower.WATT),
    _NumberDesc("batteryLowCap", "Battery Low Cap", 0, 100, 1, PERCENTAGE),
    _NumberDesc("generatorStartCap", "Generator Start Cap", 0, 100, 1, PERCENTAGE),
    _NumberDesc("gridPeakShaving", "Grid Peak Shaving", 0, 15000, 100, UnitOfPower.WATT),
]

ALL_NUMBERS = _SLOT_NUMBERS + _SYSTEM_NUMBERS


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
        await self._send_update({self._desc.key: str(int(value))})
