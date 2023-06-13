from homeassistant import config_entries, core
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
import aiohttp
import logging
DOMAIN = "solar_sunsynk"
_LOGGER = logging.getLogger(__name__)
SetSolarSettingsSchema = vol.Schema(
    {
        vol.Required("sn", default="2107269334"): cv.string,
        vol.Optional("safetyType", default="2"): cv.string,
        vol.Optional("battMode", default="-1"): cv.string,
        vol.Optional("solarSell", default="0"): cv.string,
        vol.Optional("pvMaxLimit", default="8000"): cv.string,
        vol.Optional("energyMode", default="0"): cv.string,
        vol.Optional("peakAndVallery", default="1"): cv.string,
        vol.Optional("sysWorkMode", default="2"): cv.string,
        vol.Optional("sellTime1", default="01:00"): cv.string,
        vol.Optional("sellTime2", default="05:00"): cv.string,
        vol.Optional("sellTime3", default="12:30"): cv.string,
        vol.Optional("sellTime4", default="13:00"): cv.string,
        vol.Optional("sellTime5", default="17:00"): cv.string,
        vol.Optional("sellTime6", default="21:00"): cv.string,
        vol.Optional("sellTime1Pac", default="8000"): cv.string,
        vol.Optional("sellTime2Pac", default="8000"): cv.string,
        vol.Optional("sellTime3Pac", default="8000"): cv.string,
        vol.Optional("sellTime4Pac", default="8000"): cv.string,
        vol.Optional("sellTime5Pac", default="8000"): cv.string,
        vol.Optional("sellTime6Pac", default="8000"): cv.string,
        vol.Optional("cap1", default="70"): cv.string,
        vol.Optional("cap2", default="70"): cv.string,
        vol.Optional("cap3", default="70"): cv.string,
        vol.Optional("cap4", default="70"): cv.string,
        vol.Optional("cap5", default="70"): cv.string,
        vol.Optional("cap6", default="70"): cv.string,
        vol.Optional("sellTime1Volt", default="49"): cv.string,
        vol.Optional("sellTime2Volt", default="49"): cv.string,
        vol.Optional("sellTime3Volt", default="49"): cv.string,
        vol.Optional("sellTime4Volt", default="49"): cv.string,
        vol.Optional("sellTime5Volt", default="49"): cv.string,
        vol.Optional("sellTime6Volt", default="49"): cv.string,
        vol.Optional("zeroExportPower", default="0"): cv.string,
        vol.Optional("solarMaxSellPower", default="9000"): cv.string,
        vol.Optional("mondayOn", default=True): cv.boolean,
        vol.Optional("tuesdayOn", default=True): cv.boolean,
        vol.Optional("wednesdayOn", default=True): cv.boolean,
        vol.Optional("thursdayOn", default=True): cv.boolean,
        vol.Optional("fridayOn", default=True): cv.boolean,
        vol.Optional("saturdayOn", default=True): cv.boolean,
        vol.Optional("sundayOn", default=True): cv.boolean,
        vol.Optional("time1on", default=False): cv.boolean,
        vol.Optional("time2on", default=False): cv.boolean,
        vol.Optional("time3on", default=False): cv.boolean,
        vol.Optional("time4on", default=False): cv.boolean,
        vol.Optional("time5on", default=False): cv.boolean,
        vol.Optional("time6on", default=False): cv.boolean,
        vol.Optional("genTime1on", default=False): cv.boolean,
        vol.Optional("genTime2on", default=False): cv.boolean,
        vol.Optional("genTime3on", default=False): cv.boolean,
        vol.Optional("genTime4on", default=False): cv.boolean,
        vol.Optional("genTime5on", default=False): cv.boolean,
        vol.Optional("genTime6on", default=False): cv.boolean,
    }
)

async def async_setup(hass, config):
    return True

async def async_setup_entry(hass, entry):
    return await hass.async_add_executor_job(setup, hass, entry)

