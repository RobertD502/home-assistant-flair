"""Select platform for Flair integration."""
from __future__ import annotations

from typing import Any

from flairaio.model import Puck, Room, Structure

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import(
    AWAY_MODES,
    DEFAULT_HOLD_DURATION,
    DOMAIN,
    HOME_AWAY_MODE,
    HOME_AWAY_SET_BY,
    PUCK_BACKGROUND,
    ROOM_MODES,
    SET_POINT_CONTROLLER,
    SYSTEM_MODES,
    TEMPERATURE_SCALES,
)
from .coordinator import FlairDataUpdateCoordinator


DEFAULT_HOLD_TO_FLAIR = {v: k for (k, v) in DEFAULT_HOLD_DURATION.items()}
HOME_AWAY_SET_BY_TO_FLAIR = {v: k for (k, v) in HOME_AWAY_SET_BY.items()}
SET_POINT_CONTROLLER_TO_FLAIR = {v: k for (k, v) in SET_POINT_CONTROLLER.items()}
TEMP_SCALE_TO_FLAIR = {v: k for (k, v) in TEMPERATURE_SCALES.items()}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up Flair Select Entities."""

    coordinator: FlairDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    selects = []

    for structure_id, structure_data in coordinator.data.structures.items():
            # Structures
            selects.extend((
                SystemMode(coordinator, structure_id),
                HomeAwayMode(coordinator, structure_id),
                HomeAwaySetBy(coordinator, structure_id),
                DefaultHoldDuration(coordinator, structure_id),
                SetPointController(coordinator, structure_id),
                Schedule(coordinator, structure_id),
                AwayMode(coordinator, structure_id),
            ))

            # Rooms
            if structure_data.rooms:
                for room_id, room_data in structure_data.rooms.items():
                    selects.extend((
                        RoomActivity(coordinator, structure_id, room_id),
                    ))

            # Pucks
            if structure_data.pucks:
                for puck_id, puck_data in structure_data.pucks.items():
                    selects.extend((
                        PuckBackground(coordinator, structure_id, puck_id),
                        PuckTempScale(coordinator, structure_id, puck_id),
                    ))

    async_add_entities(selects)


class SystemMode(CoordinatorEntity, SelectEntity):
    """Representation of System Mode."""

    def __init__(self, coordinator, structure_id):
        super().__init__(coordinator)
        self.structure_id = structure_id

    @property
    def structure_data(self) -> Structure:
        """Handle coordinator structure data."""

        return self.coordinator.data.structures[self.structure_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.structure_data.id)},
            "name": self.structure_data.attributes['name'],
            "manufacturer": "Flair",
            "model": "Structure",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.structure_data.id) + '_system_mode'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "System mode"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:home-circle'

    @property
    def current_option(self) -> str:
        """Returns currently active system mode."""

        current_mode = self.structure_data.attributes['mode']
        return current_mode.capitalize()

    @property
    def options(self) -> list[str]:
        """Return list of all the available system modes."""

        return SYSTEM_MODES

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        lowercase_option = option[0].lower() + option[1:]
        attributes = self.set_attributes(str(lowercase_option))
        await self.coordinator.client.update('structures', self.structure_data.id, attributes=attributes, relationships={})
        self.structure_data.attributes['mode'] = lowercase_option
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    @staticmethod
    def set_attributes(mode: str) -> dict[str, str]:
        """Creates attributes dictionary."""

        attributes = {
            "mode": mode
        }
        return attributes


class HomeAwayMode(CoordinatorEntity, SelectEntity):
    """Representation of Home/Away Mode."""

    def __init__(self, coordinator, structure_id):
        super().__init__(coordinator)
        self.structure_id = structure_id

    @property
    def structure_data(self) -> Structure:
        """Handle coordinator structure data."""

        return self.coordinator.data.structures[self.structure_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.structure_data.id)},
            "name": self.structure_data.attributes['name'],
            "manufacturer": "Flair",
            "model": "Structure",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.structure_data.id) + '_home_away_mode'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Home/Away"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.structure_data.attributes['home']:
            return 'mdi:location-enter'
        else:
            return 'mdi:location-exit'

    @property
    def current_option(self) -> str | None:
        """Returns currently active home/away mode."""

        currently_home = self.structure_data.attributes['home']
        if currently_home:
            return "Home"
        elif not currently_home:
            return "Away"
        else:
            return None

    @property
    def options(self) -> list[str]:
        """Return list of all the available home/away modes."""

        return HOME_AWAY_MODE

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Disable entity if system mode is set to manual on initial registration."""

        system_mode = self.structure_data.attributes['mode']
        if system_mode == 'manual':
            return False
        else:
            return True

    @property
    def available(self) -> bool:
        """Marks entity as unavailable if system mode is set to Manual."""

        system_mode = self.structure_data.attributes['mode']
        if system_mode == 'manual':
            return False
        else:
            return True

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        attributes = self.set_attributes(option)
        await self.coordinator.client.update('structures', self.structure_data.id, attributes=attributes, relationships={})
        self.structure_data.attributes['home'] = attributes['home']
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    @staticmethod
    def set_attributes(mode: str) -> dict[str, bool]:
        """Creates attributes dictionary."""

        if mode == 'Home':
            setting = True
        if mode == 'Away':
            setting = False

        attributes = {
            "home": setting
        }
        return attributes


