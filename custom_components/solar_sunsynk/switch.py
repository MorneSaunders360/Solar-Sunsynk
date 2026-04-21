"""Sunsynk Switch entities."""
from dataclasses import dataclass
from typing import List

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SunsynkDataUpdateCoordinator
from .helpers import SunsynkSettingsMixin, sunsynk_device_info


@dataclass
class _SwitchDesc:
    key: str
    name: str


_SWITCH_DESCRIPTIONS: List[_SwitchDesc] = [
    *[_SwitchDesc(f"time{i}on", f"Grid Charge Time {i}") for i in range(1, 7)],
    *[_SwitchDesc(f"genTime{i}on", f"Gen Charge Time {i}") for i in range(1, 7)],
    _SwitchDesc("mondayOn", "Monday"),
    _SwitchDesc("tuesdayOn", "Tuesday"),
    _SwitchDesc("wednesdayOn", "Wednesday"),
    _SwitchDesc("thursdayOn", "Thursday"),
    _SwitchDesc("fridayOn", "Friday"),
    _SwitchDesc("saturdayOn", "Saturday"),
    _SwitchDesc("sundayOn", "Sunday"),
]


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator: SunsynkDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for serial in coordinator.data:
        for desc in _SWITCH_DESCRIPTIONS:
            entities.append(SunsynkSwitch(coordinator, entry, serial, desc))
    async_add_entities(entities)


def _is_truthy(val) -> bool:
    return val is True or str(val).lower() == "true"


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
        await self._send_update({self._desc.key: "true"})

    async def async_turn_off(self, **kwargs) -> None:
        self._set_optimistic(False)
        await self._send_update({self._desc.key: "false"})
