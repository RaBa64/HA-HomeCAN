"""Demo platform that has a couple of fake sensors."""
from __future__ import annotations

from datetime import datetime, timedelta
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, cast

from homeassistant.components.binary_sensor import (
    DOMAIN as BINARY_SENSOR_DOMAIN,
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.event import async_track_time_interval

from .coordinator import HomeCANupdateCoordinator

from . import DOMAIN


@dataclass
class HomeCANBinarySensorDescriptionMixin:
    """Mixin for HomeCAN sensor."""

    value_fn: Callable[[dict[str, Any]], str | int | float | None]


@dataclass
class HomeCANSensorDescription(
    BinarySensorEntityDescription, HomeCANBinarySensorDescriptionMixin
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
    binary_sensors = [HomeCANbinarysensor(coordinator, description) for description in coordinator.binary_sensors_list]
    async_add_entities(binary_sensors)
    

class HomeCANbinarysensor(CoordinatorEntity[HomeCANupdateCoordinator], BinarySensorEntity):
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
        self._attr_is_on = self.coordinator.data.get(description.key)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""
        if self.entity_description.name.endswith('_not'):        
            self._attr_is_on = not self.coordinator.data.get(self.entity_description.key)
        else:
            self._attr_is_on = self.coordinator.data.get(self.entity_description.key)
        self.async_write_ha_state()

