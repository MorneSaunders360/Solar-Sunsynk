import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, Callable


class HomeAssistantError(Exception):
    pass


class UpdateFailed(HomeAssistantError):
    pass


class Entity:
    @property
    def available(self) -> bool:
        return True


class CoordinatorEntity(Entity):
    def __init__(self, coordinator: Any) -> None:
        self.coordinator: Any = coordinator

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success


class DataUpdateCoordinator:
    def __init__(self, hass: Any, logger: Any, **kwargs: Any) -> None:
        self.hass: Any = hass
        self.data: dict[str, Any] = {}
        self.last_update_success: bool = True

    async def async_request_refresh(self) -> None:
        pass


@dataclass
class SensorEntityDescription:
    key: str
    name: str
    native_unit_of_measurement: str | None = None
    device_class: str | None = None
    state_class: str | None = None
    entity_registry_enabled_default: bool = True


def callback(function: Callable[..., Any]) -> Callable[..., Any]:
    return function


def install_test_modules() -> None:
    package_path: Path = Path(__file__).resolve().parents[1] / "custom_components" / "solar_sunsynk"
    package: ModuleType = ModuleType("custom_components.solar_sunsynk")
    package.__path__ = [str(package_path)]
    root: ModuleType = ModuleType("custom_components")
    root.__path__ = [str(package_path.parent)]
    sys.modules["custom_components"] = root
    sys.modules["custom_components.solar_sunsynk"] = package
    modules: dict[str, dict[str, Any]] = {
        "homeassistant": {},
        "homeassistant.components": {},
        "homeassistant.helpers": {},
        "homeassistant.core": {"HomeAssistant": SimpleNamespace, "callback": callback},
        "homeassistant.exceptions": {"HomeAssistantError": HomeAssistantError},
        "homeassistant.const": {
            "EntityCategory": SimpleNamespace(CONFIG="config"),
            "PERCENTAGE": "%",
            "UnitOfElectricPotential": SimpleNamespace(VOLT="V"),
            "UnitOfPower": SimpleNamespace(WATT="W"),
            "UnitOfEnergy": SimpleNamespace(KILO_WATT_HOUR="kWh"),
        },
        "homeassistant.helpers.entity": {"DeviceInfo": dict},
        "homeassistant.helpers.device_registry": {
            "DeviceEntryType": SimpleNamespace(SERVICE="service")
        },
        "homeassistant.helpers.update_coordinator": {
            "CoordinatorEntity": CoordinatorEntity,
            "DataUpdateCoordinator": DataUpdateCoordinator,
            "UpdateFailed": UpdateFailed,
        },
        "homeassistant.components.number": {
            "NumberEntity": Entity,
            "NumberMode": SimpleNamespace(BOX="box"),
        },
        "homeassistant.components.switch": {"SwitchEntity": Entity},
        "homeassistant.components.select": {"SelectEntity": Entity},
        "homeassistant.components.text": {"TextEntity": Entity},
        "homeassistant.components.sensor": {
            "SensorEntity": Entity,
            "SensorEntityDescription": SensorEntityDescription,
            "SensorDeviceClass": SimpleNamespace(ENERGY="energy", POWER="power", BATTERY="battery"),
            "SensorStateClass": SimpleNamespace(TOTAL="total", TOTAL_INCREASING="total_increasing", MEASUREMENT="measurement"),
        },
        "custom_components.solar_sunsynk.const": {"DOMAIN": "solar_sunsynk"},
    }
    for name, attributes in modules.items():
        module: ModuleType = ModuleType(name)
        module.__dict__.update(attributes)
        sys.modules[name] = module


install_test_modules()
