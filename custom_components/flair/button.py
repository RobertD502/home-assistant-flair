"""Button platform for Flair integration."""
from __future__ import annotations

from typing import Any

from flairaio.model import Room, Structure

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FlairDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up Flair Button Entities."""

    coordinator: FlairDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    buttons = []

    for structure_id, structure_data in coordinator.data.structures.items():
            # Structures
            buttons.extend((
                HomeAwayClearHold(coordinator, structure_id),
                HomeAwayRevert(coordinator, structure_id),
            ))

            # Rooms
            if structure_data.rooms:
                for room_id, room_data in structure_data.rooms.items():
                    buttons.extend((
                        RoomClearHold(coordinator, structure_id, room_id),
                    ))

    async_add_entities(buttons)


class HomeAwayClearHold(CoordinatorEntity, ButtonEntity):
    """Representation of clearing home/away hold."""

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

        return str(self.structure_data.id) + '_home_away_clear_hold'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Clear home/away hold"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

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

    async def async_press(self) -> None:
        """Handle the button press."""

        attributes = {
            "hold-until": None
        }

        await self.coordinator.client.update('structures', self.structure_data.id, attributes, relationships={})
        self.structure_data.attributes['hold-until'] = None
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class HomeAwayRevert(CoordinatorEntity, ButtonEntity):
    """Representation of clearing home/away hold and reverting to previous state."""

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

        return str(self.structure_data.id) + '_home_away_reverse'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Reverse home/away hold"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

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

    async def async_press(self) -> None:
        """Handle the button press."""

        home_attributes, hold_attributes = self.set_attributes()
        await self.coordinator.client.update('structures', self.structure_data.id, home_attributes, relationships={})
        await self.coordinator.client.update('structures', self.structure_data.id, hold_attributes, relationships={})
        self.structure_data.attributes['home'] = home_attributes['home']
        self.structure_data.attributes['hold-until'] = None
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    def set_attributes(self) -> tuple[dict[str, bool], dict[str, None]]:
        """Creates attributes dictionary."""

        is_home = self.structure_data.attributes['home']
        if is_home:
            setting = False
        else:
            setting = True

        home_attributes = {
            "home": setting
        }

        hold_attributes = {
            "hold-until": None
        }

        return home_attributes, hold_attributes


class RoomClearHold(CoordinatorEntity, ButtonEntity):
    """Representation of clearing room temperature hold."""

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

        return str(self.room_data.id) + '_clear_hold'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Clear hold"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

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

    async def async_press(self) -> None:
        """Handle the button press."""

        attributes = {
            "hold-until": None,
            "hold-until-schedule-event": False
        }

        await self.coordinator.client.update('rooms', self.room_data.id, attributes, relationships={})
        self.room_data.attributes['hold-until'] = None
        self.room_data.attributes['hold-until-schedule-event'] = False
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()