class HomeAwaySetBy(CoordinatorEntity, SelectEntity):
    """Representation of what sets Home/Away Mode."""

    def __init__(self, coordinator, structure_id):
        super().__init__(coordinator)
        self.structure_id = structure_id

    @property
    def structure_data(self) -> Structure:
        """Handle coordinator structure data."""

        return self.coordinator.data.structures[self.structure_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.structure_data.id)},
            "name": self.structure_data.attributes['name'],
            "manufacturer": "Flair",
            "model": "Structure",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.structure_data.id) + '_home_away_set_by'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Home/Away mode set by"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def icon(self) -> str:
        """Set icon."""

        mode = self.structure_data.attributes['home-away-mode']

        if mode == 'Manual':
            return 'mdi:account-circle'
        if mode == 'Third Party Home Away':
            return 'mdi:thermostat'
        if mode == 'Flair Autohome Autoaway':
            return 'mdi:cellphone'

    @property
    def current_option(self) -> str | None:
        """Returns currently active home/away mode setter."""

        current = self.structure_data.attributes['home-away-mode']

        if current in HOME_AWAY_SET_BY.keys():
            return HOME_AWAY_SET_BY.get(current)
        else:
            return None

    @property
    def options(self) -> list[str]:
        """Return list of all the available home/away setters."""

        if self.structure_data.thermostats:
            return list(HOME_AWAY_SET_BY.values())
        else:
            return ['Manual', 'Flair App Geolocation']

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Disable entity if system mode is set to manual on initial registration."""

        system_mode = self.structure_data.attributes['mode']
        if system_mode == 'manual':
            return False
        else:
            return True

    @property
    def available(self) -> bool:
        """Marks entity as unavailable if system mode is set to Manual."""

        system_mode = self.structure_data.attributes['mode']
        if system_mode == 'manual':
            return False
        else:
            return True

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        ha_to_flair = HOME_AWAY_SET_BY_TO_FLAIR.get(option)
        attributes = self.set_attributes(ha_to_flair)
        await self.coordinator.client.update('structures', self.structure_data.id, attributes=attributes, relationships={})
        self.structure_data.attributes['home-away-mode'] = ha_to_flair
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    @staticmethod
    def set_attributes(setter: str) -> dict[str, str]:
        """Creates attributes dictionary."""

        attributes = {
            "home-away-mode": setter
        }
        return attributes


class DefaultHoldDuration(CoordinatorEntity, SelectEntity):
    """Representation of default hold duration setting."""

    def __init__(self, coordinator, structure_id):
        super().__init__(coordinator)
        self.structure_id = structure_id

    @property
    def structure_data(self) -> Structure:
        """Handle coordinator structure data."""

        return self.coordinator.data.structures[self.structure_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.structure_data.id)},
            "name": self.structure_data.attributes['name'],
            "manufacturer": "Flair",
            "model": "Structure",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.structure_data.id) + '_default_hold_duration'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Default hold duration"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:timer'

    @property
    def current_option(self) -> str | None:
        """Returns currently active default hold duration."""

        current = self.structure_data.attributes['default-hold-duration']

        if current in DEFAULT_HOLD_DURATION.keys():
            return DEFAULT_HOLD_DURATION.get(current)
        else:
            return None

    @property
    def options(self) -> list[str]:
        """Return list of all the available default hold durations."""

        return list(DEFAULT_HOLD_DURATION.values())

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Disable entity if system mode is set to manual on initial registration."""

        system_mode = self.structure_data.attributes['mode']
        if system_mode == 'manual':
            return False
        else:
            return True

    @property
    def available(self) -> bool:
        """Marks entity as unavailable if system mode is set to Manual."""

        system_mode = self.structure_data.attributes['mode']
        if system_mode == 'manual':
            return False
        else:
            return True

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        ha_to_flair = DEFAULT_HOLD_TO_FLAIR.get(option)
        attributes = self.set_attributes(ha_to_flair)
        await self.coordinator.client.update('structures', self.structure_data.id, attributes=attributes, relationships={})
        self.structure_data.attributes['default-hold-duration'] = ha_to_flair
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    @staticmethod
    def set_attributes(duration: str) -> dict[str, str]:
        """Creates attributes dictionary."""

        attributes = {
            "default-hold-duration": duration
        }
        return attributes


