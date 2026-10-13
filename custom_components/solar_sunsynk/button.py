"""Sunsynk Button entities."""
import logging
from datetime import datetime, timedelta
from typing import Callable

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import SunsynkDataUpdateCoordinator
from .helpers import SunsynkSettingsMixin, sunsynk_device_info

_LOGGER: logging.Logger = logging.getLogger(__package__)

_TIMED_BUTTONS = [
    ("15 Minute Charge", 15, True),
    ("15 Minute Discharge", 15, False),
    ("30 Minute Charge", 30, True),
    ("30 Minute Discharge", 30, False),
    ("60 Minute Charge", 60, True),
    ("60 Minute Discharge", 60, False),
]

_SLOT_COUNT = 6
_TIME_FORMAT = "%H:%M"
_MINUTES_PER_HOUR = 60


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SunsynkDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[ButtonEntity] = []
    for serial in coordinator.data:
        for label, minutes, is_charge in _TIMED_BUTTONS:
            entities.append(
                SunsynkTimedButton(coordinator, entry, serial, label, minutes, is_charge)
            )
        entities.append(SunsynkResetButton(coordinator, entry, serial))
    _LOGGER.debug("Created %s Sunsynk button entities", len(entities))
    async_add_entities(entities)


class _SunsynkButtonBase(SunsynkSettingsMixin, CoordinatorEntity, ButtonEntity):
    def __init__(
        self,
        coordinator: SunsynkDataUpdateCoordinator,
        config: ConfigEntry,
        serial: str,
    ) -> None:
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._config = config
        self._serial = serial
        self._sn: str = coordinator.data[serial]["inverter_sn"]
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_device_info = sunsynk_device_info(coordinator, serial)

    def _get_current_slot(self, current_time: datetime) -> int:
        settings: dict[str, object] = self._get_settings()
        slot_times: list[int] = [
            _parse_time(settings.get(f"sellTime{slot}"))
            for slot in range(1, _SLOT_COUNT + 1)
        ]

        for index in range(1, len(slot_times)):
            if slot_times[index] <= slot_times[index - 1]:
                _LOGGER.warning(
                    "Unable to run timed charge/discharge for %s because sell time slots are not chronological: %s",
                    self._serial,
                    _format_slot_times(settings),
                )
                raise HomeAssistantError(
                    "Sunsynk timed charge/discharge requires chronological sell time slots."
                )

        current_minutes: int = (
            current_time.hour * _MINUTES_PER_HOUR + current_time.minute
        )
        current_slot: int = _SLOT_COUNT
        for index, slot_time in enumerate(slot_times, start=1):
            if current_minutes >= slot_time:
                current_slot = index
            else:
                break
        _LOGGER.debug(
            "Selected Sunsynk slot %s for %s at %s from sell time slots %s",
            current_slot,
            self._serial,
            current_time.strftime(_TIME_FORMAT),
            _format_slot_times(settings),
        )
        return current_slot

    async def _restore_timed_grid_charge(
        self,
        restore_key: str,
        setting_key: str,
        applied_value: str,
        previous_value: str,
    ) -> None:
        self._coordinator.pending_timed_grid_charge_restores.pop(restore_key, None)
        self._coordinator.timed_grid_charge_restore_values.pop(restore_key, None)
        _LOGGER.debug(
            "Running timed grid charge restore for %s: %s from %s back to %s",
            self._serial,
            setting_key,
            applied_value,
            previous_value,
        )
        await self._coordinator.async_request_refresh()
        current_value: str = _normalize_bool_value(
            self._get_settings().get(setting_key)
        )
        if current_value == previous_value:
            _LOGGER.debug(
                "Timed grid charge setting already restored for %s: %s=%s",
                self._serial,
                setting_key,
                previous_value,
            )
            return

        if current_value != applied_value:
            _LOGGER.debug(
                "Skipped timed grid charge restore for %s because %s changed externally from %s to %s",
                self._serial,
                setting_key,
                applied_value,
                current_value,
            )
            return

        await self._send_update({setting_key: previous_value})
        _LOGGER.debug(
            "Restored timed grid charge setting for %s: %s=%s",
            self._serial,
            setting_key,
            previous_value,
        )
        await self._coordinator.async_request_refresh()

    async def _restore_pending_grid_charge(self, restore_key: str) -> None:
        restore_values: dict[str, str] | None = (
            self._coordinator.timed_grid_charge_restore_values.pop(restore_key, None)
        )
        cancel_restore: Callable[[], None] | None = (
            self._coordinator.pending_timed_grid_charge_restores.pop(
                restore_key, None
            )
        )
        if cancel_restore is not None:
            cancel_restore()
            _LOGGER.debug(
                "Cancelled pending timed grid charge restore for %s",
                restore_key,
            )

        if restore_values is None:
            _LOGGER.debug(
                "No pending timed grid charge restore values found for %s",
                restore_key,
            )
            return

        await self._send_update(
            {restore_values["setting_key"]: restore_values["previous_value"]}
        )
        _LOGGER.debug(
            "Reset restored timed grid charge setting for %s: %s=%s",
            self._serial,
            restore_values["setting_key"],
            restore_values["previous_value"],
        )
        await self._coordinator.async_request_refresh()


