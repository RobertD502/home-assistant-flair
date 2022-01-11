import logging
from homeassistant.components.climate import ClimateEntity
from homeassistant.exceptions import PlatformNotReady
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.climate.const import (
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_SWING_MODE,
    SUPPORT_FAN_MODE,
    HVAC_MODE_OFF,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    FAN_AUTO,
    FAN_HIGH,
    FAN_MEDIUM,
    FAN_LOW,
    SWING_ON,
    SWING_OFF,
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_DRY,
    CURRENT_HVAC_FAN,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_OFF,

)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS, TEMP_FAHRENHEIT
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

THERMOSTAT_MODE_MAP = {
    "float": HVAC_MODE_OFF,
    "heat": HVAC_MODE_HEAT,
    "cool": HVAC_MODE_COOL,
    "auto": HVAC_MODE_HEAT_COOL,
}

HVAC_CURRENT_MODE_MAP = {
    "Off": HVAC_MODE_OFF,
    "Dry": HVAC_MODE_DRY,
    "Heat": HVAC_MODE_HEAT,
    "Cool": HVAC_MODE_COOL,
    "Fan": HVAC_MODE_FAN_ONLY,
    "Auto": HVAC_MODE_HEAT_COOL,
}

HVAC_AVAILABLE_MODES_MAP = {
    "DRY": HVAC_MODE_DRY,
    "HEAT": HVAC_MODE_HEAT,
    "COOL": HVAC_MODE_COOL,
    "FAN": HVAC_MODE_FAN_ONLY,
    "AUTO": HVAC_MODE_HEAT_COOL,
}

HVAC_CURRENT_FAN_SPEED = {
    "Auto": FAN_AUTO,
    "High": FAN_HIGH,
    "Medium": FAN_MEDIUM,
    "Low": FAN_LOW,
}

HVAC_AVAILABLE_FAN_SPEEDS = {
    "FAN AUTO": FAN_AUTO,
    "FAN HI": FAN_HIGH,
    "FAN MID": FAN_MEDIUM,
    "FAN LOW": FAN_LOW,
}

HVAC_AUTO_STRUCTURE_FAN_SPEEDS = {
    "AUTO": FAN_AUTO,
    "HIGH": FAN_HIGH,
    "MEDIUM": FAN_MEDIUM,
    "LOW": FAN_LOW,
}

HVAC_SWING_STATE = {
    "On": SWING_ON,
    "Off": SWING_OFF,
}

HVAC_AUTO_STRUCTURE_SWING_STATE = {
    True: SWING_ON,
    False: SWING_OFF,
}

THERMOSTAT_INV_MODE_MAP = {v: k for (k, v) in THERMOSTAT_MODE_MAP.items()}

HASS_HVAC_MODE_TO_FLAIR = {v: k for (k, v) in HVAC_CURRENT_MODE_MAP.items()}

HASS_HVAC_FAN_SPEED_TO_FLAIR = {v: k for (k, v) in HVAC_CURRENT_FAN_SPEED.items()}

HASS_HVAC_SWING_TO_FLAIR = {v: k for (k, v) in HVAC_SWING_STATE.items()}

HASS_HVAC_AUTO_STRUCTURE_FAN_SPEED_TO_FLAIR = {v: k for (k, v) in HVAC_AUTO_STRUCTURE_FAN_SPEEDS.items()}

HASS_HVAC_AUTO_STRUCTURE_SWING_TO_FLAIR = {v: k for (k, v) in HVAC_AUTO_STRUCTURE_SWING_STATE.items()}



