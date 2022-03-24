import logging
from homeassistant.exceptions import PlatformNotReady
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.cover import (
    CoverEntity,
    CoverDeviceClass,
    SUPPORT_OPEN_TILT,
    SUPPORT_CLOSE_TILT,
    SUPPORT_SET_TILT_POSITION,
    ATTR_TILT_POSITION,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
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

class FlairVent(CoverEntity):
    """Representation of a Flair Vent as Cover."""

    def __init__(self, vent):
        self._vent = vent

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            "identifiers": {(DOMAIN, self._vent.vent_id)},
            "name": self._vent.vent_name,
            "manufacturer": "Flair",
            "model": "Flair Vent",
            "configuration_url": "https://my.flair.co/",
        }
    @property
    def device_class(self):
        return CoverDeviceClass.DAMPER

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
    def is_closed(self):
        """Return true if vent is closed."""
        return not self._vent.is_vent_open

    @property
    def current_cover_tilt_position(self) -> int:
        """Return the current percent open."""
        if not self._vent.is_vent_open:
            return 0
        return self._vent.vent_percent

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return SUPPORT_OPEN_TILT | SUPPORT_CLOSE_TILT | SUPPORT_SET_TILT_POSITION

    def open_cover_tilt(self, **kwargs) -> None:
        """Open the vent."""
        self._vent.set_vent_percentage(100)

    def close_cover_tilt(self, **kwargs) -> None:
        """Close the vent"""
        self._vent.set_vent_percentage(0)

    def set_cover_tilt_position(self, **kwargs):
        """Set vent percentage open."""
        if kwargs[ATTR_TILT_POSITION] == 0:
            return self.close_cover_tilt()
        elif kwargs[ATTR_TILT_POSITION] == 100:
            return self.open_cover_tilt()
        else:
            return self._vent.set_vent_percentage(50)
        
    @property
    def available(self):
        """Return true if device is available."""
        if self._vent.is_active is None:
            return False
        return self._vent.is_active

    def update(self):
        """Update automation state."""
        _LOGGER.info("Refreshing device state")
        self._vent.refresh()
