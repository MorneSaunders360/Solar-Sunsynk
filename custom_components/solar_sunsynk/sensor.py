from homeassistant.components.sensor import SensorEntity
# Constants
from .const import DOMAIN,DEVICE_INFO
from .coordinator import async_get_coordinator
async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensors from config entry."""
    # Create the data update coordinator
    coordinator = await async_get_coordinator(hass, config_entry)
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    # Create device registry
    device_registry = hass.helpers.device_registry.async_get(hass)

    # Create primary device
    primary_device = device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        **DEVICE_INFO,
    )

    # Create settings device
    settings_device_info = DEVICE_INFO.copy()
    settings_device_info["name"] += " Settings"
    settings_device_info["identifiers"] = {(DOMAIN, "solar_sunsynk_settings")}
    settings_device = device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        **settings_device_info,
    )
    
    # Create sensor entities and add them
    entities = []
    for result_key in coordinator.data.keys():
        if result_key.startswith("settings_"):
            identifier = "solar_sunsynk_settings"
            device = settings_device
        else:
            identifier = "solar_sunsynk"
            device = primary_device

        entity = SolarSunSynkSensor(coordinator, result_key, device, coordinator.data.get("id"), identifier)
        entities.append(entity)

    async_add_entities(entities)



class SolarSunSynkSensor(SensorEntity):
    """Representation of a sensor entity for Solar Sunsynk data."""

    def __init__(self, coordinator, result_key, device, id, identifier):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.result_key = result_key
        self.device = device
        self.id = id
        self.identifier = identifier

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes of the sensor."""
        attributes = {}
        if self.result_key == "income" and 'currency' in self.coordinator.data:
            attributes['currency_code'] = self.coordinator.data['currency']
        return attributes

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.identifier)},
            "name": self.device.name,
            "manufacturer": self.device.manufacturer,
            "model": self.device.model,
            "sw_version": self.device.sw_version,
            "via_device": (DOMAIN, self.device.id),
        }

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"sunsynk_{self.result_key}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"sunsynk_{self.id}_{self.result_key}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self.result_key]
    

    @property
    def unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        attributes = self.extra_state_attributes
        if self.result_key == "income":
            return attributes.get('currency_code') or "Currency"
        elif self.result_key in ["pvPower", "battPower", "gridOrMeterPower", "loadOrEpsPower", "genPower", "minPower", "pac"]:
            return "W"
        elif self.result_key in ["etoday", "etotal", "emonth", "eyear", "totalPower"]:
            return "kWh"
        elif self.result_key == "soc" or self.result_key == "efficiency":
            return "%"
        else:
            return None

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        if self.result_key == "income":
            return "monetary"
        elif self.result_key == "soc":
            return "battery"
        elif self.result_key in ["pvPower", "battPower", "gridOrMeterPower", "loadOrEpsPower", "genPower", "minPower", "pac"]:
            return "power"
        elif self.result_key in ["etoday", "etotal", "emonth", "eyear", "totalPower"]:
            return "energy"
        elif self.result_key in ["pvTo", "toLoad", "toGrid", "toBat", "batTo", "gridTo", "genTo", "minTo", "existsGen", "existsMin", "genOn", "microOn", "existsMeter", "bmsCommFaultFlag", "existThinkPower"]:
            return "switch"
        elif self.result_key == "efficiency":
            return "power_factor"
        else:
            return None



    @property
    def state_class(self):
        """Return the state class of the sensor."""
        if self.result_key in ["pvPower", "battPower", "gridOrMeterPower", "loadOrEpsPower", "genPower", "minPower", "soc", "pac", "efficiency", "etoday", "etotal", "emonth", "eyear", "income", "totalPower"]:
            return "measurement"
        else:
            return None

    async def async_update(self):
        """Update the sensor."""
        await self.coordinator.async_request_refresh()

