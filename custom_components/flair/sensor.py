"""Sensor platform for Flair integration."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from flairaio.model import Bridge, Puck, Room, Structure, Vent

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import(
    LIGHT_LUX,
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfElectricPotential,
    UnitOfPressure,
    UnitOfTemperature,

)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, TYPE_TO_MODEL
from .coordinator import FlairDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up Flair Sensor Entities."""

    coordinator: FlairDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = []

    for structure_id, structure_data in coordinator.data.structures.items():
            # Structures
            sensors.extend((
                HomeAwayHoldUntil(coordinator, structure_id),
            ))

            # Pucks
            if structure_data.pucks:
                for puck_id, puck_data in structure_data.pucks.items():
                    sensors.extend((
                        PuckTemp(coordinator, structure_id, puck_id),
                        PuckHumidity(coordinator, structure_id, puck_id),
                        PuckLight(coordinator, structure_id, puck_id),
                        PuckVoltage(coordinator, structure_id, puck_id),
                        PuckRSSI(coordinator, structure_id, puck_id),
                        PuckPressure(coordinator, structure_id, puck_id),
                        Gateway(coordinator, structure_id, puck_id, 'pucks')
                    ))
            # Vents
            if structure_data.vents:
                for vent_id, vent_data in structure_data.vents.items():
                    sensors.extend((
                        DuctTemp(coordinator, structure_id, vent_id),
                        DuctPressure(coordinator, structure_id, vent_id),
                        VentVoltage(coordinator, structure_id, vent_id),
                        VentRSSI(coordinator, structure_id, vent_id),
                        VentReportedState(coordinator, structure_id, vent_id),
                        Gateway(coordinator, structure_id, vent_id, 'vents')
                    ))
            # Rooms
            if structure_data.rooms:
                for room_id, room_data in structure_data.rooms.items():
                    sensors.extend((
                        HoldTempUntil(coordinator, structure_id, room_id),
                    ))

            # HVAC Units with only button controls
            if structure_data.hvac_units:
                for hvac_id, hvac_data in structure_data.hvac_units.items():
                    constraints = structure_data.hvac_units[hvac_id].attributes['constraints']
                    if isinstance(constraints, list):
                        sensors.append(LastButtonPressed(coordinator, structure_id, hvac_id))

            # Bridges
            if structure_data.bridges:
                for bridge_id, bridge_data in structure_data.bridges.items():
                    sensors.append(BridgeRSSI(coordinator, structure_id, bridge_id))

    async_add_entities(sensors)


class HomeAwayHoldUntil(CoordinatorEntity, SensorEntity):
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

        return str(self.structure_data.id) + '_home_away_hold_until'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Home/Away holding until"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> datetime:
        """Date/time when hold will end.

        When home/away is set manually, returns date/time when hold will end.
        Only applicable if structure default hold duration is anything other
        than 'until next scheduled event'
        """

        if self.structure_data.attributes['hold-until']:
            return datetime.fromisoformat(self.structure_data.attributes['hold-until'])

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.TIMESTAMP

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
        """Determine whether entity is available. 

        Return true if home/away is set manually and structure
        has a default hold duration other than next event.
        """

        if self.structure_data.attributes['hold-until']:
            return True
        else:
            return False


class PuckTemp(CoordinatorEntity, SensorEntity):
    """Representation of Puck Temperature."""

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

        return str(self.puck_data.id) + '_temperature'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Temperature"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> float:
        """Return current temperature in Celsius."""

        return self.puck_data.attributes['current-temperature-c']

    @property
    def native_unit_of_measurement(self) -> UnitOfTemperature:
        """Return Celsius as the native unit."""

        return UnitOfTemperature.CELSIUS

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.TEMPERATURE

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def available(self) -> bool:
        """Return true if device is available."""

        if not self.puck_data.attributes['inactive']:
            return True
        else:
            return False


