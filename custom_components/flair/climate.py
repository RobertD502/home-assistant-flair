"""Climate platform for Flair integration."""
from __future__ import annotations

from typing import Any

from flairaio.model import HVACUnit, Puck, Room, Structure

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.components.climate.const import (
    FAN_AUTO,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    SWING_OFF,
    SWING_ON,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    HVAC_AVAILABLE_FAN_SPEEDS,
    HVAC_AVAILABLE_MODES_MAP,
    HVAC_CURRENT_ACTION,
    HVAC_CURRENT_FAN_SPEED,
    HVAC_CURRENT_MODE_MAP,
    HVAC_SWING_STATE,
    LOGGER,
    ROOM_HVAC_MAP,
)
from .coordinator import FlairDataUpdateCoordinator


ROOM_HVAC_MAP_TO_FLAIR = {v: k for (k, v) in ROOM_HVAC_MAP.items()}
HASS_HVAC_MODE_TO_FLAIR = {v: k for (k, v) in HVAC_CURRENT_MODE_MAP.items()}
HASS_HVAC_FAN_SPEED_TO_FLAIR = {v: k for (k, v) in HVAC_CURRENT_FAN_SPEED.items()}
HASS_HVAC_SWING_TO_FLAIR = {v: k for (k, v) in HVAC_SWING_STATE.items()}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up Flair Climate Entities."""

    coordinator: FlairDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    climates = []

    for structure_id, structure_data in coordinator.data.structures.items():
            # Structures
            climates.extend((
                StructureClimate(coordinator, structure_id),
            ))
            # Room
            if structure_data.rooms:
                for room_id, room_data in structure_data.rooms.items():
                    climates.extend((
                        RoomTemp(coordinator, structure_id, room_id),
                    ))

            # HVAC Units
            if structure_data.hvac_units:
                for hvac_id, hvac_data in structure_data.hvac_units.items():
                    try:
                        structure_data.hvac_units[hvac_id].attributes['constraints']['temperature-scale']
                    except KeyError:
                        unit_name = structure_data.hvac_units[hvac_id].attributes['name']
                        LOGGER.error(f'''Flair HVAC Unit {unit_name} does not have a temperature scale.
                                     Contact Flair customer support to get this fixed.''')
                        continue
                    climates.extend((
                        HVAC(coordinator, structure_id, hvac_id),
                    ))

    async_add_entities(climates)


class StructureClimate(CoordinatorEntity, ClimateEntity):
    """Representation of Structure Climate entity."""

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

        return str(self.structure_data.id) + '_climate'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Structure"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def temperature_unit(self) -> str:
        """Return celsius or fahrenheit."""

        if self.hass.config.units.is_metric:
            return TEMP_CELSIUS
        else:
            return TEMP_FAHRENHEIT

    @property
    def target_temperature(self) -> float:
        """Return the temperature currently set to be reached.

        Due to how Home Assistant handles rounding,
        we need to carry it out ourselves based on if
        Home Assistant is set to imperial or metric.
        """

        value = self.structure_data.attributes['set-point-temperature-c']

        if self.hass.config.units.is_metric:
            return value
        else:
            return round(((value * (9/5)) + 32), 0)

    @property
    def target_temperature_low(self) -> float:
        """Return minimum allowed set point in celsius or fahrenheit."""

        if self.hass.config.units.is_metric:
            return 10.0
        else:
            return 50.0

    @property
    def target_temperature_high(self) -> float:
        """Return maximum allowed set point in celsius or fahrenheit."""

        if self.hass.config.units.is_metric:
            return 32.23
        else:
            return 90.0

    @property
    def target_temperature_step(self) -> float:
        """Return temp stepping by 0.5 celsius or 1 fahrenheit."""

        if self.hass.config.units.is_metric:
            return 0.5
        else:
            return 1.0

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current hvac_mode."""

        mode = self.structure_data.attributes['structure-heat-cool-mode']
        if mode in ROOM_HVAC_MAP:
            hvac_mode = ROOM_HVAC_MAP[mode]
        return hvac_mode

    @property
    def hvac_modes(self) -> list:
        """Return supported modes."""

        supported_modes = [HVACMode.OFF, HVACMode.COOL, HVACMode.HEAT, HVACMode.HEAT_COOL]
        return supported_modes

    @property
    def supported_features(self) -> int:
        """Return supported features."""

        return ClimateEntityFeature.TARGET_TEMPERATURE

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

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""

        current_controller = self.structure_data.attributes['set-point-mode']
        if current_controller == "Home Evenness For Active Rooms Follow Third Party":
            LOGGER.error(f'Target temperature for Structure {self.structure_data.attributes["name"]} can only be set when the "Set point controller" is Flair app')
        else:
            if self.hass.config.units.is_metric:
                temp = kwargs.get(ATTR_TEMPERATURE)
            else:
                temp = round(((kwargs.get(ATTR_TEMPERATURE) - 32) * (5/9)), 2)

            attributes = self.set_attributes(temp, 'temperature')
            await self.coordinator.client.update('structures', self.structure_data.id, attributes=attributes, relationships={})
            self.structure_data.attributes['set-point-temperature-c'] = temp
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""

        flair_mode = ROOM_HVAC_MAP_TO_FLAIR.get(hvac_mode)
        attributes = self.set_attributes(flair_mode, 'hvac_mode')

        await self.coordinator.client.update('structures', self.structure_data.id, attributes=attributes, relationships={})
        self.structure_data.attributes['structure-heat-cool-mode'] = flair_mode
        self.async_write_ha_state()
        return await self.coordinator.async_request_refresh()

    @staticmethod
    def set_attributes(value: float | str, mode: str) -> dict[str, Any]:
        """Creates attribute dict that is needed
        by the flairaio update method.
        """

        if mode == 'temperature':
            attributes = {
                'set-point-temperature-c': value
            }
        else:
            attributes = {
                'structure-heat-cool-mode': value,
            }

        return attributes