class SetPointController(CoordinatorEntity, SelectEntity):
    """Representation of set point controller setting."""

    def __init__(self, coordinator, structure_id):
        super().__init__(coordinator)
        self.structure_id = structure_id

    @property
    def structure_data(self) -> Structure:
        """Handle coordinator structure data."""

        return self.coordinator.data.structures[self.structure_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.structure_data.id)},
            "name": self.structure_data.attributes['name'],
            "manufacturer": "Flair",
            "model": "Structure",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.structure_data.id) + '_set_point_controller'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Set point controller"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:controller'

    @property
    def current_option(self) -> str | None:
        """Returns current set point controller."""

        current = self.structure_data.attributes['set-point-mode']

        if current in SET_POINT_CONTROLLER.keys():
            return SET_POINT_CONTROLLER.get(current)
        else:
            return None

    @property
    def options(self) -> list[str]:
        """Return list of all the available set point controllers."""

        if self.structure_data.thermostats:
            return list(SET_POINT_CONTROLLER.values())
        else:
            return ['Flair App']

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Disable entity if system mode is set to manual on initial registration."""

        system_mode = self.structure_data.attributes['mode']
        if system_mode == 'manual':
            return False
        else:
            return True

    @property
    def available(self) -> bool:
        """Marks entity as unavailable if system mode is set to Manual."""

        system_mode = self.structure_data.attributes['mode']
        if system_mode == 'manual':
            return False
        else:
            return True

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        ha_to_flair = SET_POINT_CONTROLLER_TO_FLAIR.get(option)
        attributes = self.set_attributes(ha_to_flair)
        await self.coordinator.client.update('structures', self.structure_data.id, attributes=attributes, relationships={})
        self.structure_data.attributes['set-point-mode'] = ha_to_flair
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    @staticmethod
    def set_attributes(option: str) -> dict[str, str]:
        """Creates attributes dictionary."""

        attributes = {
            "set-point-mode": option
        }
        return attributes


class Schedule(CoordinatorEntity, SelectEntity):
    """Representation of available structure schedules."""

    def __init__(self, coordinator, structure_id):
        super().__init__(coordinator)
        self.structure_id = structure_id

    @property
    def structure_data(self) -> Structure:
        """Handle coordinator structure data."""

        return self.coordinator.data.structures[self.structure_id]

    @property
    def schedules(self) -> dict[str,str]:
        """Create dictionary with all available schedules."""

        schedules: dict[str, str] = {
            "No Schedule": "No Schedule",
        }

        if self.structure_data.schedules:
            for schedule in self.structure_data.schedules:
                schedules[self.structure_data.schedules[schedule].id] = self.structure_data.schedules[schedule].attributes['name']

        return schedules

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.structure_data.id)},
            "name": self.structure_data.attributes['name'],
            "manufacturer": "Flair",
            "model": "Structure",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.structure_data.id) + '_schedule'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Active schedule"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:calendar'

    @property
    def current_option(self) -> str:
        """Returns current active schedule."""

        active_schedule = self.structure_data.attributes['active-schedule-id']

        if active_schedule is None:
            return 'No Schedule'
        else:
            return self.schedules[active_schedule]

    @property
    def options(self) -> list[str]:
        """Return list of all the available schedules."""

        return list(self.schedules.values())

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Disable entity if system mode is set to manual on initial registration."""

        system_mode = self.structure_data.attributes['mode']
        if system_mode == 'manual':
            return False
        else:
            return True

    @property
    def available(self) -> bool:
        """Marks entity as unavailable if system mode is set to Manual."""

        system_mode = self.structure_data.attributes['mode']
        if system_mode == 'manual':
            return False
        else:
            return True

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        schedule_name_to_id = {v: k for (k, v) in self.schedules.items()}

        if option == 'No Schedule':
            ha_to_flair = None
        else:
            ha_to_flair = schedule_name_to_id.get(option)

        attributes = self.set_attributes(ha_to_flair)
        await self.coordinator.client.update('structures', self.structure_data.id, attributes=attributes, relationships={})
        self.structure_data.attributes['active-schedule-id'] = ha_to_flair
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    @staticmethod
    def set_attributes(option: str) -> dict[str, str]:
        """Creates attributes dictionary."""

        attributes = {
            "active-schedule-id": option
        }
        return attributes