class PuckHumidity(CoordinatorEntity, SensorEntity):
    """Representation of Puck Humidity."""

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

        return str(self.puck_data.id) + '_humidity'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Humidity"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> float:
        """Return current humidity."""

        return self.puck_data.attributes['current-humidity']

    @property
    def native_unit_of_measurement(self) -> str:
        """Return percent as the native unit."""

        return PERCENTAGE

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.HUMIDITY

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def available(self) -> bool:
        """Return true if device is available."""

        if not self.puck_data.attributes['inactive']:
            return True
        else:
            return False


class PuckLight(CoordinatorEntity, SensorEntity):
    """Representation of Puck Light."""

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

        return str(self.puck_data.id) + '_light'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Light"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> float:
        """Return current lux level. 

        Convert value to Volts then multiply by 200
        for 200 lux per Volt.
        """

        return (self.puck_data.current_reading['light'] / 100) * 200

    @property
    def native_unit_of_measurement(self) -> str:
        """Return lux as the native unit."""

        return LIGHT_LUX

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.ILLUMINANCE

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def available(self) -> bool:
        """Return true if device is available."""

        if (self.puck_data.attributes['inactive'] == False) and \
                (self.puck_data.current_reading['light'] is not None):
            return True
        else:
            return False


class PuckVoltage(CoordinatorEntity, SensorEntity):
    """Representation of Puck Voltage."""

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

        return str(self.puck_data.id) + '_voltage'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Voltage"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> float:
        """Return voltage measurement."""

        return self.puck_data.attributes['voltage']

    @property
    def native_unit_of_measurement(self) -> UnitOfElectricPotential:
        """Return volts as the native unit."""

        return UnitOfElectricPotential.VOLT

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.VOLTAGE

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        """Return true if device is available."""

        if not self.puck_data.attributes['inactive']:
            return True
        else:
            return False


class PuckRSSI(CoordinatorEntity, SensorEntity):
    """Representation of Puck RSSI."""

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

        return str(self.puck_data.id) + '_rssi'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "RSSI"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> float:
        """Return RSSI reading."""

        return self.puck_data.attributes['current-rssi']

    @property
    def native_unit_of_measurement(self) -> str:
        """Return dBm as the native unit."""

        return SIGNAL_STRENGTH_DECIBELS_MILLIWATT

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.SIGNAL_STRENGTH

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        """Return true if device is available."""

        if not self.puck_data.attributes['inactive']:
            return True
        else:
            return False


class PuckPressure(CoordinatorEntity, SensorEntity):
    """Representation of Puck pressure reading."""

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

        return str(self.puck_data.id) + '_pressure'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Pressure"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> float:
        """Return pressure reading."""

        return round(self.puck_data.current_reading['room-pressure'], 2)

    @property
    def native_unit_of_measurement(self) -> UnitOfPressure:
        """Return kPa as the native unit."""

        return UnitOfPressure.KPA

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.PRESSURE

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def available(self) -> bool:
        """Return true if device is available."""

        if not self.puck_data.attributes['inactive']:
            return True
        else:
            return False


class DuctTemp(CoordinatorEntity, SensorEntity):
    """Representation of Duct Temperature."""

    def __init__(self, coordinator, structure_id, vent_id):
        super().__init__(coordinator)
        self.vent_id = vent_id
        self.structure_id = structure_id

    @property
    def vent_data(self) -> Vent:
        """Handle coordinator vent data."""

        return self.coordinator.data.structures[self.structure_id].vents[self.vent_id]

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

        return str(self.vent_data.id) + '_duct_temperature'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Duct temperature"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> float:
        """Return current temperature in Celsius."""

        return self.vent_data.current_reading['duct-temperature-c']

    @property
    def native_unit_of_measurement(self) -> UnitOfTemperature:
        """Return Celsius as the native unit."""

        return UnitOfTemperature.CELSIUS

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.TEMPERATURE

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def available(self) -> bool:
        """Return true if device is available."""

        if not self.vent_data.attributes['inactive']:
            return True
        else:
            return False


