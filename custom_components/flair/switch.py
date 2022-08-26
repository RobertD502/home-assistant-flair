""" Switch platform for Flair integration. """
from __future__ import annotations

from typing import Any


from flairaio.model import Puck, Structure
from homeassistant.components.switch import SwitchEntity

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FlairDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """ Set Up Flair Switch Entities. """

    coordinator: FlairDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    switches = []


    for structure_id, structure_data in coordinator.data.structures.items():
            """ Structures """
            switches.extend((
                LockIR(coordinator, structure_id),
            ))
            
            """ Pucks """
            if structure_data.pucks:
                for puck_id, puck_data in structure_data.pucks.items():
                    switches.extend((
                        PuckLock(coordinator, structure_id, puck_id),
                    ))

            """ HVAC Units """
            if structure_data.hvac_units:
                for hvac_id, hvac_data in structure_data.hvac_units.items():
                    try:
                        structure_data.hvac_units[hvac_id].attributes['constraints']['temperature-scale']
                    except KeyError:
                        unit_name = structure_data.hvac_units[hvac_id].attributes['name']
                        LOGGER.error(f'''Flair HVAC Unit {unit_name} does not have a temperature scale.
                                     Contact Flair customer support to get this fixed.''')
                        continue
                    switches.extend((
                        HVACPower(coordinator, structure_id, hvac_id),
                    ))

    async_add_entities(switches)


class LockIR(CoordinatorEntity, SwitchEntity):
    """ Representation of Structure HVAC IR lock. """

    def __init__(self, coordinator, structure_id):
        super().__init__(coordinator)
        self.structure_id = structure_id


    @property
    def structure_data(self) -> Structure:
        """ Handle coordinator structure data. """

        return self.coordinator.data.structures[self.structure_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """ Return device registry information for this entity. """

        return {
            "identifiers": {(DOMAIN, self.structure_data.id)},
            "name": self.structure_data.attributes['name'],
            "manufacturer": "Flair",
            "model": "Structure",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self) -> str:
        """ Sets unique ID for this entity. """

        return str(self.structure_data.id) + '_IR_lock'

    @property
    def name(self) -> str:
        """ Return name of the entity. """

        return "Lock IR device modes"

    @property
    def has_entity_name(self) -> bool:
        """ Indicate that entity has name defined. """

        return True

    @property
    def icon(self) -> str:
        """ Set icon. """

        ir_locked = self.structure_data.attributes['hvac-unit-group-lock']
        if ir_locked:
            return 'mdi:lock'
        else:
            return 'mdi:lock-open-variant'

    @property
    def is_on(self) -> bool:
        """ Return true if IR is locked. """

        return self.structure_data.attributes['hvac-unit-group-lock']

    @property
    def available(self) -> str:
        """ Return true if account has HVAC units. """

        if self.structure_data.hvac_units:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs):
        """ Lock the IR devices. """

        attributes = {"hvac-unit-group-lock": True}
        await self.coordinator.client.update('structures', self.structure_data.id, attributes=attributes, relationships={})
        self.structure_data.attributes['hvac-unit-group-lock'] == True
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """ Unlock the IR devices. """

        attributes = {"hvac-unit-group-lock": False}
        await self.coordinator.client.update('structures', self.structure_data.id, attributes=attributes, relationships={})
        self.structure_data.attributes['hvac-unit-group-lock'] == False
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class PuckLock(CoordinatorEntity, SwitchEntity):
    """ Representation of puck lock switch. """

    def __init__(self, coordinator, structure_id, puck_id):
        super().__init__(coordinator)
        self.puck_id = puck_id
        self.structure_id = structure_id


    @property
    def puck_data(self) -> Puck:
        """ Handle coordinator puck data. """

        return self.coordinator.data.structures[self.structure_id].pucks[self.puck_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """ Return device registry information for this entity. """

        return {
            "identifiers": {(DOMAIN, self.puck_data.id)},
            "name": self.puck_data.attributes['name'],
            "manufacturer": "Flair",
            "model": "Puck",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self) -> str:
        """ Sets unique ID for this entity. """

        return str(self.puck_data.id) + '_puck_lock'

    @property
    def name(self) -> str:
        """ Return name of the entity. """

        return "Lock puck"

    @property
    def has_entity_name(self) -> bool:
        """ Indicate that entity has name defined. """

        return True

    @property
    def icon(self) -> str:
        """ Set icon. """

        puck_locked = self.puck_data.attributes['locked']
        if puck_locked:
            return 'mdi:lock'
        else:
            return 'mdi:lock-open-variant'

    @property
    def is_on(self) -> bool:
        """ Return if puck is locked. """

        return self.puck_data.attributes['locked']

    @property
    def available(self) -> str:
        """ Return true if puck is active and
        puck lock setting isn't None within the Flair app.
        """

        puck_inactive = self.puck_data.attributes['inactive']
        puck_locked = self.puck_data.attributes['locked']
        if (puck_inactive == False) and (puck_locked is not None):
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs):
        """ Lock the puck. """

        attributes = {"locked": True}
        await self.coordinator.client.update('pucks', self.puck_data.id, attributes=attributes, relationships={})
        self.puck_data.attributes['locked'] == True
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """ Unlock the puck. """

        attributes = {"locked": False}
        await self.coordinator.client.update('pucks', self.puck_data.id, attributes=attributes, relationships={})
        self.puck_data.attributes['locked'] == False
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