async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Set up Flair Rooms."""
    flair = hass.data[DOMAIN]

    rooms = []
    try:
        for room in flair.rooms():
            rooms.append(FlairRoom(room))
    except Exception as e:
        _LOGGER.error("Failed to get Room(s) from Flair servers")
        raise PlatformNotReady from e

    hvac_units = []
    try:
        for hvac_unit in flair.hvac_units():
            hvac_units.append(FlairHvacUnit(hvac_unit))
    except Exception as e:
        _LOGGER.error("Failed to get HVAC units from Flair servers")
        raise PlatformNotReady from e

    async_add_entities(rooms)
    async_add_entities(hvac_units)

### Room Climate Entity ###
class FlairRoom(ClimateEntity):
    """Representation of a Flair Room as Climate Entity."""

    def __init__(self, room):
        self._room = room
        self._available = True

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            "identifiers": {(DOMAIN, self._room.room_id)},
            "name": self._room.room_name,
            "manufacturer": "Flair",
            "model": "Flair Room",
            "configuration_url": "https://my.flair.co/",
        }

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

### HVAC Unit Climate Entity ###
class FlairHvacUnit(ClimateEntity):
    """Representation of a Flair HVAC unit as Climate Entity."""

    def __init__(self, hvac_unit):
        self._hvac_unit = hvac_unit

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            "identifiers": {(DOMAIN, self._hvac_unit.hvac_id)},
            "name": self._hvac_unit.hvac_name,
            "manufacturer": self._hvac_unit.hvac_model,
            "model": "HVAC Unit",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self):
        """Return the ID of this HVAC unit."""
        return self._hvac_unit.hvac_id

    @property
    def name(self):
        """Return the name of the HVAC Unit."""
        return self._hvac_unit.hvac_name

    @property
    def icon(self):
        """Set hvac icon"""
        return 'mdi:hvac'

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        if self._hvac_unit.hvac_temp_scale == "F":
            return TEMP_FAHRENHEIT
        else:
            return TEMP_CELSIUS

    @property
    def hvac_mode(self):
        """Return the current hvac_mode"""
        if not self._hvac_unit.is_powered_on:
            return HVAC_MODE_OFF
        if self._hvac_unit.is_powered_on:
            mode = self._hvac_unit.hvac_mode
            if mode in HVAC_CURRENT_MODE_MAP:
                hvac_mode = HVAC_CURRENT_MODE_MAP[mode]
            return hvac_mode

    @property
    def hvac_modes(self):
        """Return the Supported Modes"""
        supported_modes = [HVAC_MODE_OFF]
        modes = self._hvac_unit.hvac_modes
        for mode in modes:
            if mode in HVAC_AVAILABLE_MODES_MAP:
                supported_modes.append(HVAC_AVAILABLE_MODES_MAP[mode])
        return supported_modes

    @property
    def hvac_action(self):
        """Return HVAC current action"""
        if (self._hvac_unit.is_powered_on and self.hvac_mode == HVAC_MODE_HEAT):
            return CURRENT_HVAC_HEAT
        if (self._hvac_unit.is_powered_on and self.hvac_mode == HVAC_MODE_COOL):
            return CURRENT_HVAC_COOL
        if (self._hvac_unit.is_powered_on and self.hvac_mode == HVAC_MODE_DRY):
            return CURRENT_HVAC_DRY
        if (self._hvac_unit.is_powered_on and self.hvac_mode == HVAC_MODE_FAN_ONLY):
            return CURRENT_HVAC_FAN
        if not self._hvac_unit.is_powered_on:
            return CURRENT_HVAC_OFF

    @property
    def fan_mode(self):
        """Return current fan speed"""
        if self._hvac_unit.hvac_fan_speed is not None:
            fan_speed = self._hvac_unit.hvac_fan_speed
            if fan_speed in HVAC_CURRENT_FAN_SPEED:
                hvac_fan_speed = HVAC_CURRENT_FAN_SPEED[fan_speed]
                return hvac_fan_speed
        else:
            return None

    @property
    def fan_modes(self):
        """Return supported fan speeds"""
        supported_fan_speeds = []
        fan_speeds = self._hvac_unit.hvac_fan_speeds
        for speed in fan_speeds:
            if speed in HVAC_AVAILABLE_FAN_SPEEDS:
                supported_fan_speeds.append(HVAC_AVAILABLE_FAN_SPEEDS[speed])
        return supported_fan_speeds

    @property
    def swing_mode(self):
        """Return current swing state"""
        if self._hvac_unit.swing_state is not None:
            swing_state = self._hvac_unit.swing_state
            if swing_state in HVAC_SWING_STATE:
                hvac_swing_state = HVAC_SWING_STATE[swing_state]
                return hvac_swing_state
        else:
            return None
    @property
    def swing_modes(self):
        """Return supported swing modes"""
        supported_swing_modes = [SWING_ON, SWING_OFF]
        return supported_swing_modes

    @property
    def current_temperature(self):
        """Return the current temperature of the associated room."""
        if not self.hass.config.units.is_metric:
            return round(((self._hvac_unit.puck_temp * (9/5))+ 32), 1)
        else:
            return self._hvac_unit.puck_temp

    @property
    def target_temperature(self):
        """Return the temperature currently set to be reached by the HVAC unit."""
        return self._hvac_unit.hvac_temp

    @property
    def current_humidity(self):
        """Return the current humidity of room HVAC unit is in."""
        if self._hvac_unit.puck_humidity is None:
            return None
        return self._hvac_unit.puck_humidity

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        if (self._hvac_unit.swing_available and len(self._hvac_unit.hvac_fan_speeds) > 0):
            if self._hvac_unit.system_mode == "auto":
                return SUPPORT_SWING_MODE | SUPPORT_FAN_MODE
            elif self.hvac_mode == HVAC_MODE_DRY or self.hvac_mode == HVAC_MODE_FAN_ONLY:
                return SUPPORT_SWING_MODE | SUPPORT_FAN_MODE
            else:
                return SUPPORT_TARGET_TEMPERATURE | SUPPORT_SWING_MODE | SUPPORT_FAN_MODE
        elif self._hvac_unit.swing_available:
            if self._hvac_unit.system_mode == "auto":
                return SUPPORT_SWING_MODE
            elif self.hvac_mode == HVAC_MODE_DRY or self.hvac_mode == HVAC_MODE_FAN_ONLY:
                return SUPPORT_SWING_MODE
            else:
                return SUPPORT_TARGET_TEMPERATURE | SUPPORT_SWING_MODE
        elif len(self._hvac_unit.hvac_fan_speeds) > 0:
            if self._hvac_unit.system_mode == "auto":
                return SUPPORT_FAN_MODE
            elif self.hvac_mode == HVAC_MODE_DRY or self.hvac_mode == HVAC_MODE_FAN_ONLY:
                return SUPPORT_FAN_MODE
            else:
                return SUPPORT_TARGET_TEMPERATURE | SUPPORT_FAN_MODE
        else:
            return SUPPORT_TARGET_TEMPERATURE

    @property
    def available(self):
        """Return true if associated puck is available."""
        return self._hvac_unit.puck_is_active

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        temp = kwargs.get(ATTR_TEMPERATURE)

        if temp is not None:
            self._hvac_unit.set_hvac_temp(temp)
        else:
            _LOGGER.error("Missing valid arguments for set_temperature in %s", kwargs)

    def set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        if self._hvac_unit.system_mode == "auto":
            _LOGGER.error("HVAC mode can't be changed when Flair Structure is set to Auto Mode. Only Fan Speed and/or Swing (if supported) can be changed.")
        elif not self._hvac_unit.is_powered_on:
            self._hvac_unit.set_hvac_power("On")
            self._hvac_unit.set_hvac_mode(HASS_HVAC_MODE_TO_FLAIR.get(hvac_mode))
        elif hvac_mode == HVAC_MODE_OFF:
            self._hvac_unit.set_hvac_power("Off")
        else:
            self._hvac_unit.set_hvac_mode(HASS_HVAC_MODE_TO_FLAIR.get(hvac_mode))

    def set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        if self._hvac_unit.system_mode == "auto":
            self._hvac_unit.set_auto_structure_hvac_fan_speed(HASS_HVAC_AUTO_STRUCTURE_FAN_SPEED_TO_FLAIR.get(fan_mode))
        else:
            self._hvac_unit.set_hvac_fan_speed(HASS_HVAC_FAN_SPEED_TO_FLAIR.get(fan_mode))

    def set_swing_mode(self, swing_mode):
        """Set new target swing operation."""
        if self._hvac_unit.system_mode == "auto":
            self._hvac_unit.set_auto_structure_hvac_swing(HASS_HVAC_AUTO_STRUCTURE_SWING_TO_FLAIR.get(swing_mode))
        else:
            self._hvac_unit.set_hvac_swing(HASS_HVAC_SWING_TO_FLAIR.get(swing_mode))

    def update(self):
        """Update automation state."""
        _LOGGER.info("Refreshing flair hvac state")
        self._hvac_unit.refresh()