class DuctPressure(CoordinatorEntity, SensorEntity):
    """Representation of Duct Pressure."""

    def __init__(self, coordinator, structure_id, vent_id):
        super().__init__(coordinator)
        self.vent_id = vent_id
        self.structure_id = structure_id

    @property
    def vent_data(self) -> Vent:
        """Handle coordinator vent data."""

        return self.coordinator.data.structures[self.structure_id].vents[self.vent_id]

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

        return str(self.vent_data.id) + '_duct_pressure'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Duct pressure"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> float:
        """Return current pressure in kPa."""

        return round(self.vent_data.current_reading['duct-pressure'], 2)

    @property
    def native_unit_of_measurement(self) -> UnitOfPressure:
        """Return kPa as the native unit."""

        return UnitOfPressure.KPA

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.PRESSURE

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def available(self) -> bool:
        """Return true if device is available."""

        if not self.vent_data.attributes['inactive']:
            return True
        else:
            return False


class VentVoltage(CoordinatorEntity, SensorEntity):
    """Representation of Vent Voltage."""

    def __init__(self, coordinator, structure_id, vent_id):
        super().__init__(coordinator)
        self.vent_id = vent_id
        self.structure_id = structure_id


    @property
    def vent_data(self) -> Vent:
        """Handle coordinator vent data."""

        return self.coordinator.data.structures[self.structure_id].vents[self.vent_id]

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

        return str(self.vent_data.id) + '_voltage'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Voltage"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> float:
        """Return voltage measurement."""

        return self.vent_data.attributes['voltage']

    @property
    def native_unit_of_measurement(self) -> UnitOfElectricPotential:
        """Return volts as the native unit."""

        return UnitOfElectricPotential.VOLT

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.VOLTAGE

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        """Return true if device is available."""

        if not self.vent_data.attributes['inactive']:
            return True
        else:
            return False


