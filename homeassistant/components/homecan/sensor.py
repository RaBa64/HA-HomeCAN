"""Demo platform that has a couple of fake sensors."""
from __future__ import annotations

from datetime import datetime, timedelta
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, cast

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfTemperature,
    LIGHT_LUX,
    UnitOfPressure,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.event import async_track_time_interval

from .coordinator import HomeCANupdateCoordinator

from . import DOMAIN


@dataclass
class HomeCANSensorDescriptionMixin:
    """Mixin for HomeCAN sensor."""

    value_fn: Callable[[dict[str, Any]], str | int | float | None]


@dataclass
class HomeCANSensorDescription(
    SensorEntityDescription, HomeCANSensorDescriptionMixin
):
    """Class describing HomeCAN sensor entities."""

    attr_fn: Callable[[dict[str, Any]], dict[str, Any]] = lambda _: {}
    day: int | None = None


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:

    coordinator: HomeCANupdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    sensors = [HomeCANsensor(coordinator, description) for description in coordinator.sensors_list]
    async_add_entities(sensors)


class HomeCANsensor(CoordinatorEntity[HomeCANupdateCoordinator], SensorEntity):
    """HomeCAN sensor."""
    print('#####################################################')
    entity_description: HomeCANSensorDescription
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self,
        coordinator: HomeCANupdateCoordinator,
        description: HomeCANSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = description.key
        self._attr_device_info = coordinator.device_info
        self._attr_native_value = self.coordinator.data.get(description.key)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""
        self._attr_native_value = self.coordinator.data.get(self.entity_description.key)
        self.async_write_ha_state()

