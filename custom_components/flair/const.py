""" Constants for Flair """

import asyncio
import logging

from aiohttp.client_exceptions import ClientConnectionError
from flairaio.exceptions import FlairAuthError, FlairError

from homeassistant.components.climate import HVACAction, HVACMode
from homeassistant.components.climate.const import (
    FAN_AUTO,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    SWING_OFF,
    SWING_ON,
)
from homeassistant.const import Platform

LOGGER = logging.getLogger(__package__)

DEFAULT_SCAN_INTERVAL = 30
DOMAIN = "flair"
PLATFORMS = [
    Platform.BUTTON,
    Platform.CLIMATE,
    Platform.COVER,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]

DEFAULT_NAME = "Flair"
TIMEOUT = 20

FLAIR_ERRORS = (
    asyncio.TimeoutError,
    ClientConnectionError,
    FlairAuthError,
    FlairError,
)

""" Dictionaries and lists. """

AWAY_MODES = [
    "Smart Away",
    "Off Only",
]

DEFAULT_HOLD_DURATION = {
    "Until": "Until next scheduled event",
    "3h": "3 Hours",
    "8h": "8 Hours",
    "24h": "24 Hours",
    "Forever": "Forever",
}

HOME_AWAY_MODE = [
    "Home",
    "Away",
]

HOME_AWAY_SET_BY = {
    "Manual": "Manual",
    "Third Party Home Away": "Thermostat",
    "Flair Autohome Autoaway": "Flair App Geolocation",
}

HVAC_AVAILABLE_FAN_SPEEDS = {
    "FAN AUTO": FAN_AUTO,
    "FAN HI": FAN_HIGH,
    "FAN MID": FAN_MEDIUM,
    "FAN LOW": FAN_LOW,
}

HVAC_AVAILABLE_MODES_MAP = {
    "DRY": HVACMode.DRY,
    "HEAT": HVACMode.HEAT,
    "COOL": HVACMode.COOL,
    "FAN": HVACMode.FAN_ONLY,
    "AUTO": HVACMode.HEAT_COOL,
}

HVAC_CURRENT_ACTION = {
    HVACMode.OFF: HVACAction.OFF,
    HVACMode.HEAT: HVACAction.HEATING,
    HVACMode.COOL: HVACAction.COOLING,
    HVACMode.DRY: HVACAction.DRYING,
    HVACMode.FAN_ONLY: HVACAction.FAN,
}

HVAC_CURRENT_FAN_SPEED = {
    "Auto": FAN_AUTO,
    "High": FAN_HIGH,
    "Medium": FAN_MEDIUM,
    "Low": FAN_LOW,
}

HVAC_CURRENT_MODE_MAP = {
    "Off": HVACMode.OFF,
    "Dry": HVACMode.DRY,
    "Heat": HVACMode.HEAT,
    "Cool": HVACMode.COOL,
    "Fan": HVACMode.FAN_ONLY,
    "Auto": HVACMode.HEAT_COOL,
}

HVAC_SWING_STATE = {
    "On": SWING_ON,
    "Off": SWING_OFF,
}

PUCK_BACKGROUND = [
    "Black",
    "White",
]

ROOM_HVAC_MAP = {
    "float": HVACMode.OFF,
    "heat": HVACMode.HEAT,
    "cool": HVACMode.COOL,
    "auto": HVACMode.HEAT_COOL,
}

ROOM_MODES = [
    "Active",
    "Inactive",
]

SET_POINT_CONTROLLER = {
    "Home Evenness For Active Rooms Follow Third Party": "Thermostat",
    "Home Evenness For Active Rooms Flair Setpoint": "Flair App",
}

STRUCTURE_MODES = [
    "Heat",
    "Cool",
    "Auto",
    "Off",
]

SYSTEM_MODES = [
    "Auto",
    "Manual",
]

TEMPERATURE_SCALES = {
    "F": "Fahrenheit",
    "C": "Celsius",
    "K": "Kelvin",
}
