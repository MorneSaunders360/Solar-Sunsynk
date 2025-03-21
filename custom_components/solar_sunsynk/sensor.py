"""Sunsynk Sensor definitions."""

from typing import List

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfEnergy, PERCENTAGE, UnitOfPower
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SunsynkDataUpdateCoordinator
from .entity import SunsynkSensorDescription
from .enums import SunsynkNames

SENSOR_DESCRIPTIONS: List[SunsynkSensorDescription] = [
    SunsynkSensorDescription(
        key=SunsynkNames.SolarProduction,
        name=SunsynkNames.SolarProduction.value,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.SolarToBattery,
        name=SunsynkNames.SolarToBattery.value,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.SolarToGrid,
        name=SunsynkNames.SolarToGrid.value,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.SolarToLoad,
        name=SunsynkNames.SolarToLoad.value,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.TotalLoad,
        name=SunsynkNames.TotalLoad.value,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.GridToLoad,
        name=SunsynkNames.GridToLoad.value,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    # SunsynkSensorDescription(
    #     key=SunsynkNames.GridToBattery,
    #     name="Grid to Battery",
    #     native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    #     device_class=SensorDeviceClass.ENERGY,
    #     state_class=SensorStateClass.TOTAL_INCREASING,
    # ),
    SunsynkSensorDescription(
        key=SunsynkNames.StateOfCharge,
        name=SunsynkNames.StateOfCharge.value,
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.SettingAverageCap,
        name=SunsynkNames.SettingAverageCap.value,
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.Charge,
        name=SunsynkNames.Charge.value,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.Discharge,
        name=SunsynkNames.Discharge.value,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.GridIOTotal,
        name=SunsynkNames.GridIOTotal.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.GridPowerTotal,
        name=SunsynkNames.GridPowerTotal.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.Generation,
        name=SunsynkNames.Generation.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.BatterySOC,
        name=SunsynkNames.BatterySOC.value,
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.BatteryIO,
        name=SunsynkNames.BatteryIO.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.Load,
        name=SunsynkNames.Load.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.PPV1,
        name=SunsynkNames.PPV1.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.PPV2,
        name=SunsynkNames.PPV2.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
]


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Defer sensor setup to the shared sensor module."""

    coordinator: SunsynkDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: List[SunsynkSensor] = []

    key_supported_states = {
        description.key: description for description in SENSOR_DESCRIPTIONS
    }

    for serial in coordinator.data:
        for description in key_supported_states:
            entities.append(
                SunsynkSensor(
                    coordinator, entry, serial, key_supported_states[description]
                )
            )
    async_add_entities(entities)

    return


class SunsynkSensor(CoordinatorEntity, SensorEntity):
    """Sunsynk Sensor."""

    def __init__(self, coordinator, config, serial, key_supported_states):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config = config
        self._name = key_supported_states.name
        self._native_unit_of_measurement = (
            key_supported_states.native_unit_of_measurement
        )
        self._device_class = key_supported_states.device_class
        self._state_class = key_supported_states.state_class
        self._serial = serial
        self._coordinator = coordinator

        for invertor in coordinator.data:
            serial = invertor
            if self._serial == serial:
                self._attr_device_info = DeviceInfo(
                    entry_type=DeviceEntryType.SERVICE,
                    identifiers={(DOMAIN, serial)},
                    manufacturer="Sunsynk",
                    model=coordinator.data[invertor]["Model"],
                    name=f"Sunsynk Statistics : {serial}",
                )

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{self._config.entry_id}_{self._serial} - {self._name}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._serial}_{self._name}"

    @property
    def native_value(self):
        """Return the state of the resources."""
        return self._coordinator.data[self._serial][self._name]

    @property
    def native_unit_of_measurement(self):
        """Return the native unit of measurement of the sensor."""
        return self._native_unit_of_measurement

    @property
    def device_class(self):
        """Return the device_class of the sensor."""
        return self._device_class

    @property
    def state_class(self):
        """Return the state_class of the sensor."""
        return self._state_class