class VentRSSI(CoordinatorEntity, SensorEntity):
    """Representation of Vent RSSI."""

    def __init__(self, coordinator, structure_id, vent_id):
        super().__init__(coordinator)
        self.vent_id = vent_id
        self.structure_id = structure_id

    @property
    def vent_data(self) -> Vent:
        """Handle coordinator vent data."""

        return self.coordinator.data.structures[self.structure_id].vents[self.vent_id]

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

        return str(self.vent_data.id) + '_rssi'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "RSSI"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return RSSI reading."""

        return self.vent_data.attributes['current-rssi']

    @property
    def native_unit_of_measurement(self) -> str:
        """Return dBm as the native unit."""

        return SIGNAL_STRENGTH_DECIBELS_MILLIWATT

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.SIGNAL_STRENGTH

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        """Return true if device is available."""

        if not self.vent_data.attributes['inactive']:
            return True
        else:
            return False


class VentReportedState(CoordinatorEntity, SensorEntity):
    """Representation of Vent RSSI."""

    def __init__(self, coordinator, structure_id, vent_id):
        super().__init__(coordinator)
        self.vent_id = vent_id
        self.structure_id = structure_id

    @property
    def vent_data(self) -> Vent:
        """Handle coordinator vent data."""

        return self.coordinator.data.structures[self.structure_id].vents[self.vent_id]

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

        return str(self.vent_data.id) + '_reported_state'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Reported state"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return the most recent percent open reading as returned by sensors on vent."""

        return self.vent_data.current_reading['percent-open']

    @property
    def native_unit_of_measurement(self) -> str:
        """Return % as the native unit."""

        return PERCENTAGE

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Disable entity on initial registration."""

        return False

    @property
    def available(self) -> bool:
        """Return true if device is available."""

        if not self.vent_data.attributes['inactive']:
            return True
        else:
            return False


class HoldTempUntil(CoordinatorEntity, SensorEntity):
    """Representation of Room Temperature Hold End Time."""

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

        return str(self.room_data.id) + '_hold_until'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Temperature holding until"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> datetime:
        """Date/time when hold will end.

        When room temperature is set manually,
        returns date/time when hold will end.
        """

        if self.room_data.attributes['hold-until']:
            return datetime.fromisoformat(self.room_data.attributes['hold-until'])

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.TIMESTAMP

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
        """Determine if device is available.

        Return true if temp is set manually
        and structure has a default hold duration
        other than next event.
        """

        if self.room_data.attributes['hold-until']:
            return True
        else:
            return False


class LastButtonPressed(CoordinatorEntity, SensorEntity):
    """Representation of last button pressed on HVAC unit with only button control."""

    def __init__(self, coordinator, structure_id, hvac_id):
        super().__init__(coordinator)
        self.hvac_id = hvac_id
        self.structure_id = structure_id

    @property
    def hvac_data(self) -> HVACUnit:
        """Handle coordinator HVAC unit data."""

        return self.coordinator.data.structures[self.structure_id].hvac_units[self.hvac_id]

    @property
    def structure_data(self) -> Structure:
        """Handle coordinator structure data."""

        return self.coordinator.data.structures[self.structure_id]

    @property
    def puck_data(self) -> Puck:
        """Handle coordinator puck data."""

        puck_id = self.hvac_data.relationships['puck']['data']['id']
        return self.coordinator.data.structures[self.structure_id].pucks[puck_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.hvac_data.id)},
            "name": self.hvac_data.attributes['name'],
            "manufacturer": self.hvac_data.attributes['make-name'],
            "model": "HVAC Unit",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.hvac_data.id) + '_last_button_pressed'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Last button pressed"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def icon(self) -> str:
        """Set hvac icon."""

        return 'mdi:hvac'

    @property
    def native_value(self) -> float:
        """Return last button pressed."""

        last_pressed = self.hvac_data.attributes['button-presses']
        if last_pressed:
            return last_pressed[0].capitalize()
        else:
            return "No button pressed"

    @property
    def available(self) -> bool:
        """Return true if associated puck is available."""

        if not self.puck_data.attributes['inactive']:
            return True
        else:
            return False


class BridgeRSSI(CoordinatorEntity, SensorEntity):
    """Representation of Bridge RSSI."""

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

        return str(self.bridge_data.id) + '_rssi'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "RSSI"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> float:
        """Return RSSI reading."""

        return self.bridge_data.attributes['current-rssi']

    @property
    def native_unit_of_measurement(self) -> str:
        """Return dBm as the native unit."""

        return SIGNAL_STRENGTH_DECIBELS_MILLIWATT

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.SIGNAL_STRENGTH

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        """Return true if device is available."""

        if not self.bridge_data.attributes['inactive']:
            return True
        else:
            return False


class Gateway(CoordinatorEntity, SensorEntity):
    """Representation of device's associated gateway."""

    def __init__(self, coordinator, structure_id, device_id, device_type):
        super().__init__(coordinator)
        self.device_id = device_id
        self.device_type = device_type
        self.structure_id = structure_id

    @property
    def structure_data(self) -> Structure:
        """Handle coordinator structure data."""

        return self.coordinator.data.structures[self.structure_id]

    @property
    def device_data(self) -> Puck | Vent:
        """Handle coordinator device data."""

        if self.device_type == 'pucks':
            return self.structure_data.pucks[self.device_id]
        else:
            return self.structure_data.vents[self.device_id]

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

        return str(self.device_data.id) + '_gateway'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Associated gateway"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> str | None:
        """Return name of associated gateway."""

        return self.get_associated_gateway()

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        """Return true if device is available."""

        if not self.device_data.attributes['inactive']:
            return True
        else:
            return False

    def get_associated_gateway(self) -> str | None:
        """Determines the gateway device is using."""

        connected_gateway_id = self.device_data.attributes['connected-gateway-id']
        connected_gateway_type = self.device_data.attributes['connected-gateway-type']

        if connected_gateway_id:
            if connected_gateway_id == self.device_data.id:
                return 'Self'
            else:
                if connected_gateway_type == 'puck':
                    if gateway := self.structure_data.pucks.get(connected_gateway_id):
                        return gateway.attributes['name']
                    # If the gateway isn't found
                    else:
                        return None
                elif connected_gateway_type == 'bridge':
                    if gateway := self.structure_data.bridges.get(connected_gateway_id):
                        return gateway.attributes['name']
                    # If gateway isn't found
                    else:
                        return None
                else:
                    return None
        else:
            return None
        