class AwayMode(CoordinatorEntity, SelectEntity):
    """Representation of structure away mode setting."""

    def __init__(self, coordinator, structure_id):
        super().__init__(coordinator)
        self.structure_id = structure_id

    @property
    def structure_data(self) -> Structure:
        """Handle coordinator structure data."""

        return self.coordinator.data.structures[self.structure_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.structure_data.id)},
            "name": self.structure_data.attributes['name'],
            "manufacturer": "Flair",
            "model": "Structure",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.structure_data.id) + '_away_mode'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Away Mode"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:clipboard-list'

    @property
    def current_option(self) -> str:
        """Returns current away mode setting."""

        return self.structure_data.attributes['structure-away-mode']

    @property
    def options(self) -> list[str]:
        """Return list of all the available away modes."""

        return AWAY_MODES

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Disable entity if system mode is set to manual on initial registration."""

        system_mode = self.structure_data.attributes['mode']
        if system_mode == 'manual':
            return False
        else:
            return True

    @property
    def available(self) -> bool:
        """Marks entity as unavailable if system mode is set to Manual."""

        system_mode = self.structure_data.attributes['mode']
        if system_mode == 'manual':
            return False
        else:
            return True

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        attributes = self.set_attributes(option)
        await self.coordinator.client.update('structures', self.structure_data.id, attributes=attributes, relationships={})
        self.structure_data.attributes['structure-away-mode'] = option
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    @staticmethod
    def set_attributes(option: str) -> dict[str, str]:
        """Creates attributes dictionary."""

        attributes = {
            "structure-away-mode": option
        }
        return attributes


class RoomActivity(CoordinatorEntity, SelectEntity):
    """Representation of Flair room activity setting."""

    def __init__(self, coordinator, structure_id, room_id):
        super().__init__(coordinator)
        self.room_id = room_id
        self.structure_id = structure_id

    @property
    def room_data(self) -> Room:
        """Handle coordinator room data."""

        return self.coordinator.data.structures[self.structure_id].rooms[self.room_id]

    @property
    def structure_data(self) -> Structure:
        """Handle coordinator structure data."""

        return self.coordinator.data.structures[self.structure_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.room_data.id)},
            "name": self.room_data.attributes['name'],
            "manufacturer": "Flair",
            "model": "Room",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.room_data.id) + '_activity_status'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Activity status"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.room_data.attributes['active']:
            return 'mdi:toggle-switch'
        else:
            return 'mdi:toggle-switch-off'

    @property
    def current_option(self) -> str:
        """Returns current activity status."""

        active = self.room_data.attributes['active']

        if active:
            return 'Active'
        else:
            return 'Inactive'

    @property
    def options(self) -> list[str]:
        """Return list of all the available activity status states."""

        return ROOM_MODES

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Disable entity if system mode is set to manual on initial registration."""

        system_mode = self.structure_data.attributes['mode']
        if system_mode == 'manual':
            return False
        else:
            return True

    @property
    def available(self) -> bool:
        """Marks entity as unavailable if system mode is set to Manual."""

        system_mode = self.structure_data.attributes['mode']
        if system_mode == 'manual':
            return False
        else:
            return True

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        if option == 'Active':
            ha_to_flair = True
        else:
            ha_to_flair = False

        attributes = self.set_attributes(ha_to_flair)
        await self.coordinator.client.update('rooms', self.room_data.id, attributes=attributes, relationships={})
        self.room_data.attributes['active'] = ha_to_flair
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    @staticmethod
    def set_attributes(option: bool) -> dict[str, bool]:
        """Creates attributes dictionary."""

        attributes = {
            "active": option
        }
        return attributes


