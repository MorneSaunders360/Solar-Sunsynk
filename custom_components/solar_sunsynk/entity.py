"""Parent class for Sunsynk devices."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntityDescription


@dataclass
class SunsynkSensorDescription(SensorEntityDescription):
    """Class to describe an Sunsynk sensor."""

    native_value: Callable[
        [str | int | float], str | int | float
    ] | None = lambda val: val
