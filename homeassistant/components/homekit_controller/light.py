"""Support for Homekit lights."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aiohomekit.model.characteristics import CharacteristicsTypes
from aiohomekit.model.services import Service, ServicesTypes

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_HS_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import KNOWN_DEVICES
from .connection import HKDevice
from .entity import HomeKitEntity

if TYPE_CHECKING:
    from functools import cached_property
else:
    from homeassistant.backports.functools import cached_property


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Homekit lightbulb."""
    hkid: str = config_entry.data["AccessoryPairingID"]
    conn: HKDevice = hass.data[KNOWN_DEVICES][hkid]

    @callback
    def async_add_service(service: Service) -> bool:
        if service.type != ServicesTypes.LIGHTBULB:
            return False
        info = {"aid": service.accessory.aid, "iid": service.iid}
        entity = HomeKitLight(conn, info)
        conn.async_migrate_unique_id(
            entity.old_unique_id, entity.unique_id, Platform.LIGHT
        )
        async_add_entities([entity])
        return True

    conn.add_listener(async_add_service)


class HomeKitLight(HomeKitEntity, LightEntity):
    """Representation of a Homekit light."""

    @callback
    def _async_reconfigure(self) -> None:
        """Reconfigure entity."""
        self._async_clear_property_cache(
            ("supported_features", "min_mireds", "max_mireds", "supported_color_modes")
        )
        super()._async_reconfigure()

    def get_characteristic_types(self) -> list[str]:
        """Define the homekit characteristics the entity cares about."""
        return [
            CharacteristicsTypes.ON,
            CharacteristicsTypes.BRIGHTNESS,
            CharacteristicsTypes.COLOR_TEMPERATURE,
            CharacteristicsTypes.HUE,
            CharacteristicsTypes.SATURATION,
        ]

    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        return self.service.value(CharacteristicsTypes.ON)

    @property
    def brightness(self) -> int:
        """Return the brightness of this light between 0..255."""
        return self.service.value(CharacteristicsTypes.BRIGHTNESS) * 255 / 100

    @property
    def hs_color(self) -> tuple[float, float]:
        """Return the color property."""
        return (
            self.service.value(CharacteristicsTypes.HUE),
            self.service.value(CharacteristicsTypes.SATURATION),
        )

    @cached_property
    def min_mireds(self) -> int:
        """Return minimum supported color temperature."""
        min_value = self.service[CharacteristicsTypes.COLOR_TEMPERATURE].minValue
        return int(min_value) if min_value else super().min_mireds

    @cached_property
    def max_mireds(self) -> int:
        """Return the maximum color temperature."""
        max_value = self.service[CharacteristicsTypes.COLOR_TEMPERATURE].maxValue
        return int(max_value) if max_value else super().max_mireds

    @property
    def color_temp(self) -> int:
        """Return the color temperature."""
        return self.service.value(CharacteristicsTypes.COLOR_TEMPERATURE)

    @property
    def color_mode(self) -> str:
        """Return the color mode of the light."""
        # aiohomekit does not keep track of the light's color mode, report
        # hs for light supporting both hs and ct
        if self.service.has(CharacteristicsTypes.HUE) or self.service.has(
            CharacteristicsTypes.SATURATION
        ):
            return ColorMode.HS

        if self.service.has(CharacteristicsTypes.COLOR_TEMPERATURE):
            return ColorMode.COLOR_TEMP

        if self.service.has(CharacteristicsTypes.BRIGHTNESS):
            return ColorMode.BRIGHTNESS

        return ColorMode.ONOFF

    @cached_property
    def supported_color_modes(self) -> set[ColorMode]:
        """Flag supported color modes."""
        color_modes: set[ColorMode] = set()

        if self.service.has(CharacteristicsTypes.HUE) or self.service.has(
            CharacteristicsTypes.SATURATION
        ):
            color_modes.add(ColorMode.HS)

        if self.service.has(CharacteristicsTypes.COLOR_TEMPERATURE):
            color_modes.add(ColorMode.COLOR_TEMP)

        if not color_modes and self.service.has(CharacteristicsTypes.BRIGHTNESS):
            color_modes.add(ColorMode.BRIGHTNESS)

        if not color_modes:
            color_modes.add(ColorMode.ONOFF)

        return color_modes

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the specified light on."""
        hs_color = kwargs.get(ATTR_HS_COLOR)
        temperature = kwargs.get(ATTR_COLOR_TEMP)
        brightness = kwargs.get(ATTR_BRIGHTNESS)

        characteristics = {}

        if hs_color is not None:
            characteristics.update(
                {
                    CharacteristicsTypes.HUE: hs_color[0],
                    CharacteristicsTypes.SATURATION: hs_color[1],
                }
            )

        if brightness is not None:
            characteristics[CharacteristicsTypes.BRIGHTNESS] = int(
                brightness * 100 / 255
            )

        if temperature is not None:
            characteristics[CharacteristicsTypes.COLOR_TEMPERATURE] = int(temperature)

        characteristics[CharacteristicsTypes.ON] = True

        await self.async_put_characteristics(characteristics)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the specified light off."""
        await self.async_put_characteristics({CharacteristicsTypes.ON: False})
