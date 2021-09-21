import logging
from homeassistant.util.percentage import ordered_list_item_to_percentage
from homeassistant.exceptions import PlatformNotReady
from homeassistant.components.fan import (
    FanEntity,
    SUPPORT_SET_SPEED,
)
from .const import (
    DOMAIN,
    VENT_CLOSED,
    VENT_HALF_OPEN,
    VENT_OPEN
)

"""Attributes"""

ATTR_PERCENT_OPEN = "percent_open"
ATTR_IS_ACTIVE = "is_active"
ATTR_RSSI = "rssi"
ATTR_VOLTAGE = "voltage"
ATTR_DUCT_TEMP = "duct_temp"
ATTR_DUCT_PRESSURE = "duct_pressure_kPa"

ORDERED_NAMED_VENT_STATES = [VENT_HALF_OPEN, VENT_OPEN]

VENT_STATE_TO_HASS = {
    VENT_CLOSED: 0,
    VENT_HALF_OPEN: ordered_list_item_to_percentage(ORDERED_NAMED_VENT_STATES, VENT_HALF_OPEN),
    VENT_OPEN: ordered_list_item_to_percentage(ORDERED_NAMED_VENT_STATES, VENT_OPEN)
}

HASS_FAN_SPEED_TO_FLAIR = {v: k for (k, v) in VENT_STATE_TO_HASS.items()}

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Platform uses config entry setup."""
    pass

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Flair Vents."""
    flair = hass.data[DOMAIN]

    vents = []
    try:
        for vent in flair.vents():
            vents.append(FlairVent(vent))
    except Exception as e:
        _LOGGER.error("Failed to get vents from Flair servers")
        raise PlatformNotReady from e

    async_add_entities(vents)

class FlairVent(FanEntity):
    """Representation of a Flair Vent as Fan."""

    def __init__(self, vent):
        self._vent = vent
        self._available = True

    @property
    def unique_id(self):
        """Return the ID of this vent."""
        return self._vent.vent_id

    @property
    def name(self):
        """Return the name of the vent."""
        return "flair_vent_" + self._vent.vent_name

    @property
    def icon(self):
        """Set vent icon"""
        return 'mdi:air-filter'

    @property
    def is_on(self):
        """Return true if vent is open."""
        return self._vent.is_vent_open

    @property
    def percent_open(self) -> int:
        if self._vent.vent_percent is None:
            return None
        return self._vent.vent_percent

    @property
    def is_active(self):
        if self._vent.is_active is None:
            return None
        return self._vent.is_active

    @property
    def rssi(self) -> int:
        if self._vent.rssi is None:
            return None
        return self._vent.rssi

    @property
    def voltage(self) -> int:
        return self._vent.voltage

    @property
    def duct_temp(self):
        if self._vent.duct_temp is None:
            return None
        elif not self.hass.config.units.is_metric:
            return round(((self._vent.duct_temp * (9/5))+ 32), 2)
        else:
            return self._vent.duct_temp

    @property
    def duct_pressure(self):
        if self._vent.duct_pressure is None:
            return None
        return self._vent.duct_pressure

    @property
    def available(self):
        """Return true if device is available."""
        return self._available

    @property
    def device_state_attributes(self) -> dict:
        """Return optional state attributes."""
        return {
            ATTR_PERCENT_OPEN: self.percent_open,
            ATTR_DUCT_TEMP: self.duct_temp,
            ATTR_DUCT_PRESSURE: self.duct_pressure,
            ATTR_VOLTAGE: self.voltage,
            ATTR_IS_ACTIVE: self.is_active,
            ATTR_RSSI: self.rssi,
        }

    @property
    def percentage(self) -> int:
        """Return the current percent open."""
        if not self._vent.is_vent_open:
            return 0
        return VENT_STATE_TO_HASS.get(self._vent.vent_percent)

    @property
    def speed_count(self) -> int:
        """Get the list of available vent percentage open states."""
        return len(ORDERED_NAMED_VENT_STATES)

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return SUPPORT_SET_SPEED

    def turn_on(self, percentage: int = None, **kwargs) -> None:
        """Open the vent."""
        self._vent.set_vent_percentage(100)
        if percentage is not None:
            self.set_percentage(percentage)

    def turn_off(self, **kwargs) -> None:
        """Close the vent"""
        self._vent.set_vent_percentage(0)

    def set_percentage(self, percentage: int) -> None:
        """Set vent percentage open."""
        if percentage == 0:
            return self.turn_off()
        if not self.is_on:
            self._vent.set_vent_percentage(HASS_FAN_SPEED_TO_FLAIR.get(percentage))
        self._vent.set_vent_percentage(HASS_FAN_SPEED_TO_FLAIR.get(percentage))

    def update(self):
        """Update automation state."""
        _LOGGER.debug("Refreshing device state")
        self._vent.refresh()
