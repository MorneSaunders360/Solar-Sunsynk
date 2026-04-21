"""Shared helpers for Sunsynk config entities."""
import time

from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

_OPTIMISTIC_HOLD_SECONDS = 10


def sunsynk_device_info(coordinator, serial: str) -> DeviceInfo:
    return DeviceInfo(
        entry_type=DeviceEntryType.SERVICE,
        identifiers={(DOMAIN, serial)},
        manufacturer="Sunsynk",
        model=coordinator.data[serial].get("Model", ""),
        name=f"Sunsynk Statistics : {serial}",
    )


class SunsynkSettingsMixin:
    """Provides payload building, API update, and optimistic state for setting entities."""

    # Class-level defaults; instance variables shadow these after first write
    _optimistic_state = None
    _optimistic_until: float = 0.0

    def _build_payload(self, overrides: dict) -> dict:
        payload = dict(self._coordinator.data[self._serial].get("settings", {}))
        payload["sn"] = self._sn
        payload.update(overrides)
        return payload

    async def _send_update(self, overrides: dict) -> None:
        await self._coordinator.api.set_settings(
            self._sn, self._build_payload(overrides)
        )

    def _set_optimistic(self, state) -> None:
        """Store optimistic state and immediately push it to HA."""
        self._optimistic_state = state
        self._optimistic_until = time.monotonic() + _OPTIMISTIC_HOLD_SECONDS
        self.async_write_ha_state()

    def _get_optimistic(self):
        """Return optimistic state if still within the hold window, else None."""
        if self._optimistic_state is not None and time.monotonic() < self._optimistic_until:
            return self._optimistic_state
        self._optimistic_state = None
        return None
