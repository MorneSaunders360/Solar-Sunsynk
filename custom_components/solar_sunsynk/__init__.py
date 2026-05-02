"""The Sunsynk integration."""

from __future__ import annotations

from .sunsynkapi import sunsynk_api

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from .const import (
    DOMAIN,
    PLATFORMS,
    SetAdvancedSettingsSchema,
    SetBasicSettingsSchema,
    SetAuxiliaryLoadSettingsSchema,
    SetBatterySettingsSchema,
    SetGridSettingsSchema,
    SetSolarSettingsSchema,
)
from .coordinator import SunsynkDataUpdateCoordinator


# import logging
# _LOGGER = logging.getLogger(__name__)
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sunsynk from a config entry."""
    client = sunsynk_api(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD], hass)
    coordinator = SunsynkDataUpdateCoordinator(hass, client=client)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    async def async_set_settings(call):
        sn = call.data.get("sn")
        setting_data = dict(call.data)
        setting_data["sn"] = sn
        response = await client.set_settings(sn, setting_data)
        if response.get("success") == True:
            return True
        else:
            return False

    hass.services.async_register(
        DOMAIN, "set_solar_settings", async_set_settings, SetSolarSettingsSchema
    )
    hass.services.async_register(
        DOMAIN,
        "set_battery_settings",
        async_set_settings,
        SetBatterySettingsSchema,
    )
    hass.services.async_register(
        DOMAIN,
        "set_basic_settings",
        async_set_settings,
        SetBasicSettingsSchema,
    )
    hass.services.async_register(
        DOMAIN,
        "set_auxiliary_load_settings",
        async_set_settings,
        SetAuxiliaryLoadSettingsSchema,
    )
    hass.services.async_register(
        DOMAIN,
        "set_advanced_settings",
        async_set_settings,
        SetAdvancedSettingsSchema,
    )
    hass.services.async_register(
        DOMAIN,
        "set_grid_settings",
        async_set_settings,
        SetGridSettingsSchema,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator = hass.data[DOMAIN].get(entry.entry_id)
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        if coordinator:
            await coordinator.api.async_close()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