class PuckBackground(CoordinatorEntity, SelectEntity):
    """Representation of puck background color."""

    def __init__(self, coordinator, structure_id, puck_id):
        super().__init__(coordinator)
        self.puck_id = puck_id
        self.structure_id = structure_id

    @property
    def puck_data(self) -> Puck:
        """Handle coordinator puck data."""

        return self.coordinator.data.structures[self.structure_id].pucks[self.puck_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.puck_data.id)},
            "name": self.puck_data.attributes['name'],
            "manufacturer": "Flair",
            "model": "Puck",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.puck_data.id) + '_background_color'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Background color"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:invert-colors'

    @property
    def current_option(self) -> str:
        """Returns current puck background color."""

        return self.puck_data.attributes['puck-display-color'].capitalize()

    @property
    def options(self) -> list[str]:
        """Return list of all the available puck background colors."""

        return PUCK_BACKGROUND

    @property
    def available(self) -> bool:
        """Return true if puck is active."""

        if not self.puck_data.attributes['inactive']:
            return True
        else:
            return False

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        ha_to_flair = option.lower()
        attributes = self.set_attributes(ha_to_flair)
        await self.coordinator.client.update('pucks', self.puck_data.id, attributes=attributes, relationships={})
        self.puck_data.attributes['puck-display-color'] = ha_to_flair
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    @staticmethod
    def set_attributes(option: str) -> dict[str, str]:
        """Creates attributes dictionary."""

        attributes = {
            "puck-display-color": option
        }
        return attributes


class PuckTempScale(CoordinatorEntity, SelectEntity):
    """Representation of puck temp scale selection."""

    def __init__(self, coordinator, structure_id, puck_id):
        super().__init__(coordinator)
        self.puck_id = puck_id
        self.structure_id = structure_id

    @property
    def puck_data(self) -> Puck:
        """Handle coordinator puck data."""

        return self.coordinator.data.structures[self.structure_id].pucks[self.puck_id]

    @property
    def structure_data(self) -> Structure:
        """Handle coordinator structure data."""

        return self.coordinator.data.structures[self.structure_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.puck_data.id)},
            "name": self.puck_data.attributes['name'],
            "manufacturer": "Flair",
            "model": "Puck",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.puck_data.id) + '_temp_scale'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Temperature scale"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def icon(self) -> str:
        """Set icon."""

        temp_scale = self.structure_data.attributes['temperature-scale']

        if temp_scale == 'F':
            return 'mdi:temperature-fahrenheit'
        if temp_scale == 'C':
            return 'mdi:temperature-celsius'
        if temp_scale == 'K':
            return 'mdi:temperature-kelvin'

    @property
    def current_option(self) -> str:
        """Returns current puck temp scale."""

        current_scale = self.structure_data.attributes['temperature-scale']
        return TEMPERATURE_SCALES.get(current_scale)

    @property
    def options(self) -> list[str]:
        """Return list of all the available temperature scales."""

        return list(TEMPERATURE_SCALES.values())

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        ha_to_flair = TEMP_SCALE_TO_FLAIR.get(option)
        attributes = self.set_attributes(ha_to_flair)
        await self.coordinator.client.update('structures', self.structure_data.id, attributes=attributes, relationships={})
        self.puck_data.attributes['temperature-scale'] = ha_to_flair
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    @staticmethod
    def set_attributes(option: str) -> dict[str, str]:
        """Creates attributes dictionary."""

        attributes = {
            "temperature-scale": option
        }
        return attributes
