import logging
from homeassistant.components.climate import ClimateEntity
from homeassistant.exceptions import PlatformNotReady
from homeassistant.components.climate.const import (
    SUPPORT_TARGET_TEMPERATURE,
    HVAC_MODE_OFF,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    HVAC_MODE_HEAT_COOL,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS
from .const import DOMAIN

"""Attributes"""
ATTR_IS_ACTIVE = "is_active"


_LOGGER = logging.getLogger(__name__)

THERMOSTAT_MODE_MAP = {
    "float": HVAC_MODE_OFF,
    "heat": HVAC_MODE_HEAT,
    "cool": HVAC_MODE_COOL,
    "auto": HVAC_MODE_HEAT_COOL,
}
THERMOSTAT_INV_MODE_MAP = {v: k for k, v in THERMOSTAT_MODE_MAP.items()}

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Platform uses config entry setup."""
    pass

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Flair Rooms."""
    flair = hass.data[DOMAIN]

    rooms = []
    try:
        for room in flair.rooms():
            rooms.append(FlairRoom(room))
    except Exception as e:
        _LOGGER.error("Failed to get Room(s) from Flair servers")
        raise PlatformNotReady from e 

    async_add_entities(rooms)

class FlairRoom(ClimateEntity):
    """Representation of a Flair Room as Climate Entity."""

    def __init__(self, room):
        self._room = room
        self._available = True

    @property
    def unique_id(self):
        """Return the ID of this room."""
        return self._room.room_id

    @property
    def name(self):
        """Return the name of the room."""
        return "flair_room_" + self._room.room_name

    @property
    def icon(self):
        """Set room icon"""
        return 'mdi:door-open'

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def hvac_mode(self):
        """Return the current hvac_mode"""
        mode = self._room.current_hvac_mode
        if mode in THERMOSTAT_MODE_MAP:
            hvac_mode = THERMOSTAT_MODE_MAP[mode]
        return hvac_mode

    @property
    def hvac_modes(self):
        """Return the Supported Modes"""
        supported_modes = [HVAC_MODE_OFF, HVAC_MODE_COOL, HVAC_MODE_HEAT, HVAC_MODE_HEAT_COOL]
        return supported_modes

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._room.current_temp

    @property
    def target_temperature(self):
        """Return the temperature currently set to be reached."""
        return self._room.temp_set_point

    @property
    def current_humidity(self):
        """Return the current humidity."""
        if self._room.current_humidity is None:
            return None
        return self._room.current_humidity

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return SUPPORT_TARGET_TEMPERATURE

    @property
    def available(self):
        """Return true if room is available."""
        return self._available

    @property
    def is_active(self):
        if self._room.is_active is None:
            return None
        return self._room.is_active

    @property
    def extra_state_attributes(self) -> dict:
        """Return optional state attributes."""
        return {
            ATTR_IS_ACTIVE: self.is_active,
        }

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        temp = kwargs.get(ATTR_TEMPERATURE)

        if temp is not None:
            self._room.set_temperature(temp)
        else:
            _LOGGER.error("Missing valid arguments for set_temperature in %s", kwargs)

    def update(self):
        """Update automation state."""
        _LOGGER.info("Refreshing room state")
        self._room.refresh()
