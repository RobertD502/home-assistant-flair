""" Setting Up Flair Select Entities """

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import PlatformNotReady

from .const import DOMAIN, STRUCTURE_MODES, SYSTEM_MODES, HOME_AWAY_MODE, ROOM_MODES



_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Set up Select Entities."""
    flair = hass.data[DOMAIN]

    structures = []

    try:
        for structure in flair.structures():
            structures.append(FlairStructureSchedule(structure))
            structures.append(FlairStructureMode(structure))
            structures.append(FlairSystemMode(structure))
            structures.append(FlairHomeAwayMode(structure))
    except Exception as e:
        _LOGGER.error("Failed to get Structure(s) from Flair servers")
        raise PlatformNotReady from e

    rooms = []
    try:
        for room in flair.rooms():
            rooms.append(FlairRoomStatus(room))
    except Exception as e:
        _LOGGER.error("Failed to get Room(s) from Flair servers")
        raise PlatformNotReady from e

    async_add_entities(structures)
    async_add_entities(rooms)


######### Structure Select Entities #########

class FlairStructureSchedule(SelectEntity):
    """Representation of a Flair Schedule Select Entity."""

    def __init__(self, structure):
        self._structure = structure
        self._available = False

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            "identifiers": {(DOMAIN, self._structure.structure_id)},
            "name": self._structure.structure_name,
            "manufacturer": "Flair",
            "model": "Flair Structure",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self):
        """Return the ID of this Structure."""
        return self._structure.structure_id + "_schedules"

    @property
    def name(self):
        """Return the name of the Structure if any."""
        return self._structure.structure_name + " Schedules"

    @property
    def icon(self):
        """Set icon"""
        return 'mdi:calendar'

    @property
    def current_option(self):
        """Returns Currently Active Structure Schedule"""
        if self._structure.active_schedule is None:
            return "No Schedule"
        elif self._structure.active_schedule is not None:
            COMBINED_SCHEDULES = self._structure.schedules_dictionary
            SCHEDULE_ID_TO_NAME = {v: k for (k, v) in COMBINED_SCHEDULES.items()}
            return SCHEDULE_ID_TO_NAME.get(self._structure.active_schedule)
        else:
            return None

    @property
    def options(self):
        try:
            SCHEDULES_LIST = list(self._structure.schedules_dictionary.keys())
            if len(SCHEDULES_LIST) > 0:
                self._available = True
                return SCHEDULES_LIST
            else:
                self._available = False
        except AttributeError:
            _LOGGER.warning(f"Failed to get schedules for Flair Structure: {self._structure.structure_name}")
            self._available = False
        except:
            _LOGGER.warning(f"Failed to get schedules for Flair Structure: {self._structure.structure_name}")
            self._available = False

    @property
    def available(self):
        """Return true if device is available."""
        return self._available

    def select_option(self, option) -> None:
        """Change the selected option."""
        COMBINED_SCHEDULES = self._structure.schedules_dictionary
        NAME_TO_SCHEDULE_ID = {k: v for (k, v) in COMBINED_SCHEDULES.items()}
        if option == "No Schedule":
            self._structure.set_schedule(None)
        else:
            self._structure.set_schedule(NAME_TO_SCHEDULE_ID.get(option))

    def update(self):
        """Update Flair Structure data."""
        _LOGGER.info("Refreshing structure state")
        self._structure.refresh()

class FlairStructureMode(SelectEntity):
    """Representation of a Flair Structure Mode Select Entity."""

    def __init__(self, structure):
        self._structure = structure

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            "identifiers": {(DOMAIN, self._structure.structure_id)},
            "name": self._structure.structure_name,
            "manufacturer": "Flair",
            "model": "Flair Structure",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self):
        """Return the ID of this Structure."""
        return self._structure.structure_id + "_mode"

    @property
    def name(self):
        """Return the name of the Structure if any."""
        return self._structure.structure_name + " Structure Mode"

    @property
    def icon(self):
        """Set icon"""
        return 'mdi:sun-snowflake'

    @property
    def current_option(self):
        """Returns Currently Active Structure Mode"""
        CURRENT_STRUCTURE_MODE = self._structure.current_hvac_mode
        if CURRENT_STRUCTURE_MODE == "float":
            return "Off"
        else:
            return CURRENT_STRUCTURE_MODE.capitalize()

    @property
    def options(self):
        return STRUCTURE_MODES

    @property
    def available(self):
        """Return true if device is available."""
        if self._structure.current_hvac_mode is not None:
            return True
        else:
            return False

    def select_option(self, option) -> None:
        """Change the selected option."""
        if option == "Off":
            self._structure.set_structure_mode("float")
        else:
            lowercase_option = option[0].lower() + option[1:]
            self._structure.set_structure_mode(str(lowercase_option))

    def update(self):
        """Update Flair Structure data."""
        _LOGGER.info("Refreshing structure state")
        self._structure.refresh()

class FlairSystemMode(SelectEntity):
    """Representation of a Flair Structure System Mode Select Entity."""

    def __init__(self, structure):
        self._structure = structure

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            "identifiers": {(DOMAIN, self._structure.structure_id)},
            "name": self._structure.structure_name,
            "manufacturer": "Flair",
            "model": "Flair Structure",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self):
        """Return the ID of this Structure."""
        return self._structure.structure_id + "system_mode"

    @property
    def name(self):
        """Return the name of the Structure if any."""
        return self._structure.structure_name + " System Mode"

    @property
    def icon(self):
        """Set icon"""
        return 'mdi:home-circle'

    @property
    def current_option(self):
        """Returns Currently Active Structure System Mode"""
        CURRENT_SYSTEM_MODE = self._structure.current_system_mode
        return CURRENT_SYSTEM_MODE.capitalize()

    @property
    def options(self):
        return SYSTEM_MODES

    @property
    def available(self):
        """Return true if device is available."""
        if self._structure.current_system_mode is not None:
            return True
        else:
            return False

    def select_option(self, option) -> None:
        """Change the selected option."""
        lowercase_option = option[0].lower() + option[1:]
        self._structure.set_system_mode(str(lowercase_option))

    def update(self):
        """Update Flair Structure data."""
        _LOGGER.info("Refreshing structure state")
        self._structure.refresh()

class FlairHomeAwayMode(SelectEntity):
    """Representation of a Flair Home and Away Mode Select Entity."""

    def __init__(self, structure):
        self._structure = structure

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            "identifiers": {(DOMAIN, self._structure.structure_id)},
            "name": self._structure.structure_name,
            "manufacturer": "Flair",
            "model": "Flair Structure",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self):
        """Return the ID of this Structure."""
        return self._structure.structure_id + "home_away_mode"

    @property
    def name(self):
        """Return the name of the Structure if any."""
        return self._structure.structure_name + " Home/Away Mode"

    @property
    def icon(self):
        """Set icon"""
        if self._structure.is_home == True:
            return 'mdi:location-enter'
        else:
            return 'mdi:location-exit'

    @property
    def current_option(self):
        """Returns Currently Active Structure Home/Away Mode"""
        CURRENT_HOME_AWAY_MODE = self._structure.is_home
        if CURRENT_HOME_AWAY_MODE:
            return "Home"
        elif not CURRENT_HOME_AWAY_MODE:
            return "Away"
        else:
            return None

    @property
    def options(self):
        return HOME_AWAY_MODE

    @property
    def available(self):
        """Return true if device is available."""
        if self._structure.is_home is not None:
            return True
        else:
            return False

    def select_option(self, option) -> None:
        """Change the selected option."""
        if option == "Home":
            self._structure.set_home_away_mode(True)
        else:
            self._structure.set_home_away_mode(False)

    def update(self):
        """Update Flair Structure data."""
        _LOGGER.info("Refreshing structure state")
        self._structure.refresh()

######### Room Select Entities #########

class FlairRoomStatus(SelectEntity):
    """Representation of a Flair Room Status Select Entity."""

    def __init__(self, room):
        self._room = room

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
        return self._room.room_name + " Activity Status"

    @property
    def icon(self):
        """Set room activity icon"""
        if self._room.is_active:
            return 'mdi:toggle-switch'
        else:
            return 'mdi:toggle-switch-off'

    @property
    def current_option(self):
        """Returns Currently Active Room Mode"""
        CURRENT_ROOM_MODE = self._room.is_active
        if CURRENT_ROOM_MODE == True:
            return "Active"
        else:
            return "Inactive"

    @property
    def options(self):
        return ROOM_MODES

    @property
    def available(self):
        """Return true if device is available."""
        if self._room.is_active is not None:
            return True
        else:
            return False

    def select_option(self, option) -> None:
        """Change the selected option."""
        if option == "Active":
            self._room.set_activity(True)
        else:
            self._room.set_activity(False)

    def update(self):
        """Update Flair Room data."""
        _LOGGER.info("Refreshing room state")
        self._room.refresh()