class SunsynkTimedButton(_SunsynkButtonBase):
    def __init__(
        self,
        coordinator: SunsynkDataUpdateCoordinator,
        config: ConfigEntry,
        serial: str,
        label: str,
        minutes: int,
        is_charge: bool,
    ) -> None:
        super().__init__(coordinator, config, serial)
        self._minutes = minutes
        self._is_charge = is_charge
        self._attr_name = label
        self._attr_unique_id = (
            f"{config.entry_id}_{serial}_{label.lower().replace(' ', '_')}"
        )

    async def async_press(self) -> None:
        now: datetime = dt_util.now()
        action: str = "charge" if self._is_charge else "discharge"
        _LOGGER.debug(
            "Timed %s requested for %s minutes on %s at %s",
            action,
            self._minutes,
            self._serial,
            now.strftime(_TIME_FORMAT),
        )
        current_slot: int = self._get_current_slot(now)
        setting_key: str = f"time{current_slot}on"
        restore_key: str = f"{self._serial}_{setting_key}"
        current_value: str = _normalize_bool_value(self._get_settings().get(setting_key))
        restore_values: dict[str, str] | None = (
            self._coordinator.timed_grid_charge_restore_values.get(restore_key)
        )
        previous_value: str = (
            restore_values["previous_value"]
            if restore_values is not None
            else current_value
        )
        applied_value: str = "true" if self._is_charge else "false"
        _LOGGER.debug(
            "Timed %s for %s will set %s from %s to %s and restore to %s",
            action,
            self._serial,
            setting_key,
            current_value,
            applied_value,
            previous_value,
        )

        cancel_restore: Callable[[], None] | None = (
            self._coordinator.pending_timed_grid_charge_restores.pop(
                restore_key, None
            )
        )
        if cancel_restore is not None:
            cancel_restore()
            _LOGGER.debug("Cancelled existing timed restore for %s", restore_key)

        self._coordinator.timed_grid_charge_restore_values.pop(restore_key, None)

        if current_value != applied_value:
            _LOGGER.debug(
                "Sending timed %s update for %s: %s=%s",
                action,
                self._serial,
                setting_key,
                applied_value,
            )
            await self._send_update({setting_key: applied_value})
            _LOGGER.debug(
                "Sent timed %s update for %s: %s=%s",
                action,
                self._serial,
                setting_key,
                applied_value,
            )
        else:
            _LOGGER.debug(
                "No timed %s update needed for %s: %s is already %s",
                action,
                self._serial,
                setting_key,
                applied_value,
            )

        if previous_value == applied_value:
            _LOGGER.debug(
                "No restore scheduled for timed %s on %s because previous value already matched %s",
                action,
                self._serial,
                applied_value,
            )
            return

        async def async_restore(now: datetime) -> None:
            await self._restore_timed_grid_charge(
                restore_key, setting_key, applied_value, previous_value
            )

        cancel_new_restore: Callable[[], None] = async_call_later(
            self._coordinator.hass,
            timedelta(minutes=self._minutes),
            async_restore,
        )
        self._coordinator.pending_timed_grid_charge_restores[
            restore_key
        ] = cancel_new_restore
        self._coordinator.timed_grid_charge_restore_values[restore_key] = {
            "setting_key": setting_key,
            "previous_value": previous_value,
        }
        _LOGGER.debug(
            "Scheduled timed %s restore for %s in %s minutes: %s=%s",
            action,
            self._serial,
            self._minutes,
            setting_key,
            previous_value,
        )


class SunsynkResetButton(_SunsynkButtonBase):
    def __init__(
        self,
        coordinator: SunsynkDataUpdateCoordinator,
        config: ConfigEntry,
        serial: str,
    ) -> None:
        super().__init__(coordinator, config, serial)
        self._attr_name = "Reset Charge/Discharge"
        self._attr_unique_id = f"{config.entry_id}_{serial}_reset_charge_discharge"

    async def async_press(self) -> None:
        restore_keys: list[str] = [
            restore_key
            for restore_key in self._coordinator.timed_grid_charge_restore_values
            if restore_key.startswith(f"{self._serial}_")
        ]
        _LOGGER.debug(
            "Reset Charge/Discharge pressed for %s with %s pending restores",
            self._serial,
            len(restore_keys),
        )
        for restore_key in restore_keys:
            await self._restore_pending_grid_charge(restore_key)


def _parse_time(value: object) -> int:
    if not isinstance(value, str):
        raise HomeAssistantError(
            "Sunsynk timed charge/discharge requires configured sell time slots."
        )

    try:
        parsed_time: datetime = datetime.strptime(value, _TIME_FORMAT)
    except ValueError as ex:
        raise HomeAssistantError(
            "Sunsynk timed charge/discharge requires sell time slots in HH:MM format."
        ) from ex

    return parsed_time.hour * _MINUTES_PER_HOUR + parsed_time.minute


def _normalize_bool_value(value: object) -> str:
    return (
        "true"
        if value is True or str(value).lower() in {"true", "1", "on", "yes"}
        else "false"
    )


def _format_slot_times(settings: dict[str, object]) -> str:
    slot_values: list[str] = [
        f"sellTime{slot}={settings.get(f'sellTime{slot}')}"
        for slot in range(1, _SLOT_COUNT + 1)
    ]
    return ", ".join(slot_values)