class RoomTemp(CoordinatorEntity, ClimateEntity):
    """Representation of Flair Room Climate entity."""

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

        return str(self.room_data.id) + '_room'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Room"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def icon(self) -> str:
        """Set room icon."""

        return 'mdi:door-open'

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement."""

        return TEMP_CELSIUS

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current hvac_mode."""

        mode = self.structure_data.attributes['structure-heat-cool-mode']
        if mode in ROOM_HVAC_MAP:
            hvac_mode = ROOM_HVAC_MAP[mode]
        return hvac_mode

    @property
    def hvac_modes(self) -> list:
        """Return supported modes."""

        supported_modes = [HVACMode.OFF, HVACMode.COOL, HVACMode.HEAT, HVACMode.HEAT_COOL]
        return supported_modes

    @property
    def current_temperature(self) -> float:
        """Return the current temperature."""

        return self.room_data.attributes['current-temperature-c']

    @property
    def target_temperature(self) -> float:
        """Return the temperature currently set to be reached."""

        return self.room_data.attributes['set-point-c']

    @property
    def current_humidity(self) -> int:
        """Return the current humidity."""

        return self.room_data.attributes['current-humidity']

    @property
    def supported_features(self) -> int:
        """Return supported features."""

        return ClimateEntityFeature.TARGET_TEMPERATURE

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
        """Return true only if room has temp reading."""

        system_mode = self.structure_data.attributes['mode']
        if system_mode == 'manual':
            return False
        elif self.room_data.attributes['current-temperature-c'] is not None:
            return True
        else:
            return False

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""

        temp = kwargs.get(ATTR_TEMPERATURE)
        attributes = self.set_attributes(temp, 'temperature')

        if temp is not None:
            await self.coordinator.client.update('rooms', self.room_data.id, attributes=attributes, relationships={})
            self.room_data.attributes['set-point-c'] = temp
            self.async_write_ha_state()
            return await self.coordinator.async_request_refresh()
        else:
            LOGGER.error(f'Missing valid arguments for set_temperature in {kwargs}')

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""

        flair_mode = ROOM_HVAC_MAP_TO_FLAIR.get(hvac_mode)
        attributes = self.set_attributes(flair_mode, 'hvac_mode')

        await self.coordinator.client.update('structures', self.structure_data.id, attributes=attributes, relationships={})
        self.structure_data.attributes['structure-heat-cool-mode'] = flair_mode
        self.async_write_ha_state()
        return await self.coordinator.async_request_refresh()

    @staticmethod
    def set_attributes(value: float | str, mode: str) -> dict[str, Any]:
        """Creates attribute dict that is needed
        by the flairaio update method.
        """

        if mode == 'temperature':
            attributes = {
                'set-point-c': value,
                'active': True,
            }
        else:
            attributes = {
                'structure-heat-cool-mode': value,
            }

        return attributes


