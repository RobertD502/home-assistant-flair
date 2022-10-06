"""Cover platform for Flair integration."""
from __future__ import annotations

from typing import Any

from flairaio.model import Room, Structure, Vent

from homeassistant.components.cover import (
    ATTR_TILT_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOGGER
from .coordinator import FlairDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up Flair Cover Entities."""

    coordinator: FlairDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    covers = []

    for structure_id, structure_data in coordinator.data.structures.items():
            # Vents
            if structure_data.vents:
                for vent_id, vent_data in structure_data.vents.items():
                    covers.extend((
                        FlairVent(coordinator, structure_id, vent_id),
                    ))

    async_add_entities(covers)


class FlairVent(CoordinatorEntity, CoverEntity):
    """Representation of Vent device."""

    def __init__(self, coordinator, structure_id, vent_id):
        super().__init__(coordinator)
        self.vent_id = vent_id
        self.structure_id = structure_id

    @property
    def vent_data(self) -> Vent:
        """Handle coordinator vent data."""

        return self.coordinator.data.structures[self.structure_id].vents[self.vent_id]

    @property
    def structure_data(self) -> Structure:
        """Handle coordinator structure data."""

        return self.coordinator.data.structures[self.structure_id]

    @property
    def room_data(self) -> Room:
        """Handle coordinator room data."""

        room_id = self.vent_data.relationships['room']['data']['id']
        return self.coordinator.data.structures[self.structure_id].rooms[room_id]

    @property
    def manual_struct_room(self) -> bool:
        """Return true if structure or room is in manual mode."""

        if (self.structure_data.attributes['mode'] == 'manual') or \
           (self.room_data.attributes['current-temperature-c'] is None):
            return True
        else:
            return False

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.vent_data.id)},
            "name": self.vent_data.attributes['name'],
            "manufacturer": "Flair",
            "model": "Vent",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.vent_data.id) + '_vent'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Vent"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def device_class(self) -> CoverDeviceClass:
        """Return entity device class."""

        return CoverDeviceClass.DAMPER

    @property
    def icon(self) -> str:
        """Set vent icon."""

        return 'mdi:air-filter'

    @property
    def is_closed(self) -> bool:
        """Return true if vent percent open is zero."""

        if self.vent_data.attributes['percent-open'] == 0:
            return True
        else:
            return False

    @property
    def current_cover_tilt_position(self) -> int:
        """Return the current percent open."""

        return self.vent_data.attributes['percent-open']

    @property
    def supported_features(self) -> int:
        """Vent supported features."""

        return CoverEntityFeature.OPEN_TILT | CoverEntityFeature.CLOSE_TILT | CoverEntityFeature.SET_TILT_POSITION

    @property
    def available(self) -> bool:
        """Return true if device is available."""

        if not self.vent_data.attributes['inactive']:
            return True
        else:
            return False

    async def async_open_cover_tilt(self, **kwargs) -> None:
        """Open the vent."""

        attributes = self.set_attributes(100)
        await self.coordinator.client.update('vents', self.vent_data.id, attributes=attributes, relationships={})
        self.vent_data.attributes['percent-open'] = 100
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

        if not self.manual_struct_room:
            LOGGER.warning(f'''Flair structure or room not in manual mode.
                            Position changes to your Flair vent {self.vent_data.attributes["name"]}
                            will eventually be reversed by Flair.
                            '''
                          )

    async def async_close_cover_tilt(self, **kwargs) -> None:
        """Close the vent."""

        attributes = self.set_attributes(0)
        await self.coordinator.client.update('vents', self.vent_data.id, attributes=attributes, relationships={})
        self.vent_data.attributes['percent-open'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

        if not self.manual_struct_room:
            LOGGER.warning(f'''Flair structure or room not in manual mode.
                            Position changes to your Flair vent {self.vent_data.attributes["name"]}
                            will eventually be reversed by Flair.
                            '''
                          )

    async def async_set_cover_tilt_position(self, **kwargs) -> None:
        """Set vent percentage open."""

        tilt_position = kwargs.get(ATTR_TILT_POSITION)
        if tilt_position == 0:
            await self.async_close_cover_tilt()
        elif tilt_position == 100:
            await self.async_open_cover_tilt()
        else:
            attributes = self.set_attributes(50)
            await self.coordinator.client.update('vents', self.vent_data.id, attributes=attributes, relationships={})
            self.vent_data.attributes['percent-open'] = 50
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()

            if not self.manual_struct_room:
                LOGGER.warning(f'''Flair structure or room not in manual mode.
                                Position changes to your Flair vent {self.vent_data.attributes["name"]}
                                will eventually be reversed by Flair.
                                '''
                              )

    @staticmethod
    def set_attributes(percent: int) -> dict[str, Any]:
        """Creates attributes dict that is needed
        by the flairaio update method.
        """

        attributes = {
            "percent-open": percent,
        }
        return attributes