def setup(hass: core.HomeAssistant, entry: config_entries.ConfigEntry):

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    USERNAME = entry.data["username"]
    PASSWORD = entry.data["password"]
    region = entry.data["region"]
    if region == "Region 1":
        API_URL = "https://pv.inteless.com/"
    elif region == "Region 2":
        API_URL = "https://api.sunsynk.net/"

    async def async_set_solar_settings(call):
        session = aiohttp.ClientSession()
        token = ""
        headers = {
            'Content-type':'application/json', 
            'Accept':'application/json'
        }
        payload = {
            "username": USERNAME,
            "password": PASSWORD,
            "grant_type":"password",
            "client_id":"csp-web"
        }
        async with session.post(API_URL+"oauth/token", json=payload, headers=headers) as resp:
            responseAuth = await resp.json()
            token = responseAuth["data"]["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        sn = call.data.get("sn")
        read_url = f"{API_URL}api/v1/common/setting/{sn}/read"
        set_url = f"{API_URL}api/v1/common/setting/{sn}/set"

        async with session.get(read_url, headers=headers) as response:
            if response.status == 200:
                current_values = await response.json()
            else:
                # Failed to retrieve current values
                return False

        # Get values from the ServiceCall
        beep = call.data.get("beep", current_values.get("beep"))
        genTime2on = call.data.get("genTime2on", current_values.get("genTime2on"))
        sellTime1 = call.data.get("sellTime1", current_values.get("sellTime1"))
        sellTime2 = call.data.get("sellTime2", current_values.get("sellTime2"))
        pvMaxLimit = call.data.get("pvMaxLimit", current_values.get("pvMaxLimit"))
        energyMode = call.data.get("energyMode", current_values.get("energyMode"))
        peakAndVallery = call.data.get("peakAndVallery", current_values.get("peakAndVallery"))
        sysWorkMode = call.data.get("sysWorkMode", current_values.get("sysWorkMode"))
        sellTime3 = call.data.get("sellTime3", current_values.get("sellTime3"))
        sellTime4 = call.data.get("sellTime4", current_values.get("sellTime4"))
        sellTime5 = call.data.get("sellTime5", current_values.get("sellTime5"))
        sellTime6 = call.data.get("sellTime6", current_values.get("sellTime6"))
        cap1 = call.data.get("cap1", current_values.get("cap1"))
        cap2 = call.data.get("cap2", current_values.get("cap2"))
        cap3 = call.data.get("cap3", current_values.get("cap3"))
        cap4 = call.data.get("cap4", current_values.get("cap4"))
        cap5 = call.data.get("cap5", current_values.get("cap5"))
        cap6 = call.data.get("cap6", current_values.get("cap6"))
        sellTime1Volt = call.data.get("sellTime1Volt", current_values.get("sellTime1Volt"))
        sellTime2Volt = call.data.get("sellTime2Volt", current_values.get("sellTime2Volt"))
        sellTime3Volt = call.data.get("sellTime3Volt", current_values.get("sellTime3Volt"))
        sellTime4Volt = call.data.get("sellTime4Volt", current_values.get("sellTime4Volt"))
        sellTime5Volt = call.data.get("sellTime5Volt", current_values.get("sellTime5Volt"))
        sellTime6Volt = call.data.get("sellTime6Volt", current_values.get("sellTime6Volt"))
        zeroExportPower = call.data.get("zeroExportPower", current_values.get("zeroExportPower"))
        solarMaxSellPower = call.data.get("solarMaxSellPower", current_values.get("solarMaxSellPower"))
        mondayOn = call.data.get("mondayOn", current_values.get("mondayOn"))
        tuesdayOn = call.data.get("tuesdayOn", current_values.get("tuesdayOn"))
        wednesdayOn = call.data.get("wednesdayOn", current_values.get("wednesdayOn"))
        thursdayOn = call.data.get("thursdayOn", current_values.get("thursdayOn"))
        fridayOn = call.data.get("fridayOn", current_values.get("fridayOn"))
        saturdayOn = call.data.get("saturdayOn", current_values.get("saturdayOn"))
        sundayOn = call.data.get("sundayOn", current_values.get("sundayOn"))
        time1on = call.data.get("time1on", current_values.get("time1on"))
        time2on = call.data.get("time2on", current_values.get("time2on"))
        time3on = call.data.get("time3on", current_values.get("time3on"))
        time4on = call.data.get("time4on", current_values.get("time4on"))
        time5on = call.data.get("time5on", current_values.get("time5on"))
        time6on = call.data.get("time6on", current_values.get("time6on"))
        genTime1on = call.data.get("genTime1on", current_values.get("genTime1on"))
        genTime2on = call.data.get("genTime2on", current_values.get("genTime2on"))
        genTime3on = call.data.get("genTime3on", current_values.get("genTime3on"))
        genTime4on = call.data.get("genTime4on", current_values.get("genTime4on"))
        genTime5on = call.data.get("genTime5on", current_values.get("genTime5on"))
        genTime6on = call.data.get("genTime6on", current_values.get("genTime6on"))
        # Prepare the payload
        payload = {
            "sn": sn,
            "beep": beep,
            "genTime2on": genTime2on,
            "sellTime1": sellTime1,
            "sellTime2": sellTime2,
            "pvMaxLimit": pvMaxLimit,
            "energyMode": energyMode,
            "peakAndVallery": peakAndVallery,
            "sysWorkMode": sysWorkMode,
            "sellTime3": sellTime3,
            "sellTime4": sellTime4,
            "sellTime5": sellTime5,
            "sellTime6": sellTime6,
            "cap1": cap1,
            "cap2": cap2,
            "cap3": cap3,
            "cap4": cap4,
            "cap5": cap5,
            "cap6": cap6,
            "sellTime1Volt": sellTime1Volt,
            "sellTime2Volt": sellTime2Volt,
            "sellTime3Volt": sellTime3Volt,
            "sellTime4Volt": sellTime4Volt,
            "sellTime5Volt": sellTime5Volt,
            "sellTime6Volt": sellTime6Volt,
            "zeroExportPower": zeroExportPower,
            "solarMaxSellPower": solarMaxSellPower,
            "mondayOn": mondayOn,
            "tuesdayOn": tuesdayOn,
            "wednesdayOn": wednesdayOn,
            "thursdayOn": thursdayOn,
            "fridayOn": fridayOn,
            "saturdayOn": saturdayOn,
            "sundayOn": sundayOn,
            "time1on": str(time1on),
            "time2on": str(time2on),
            "time3on": str(time3on),
            "time4on": str(time4on),
            "time5on": str(time5on),
            "time6on": str(time6on),
            "genTime1on": str(genTime1on),
            "genTime2on": str(genTime2on),
            "genTime3on": str(genTime3on),
            "genTime4on": str(genTime4on),
            "genTime5on": str(genTime5on),
            "genTime6on": str(genTime6on),
        }
        #_LOGGER.error("payload: %s", payload)
        async with session.post(set_url, json=payload, headers=headers) as response:
            if response.status == 200:
                # Request successful
                await session.close()
                return True
            else:
                # Request failed
                session.close()
                return False

    hass.services.async_register(
        DOMAIN, "set_solar_settings", async_set_solar_settings, SetSolarSettingsSchema
    )

    # Return boolean to indicate that initialization was successful.
    return True