class HVAC(CoordinatorEntity, ClimateEntity):
    """Representation of Flair HVAC unit climate entity."""

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
    def room_data(self) -> Room:
        """Handle coordinator room data."""

        room_id = self.hvac_data.relationships['room']['data']['id']
        return self.coordinator.data.structures[self.structure_id].rooms[room_id]

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

        return str(self.hvac_data.id) + '_hvac_unit'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "HVAC unit"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def icon(self) -> str:
        """Set hvac icon."""

        return 'mdi:hvac'

    @property
    def temperature_unit(self) -> str:
        """Return temp scale unit of measurement."""

        if self.hvac_data.attributes['constraints']['temperature-scale'] == 'F':
            return TEMP_FAHRENHEIT
        else:
            return TEMP_CELSIUS

    @property
    def is_on(self) -> bool:
        """Return true if HVAC unit is on."""

        if self.hvac_data.attributes['power'] == 'On':
            return True
        else:
            return False

    @property
    def available_hvac_modes(self) -> list:
        """Return what modes are available for HVAC unit."""

        hvac_modes = []
        for key in self.hvac_data.attributes['constraints']['ON'].keys():
            hvac_modes.append(key)
        return hvac_modes

    @property
    def available_fan_speeds(self) -> list:
        """Returns available fan speeds based on current hvac mode."""

        mode = self.hvac_data.attributes['mode'].upper()
        fan_speeds = []

        if "ON" in self.hvac_data.attributes['constraints']['ON'][mode].keys():
            for key in self.hvac_data.attributes['constraints']['ON'][mode]['ON'].keys():
                fan_speeds.append(key)
            return fan_speeds
        else:
            for key in self.hvac_data.attributes['constraints']['ON'][mode]['OFF'].keys():
                fan_speeds.append(key)
            return fan_speeds

    @property
    def swing_available(self) -> bool:
        """Determine if swing mode is available."""

        if self.hvac_data.attributes['swing'] is not None:
            return True
        else:
            return False

    @property
    def structure_mode(self) -> str:
        """Return structure mode of associated structure."""

        return self.structure_data.attributes['mode']

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current hvac_mode."""

        mode = self.hvac_data.attributes['mode']

        if mode in HVAC_CURRENT_MODE_MAP:
            return HVAC_CURRENT_MODE_MAP[mode]

    @property
    def hvac_modes(self) -> list:
        """Return the Supported Modes. 

        Can't change modes when structure mode is manual & off
        or when in auto mode regardless of power state. So, we
        need to only return the last mode it was in.
        """

        current_mode = self.hvac_data.attributes['mode']

        if (self.structure_mode == 'manual') and (not self.is_on):
            supported_modes = []
            if current_mode in HVAC_CURRENT_MODE_MAP:
                supported_modes.append(HVAC_CURRENT_MODE_MAP[current_mode])
                return supported_modes
        elif self.structure_mode =='auto':
            supported_modes = []
            if current_mode in HVAC_CURRENT_MODE_MAP:
                supported_modes.append(HVAC_CURRENT_MODE_MAP[current_mode])
                return supported_modes
        else:
            modes = self.available_hvac_modes
            supported_modes = []
            for mode in modes:
                if mode in HVAC_AVAILABLE_MODES_MAP:
                    supported_modes.append(HVAC_AVAILABLE_MODES_MAP[mode])
            return supported_modes

    @property
    def hvac_action(self) -> HVACAction:
        """Return HVAC current action."""

        if self.is_on:
            if self.hvac_mode == HVACMode.HEAT_COOL:
                return None
            else:
                return HVAC_CURRENT_ACTION[self.hvac_mode]
        else:
            return HVACAction.OFF

    @property
    def fan_mode(self) -> str:
        """Return current fan speed."""

        fan_speed = self.hvac_data.attributes['fan-speed']

        if fan_speed is not None:
            if fan_speed in HVAC_CURRENT_FAN_SPEED:
                hvac_fan_speed = HVAC_CURRENT_FAN_SPEED[fan_speed]
                return hvac_fan_speed
        else:
            return None

    @property
    def fan_modes(self) -> list:
        """Return supported fan speeds."""

        supported_fan_speeds = []
        fan_speeds = self.available_fan_speeds

        for speed in fan_speeds:
            if speed in HVAC_AVAILABLE_FAN_SPEEDS:
                supported_fan_speeds.append(HVAC_AVAILABLE_FAN_SPEEDS[speed])
        return supported_fan_speeds

    @property
    def swing_mode(self) -> str:
        """Return current swing mode."""

        if 'swing' in self.hvac_data.attributes:
            swing_mode = self.hvac_data.attributes['swing']
            if swing_mode is not None:
                if swing_mode in HVAC_SWING_STATE:
                    hvac_swing_state = HVAC_SWING_STATE[swing_mode]
                    return hvac_swing_state
        else:
            return None

    @property
    def swing_modes(self) -> list:
        """Return supported swing modes."""

        swing_modes = [SWING_ON, SWING_OFF]
        return swing_modes

    @property
    def current_temperature(self) -> float:
        """Return the current temperature of the room HVAC unit is in."""

        temp = self.room_data.attributes['current-temperature-c']

        if self.hass.config.units.is_metric:
            return temp
        else:
            return round(((temp * (9/5)) + 32), 1)

    @property
    def target_temperature(self) -> float:
        """Return the temperature currently set to be reached by the HVAC unit."""

        return float(self.hvac_data.attributes['temperature'])

    @property
    def current_humidity(self) -> int:
        """Return the current humidity of room where HVAC unit is located."""

        return self.room_data.attributes['current-humidity']

    @property
    def supported_features(self) -> int:
        """HVAC unit supported features."""

        if self.swing_available and self.available_fan_speeds:
            # Determine if Flair structure is set to auto mode.
            if self.structure_mode == 'auto':
                if self.is_on:
                    # Only allow setting swing and fan if HVAC is in dry or fan only mode.
                    if self.hvac_mode in (HVACMode.DRY, HVACMode.FAN_ONLY):
                        return ClimateEntityFeature.SWING_MODE | ClimateEntityFeature.FAN_MODE
                    else:
                        return ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.SWING_MODE | ClimateEntityFeature.FAN_MODE
                else:
                    return ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.SWING_MODE | ClimateEntityFeature.FAN_MODE
            if self.structure_mode == 'manual':
                if self.is_on:
                    if self.hvac_mode in (HVACMode.DRY, HVACMode.FAN_ONLY):
                        return ClimateEntityFeature.SWING_MODE | ClimateEntityFeature.FAN_MODE
                    else:
                        return ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.SWING_MODE | ClimateEntityFeature.FAN_MODE
                else:
                    return ClimateEntityFeature.TARGET_TEMPERATURE

        # If only swing is available.
        if self.swing_available:
            if self.structure_mode == 'auto':
                if self.is_on:
                    if self.hvac_mode in (HVACMode.DRY, HVACMode.FAN_ONLY):
                        return ClimateEntityFeature.SWING_MODE
                    else:
                        return ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.SWING_MODE
            if self.structure_mode == 'manual':
                if self.is_on:
                    if self.hvac_mode in (HVACMode.DRY, HVACMode.FAN_ONLY):
                        return ClimateEntityFeature.SWING_MODE
                    else:
                        return ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.SWING_MODE
                else:
                    return ClimateEntityFeature.TARGET_TEMPERATURE

        # If only fan speeds are available.
        if self.available_fan_speeds:
            if self.structure_mode == 'auto':
                if self.is_on:
                    if self.hvac_mode in (HVACMode.DRY, HVACMode.FAN_ONLY):
                        return ClimateEntityFeature.FAN_MODE
                    else:
                        return ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE
            if self.structure_mode == 'manual':
                if self.is_on:
                    if self.hvac_mode in (HVACMode.DRY, HVACMode.FAN_ONLY):
                        return ClimateEntityFeature.FAN_MODE
                    else:
                        return ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE
                else:
                    return ClimateEntityFeature.TARGET_TEMPERATURE

    @property
    def available(self) -> bool:
        """Return true if associated puck is available."""

        if self.puck_data.attributes['inactive'] == False:
            return True
        else:
            return False

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""

        temp = kwargs.get(ATTR_TEMPERATURE)

        # Get room ID if in auto mode or HVAC ID if in manual mode.
        if self.structure_mode == 'auto':
            auto_mode = True
            type_id = self.room_data.id
            type = 'rooms'

            if not self.hass.config.units.is_metric:
                # Since we are setting the room temp when in auto structure mode, which is always in celsius,
                # we need to convert the temp to celsius if HA is not in celsius. However, the target temp is read
                # from the HVAC unit - the temp scale key from the HVAC constraints, used to set the temperature_unit
                # property, eliminates us from having to do this conversion when setting the HVAC 'temperature' attribute.
                converted = ((temp - 32) * (5/9))
                attributes = self.set_attributes('temp', converted, auto_mode)
                await self.coordinator.client.update(type, type_id, attributes=attributes, relationships={})
                self.hvac_data.attributes['temperature'] = temp
                self.async_write_ha_state()
                await self.coordinator.async_request_refresh()
            else:
                attributes = self.set_attributes('temp', temp, auto_mode)
                await self.coordinator.client.update(type, type_id, attributes=attributes, relationships={})
                self.hvac_data.attributes['temperature'] = temp
                self.async_write_ha_state()
                await self.coordinator.async_request_refresh()

        if self.structure_mode == 'manual':
            if not self.is_on:
                LOGGER.error(f'Temperature for {self.hvac_data.attributes["name"]} can only be set when it is powered on.')
            else:
                auto_mode = False
                type_id = self.hvac_data.id
                type = 'hvac-units'
                attributes = self.set_attributes('temp', temp, auto_mode)
                await self.coordinator.client.update(type, type_id, attributes=attributes, relationships={})
                self.hvac_data.attributes['temperature'] = temp
                self.async_write_ha_state()
                await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode. 

        Setting the targert temperature can only be done
        when structure state is manual and HVAC unit is on.
        """

        mode = HASS_HVAC_MODE_TO_FLAIR.get(hvac_mode)
        attributes = self.set_attributes('hvac_mode', mode, False)

        if hvac_mode == HVACMode.DRY:
            await self.async_set_fan_mode(FAN_AUTO)
        await self.coordinator.client.update('hvac-units', self.hvac_data.id, attributes=attributes, relationships={})
        self.hvac_data.attributes['mode'] = mode
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_set_fan_mode(self, fan_mode):
        """Set new target fan mode."""

        if self.structure_mode == "auto":
            mode = HASS_HVAC_FAN_SPEED_TO_FLAIR.get(fan_mode).upper()
            attributes = self.set_attributes('fan_mode', mode, True)
            await self.coordinator.client.update('hvac-units', self.hvac_data.id, attributes=attributes, relationships={})
            # Key for default-fan-speed uses all capital letters while fan-speed only capitalizes first letter.
            self.hvac_data.attributes['fan-speed'] = mode.title()
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()

        if self.structure_mode == 'manual':
            if self.hvac_mode == HVACMode.DRY:
                mode = HASS_HVAC_FAN_SPEED_TO_FLAIR.get(FAN_AUTO)
                attributes = self.set_attributes('fan_mode', mode, False)
                await self.coordinator.client.update('hvac-units', self.hvac_data.id, attributes=attributes, relationships={})
                self.hvac_data.attributes['fan-speed'] = mode
                self.async_write_ha_state()
                await self.coordinator.async_request_refresh()
            else:
                mode = HASS_HVAC_FAN_SPEED_TO_FLAIR.get(fan_mode)
                attributes = self.set_attributes('fan_mode', mode, False)
                await self.coordinator.client.update('hvac-units', self.hvac_data.id, attributes=attributes, relationships={})
                self.hvac_data.attributes['fan-speed'] = mode
                self.async_write_ha_state()
                await self.coordinator.async_request_refresh()

    async def async_set_swing_mode(self, swing_mode):
        """Set new target swing operation."""

        if self.structure_mode == "auto":
            # Auto mode takes True or False for swing mode.
            mode = HASS_HVAC_SWING_TO_FLAIR.get(swing_mode) == 'On'
            attributes = self.set_attributes('swing_mode', mode, True)
            await self.coordinator.client.update('hvac-units', self.hvac_data.id, attributes=attributes, relationships={})
            # 'swing-auto' key uses boolean while 'swing' uses On and Off.
            self.hvac_data.attributes['swing'] = HASS_HVAC_SWING_TO_FLAIR.get(swing_mode)
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()

        if self.structure_mode == 'manual':
            mode = HASS_HVAC_SWING_TO_FLAIR.get(swing_mode)
            attributes = self.set_attributes('swing_mode', mode, False)
            await self.coordinator.client.update('hvac-units', self.hvac_data.id, attributes=attributes, relationships={})
            self.hvac_data.attributes['swing'] = mode
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()

    @staticmethod
    def set_attributes(setting: str, value: Any, auto_mode: bool) -> dict[str, Any]:
        """Create attributes dictionary for client update method."""

        if auto_mode:
            if setting == 'temp':
                attributes = {
                    "set-point-c": value,
                    "active": True,
                }
            if setting == 'fan_mode':
                attributes = {
                    "default-fan-speed": value,
                }
            if setting == 'swing_mode':
                attributes ={
                    "swing-auto": value,
                }
        else:
            if setting == 'temp':
                attributes = {
                    "temperature": value,
                }
            if setting == 'hvac_mode':
                attributes = {
                    "mode": value,
                }
            if setting == 'fan_mode':
                attributes = {
                    "fan-speed": value,
                }
            if setting == 'swing_mode':
                attributes ={
                    "swing": value,
                }

        return attributes
