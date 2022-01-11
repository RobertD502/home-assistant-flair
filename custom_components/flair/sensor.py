"""Setting up Flair Puck and Vent Sensors"""

import logging
from homeassistant.helpers.entity import EntityCategory
from homeassistant.exceptions import PlatformNotReady
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import SensorEntity, STATE_CLASS_MEASUREMENT, SensorDeviceClass
from homeassistant.const import TEMP_CELSIUS, LIGHT_LUX, PERCENTAGE, ELECTRIC_POTENTIAL_VOLT, SIGNAL_STRENGTH_DECIBELS_MILLIWATT, PRESSURE_KPA


from .const import (
    DOMAIN
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Set up Flair Pucks."""
    flair = hass.data[DOMAIN]

    pucks = []
    vents = []

    try:
        for puck in flair.pucks():
            pucks.append(FlairPuck(puck))
            pucks.append(PuckLight(puck))
            pucks.append(PuckHumidity(puck))
            pucks.append(PuckVoltage(puck))
            pucks.append(PuckRSSI(puck))
    except Exception as e:
        _LOGGER.error("Failed to get Puck(s) from Flair servers")
        raise PlatformNotReady from e

    try:
        for vent in flair.vents():
            vents.append(FlairVentDuctTemp(vent))
            vents.append(FlairVentDuctPressure(vent))
            vents.append(FlairVentVoltage(vent))
            vents.append(FlairVentRSSI(vent))
    except Exception as e:
        _LOGGER.error("Failed to get vents from Flair servers")
        raise PlatformNotReady from e

    async_add_entities(pucks)
    async_add_entities(vents)

##########       PUCK SENSORS       ##########

class FlairPuck(SensorEntity):
    """Representation of a Flair Puck."""

    def __init__(self, puck):
        self._puck = puck

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            "identifiers": {(DOMAIN, self._puck.puck_id)},
            "name": self._puck.puck_name,
            "manufacturer": "Flair",
            "model": "Flair Puck",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self):
        """Return the ID of this Puck."""
        return self._puck.puck_id

    @property
    def name(self):
        """Return the name of the Puck if any."""
        return 'flair_puck_' + self._puck.puck_name + "Temperature"

    @property
    def native_value(self):
        """Returns Puck Temperature"""
        if self._puck.current_temp is None:
            return None
        return self._puck.current_temp

    @property
    def native_unit_of_measurement(self):
        return TEMP_CELSIUS

    @property
    def device_class(self) -> SensorDeviceClass:
        return SensorDeviceClass.TEMPERATURE

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

    @property
    def icon(self):
        """Set puck icon"""
        return 'mdi:circle-double'

    @property
    def available(self):
        """Return true if device is available."""
        if self._puck.is_active is None:
            return False
        return self._puck.is_active

    def update(self):
        """Update automation state."""
        _LOGGER.info("Refreshing device state")
        self._puck.refresh()

class PuckLight(SensorEntity):
    """Representation of a Flair Puck Light Sensor."""

    def __init__(self, puck):
        self._puck = puck

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            "identifiers": {(DOMAIN, self._puck.puck_id)},
            "name": self._puck.puck_name,
            "manufacturer": "Flair",
            "model": "Flair Puck",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self):
        """Return the ID of this Puck."""
        return self._puck.puck_id + '_light_sensor'

    @property
    def name(self):
        """Return the name of the Puck if any."""
        return 'flair_puck_' + self._puck.puck_name + 'Light Level'

    @property
    def native_value(self):
        """Returns Puck Light Level in lux"""
        """Convert value to Volts then multiply by 200 for 200 lux per Volt"""
        return ((self._puck.light_level / 100) * 200)) 

    @property
    def native_unit_of_measurement(self):
        return LIGHT_LUX

    @property
    def device_class(self) -> SensorDeviceClass:
        return SensorDeviceClass.ILLUMINANCE

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

    @property
    def available(self):
        """Return true if device is available."""
        if self._puck.is_active is None:
            return False
        elif self._puck.is_active == False:
            return False
        elif (self._puck.is_active and self._puck.light_level_available):
            return True
        else:
            return False

    def update(self):
        """Update automation state."""
        _LOGGER.info("Refreshing device state")
        self._puck.refresh()

class PuckHumidity(SensorEntity):
    """Representation of a Flair Puck Humidity Sensor."""

    def __init__(self, puck):
        self._puck = puck

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            "identifiers": {(DOMAIN, self._puck.puck_id)},
            "name": self._puck.puck_name,
            "manufacturer": "Flair",
            "model": "Flair Puck",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self):
        """Return the ID of this Puck."""
        return self._puck.puck_id + '_humidity_sensor'

    @property
    def name(self):
        """Return the name of the Puck if any."""
        return 'flair_puck_' + self._puck.puck_name + 'Humidity Sensor'

    @property
    def native_value(self):
        """Returns Puck Humidity Measurement"""
        if self._puck.current_humidity is None:
            return None
        return self._puck.current_humidity

    @property
    def native_unit_of_measurement(self):
        return PERCENTAGE

    @property
    def device_class(self) -> SensorDeviceClass:
        return SensorDeviceClass.HUMIDITY

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

    @property
    def available(self):
        """Return true if device is available."""
        if self._puck.is_active is None:
            return False
        return self._puck.is_active

    def update(self):
        """Update automation state."""
        _LOGGER.info("Refreshing device state")
        self._puck.refresh()

class PuckVoltage(SensorEntity):
    """Representation of a Flair Puck Humidity Sensor."""

    def __init__(self, puck):
        self._puck = puck

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            "identifiers": {(DOMAIN, self._puck.puck_id)},
            "name": self._puck.puck_name,
            "manufacturer": "Flair",
            "model": "Flair Puck",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self):
        """Return the ID of this Puck."""
        return self._puck.puck_id + '_voltage_sensor'

    @property
    def name(self):
        """Return the name of the Puck if any."""
        return 'flair_puck_' + self._puck.puck_name + 'Voltage'

    @property
    def native_value(self):
        """Returns Puck Voltage Measurement"""
        if self._puck.voltage is None:
            return None
        return self._puck.voltage

    @property
    def native_unit_of_measurement(self):
        return ELECTRIC_POTENTIAL_VOLT

    @property
    def device_class(self) -> SensorDeviceClass:
        return SensorDeviceClass.VOLTAGE

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC

    @property
    def available(self):
        """Return true if device is available."""
        if self._puck.is_active is None:
            return False
        return self._puck.is_active

    def update(self):
        """Update automation state."""
        _LOGGER.info("Refreshing device state")
        self._puck.refresh()

class PuckRSSI(SensorEntity):
    """Representation of a Flair Puck Humidity Sensor."""

    def __init__(self, puck):
        self._puck = puck

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            "identifiers": {(DOMAIN, self._puck.puck_id)},
            "name": self._puck.puck_name,
            "manufacturer": "Flair",
            "model": "Flair Puck",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def unique_id(self):
        """Return the ID of this Puck."""
        return self._puck.puck_id + '_rssi_sensor'

    @property
    def name(self):
        """Return the name of the Puck if any."""
        return 'flair_puck_' + self._puck.puck_name + 'RSSI'

    @property
    def native_value(self):
        """Returns Puck RSSI Measurement"""
        if self._puck.rssi is None:
            return None
        return self._puck.rssi

    @property
    def native_unit_of_measurement(self):
        return SIGNAL_STRENGTH_DECIBELS_MILLIWATT

    @property
    def device_class(self) -> SensorDeviceClass:
        return SensorDeviceClass.SIGNAL_STRENGTH

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC

    @property
    def available(self):
        """Return true if device is available."""
        if self._puck.is_active is None:
            return False
        return self._puck.is_active

    def update(self):
        """Update automation state."""
        _LOGGER.info("Refreshing device state")
        self._puck.refresh()

##########       VENT SENSORS       ##########

class FlairVentDuctTemp(SensorEntity):
    """Representation of a Flair Vent Duct Temp Sensor."""

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
        return self._vent.vent_id + "_duct_temp"

    @property
    def name(self):
        """Return the name of the Sensor"""
        return 'flair_vent_' + self._vent.vent_name + "Duct Temperature"

    @property
    def native_value(self):
        """Returns Duct Temperature"""
        if self._vent.duct_temp is None:
            return None
        return self._vent.duct_temp

    @property
    def native_unit_of_measurement(self):
        return TEMP_CELSIUS

    @property
    def device_class(self) -> SensorDeviceClass:
        return SensorDeviceClass.TEMPERATURE

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

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

class FlairVentDuctPressure(SensorEntity):
    """Representation of a Flair Vent Duct Pressure Sensor."""

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
        return self._vent.vent_id + "_duct_pressure"

    @property
    def name(self):
        """Return the name of the Sensor"""
        return 'flair_vent_' + self._vent.vent_name + "Duct Pressure"

    @property
    def native_value(self):
        """Returns Duct Pressure"""
        if self._vent.duct_pressure is None:
            return None
        return self._vent.duct_pressure

    @property
    def native_unit_of_measurement(self):
        return PRESSURE_KPA

    @property
    def device_class(self) -> SensorDeviceClass:
        return SensorDeviceClass.PRESSURE

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

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

class FlairVentVoltage(SensorEntity):
    """Representation of a Flair Vent Voltage Sensor."""

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
        return self._vent.vent_id + "_voltage"

    @property
    def name(self):
        """Return the name of the Sensor"""
        return 'flair_vent_' + self._vent.vent_name + "Voltage"

    @property
    def native_value(self):
        """Returns Vent Voltage"""
        if self._vent.voltage is None:
            return None
        return self._vent.voltage

    @property
    def native_unit_of_measurement(self):
        return ELECTRIC_POTENTIAL_VOLT

    @property
    def device_class(self) -> SensorDeviceClass:
        return SensorDeviceClass.VOLTAGE

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC

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

class FlairVentRSSI(SensorEntity):
    """Representation of a Flair Vent RSSI Sensor."""

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
        return self._vent.vent_id + "_rssi_sensor"

    @property
    def name(self):
        """Return the name of the Sensor"""
        return 'flair_vent_' + self._vent.vent_name + "RSSI"

    @property
    def native_value(self):
        """Returns Vent Voltage"""
        if self._vent.rssi is None:
            return None
        return self._vent.rssi

    @property
    def native_unit_of_measurement(self):
        return SIGNAL_STRENGTH_DECIBELS_MILLIWATT

    @property
    def device_class(self) -> SensorDeviceClass:
        return SensorDeviceClass.SIGNAL_STRENGTH

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC

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
