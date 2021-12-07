"""Setting up Flair Pucks and Structures"""

import logging
import voluptuous as vol
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.exceptions import PlatformNotReady
from homeassistant.components.sensor import SensorEntity, STATE_CLASS_MEASUREMENT, SensorDeviceClass
from homeassistant.const import TEMP_CELSIUS, LIGHT_LUX, ATTR_ENTITY_ID


"""Attributes"""

ATTR_HUMIDITY = "humidity"
ATTR_IS_ACTIVE = "is_active"
ATTR_IS_GATEWAY = "is_gateway"
ATTR_VOLTAGE = "voltage"
ATTR_RSSI = "rssi"

ATTR_AVAILABLE_SCHEDULES = "available_schedules"
ATTR_SCHEDULE_NAME = "schedule_name"

"""Services"""
SERVICE_SET_SCHEDULE = "set_schedule"

SET_SCHEDULE_SCHEMA = {
    vol.Required(ATTR_ENTITY_ID): cv.entity_id,
    vol.Required(ATTR_SCHEDULE_NAME): cv.string,
}


from .const import (
    DOMAIN
)



_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Platform uses config entry setup."""
    pass


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Flair Pucks."""
    flair = hass.data[DOMAIN]

    platform = entity_platform.current_platform.get()

    pucks = []
    structures = []
    puck_light = []

    try:
        for puck in flair.pucks():
            pucks.append(FlairPuck(puck))
    except Exception as e:
        _LOGGER.error("Failed to get Puck(s) from Flair servers")
        raise PlatformNotReady from e

    try:
        for puck in flair.pucks():
            puck_light.append(PuckLight(puck))
    except Exception as e:
        _LOGGER.error("Failed to get Puck(s) Light data from Flair servers")
        raise PlatformNotReady from e 

    try:
        for structure in flair.structures():
            structures.append(FlairStructure(structure))
    except Exception as e:
        _LOGGER.error("Failed to get Structure(s) from Flair servers")
        raise PlatformNotReady from e

    async_add_entities(pucks)
    async_add_entities(puck_light)
    async_add_entities(structures)

    platform.async_register_entity_service(
        SERVICE_SET_SCHEDULE,
        SET_SCHEDULE_SCHEMA,
        "set_schedule",
    )

class FlairPuck(SensorEntity):
    """Representation of a Flair Puck."""

    def __init__(self, puck):
        self._puck = puck
        self._available = True

    @property
    def unique_id(self):
        """Return the ID of this Puck."""
        return self._puck.puck_id

    @property
    def name(self):
        """Return the name of the Puck if any."""
        return 'flair_puck_' + self._puck.puck_name

    @property
    def native_value(self):
        """Returns Puck Temperature"""
        if self._puck.current_temp is None:
            return None
        return self._puck.current_temp

    @property
    def native_unit_of_measurement(self):
        return TEMP_CELSIUS

    @property
    def device_class(self) -> SensorDeviceClass:
        return SensorDeviceClass.TEMPERATURE

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

    @property
    def icon(self):
        """Set puck icon"""
        return 'mdi:circle-double'

    @property
    def humidity(self) -> int:
        if self._puck.current_humidity is None:
            return None
        return self._puck.current_humidity

    @property
    def is_active(self):
        if self._puck.is_active is None:
            return None
        return self._puck.is_active

    @property
    def is_gateway(self):
        if self._puck.is_gateway is None:
            return None
        return self._puck.is_gateway

    @property
    def voltage(self) -> int:
        if self._puck.voltage is None:
            return None
        return self._puck.voltage

    @property
    def rssi(self) -> int:
        if self._puck.rssi is None:
            return None
        return self._puck.rssi

    @property
    def available(self):
        """Return true if device is available."""
        return self._available

    @property
    def extra_state_attributes(self) -> dict:
        """Return optional state attributes."""
        return {
            ATTR_HUMIDITY: self.humidity,
            ATTR_IS_ACTIVE: self.is_active,
            ATTR_IS_GATEWAY: self.is_gateway,
            ATTR_VOLTAGE: self.voltage,
            ATTR_RSSI: self.rssi,
        }

    def update(self):
        """Update automation state."""
        _LOGGER.info("Refreshing device state")
        self._puck.refresh()

