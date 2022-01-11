import logging
from homeassistant.util.percentage import ordered_list_item_to_percentage
from homeassistant.exceptions import PlatformNotReady
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
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

ORDERED_NAMED_VENT_STATES = [VENT_HALF_OPEN, VENT_OPEN]

VENT_STATE_TO_HASS = {
    VENT_CLOSED: 0,
    VENT_HALF_OPEN: ordered_list_item_to_percentage(ORDERED_NAMED_VENT_STATES, VENT_HALF_OPEN),
    VENT_OPEN: ordered_list_item_to_percentage(ORDERED_NAMED_VENT_STATES, VENT_OPEN)
}

HASS_FAN_SPEED_TO_FLAIR = {v: k for (k, v) in VENT_STATE_TO_HASS.items()}

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

class FlairVent(FanEntity):
    """Representation of a Flair Vent as Fan."""

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
