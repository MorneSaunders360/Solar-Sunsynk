"""Sunsynk Text entities (time slot strings)."""
from homeassistant.components.text import TextEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SunsynkDataUpdateCoordinator
from .helpers import SunsynkSettingsMixin, sunsynk_device_info

_TIME_KEYS = [f"sellTime{i}" for i in range(1, 7)]


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator: SunsynkDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for serial in coordinator.data:
        for i, key in enumerate(_TIME_KEYS, start=1):
            entities.append(SunsynkTimeText(coordinator, entry, serial, key, i))
    async_add_entities(entities)


class SunsynkTimeText(SunsynkSettingsMixin, CoordinatorEntity, TextEntity):
    _attr_pattern = r"^([01]\d|2[0-3]):[0-5]\d$"

    def __init__(
        self,
        coordinator: SunsynkDataUpdateCoordinator,
        config,
        serial: str,
        key: str,
        slot: int,
    ):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._config = config
        self._serial = serial
        self._sn: str = coordinator.data[serial]["inverter_sn"]
        self._key = key
        self._attr_name = f"Sell Time {slot}"
        self._attr_unique_id = f"{config.entry_id}_{serial}_{key}"
        self._attr_device_info = sunsynk_device_info(coordinator, serial)

    @property
    def native_value(self) -> str:
        optimistic = self._get_optimistic()
        if optimistic is not None:
            return optimistic
        return self.coordinator.data[self._serial].get("settings", {}).get(self._key, "00:00")

    async def async_set_value(self, value: str) -> None:
        self._set_optimistic(value)
        await self._send_update({self._key: value})