class PuckLight(SensorEntity):
    """Representation of a Flair Puck Light Sensor."""

    def __init__(self, puck):
        self._puck = puck
        self._available = True

    @property
    def unique_id(self):
        """Return the ID of this Puck."""
        return self._puck.puck_id + '_light_sensor'

    @property
    def name(self):
        """Return the name of the Puck if any."""
        return 'flair_puck_' + self._puck.puck_name + '_light_level'

    @property
    def native_value(self):
        """Returns Puck Light Level"""
        if self._puck.light_level is None:
            return None
        return self._puck.light_level

    @property
    def native_unit_of_measurement(self):
        return LIGHT_LUX

    @property
    def device_class(self) -> SensorDeviceClass:
        return SensorDeviceClass.ILLUMINANCE

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

    @property
    def available(self):
        """Return true if device is available."""
        return self._available

    def update(self):
        """Update automation state."""
        _LOGGER.info("Refreshing device state")
        self._puck.refresh()

class FlairStructure(SensorEntity):
    """Representation of a Flair Structure."""

    def __init__(self, structure):
        self._structure = structure
        self._available = True

    @property
    def unique_id(self):
        """Return the ID of this Structure."""
        return self._structure.structure_id

    @property
    def name(self):
        """Return the name of the Structure if any."""
        return 'flair_structure_' + self._structure.structure_name

    @property
    def icon(self):
        """Set structure icon"""
        return 'mdi:home'

    @property
    def native_value(self):
        """Returns Current Structure Schedule"""
        if self._structure.active_schedule == None:
            return "No Active Schedule"
        elif self._structure.schedules_list is not None:
            SCHEDULE_LIST = self._structure.schedules_list
            COMBINED_SCHEDULES = {}
            for dictc in SCHEDULE_LIST:
                COMBINED_SCHEDULES.update(dictc)
            SCHEDULE_ID_TO_NAME = {v: k for (k, v) in COMBINED_SCHEDULES.items()}
            return SCHEDULE_ID_TO_NAME.get(self._structure.active_schedule)
        else:
            return None

    @property
    def available_schedules(self):
        try:
            SCHEDULE_LIST = self._structure.schedules_list
            COMBINED_SCHEDULES = {}
            for dictc in SCHEDULE_LIST:
                COMBINED_SCHEDULES.update(dictc)
            """Returns a list of available schedules for that structure"""
            if self._structure.schedules_list is None:
                return None
            else:
                return list(COMBINED_SCHEDULES.keys())
        except AttributeError:
            print("This structure doesn't have a Schedule Attribute")

    @property
    def available(self):
        """Return true if device is available."""
        return self._available

    @property
    def extra_state_attributes(self) -> dict:
        """Return optional state attributes."""
        return {
            ATTR_AVAILABLE_SCHEDULES: self.available_schedules,
        }

    def set_schedule(self, schedule_name) -> None:
        """Set Schedule By Name"""
        SCHEDULE_LIST = self._structure.schedules_list
        COMBINED_SCHEDULES = {}
        for dictc in SCHEDULE_LIST:
            COMBINED_SCHEDULES.update(dictc)
        NAME_TO_SCHEDULE_ID = {k: v for (k, v) in COMBINED_SCHEDULES.items()}
        while schedule_name not in list(COMBINED_SCHEDULES.keys()):
            return _LOGGER.error("Invalid schedule name")
        self._structure.set_schedule(NAME_TO_SCHEDULE_ID.get(schedule_name))
        self.state

    def update(self):
        """Update automation state."""
        _LOGGER.info("Refreshing puck state")
        self._structure.refresh()
