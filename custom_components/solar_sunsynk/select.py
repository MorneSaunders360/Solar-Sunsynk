"""Sunsynk Select entities (mode selections)."""
from dataclasses import dataclass
from typing import Dict, List

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SunsynkDataUpdateCoordinator
from .helpers import SunsynkSettingsMixin, sunsynk_device_info


@dataclass
class _SelectDesc:
    key: str
    name: str
    options: Dict[str, str]  # api_value -> display_label


_SELECT_DESCRIPTIONS: List[_SelectDesc] = [
    _SelectDesc(
        key="sysWorkMode",
        name="Work Mode",
        options={
            "0": "Selling First",
            "1": "Zero Export + Limit to Load",
            "2": "Limited to Home",
        },
    ),
    _SelectDesc(
        key="battMode",
        name="Battery Type",
        options={
            "-1": "Lithium",
            "0": "AGM Voltage",
            "1": "AGM Percentage",
            "2": "No Battery",
        },
    ),
    _SelectDesc(
        key="energyMode",
        name="Energy Pattern",
        options={
            "0": "Priority Battery",
            "1": "Priority Load",
        },
    ),
    _SelectDesc(
        key="peakAndVallery",
        name="Peak and Valley",
        options={
            "0": "Disabled",
            "1": "Enabled",
        },
    ),
]


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator: SunsynkDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for serial in coordinator.data:
        for desc in _SELECT_DESCRIPTIONS:
            entities.append(SunsynkSelect(coordinator, entry, serial, desc))
    async_add_entities(entities)


class SunsynkSelect(SunsynkSettingsMixin, CoordinatorEntity, SelectEntity):
    def __init__(
        self,
        coordinator: SunsynkDataUpdateCoordinator,
        config,
        serial: str,
        desc: _SelectDesc,
    ):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._config = config
        self._serial = serial
        self._sn: str = coordinator.data[serial]["inverter_sn"]
        self._desc = desc
        self._attr_name = desc.name
        self._attr_unique_id = f"{config.entry_id}_{serial}_{desc.key}"
        self._attr_options = list(desc.options.values())
        self._attr_device_info = sunsynk_device_info(coordinator, serial)

    @property
    def current_option(self) -> str | None:
        optimistic = self._get_optimistic()
        if optimistic is not None:
            return optimistic
        api_val = self.coordinator.data[self._serial].get("settings", {}).get(self._desc.key)
        return self._desc.options.get(str(api_val) if api_val is not None else "")

    async def async_select_option(self, option: str) -> None:
        self._set_optimistic(option)
        api_val = next(k for k, v in self._desc.options.items() if v == option)
        await self._send_update({self._desc.key: api_val})