class HVACPower(CoordinatorEntity, SwitchEntity):
    """ Representation of HVAC Unit Power. """

    def __init__(self, coordinator, structure_id, hvac_id):
        super().__init__(coordinator)
        self.hvac_id = hvac_id
        self.structure_id = structure_id


    @property
    def hvac_data(self) -> HVACUnit:
        """ Handle coordinator HVAC unit data. """

        return self.coordinator.data.structures[self.structure_id].hvac_units[self.hvac_id]

    @property
    def structure_data(self) -> Structure:
        """ Handle coordinator structure data. """

        return self.coordinator.data.structures[self.structure_id]

    @property
    def puck_data(self) -> Puck:
        """ Handle coordinator puck data. """

        puck_id = self.hvac_data.relationships['puck']['data']['id']

        return self.coordinator.data.structures[self.structure_id].pucks[puck_id]

    @property
    def structure_mode(self) -> str:
        """ Return structure mode of associated structure. """

        return self.structure_data.attributes['mode']

    @property
    def device_info(self) -> dict[str, Any]:
        """ Return device registry information for this entity. """

        return {
            "identifiers": {(DOMAIN, self.hvac_data.id)},
            "name": self.hvac_data.attributes['name'],
            "manufacturer": self.hvac_data.attributes['make-name'],
            "model": "HVAC Unit",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self) -> str:
        """ Sets unique ID for this entity. """

        return str(self.hvac_data.id) + '_hvac_power'

    @property
    def name(self) -> str:
        """ Return name of the entity. """

        return "HVAC power"

    @property
    def has_entity_name(self) -> bool:
        """ Indicate that entity has name defined. """

        return True

    @property
    def icon(self) -> str:
        """ Set hvac icon. """

        return 'mdi:hvac'

    @property
    def is_on(self) -> bool:
        """ Return if HVAC unit is on. """

        return self.hvac_data.attributes['power'] == 'On'

    @property
    def available(self) -> str:
        """ Return true if puck is active and
        structure is set to manual mode.
        """

        puck_inactive = self.puck_data.attributes['inactive']
        if (puck_inactive == False) and (self.structure_mode == 'manual'):
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs):
        """ Turn on HVAC unit. """

        attributes = {"power": "On"}
        await self.coordinator.client.update('hvac-units', self.hvac_data.id, attributes=attributes, relationships={})
        self.hvac_data.attributes['power'] == 'On'
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """ Turn off HVAC unit. """

        attributes = {"power": "Off"}
        await self.coordinator.client.update('hvac-units', self.hvac_data.id, attributes=attributes, relationships={})
        self.hvac_data.attributes['power'] == 'Off'
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()
