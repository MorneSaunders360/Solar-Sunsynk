"""Sunsynk Button entities."""
from datetime import datetime, timedelta

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SunsynkDataUpdateCoordinator
from .helpers import SunsynkSettingsMixin, sunsynk_device_info

_TIMED_BUTTONS = [
    ("15 Minute Charge", 15, True),
    ("15 Minute Discharge", 15, False),
    ("30 Minute Charge", 30, True),
    ("30 Minute Discharge", 30, False),
    ("60 Minute Charge", 60, True),
    ("60 Minute Discharge", 60, False),
]


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator: SunsynkDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for serial in coordinator.data:
        for label, minutes, is_charge in _TIMED_BUTTONS:
            entities.append(
                SunsynkTimedButton(coordinator, entry, serial, label, minutes, is_charge)
            )
        entities.append(SunsynkResetButton(coordinator, entry, serial))
    async_add_entities(entities)


class _SunsynkButtonBase(SunsynkSettingsMixin, CoordinatorEntity, ButtonEntity):
    def __init__(self, coordinator: SunsynkDataUpdateCoordinator, config, serial: str):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._config = config
        self._serial = serial
        self._sn: str = coordinator.data[serial]["inverter_sn"]
        self._attr_device_info = sunsynk_device_info(coordinator, serial)


class SunsynkTimedButton(_SunsynkButtonBase):
    def __init__(
        self,
        coordinator: SunsynkDataUpdateCoordinator,
        config,
        serial: str,
        label: str,
        minutes: int,
        is_charge: bool,
    ):
        super().__init__(coordinator, config, serial)
        self._minutes = minutes
        self._is_charge = is_charge
        self._attr_name = label
        self._attr_unique_id = (
            f"{config.entry_id}_{serial}_{label.lower().replace(' ', '_')}"
        )

    async def async_press(self) -> None:
        now = datetime.now()
        end = now + timedelta(minutes=self._minutes)
        await self._send_update(
            {
                "sellTime1": now.strftime("%H:%M"),
                "sellTime2": end.strftime("%H:%M"),
                "time1on": "true" if self._is_charge else "false",
                "time2on": "false",
                "time3on": "false",
                "time4on": "false",
                "time5on": "false",
                "time6on": "false",
            }
        )


class SunsynkResetButton(_SunsynkButtonBase):
    def __init__(self, coordinator: SunsynkDataUpdateCoordinator, config, serial: str):
        super().__init__(coordinator, config, serial)
        self._attr_name = "Reset Charge/Discharge"
        self._attr_unique_id = f"{config.entry_id}_{serial}_reset_charge_discharge"

    async def async_press(self) -> None:
        await self._send_update(
            {
                "time1on": "false",
                "time2on": "false",
                "time3on": "false",
                "time4on": "false",
                "time5on": "false",
                "time6on": "false",
            }
        )
