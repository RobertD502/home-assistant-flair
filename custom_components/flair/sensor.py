"""Setting up Flair Pucks."""

import logging
from homeassistant.helpers import entity_platform
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import TEMP_CELSIUS


"""Attributes"""

ATTR_HUMIDITY = "humidity"
ATTR_IS_ACTIVE = "is_active"
ATTR_IS_GATEWAY = "is_gateway"
ATTR_VOLTAGE = "voltage"
ATTR_RSSI = "rssi"



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

    pucks = []
    for puck in flair.pucks():
        pucks.append(FlairPuck(puck))

    async_add_entities(pucks)


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
    def state(self):
        """Returns Puck Temperature"""
        if self._puck.current_temp is None:
            return None
        return self._puck.current_temp

    @property
    def unit_of_measurement(self):
        return TEMP_CELSIUS

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
    def device_state_attributes(self) -> dict:
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
