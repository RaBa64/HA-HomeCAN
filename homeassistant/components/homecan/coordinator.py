"""Example integration using DataUpdateCoordinator."""

from datetime import timedelta
import logging

import async_timeout

from homeassistant.components.light import LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.components.binary_sensor import (
    DOMAIN as BINARY_SENSOR_DOMAIN,
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
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
from homeassistant.const import (
    CONF_HOST,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_ACCESS_TOKEN,
    CONF_PORT,
    CONF_TIMEOUT,
    CONF_SENSORS,
    CONF_BINARY_SENSORS,
)

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from asyncio import timeout
from enum import Enum
from .homecanio import HomeCANio 

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=10)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Config entry example."""
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    # assuming API object stored here by __init__.py
    homecanio_api = hass.data[DOMAIN][entry.entry_id]
    coordinator = HomeCANupdateCoordinator(hass, homecanio_api)

    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    await coordinator.async_config_entry_first_refresh()

    # async_add_entities(
    #     MyEntity(coordinator, idx) for idx, ent in enumerate(coordinator.data)
    # )


class HomeCANupdateCoordinator(DataUpdateCoordinator[dict[str, any]]):
    """HomeCAN coordinator."""

    def __init__(self, 
                 hass: HomeAssistant, 
                 api: HomeCANio) -> None:
        """Initialize coordinator."""
        super().__init__(hass, 
                         _LOGGER, 
                         name=DOMAIN, 
                         update_method=self._async_update_data,
                         update_interval=UPDATE_INTERVAL)
        self._api = api
        self._data = {}
        self._lasttime = ''
        self._sensors_list: tuple[SensorEntityDescription, ...] = []
        self._binary_sensors_list: tuple[BinarySensorEntityDescription, ...] = []
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, 'HomeCAN')},
            name='HomeCAN',
            manufacturer='Ralf Bauer',
        )

        # self._api = HomeCANio(
        #     f"https://{config_entry.data.get(CONF_HOST)}:",
        #     config_entry.data.get(CONF_PORT),
        #     config_entry.data.get(CONF_USERNAME),
        #     config_entry.data.get(CONF_ACCESS_TOKEN),
        #     timeout=config_entry.data.get(CONF_TIMEOUT),
        # )

    @property
    def sensors_list(self):
        return(self._sensors_list)

    @property
    def binary_sensors_list(self):
        return(self._binary_sensors_list)

    @property
    def data(self):
        return(self._data)

    @data.setter
    def data(self, value):
        self._data = value


    async def _async_update_data(self) -> dict[str, any]:
        """Fetch data from API endpoint."""
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):
                # listening_idx = set(self.async_contexts())
                changes = await self._api.async_getjson(self._lasttime)
                if changes is None:
                    self._lasttime = None
                    messages = None
                else:
                    self._lasttime = changes['Time']
                    messages = changes['Msgs']
                    print(messages)

                for k1,v1 in messages.items():
                    device_name = k1[:k1.rfind('_')]
                    if k1.endswith('_Sensor'):
                        for k2,v2 in v1.items():
                            if k2 == 'Temperature':
                                uuid = k1 + '.' + k2
                                notinlist = uuid not in self._data
                                self._data[uuid] = float(v2)
                                if notinlist:
                                    self._sensors_list.append(SensorEntityDescription(
                                        key = uuid,
                                        name = uuid,
                                        state_class = SensorStateClass.MEASUREMENT,
                                        device_class = SensorDeviceClass.TEMPERATURE,
                                        native_unit_of_measurement = UnitOfTemperature.CELSIUS,
                                        suggested_display_precision = 1,
                                    ))
                            if k2 == 'Humidity':
                                uuid = k1 + '.' + k2
                                notinlist = uuid not in self._data
                                self._data[uuid] = float(v2)
                                if notinlist:
                                    self._sensors_list.append(SensorEntityDescription(
                                        key = uuid,
                                        name = uuid,
                                        state_class = SensorStateClass.MEASUREMENT,
                                        device_class = SensorDeviceClass.HUMIDITY,
                                        native_unit_of_measurement = PERCENTAGE,
                                        suggested_display_precision = 0,
                                    ))
                            if k2 == 'DewPoint':
                                uuid = k1 + '.' + k2
                                notinlist = uuid not in self._data
                                self._data[uuid] = float(v2)
                                if notinlist:
                                    self._sensors_list.append(SensorEntityDescription(
                                        key = uuid,
                                        name = uuid,
                                        state_class = SensorStateClass.MEASUREMENT,
                                        device_class = SensorDeviceClass.TEMPERATURE,
                                        native_unit_of_measurement = UnitOfTemperature.CELSIUS,
                                        suggested_display_precision = 1,
                                    ))
                            if k2 == 'Light':
                                uuid = k1 + '.' + k2
                                notinlist = uuid not in self._data
                                self._data[uuid] = float(v2)
                                if notinlist:
                                    self._sensors_list.append(SensorEntityDescription(
                                        key = uuid,
                                        name = uuid,
                                        state_class = SensorStateClass.MEASUREMENT,
                                        device_class = SensorDeviceClass.ILLUMINANCE,
                                        native_unit_of_measurement = LIGHT_LUX,
                                        suggested_display_precision = 0,
                                    ))
                    elif k1.endswith('_Temperature'):
                        for k2,v2 in v1.items():
                            if k2 != 'Time':
                                uuid = k1 + '.' + k2
                                notinlist = uuid not in self._data
                                self._data[uuid] = float(v2)
                                if notinlist:
                                    self._sensors_list.append(SensorEntityDescription(
                                        key = uuid,
                                        name = uuid,
                                        state_class = SensorStateClass.MEASUREMENT,
                                        device_class = SensorDeviceClass.TEMPERATURE,
                                        native_unit_of_measurement = UnitOfTemperature.CELSIUS,
                                        suggested_display_precision = 1,
                                    ))
                    elif k1 == 'Cistern':
                        for k2,v2 in v1.items():
                            if k2 == 'Cistern_Pressure':
                                uuid = k1 + '.' + k2
                                notinlist = uuid not in self._data
                                self._data[uuid] = float(v2)
                                if notinlist:
                                    self._sensors_list.append(SensorEntityDescription(
                                        key = uuid,
                                        name = uuid,
                                        state_class = SensorStateClass.MEASUREMENT,
                                        device_class = SensorDeviceClass.PRESSURE,
                                        native_unit_of_measurement = UnitOfPressure.BAR,
                                        suggested_display_precision = 1,
                                    ))
                            if k2 == 'Cistern_Level':
                                uuid = k1 + '.' + k2
                                notinlist = uuid not in self._data
                                self._data[uuid] = float(v2)
                                if notinlist:
                                    self._sensors_list.append(SensorEntityDescription(
                                        key = uuid,
                                        name = uuid,
                                        state_class = SensorStateClass.MEASUREMENT,
                                        device_class = None,
                                        native_unit_of_measurement = PERCENTAGE,
                                        suggested_display_precision = 0,
                                    ))
                    elif k1.endswith('_Input'):
                        for k2,v2 in v1.items():
                            if k2 != 'Time':
                                dc = None
                                uuid = k1 + '.' + k2
                                notinlist = uuid not in self._data
                                self._data[uuid] = bool(v2)
                                if notinlist:
                                    name = uuid
                                    if 'Door_' in k2:
                                        dc = BinarySensorDeviceClass.DOOR
                                        name = name + '_not'
                                    elif 'Blinds_' in k2:
                                        dc = BinarySensorDeviceClass.TAMPER
                                    elif 'Window_' in k2:
                                        dc = BinarySensorDeviceClass.WINDOW
                                        name = name + '_not'
                                    elif 'Alert_' in k2:
                                        dc = BinarySensorDeviceClass.TAMPER
                                    elif 'Hood' in k2:
                                        dc = BinarySensorDeviceClass.POWER
                                    elif 'Taster_' in k2:
                                        dc = BinarySensorDeviceClass.LIGHT
                                    elif 'Tor_' in k2:
                                        dc = BinarySensorDeviceClass.GARAGE_DOOR
                                        name = name + '_not'
                                    else:
                                        dc = None

                                    self._binary_sensors_list.append(BinarySensorEntityDescription(
                                        key = uuid,
                                        name = name,
                                        device_class = dc,
                                    ))

                # print(self._data)
                return(self._data)
        except:     # ApiError as err
            raise UpdateFailed(f"Error communicating with API")     # {err}



# class MyEntity(CoordinatorEntity, LightEntity):
#     """An entity using CoordinatorEntity.

