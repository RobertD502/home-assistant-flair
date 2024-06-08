"""Number platform for Flair integration."""
from __future__ import annotations

from typing import Any

from flairaio.model import Bridge, Puck, Structure

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfTemperature
from homeassistant.util.unit_system import METRIC_SYSTEM

from .const import DOMAIN
from .coordinator import FlairDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up Flair Number Entities."""

    coordinator: FlairDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    numbers = []

    for structure_id, structure_data in coordinator.data.structures.items():
            # Structures
            numbers.extend((
                TempAwayMin(coordinator, structure_id),
                TempAwayMax(coordinator, structure_id),
            ))

            # Pucks
            if structure_data.pucks:
                for puck_id, puck_data in structure_data.pucks.items():
                    numbers.extend((
                        PuckLowerLimit(coordinator, structure_id, puck_id),
                        PuckUpperLimit(coordinator, structure_id, puck_id),
                        TempCalibration(coordinator, structure_id, puck_id),
                    ))

            # Bridge
            if structure_data.bridges:
                for bridge_id, bridge_data in structure_data.bridges.items():
                    numbers.append(BridgeLED(coordinator, structure_id, bridge_id))

    async_add_entities(numbers)


class TempAwayMin(CoordinatorEntity, NumberEntity):
    """Representation of minimum away temperature."""

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

        return str(self.structure_data.id) + '_temp_away_min'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Away temperature minimum"

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

        return 'mdi:thermometer'

    @property
    def native_value(self) -> float:
        """Returns current set point. 

        Due to how Home Assistant handles rounding,
        we need to carry it out ourselves based on if
        Home Assistant is set to imperial or metric.
        """

        value = self.structure_data.attributes['temp-away-min-c']

        if self.hass.config.units is METRIC_SYSTEM:
            return value
        else:
            return round(((value * (9/5)) + 32), 0)

    @property
    def native_unit_of_measurement(self) -> UnitOfTemperature:
        """Return celsius or fahrenheit."""

        if self.hass.config.units is METRIC_SYSTEM:
            return UnitOfTemperature.CELSIUS
        else:
            return UnitOfTemperature.FAHRENHEIT

    @property
    def device_class(self) -> NumberDeviceClass:
        """Return temp device class."""

        return NumberDeviceClass.TEMPERATURE

    @property
    def mode(self) -> NumberMode:
        """Return slider mode."""

        return NumberMode.SLIDER

    @property
    def native_min_value(self) -> float:
        """Return minimum allowed set point in celsius."""

        if self.hass.config.units is METRIC_SYSTEM:
            return 10.0
        else:
            return 50.0

    @property
    def native_max_value(self) -> float:
        """Return maximum allowed min away temp in celsius.

        Always has to be 3 degrees celsius less than the
        maximum away temp setting.
        """

        away_max = self.structure_data.attributes['temp-away-max-c'] - 3

        if self.hass.config.units is METRIC_SYSTEM:
            return away_max
        else:
            return round(((away_max * (9/5)) + 32), 0)

    @property
    def native_step(self) -> float:
        """Return temp stepping by 1 celsius or fahrenheit."""

        return 1.0

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
        """Return true only if the set point controller
        is set to Flair App, away mode is set to Smart Away,
        and system mode is set to auto
        """

        set_point_mode = self.structure_data.attributes['set-point-mode']
        structure_away_mode = self.structure_data.attributes['structure-away-mode']
        system_mode = self.structure_data.attributes['mode'] 
        if (set_point_mode == 'Home Evenness For Active Rooms Flair Setpoint' and structure_away_mode == 'Smart Away') and \
                (system_mode == 'auto'):
            return True
        else:
            return False

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""

        if self.hass.config.units is METRIC_SYSTEM:
            temp = value
        else:
            temp = round(((value - 32) * (5/9)), 2)

        attributes = self.set_attributes(temp)
        await self.coordinator.client.update('structures', self.structure_data.id, attributes=attributes, relationships={})
        self.structure_data.attributes['temp-away-min-c'] = temp
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    @staticmethod
    def set_attributes(value: float) -> dict[str, float]:
        """Creates attributes dictionary."""

        attributes = {
            "temp-away-min-c": value
        }
        return attributes


class TempAwayMax(CoordinatorEntity, NumberEntity):
    """Representation of max away temperature."""

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

        return str(self.structure_data.id) + '_temp_away_max'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Away temperature maximum"

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

        return 'mdi:thermometer'

    @property
    def native_value(self) -> float:
        """Returns current set point. 

        Due to how Home Assistant handles rounding,
        we need to carry it out ourselves based on if
        Home Assistant is set to imperial or metric.
        """

        value = self.structure_data.attributes['temp-away-max-c']

        if self.hass.config.units is METRIC_SYSTEM:
            return value
        else:
            return round(((value * (9/5)) + 32), 0)

    @property
    def native_unit_of_measurement(self) -> UnitOfTemperature:
        """Return celsius or fahrenheit."""

        if self.hass.config.units is METRIC_SYSTEM:
            return UnitOfTemperature.CELSIUS
        else:
            return UnitOfTemperature.FAHRENHEIT

    @property
    def device_class(self) -> NumberDeviceClass:
        """Return temp device class."""

        return NumberDeviceClass.TEMPERATURE

    @property
    def mode(self) -> NumberMode:
        """Return slider mode."""

        return NumberMode.SLIDER

    @property
    def native_min_value(self) -> float:
        """Return minimum allowed max away temp in celsius.

        Always has to be 3 degrees celsius more than
        the min away temp setting.
        """

        away_min = self.structure_data.attributes['temp-away-min-c'] + 3

        if self.hass.config.units is METRIC_SYSTEM:
            return away_min
        else:
            return round(((away_min * (9/5)) + 32), 0)

    @property
    def native_max_value(self) -> float:
        """Return maximum allowed max away temp in celsius or fahrenheit."""

        if self.hass.config.units is METRIC_SYSTEM:
            return 32.2
        else:
            return 90.0

    @property
    def native_step(self) -> float:
        """Return temp stepping by 1 celsius or fahrenheit."""

        return 1.0

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
        """Return true only if the set point controller
        is set to Flair App, away mode is set to Smart Away,
        and system mode is set to auto
        """

        set_point_mode = self.structure_data.attributes['set-point-mode']
        structure_away_mode = self.structure_data.attributes['structure-away-mode']
        system_mode = self.structure_data.attributes['mode'] 
        if (set_point_mode == 'Home Evenness For Active Rooms Flair Setpoint' and structure_away_mode == 'Smart Away') and \
                (system_mode == 'auto'):
            return True
        else:
            return False

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""

        if self.hass.config.units is METRIC_SYSTEM:
            temp = value
        else:
            temp = round(((value - 32) * (5/9)), 2)
        attributes = self.set_attributes(temp)
        await self.coordinator.client.update('structures', self.structure_data.id, attributes=attributes, relationships={})
        self.structure_data.attributes['temp-away-max-c'] = temp
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    @staticmethod
    def set_attributes(value: float) -> dict[str, float]:
        """Creates attributes dictionary."""

        attributes = {
            "temp-away-max-c": value
        }
        return attributes


class PuckLowerLimit(CoordinatorEntity, NumberEntity):
    """Representation of puck set point lower limit."""

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

        return str(self.puck_data.id) + '_lower_limit'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Set point lower limit"

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

        return 'mdi:thermometer'

    @property
    def native_value(self) -> float:
        """Returns current lower limit. 

        Due to how Home Assistant handles rounding,
        we need to carry out rounding on our own depending
        on if HA is in metric or imperial.
        """

        value = self.puck_data.attributes['setpoint-bound-low']

        if self.hass.config.units is METRIC_SYSTEM:
            return value
        else:
            return round(((value * (9/5)) + 32), 0)

    @property
    def native_unit_of_measurement(self) -> UnitOfTemperature:
        """Return celsius or fahrenheit."""

        if self.hass.config.units is METRIC_SYSTEM:
            return UnitOfTemperature.CELSIUS
        else:
            return UnitOfTemperature.FAHRENHEIT

    @property
    def device_class(self) -> NumberDeviceClass:
        """Return temp device class."""

        return NumberDeviceClass.TEMPERATURE

    @property
    def mode(self) -> NumberMode:
        """Return slider mode."""

        return NumberMode.SLIDER

    @property
    def native_min_value(self) -> float:
        """Return minimum allowed lower limit."""

        if self.hass.config.units is METRIC_SYSTEM:
            return 10.0
        else:
            return 50.0

    @property
    def native_max_value(self) -> float:
        """Return maximum allowed lower limit.

        Can only go as high as the current upper limit.
        """

        upper_limit = self.puck_data.attributes['setpoint-bound-high']

        if self.hass.config.units is METRIC_SYSTEM:
            return upper_limit
        else:
            return round(((upper_limit * (9/5)) + 32), 0)

    @property
    def native_step(self) -> float:
        """Return temp stepping by 0.5 celsius or 1 fahrenheit."""

        if self.hass.config.units is METRIC_SYSTEM:
            return 0.5
        else:
            return 1.0

    @property
    def available(self) -> bool:
        """Return true if puck is active."""

        if not self.puck_data.attributes['inactive']:
            return True
        else:
            return False

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""

        if self.hass.config.units is METRIC_SYSTEM:
            temp = value
        else:
            temp = round(((value - 32) * (5/9)), 2)

        attributes = self.set_attributes(temp)
        await self.coordinator.client.update('pucks', self.puck_data.id, attributes=attributes, relationships={})
        self.puck_data.attributes['setpoint-bound-low'] = temp
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    @staticmethod
    def set_attributes(value: float) -> dict[str, float]:
        """Creates attributes dictionary."""

        attributes = {
            "setpoint-bound-low": value
        }
        return attributes


class PuckUpperLimit(CoordinatorEntity, NumberEntity):
    """Representation of puck set point upper limit."""

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

        return str(self.puck_data.id) + '_upper_limit'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Set point upper limit"

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

        return 'mdi:thermometer'

    @property
    def native_value(self) -> float:
        """Returns current upper limit. 

        Due to how Home Assistant handles rounding,
        we need to carry out rounding on our own depending
        on if HA is in metric or imperial.
        """

        value = self.puck_data.attributes['setpoint-bound-high']

        if self.hass.config.units is METRIC_SYSTEM:
            return value
        else:
            return round(((value * (9/5)) + 32), 0)

    @property
    def native_unit_of_measurement(self) -> UnitOfTemperature:
        """Return celsius or fahrenheit."""

        if self.hass.config.units is METRIC_SYSTEM:
            return UnitOfTemperature.CELSIUS
        else:
            return UnitOfTemperature.FAHRENHEIT

    @property
    def device_class(self) -> NumberDeviceClass:
        """Return temp device class."""

        return NumberDeviceClass.TEMPERATURE

    @property
    def mode(self) -> NumberMode:
        """Return slider mode."""

        return NumberMode.SLIDER

    @property
    def native_min_value(self) -> float:
        """Return minimum allowed upper limit.

        Can only be as low as the current lower limit.
        """

        lower_limit = self.puck_data.attributes['setpoint-bound-low']

        if self.hass.config.units is METRIC_SYSTEM:
            return lower_limit
        else:
            return round(((lower_limit * (9/5)) + 32), 0)

    @property
    def native_max_value(self) -> float:
        """Return maximum allowed upper limit."""

        if self.hass.config.units is METRIC_SYSTEM:
            return 32.23
        else:
            return 90.0

    @property
    def native_step(self) -> float:
        """Return temp stepping by 0.5 celsius or 1 fahrenheit."""

        if self.hass.config.units is METRIC_SYSTEM:
            return 0.5
        else:
            return 1.0

    @property
    def available(self) -> bool:
        """Return true if puck is active."""

        if not self.puck_data.attributes['inactive']:
            return True
        else:
            return False

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""

        if self.hass.config.units is METRIC_SYSTEM:
            temp = value
        else:
            temp = round(((value - 32) * (5/9)), 2)

        attributes = self.set_attributes(temp)
        await self.coordinator.client.update('pucks', self.puck_data.id, attributes=attributes, relationships={})
        self.puck_data.attributes['setpoint-bound-high'] = temp
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    @staticmethod
    def set_attributes(value: float) -> dict[str, float]:
        """Creates attributes dictionary."""

        attributes = {
            "setpoint-bound-high": value
        }
        return attributes


class TempCalibration(CoordinatorEntity, NumberEntity):
    """Representation of puck temperature calibration."""

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

        return str(self.puck_data.id) + '_temp_calibration'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Temperature calibration"

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

        return 'mdi:thermometer'

    @property
    def native_value(self) -> float:
        """Returns current temp calibration.

        Need to add 5C to the reading to get real temp in celsius.
        If HA is set to imperial, we need to subtract 32F from the
        conversion in order to replicate the Flair app UI.
        """

        temp_c = self.puck_data.attributes['temperature-offset-override-c'] + 5.0

        if self.hass.config.units is METRIC_SYSTEM:
            return temp_c
        else:
            return round((temp_c * (9/5)), 0)

    @property
    def native_unit_of_measurement(self) -> UnitOfTemperature:
        """Return celsius or fahrenheit depending on HA settings."""

        if self.hass.config.units is METRIC_SYSTEM:
            return UnitOfTemperature.CELSIUS
        else:
            return UnitOfTemperature.FAHRENHEIT

    @property
    def device_class(self) -> NumberDeviceClass:
        """Return temp device class."""

        return NumberDeviceClass.TEMPERATURE

    @property
    def mode(self) -> NumberMode:
        """Return slider mode."""

        return NumberMode.SLIDER

    @property
    def native_min_value(self) -> float:
        """Return minimum allowed temp calibration.

        If system is in Fahrenheit, we need the lower to be equal
        to -18F.
        """

        if self.hass.config.units is METRIC_SYSTEM:
            return -10.0
        else:
            return -18.0

    @property
    def native_max_value(self) -> float:
        """Return maximum allowed temp calibration.

        If the system is in Fahrenheit, we need the upper value to
        be equal to 9F.
        """

        if self.hass.config.units is METRIC_SYSTEM:
            return 5.0
        else:
            return 9.0

    @property
    def native_step(self) -> float:
        """Return temp stepping by 0.5C or 1F."""

        if self.hass.config.units is METRIC_SYSTEM:
            return 0.5
        else:
            return 1.0

    @property
    def available(self) -> bool:
        """Return true if puck is active and offset exists."""

        puck_inactive = self.puck_data.attributes['inactive']
        temp_offset = self.puck_data.attributes['temperature-offset-override-c']

        if (puck_inactive == False) and (temp_offset is not None):
            return True
        else:
            return False

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""

        if self.hass.config.units is METRIC_SYSTEM:
            # Need to subtract 5 celsius to get value
            # Flair servers expect.
            ha_to_flair = value - 5.0
        else:
            # Need to get 0F baseline and add the Flair server
            # correction of 5C. Then we subtract this value from our
            # HA value in celsius.
            zero_f_to_c = (-32 * (5/9)) + 5
            value_to_c =  ((value - 32) * (5/9))
            ha_to_flair = (value_to_c - zero_f_to_c)

        attributes = self.set_attributes(ha_to_flair)
        await self.coordinator.client.update('pucks', self.puck_data.id, attributes=attributes, relationships={})
        self.puck_data.attributes['temperature-offset-override-c'] = ha_to_flair
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    @staticmethod
    def set_attributes(value: float) -> dict[str, float]:
        """Creates attributes dictionary."""

        attributes = {
            "temperature-offset-override-c": value
        }
        return attributes


class BridgeLED(CoordinatorEntity, NumberEntity):
    """Representation of bridge LED brightness."""

    def __init__(self, coordinator, structure_id, bridge_id):
        super().__init__(coordinator)
        self.bridge_id = bridge_id
        self.structure_id = structure_id

    @property
    def bridge_data(self) -> Bridge:
        """Handle coordinator bridge data."""

        return self.coordinator.data.structures[self.structure_id].bridges[self.bridge_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.bridge_data.id)},
            "name": self.bridge_data.attributes['name'],
            "manufacturer": "Flair",
            "model": "Bridge",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.bridge_data.id) + '_led'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "LED brightness"

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

        return 'mdi:led-on'

    @property
    def native_value(self) -> int:
        """Returns current LED brightness."""

        return self.bridge_data.attributes['led-brightness']

    @property
    def mode(self) -> NumberMode:
        """Return slider mode."""

        return NumberMode.SLIDER

    @property
    def native_min_value(self) -> int:
        """Return minimum allowed brightness."""

        return 20

    @property
    def native_max_value(self) -> int:
        """Return max allowed brightness."""

        return 100

    @property
    def native_step(self) -> int:
        """Return whole number stepping."""

        return 1

    @property
    def available(self) -> bool:
        """Return true if device is available."""

        if not self.bridge_data.attributes['inactive']:
            return True
        else:
            return False

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""

        attributes = self.set_attributes(value)
        await self.coordinator.client.update('bridges', self.bridge_data.id, attributes=attributes, relationships={})
        self.bridge_data.attributes['led-brightness'] = value
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    @staticmethod
    def set_attributes(value: int) -> dict[str, int]:
        """Creates attributes dictionary."""

        attributes = {
            "led-brightness": value
        }
        return attributes
