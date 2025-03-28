"""Constants for the Sunsynk integration."""

from homeassistant.const import Platform

import voluptuous as vol

import homeassistant.helpers.config_validation as cv

DOMAIN = "solar_sunsynk"
PLATFORMS = [Platform.SENSOR]

NAME = "Solar Sunsynk"
ISSUE_URL = "https://github.com/MorneSaunders360/Solar-Sunsynk/issues"

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
SetSolarSettingsSchema = vol.Schema(
    {
        vol.Required("sn"): cv.string,
        vol.Optional("safetyType"): cv.string,
        vol.Optional("battMode"): cv.string,
        vol.Optional("solarSell"): cv.string,
        vol.Optional("pvMaxLimit"): cv.string,
        vol.Optional("energyMode"): cv.string,
        vol.Optional("peakAndVallery"): cv.string,
        vol.Optional("sysWorkMode"): cv.string,
        vol.Optional("sellTime1"): cv.string,
        vol.Optional("sellTime2"): cv.string,
        vol.Optional("sellTime3"): cv.string,
        vol.Optional("sellTime4"): cv.string,
        vol.Optional("sellTime5"): cv.string,
        vol.Optional("sellTime6"): cv.string,
        vol.Optional("sellTime1Pac"): cv.string,
        vol.Optional("sellTime2Pac"): cv.string,
        vol.Optional("sellTime3Pac"): cv.string,
        vol.Optional("sellTime4Pac"): cv.string,
        vol.Optional("sellTime5Pac"): cv.string,
        vol.Optional("sellTime6Pac"): cv.string,
        vol.Optional("cap1"): cv.string,
        vol.Optional("cap2"): cv.string,
        vol.Optional("cap3"): cv.string,
        vol.Optional("cap4"): cv.string,
        vol.Optional("cap5"): cv.string,
        vol.Optional("cap6"): cv.string,
        vol.Optional("sellTime1Volt"): cv.string,
        vol.Optional("sellTime2Volt"): cv.string,
        vol.Optional("sellTime3Volt"): cv.string,
        vol.Optional("sellTime4Volt"): cv.string,
        vol.Optional("sellTime5Volt"): cv.string,
        vol.Optional("sellTime6Volt"): cv.string,
        vol.Optional("zeroExportPower"): cv.string,
        vol.Optional("solarMaxSellPower"): cv.string,
        vol.Optional("mondayOn"): cv.boolean,
        vol.Optional("tuesdayOn"): cv.boolean,
        vol.Optional("wednesdayOn"): cv.boolean,
        vol.Optional("thursdayOn"): cv.boolean,
        vol.Optional("fridayOn"): cv.boolean,
        vol.Optional("saturdayOn"): cv.boolean,
        vol.Optional("sundayOn"): cv.boolean,
        vol.Optional("time1on"): cv.boolean,
        vol.Optional("time2on"): cv.boolean,
        vol.Optional("time3on"): cv.boolean,
        vol.Optional("time4on"): cv.boolean,
        vol.Optional("time5on"): cv.boolean,
        vol.Optional("time6on"): cv.boolean,
        vol.Optional("genTime1on"): cv.boolean,
        vol.Optional("genTime2on"): cv.boolean,
        vol.Optional("genTime3on"): cv.boolean,
        vol.Optional("genTime4on"): cv.boolean,
        vol.Optional("genTime5on"): cv.boolean,
        vol.Optional("genTime6on"): cv.boolean,
    }
)