#     The CoordinatorEntity class provides:
#       should_poll
#       async_update
#       async_added_to_hass
#       available
#     """

#     def __init__(self, coordinator: HomeCANupdateCoordinator, idx) -> None:
#         """Pass coordinator to CoordinatorEntity."""
#         super().__init__(coordinator, context=idx)
#         self.idx = idx

#     @callback
#     def _handle_coordinator_update(self) -> None:
#         """Handle updated data from the coordinator."""
#         self._attr_is_on = self.coordinator.data[self.idx]["state"]
#         self.async_write_ha_state()

#     async def async_turn_on(self, **kwargs):
#         """Turn the light on.

#         Example method how to request data updates.
#         """
#         # Do the turning on.
#         # ...

#         # Update the data
#         await self.coordinator.async_request_refresh()



# class HomeCANdataUpdateCoordinator(DataUpdateCoordinator[dict[str, any]]):
#     """Class to manage fetching AccuWeather data API."""

#     def __init__(
#         self,
#         hass: HomeAssistant,
#         session: ClientSession,
#         host: str,
#         name: str,
#         api_key: str,
#     ) -> None:
#         """Initialize."""
#         self._lasttime = ''
#         self._messages = {}
#         self.homecan = HomeCANio(session, host, name, api_key)
#         self.device_info = DeviceInfo(
#             entry_type=DeviceEntryType.SERVICE,
#             #identifiers={(DOMAIN, location_key)},
#             manufacturer='Ralf Bauer',
#             name=name,
#             # configuration_url=(
#             #     "http://accuweather.com/en/"
#             #     f"_/_/{location_key}/"
#             #     f"weather-forecast/{location_key}/"
#             # ),
#         )

#         update_interval = timedelta(minutes=10)
#         # _LOGGER.debug("Data will be update every %s", update_interval)

#         super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

#     async def _async_update_data(self) -> dict[str, any]:
#         """Update data."""
#         forecast: list[dict[str, any]] = []
#         try:
#             async with timeout(10):
#                 # current = await self.async_getjson(self._lasttime)
#                 current = await self.async_test(self._lasttime)
#                 if current is not None:
#                     self._lasttime = current['Time']
#                     self._messages = current['Msgs']
#                 else:
#                     self._lasttime = None
#                     self._messages = None
#         except (
#             ClientConnectorError,
#             # ApiError,
#             # InvalidApiKeyError,
#             # RequestsExceededError,
#         ) as error:
#             raise UpdateFailed(error) from error
#         # _LOGGER.debug("Requests remaining: %d", self.accuweather.requests_remaining)
#         return(current)
