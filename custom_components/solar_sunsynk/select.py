"""Sunsynk Select entities (mode selections)."""
from dataclasses import dataclass
from typing import Dict, List

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SunsynkDataUpdateCoordinator
from .helpers import SunsynkSettingsMixin, sunsynk_device_info


@dataclass
class _SelectDesc:
    key: str
    name: str
    group: str
    options: Dict[str, str]  # api_value -> display_label


SOLAR_SETTINGS = "System Mode"
BATTERY_SETTINGS = "Battery Settings"
AUXILIARY_LOAD_SETTINGS = "Auxiliary Load Settings"
ADVANCED_SETTINGS = "Advanced Settings"
GRID_SETTINGS = "Grid Settings"


_SELECT_DESCRIPTIONS: List[_SelectDesc] = [
    _SelectDesc(
        key="sysWorkMode",
        name="Work Mode",
        group=SOLAR_SETTINGS,
        options={
            "0": "Selling First",
            "1": "Zero Export + Limit to Load",
            "2": "Limited to Home",
        },
    ),
    _SelectDesc(
        key="battMode",
        name="Battery Type",
        group=BATTERY_SETTINGS,
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
        group=SOLAR_SETTINGS,
        options={
            "0": "Priority Battery",
            "1": "Priority Load",
        },
    ),
    _SelectDesc(
        key="peakAndVallery",
        name="Peak and Valley",
        group=SOLAR_SETTINGS,
        options={
            "0": "Disabled",
            "1": "Enabled",
        },
    ),
    _SelectDesc(
        key="loadMode",
        name="Smart Load Mode",
        group=AUXILIARY_LOAD_SETTINGS,
        options={
            "0": "Generator Input",
            "1": "Aux Load Output",
            "2": "Micro Inverter Input",
        },
    ),
    _SelectDesc(
        key="equipMode",
        name="Equipment Mode",
        group=ADVANCED_SETTINGS,
        options={
            "1": "Master",
            "0": "Slave",
        },
    ),
    _SelectDesc(
        key="phase",
        name="Grid Type",
        group=GRID_SETTINGS,
        options={
            "0": "Single Phase",
            "1": "120/240V Split Phase",
            "2": "120/208V 3 Phase",
        },
    ),
    _SelectDesc(
        key="meterSelect",
        name="Meter Select",
        group=ADVANCED_SETTINGS,
        options={
            "0": "No Meter",
            "1": "Meter 1",
            "2": "Meter 2",
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
        self._attr_entity_category = EntityCategory.CONFIG
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
