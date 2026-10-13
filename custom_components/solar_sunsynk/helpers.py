import asyncio
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

if TYPE_CHECKING:
    from .coordinator import SunsynkDataUpdateCoordinator

_LOGGER: logging.Logger = logging.getLogger(__name__)


def sunsynk_device_info(
    coordinator: "SunsynkDataUpdateCoordinator", serial: str
) -> DeviceInfo:
    inverter: dict[str, Any] = (coordinator.data or {}).get(serial, {})
    return DeviceInfo(
        entry_type=DeviceEntryType.SERVICE,
        identifiers={(DOMAIN, serial)},
        manufacturer="Sunsynk",
        model=inverter.get("Model", ""),
        name=f"Sunsynk Statistics : {serial}",
    )


class SunsynkSettingsMixin:
    _coordinator: "SunsynkDataUpdateCoordinator"
    _serial: str
    _sn: str
    _setting_key: str | None = None

    def _get_settings(self) -> dict[str, Any]:
        inverter: object = (self._coordinator.data or {}).get(self._serial)
        if not isinstance(inverter, dict):
            return {}
        settings: object = inverter.get("settings")
        return settings if isinstance(settings, dict) else {}

    @property
    def available(self) -> bool:
        settings: dict[str, Any] = self._get_settings()
        return (
            super().available
            and bool(settings)
            and (
                self._setting_key is None
                or settings.get(self._setting_key) is not None
            )
        )

    def _validate_settings(
        self, settings: dict[str, Any], required_keys: set[str]
    ) -> None:
        if not settings or any(
            not isinstance(settings.get(key), (str, int, float, bool))
            or (isinstance(settings.get(key), str) and settings[key].strip() in {"", "--"})
            for key in required_keys
        ):
            raise HomeAssistantError(
                "Sunsynk settings are incomplete; no write was sent. "
                "Wait for a successful settings refresh."
            )

    async def _send_update(self, overrides: dict[str, Any]) -> None:
        setting_keys: list[str] = sorted(key for key in overrides if key != "sn")
        write_lock: asyncio.Lock = self._coordinator.settings_write_locks.setdefault(
            self._serial, asyncio.Lock()
        )
        async with write_lock:
            try:
                if not self._coordinator.last_update_success:
                    raise HomeAssistantError(
                        "Sunsynk data refresh failed; no write was sent."
                    )
                cached_settings: dict[str, Any] = self._get_settings()
                required_keys: set[str] = (
                    {key for key, value in cached_settings.items() if value is not None}
                    | self._coordinator.settings_keys.get(self._serial, set())
                    | set(overrides)
                    | {"safetyType", "battMode"}
                ) - {"sn"}
                schedule_keys: set[str] = {
                    f"{prefix}{slot}"
                    for prefix in ("cap", "sellTime")
                    for slot in range(1, 7)
                }
                if schedule_keys.intersection(overrides):
                    required_keys.update(schedule_keys)
                self._validate_settings(cached_settings, required_keys)
                response: dict[str, Any] = await self._coordinator.api.get_settings(
                    self._sn
                )
                fresh_settings: object = response.get("data")
                if response.get("success") is False or not isinstance(fresh_settings, dict):
                    raise HomeAssistantError(
                        "Sunsynk settings could not be read; no write was sent."
                    )
                self._validate_settings(fresh_settings, required_keys)
                payload: dict[str, Any] = dict(fresh_settings)
                payload.update(overrides)
                payload["sn"] = self._sn
                await self._coordinator.api.set_settings(self._sn, payload)
            except HomeAssistantError:
                _LOGGER.warning(
                    "Settings write failed or was blocked for keys %s", setting_keys
                )
                raise
            except Exception as error:
                _LOGGER.warning(
                    "Settings write failed for keys %s (%s)",
                    setting_keys,
                    type(error).__name__,
                )
                raise HomeAssistantError(
                    "Sunsynk settings write failed; check the integration logs."
                ) from None

        _LOGGER.debug(
            "Settings request accepted for keys %s; awaiting cloud readback", setting_keys
        )
        await self._coordinator.async_request_refresh()
        readback: dict[str, Any] = self._get_settings()
        unconfirmed_keys: list[str] = [
            key
            for key in setting_keys
            if not _settings_match(readback.get(key), overrides[key])
        ]
        if not self._coordinator.last_update_success or unconfirmed_keys:
            _LOGGER.warning(
                "Settings request accepted, but cloud readback has not confirmed keys %s; "
                "check Sunsynk Connect before another write",
                unconfirmed_keys or setting_keys,
            )


def _settings_match(actual: object, requested: object) -> bool:
    if actual is None:
        return False
    actual_text: str = str(actual).strip().lower()
    requested_text: str = str(requested).strip().lower()
    if actual_text == requested_text:
        return True
    boolean_values: dict[str, str] = {"true": "1", "false": "0"}
    try:
        return float(boolean_values.get(actual_text, actual_text)) == float(
            boolean_values.get(requested_text, requested_text)
        )
    except ValueError:
        return False
