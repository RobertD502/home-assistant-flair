"""Binary Sensor platform for Flair integration."""
from __future__ import annotations

from typing import Any

from datetime import datetime, timedelta
from flairaio.model import Bridge, Puck, Vent

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOGGER, TYPE_TO_MODEL
from .coordinator import FlairDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up Flair Binary Sensor Entities."""

    coordinator: FlairDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    binary_sensors = []

    for structure_id, structure_data in coordinator.data.structures.items():
            # Pucks
            if structure_data.pucks:
                for puck_id, puck_data in structure_data.pucks.items():
                    binary_sensors.append(Connectivity(coordinator, structure_id, puck_id, 'pucks'))
            # Vents
            if structure_data.vents:
                for vent_id, vent_data in structure_data.vents.items():
                    binary_sensors.append(Connectivity(coordinator, structure_id, vent_id, 'vents'))
            # Bridges
            if structure_data.bridges:
                for bridge_id, bridge_data in structure_data.bridges.items():
                    binary_sensors.append(Connectivity(coordinator, structure_id, bridge_id, 'bridges'))

    async_add_entities(binary_sensors)


class Connectivity(CoordinatorEntity, BinarySensorEntity):
    """Representation of Bridge, Puck, and Vent connection status."""

    def __init__(self, coordinator, structure_id, device_id, device_type):
        super().__init__(coordinator)
        self.device_id = device_id
        self.device_type = device_type
        self.structure_id = structure_id
        self.last_logged = None
        self.next_log = None

    @property
    def structure_data(self) -> Structure:
        """Handle coordinator structure data."""

        return self.coordinator.data.structures[self.structure_id]

    @property
    def device_data(self) -> Bridge | Puck | Vent:
        """Handle coordinator device data."""

        if self.device_type == 'pucks':
            return self.structure_data.pucks[self.device_id]
        elif self.device_type == 'vents':
            return self.structure_data.vents[self.device_id]
        else:
            return self.structure_data.bridges[self.device_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.device_data.id)},
            "name": self.device_data.attributes['name'],
            "manufacturer": "Flair",
            "model": TYPE_TO_MODEL[self.device_type],
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.device_data.id) + '_connectivity'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Connection status"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return entity device class."""

        return BinarySensorDeviceClass.CONNECTIVITY

    @property
    def is_on(self) -> bool:
        """Return True if device is online (connected to a gateway)."""

        if not self.device_data.attributes['inactive']:
            return True
        else:
            current_dt = datetime.now()
            if not self.last_logged:
                LOGGER.warning(
                    f'Flair {TYPE_TO_MODEL[self.device_type]}: {self.device_data.attributes["name"]} is reported to be offline.'
                )
                self.last_logged = current_dt
                self.next_log = current_dt + timedelta(seconds=300)
            else:
                # If 5 minutes has elapsed since the last log, log the device being offline.
                if (self.next_log - current_dt).total_seconds() <= 0:
                    LOGGER.warning(
                        f'Flair {TYPE_TO_MODEL[self.device_type]}: {self.device_data.attributes["name"]} is reported to be offline.'
                    )
                    self.last_logged = current_dt
                    self.next_log = current_dt + timedelta(seconds=300)
            return False
