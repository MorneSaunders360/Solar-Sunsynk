"""Sunsynk Sensor definitions."""

from typing import List

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfEnergy,
    PERCENTAGE,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfElectricPotential,
    UnitOfElectricCurrent,
    UnitOfFrequency,
)
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
    # --- PV strings 3 & 4 ---
    SunsynkSensorDescription(
        key=SunsynkNames.PPV3,
        name=SunsynkNames.PPV3.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.PPV4,
        name=SunsynkNames.PPV4.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # --- PV currents ---
    SunsynkSensorDescription(
        key=SunsynkNames.IPV1,
        name=SunsynkNames.IPV1.value,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.IPV2,
        name=SunsynkNames.IPV2.value,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.IPV3,
        name=SunsynkNames.IPV3.value,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.IPV4,
        name=SunsynkNames.IPV4.value,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # --- PV voltages ---
    SunsynkSensorDescription(
        key=SunsynkNames.VPV1,
        name=SunsynkNames.VPV1.value,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.VPV2,
        name=SunsynkNames.VPV2.value,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.VPV3,
        name=SunsynkNames.VPV3.value,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.VPV4,
        name=SunsynkNames.VPV4.value,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.PVCurrent,
        name=SunsynkNames.PVCurrent.value,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.PVEtotal,
        name=SunsynkNames.PVEtotal.value,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    # --- Load ---
    SunsynkSensorDescription(
        key=SunsynkNames.LoadTotalUsed,
        name=SunsynkNames.LoadTotalUsed.value,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.LoadVolt,
        name=SunsynkNames.LoadVolt.value,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.LoadUpsPower,
        name=SunsynkNames.LoadUpsPower.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.LoadFac,
        name=SunsynkNames.LoadFac.value,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.LoadCurrent,
        name=SunsynkNames.LoadCurrent.value,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # --- Battery extended ---
    SunsynkSensorDescription(
        key=SunsynkNames.BatteryTemp,
        name=SunsynkNames.BatteryTemp.value,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.BatteryVoltage,
        name=SunsynkNames.BatteryVoltage.value,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.BatteryChargeVolt,
        name=SunsynkNames.BatteryChargeVolt.value,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.BatteryStatus,
        name=SunsynkNames.BatteryStatus.value,
        native_unit_of_measurement=None,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.BatteryChargeCurrentLimit,
        name=SunsynkNames.BatteryChargeCurrentLimit.value,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.BatteryDischargeCurrentLimit,
        name=SunsynkNames.BatteryDischargeCurrentLimit.value,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.BatteryCapacity,
        name=SunsynkNames.BatteryCapacity.value,
        native_unit_of_measurement=None,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.BatteryCurrent,
        name=SunsynkNames.BatteryCurrent.value,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.BatteryEtotalChg,
        name=SunsynkNames.BatteryEtotalChg.value,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.BatteryEtotalDischg,
        name=SunsynkNames.BatteryEtotalDischg.value,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.BatteryEfficiency,
        name=SunsynkNames.BatteryEfficiency.value,
        native_unit_of_measurement=PERCENTAGE,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # --- Grid extended ---
    SunsynkSensorDescription(
        key=SunsynkNames.GridTotalIn,
        name=SunsynkNames.GridTotalIn.value,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.GridTotalOut,
        name=SunsynkNames.GridTotalOut.value,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.GridFac,
        name=SunsynkNames.GridFac.value,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.GridStatus,
        name=SunsynkNames.GridStatus.value,
        native_unit_of_measurement=None,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.GridPF,
        name=SunsynkNames.GridPF.value,
        native_unit_of_measurement=None,
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.GridVolt,
        name=SunsynkNames.GridVolt.value,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.GridCurrent,
        name=SunsynkNames.GridCurrent.value,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # --- Output ---
    SunsynkSensorDescription(
        key=SunsynkNames.OutputPowerAux,
        name=SunsynkNames.OutputPowerAux.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.OutputEtotal,
        name=SunsynkNames.OutputEtotal.value,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.OutputEtoday,
        name=SunsynkNames.OutputEtoday.value,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.OutputPAC,
        name=SunsynkNames.OutputPAC.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.OutputPInv,
        name=SunsynkNames.OutputPInv.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.OutputFac,
        name=SunsynkNames.OutputFac.value,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.OutputVolt,
        name=SunsynkNames.OutputVolt.value,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.OutputCurrent,
        name=SunsynkNames.OutputCurrent.value,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # --- Energy Flow ---
    SunsynkSensorDescription(
        key=SunsynkNames.FlowBatterySOC,
        name=SunsynkNames.FlowBatterySOC.value,
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.FlowLoadPower,
        name=SunsynkNames.FlowLoadPower.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.FlowPVPower,
        name=SunsynkNames.FlowPVPower.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.FlowBatteryPower,
        name=SunsynkNames.FlowBatteryPower.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.FlowGridPower,
        name=SunsynkNames.FlowGridPower.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.FlowGenPower,
        name=SunsynkNames.FlowGenPower.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.FlowMinPower,
        name=SunsynkNames.FlowMinPower.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.FlowHeatPumpPower,
        name=SunsynkNames.FlowHeatPumpPower.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.FlowSmartLoadPower,
        name=SunsynkNames.FlowSmartLoadPower.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.FlowHomeLoadPower,
        name=SunsynkNames.FlowHomeLoadPower.value,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # --- Inverter Status ---
    SunsynkSensorDescription(
        key=SunsynkNames.InverterStatus,
        name=SunsynkNames.InverterStatus.value,
        native_unit_of_measurement=None,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsynkSensorDescription(
        key=SunsynkNames.GatewayStatus,
        name=SunsynkNames.GatewayStatus.value,
        native_unit_of_measurement=None,
        device_class=None,
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
