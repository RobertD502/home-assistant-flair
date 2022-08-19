# Flair Home Assistant Integration
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs) ![GitHub manifest version (path)](https://img.shields.io/github/manifest-json/v/RobertD502/home-assistant-flair?filename=custom_components%2Fflair%2Fmanifest.json)

<a href="https://www.buymeacoffee.com/RobertD502" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="100" width="424"></a>

### A lot of work has been put into creating the backend and this integration. If you enjoy this integration, consider donating by clicking on the logo above.

***All proceeds go towards helping a local animal rescue.**

___

Custom Home Assistant component for controlling and monitoring Flair structures, pucks, vents, rooms, and IR HVAC units.

## **Prior To Installation**

**Starting with version `0.1.0` and above**: You will need credentials consisting of **OAuth 2.0** `client_id` and `client_secret`.

If you don't already have these, please [contact Flair Support](https://support.flair.co/hc/en-us/requests/new) with the email address associated with your registered Flair account.

# Installation

## With HACS
1. Within HACS, add this repository (https://github.com/RobertD502/home-assistant-flair)
as a Custom Repository (use **Integration** as the category).
2. The `Flair` page should automatically load (or find it in the HACS Store)
3. Click `Install`

## Manual
Copy the `flair` directory, from `custom_components` in this repository,
and place it inside your Home Assistant Core installation's `custom_components` directory.

## Setup
1. Install this integration.
2. Navigate to the Home Assistant Integrations page (Settings --> Devices & Services)
3. Click the `+ ADD INTEGRATION` button in the lower right-hand corner
4. Search for `Flair`

# Devices

Each Flair mini-split, puck, room, structure, and vent is represented as a device in Home Assistant. Within each device
are several entities described below.


## Structure

Each structure has the following entities:

| Entity                 | Entity Type | Additional Comments                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|------------------------| --- |-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Active Schedule`      | `Select` | Schedules are only available if the Flair System Mode is set to "Auto". All schedules created within the Flair app will appear here. To turn off a schedule, select "No Schedule".                                                                                                                                                                                                                                                                                                              |
| `Clear home/away hold` | `Button` | If you have a hold duration other than "Until next scheduled event", setting the home/away mode manually will result in your setting being held for the defined period of time. Pressing this button will remove the hold. `Note:` Pressing this button will only remove the time period hold, but will keep the home/away mode set to whatever you switched it to. In order to remove the hold and revert back to the original home/away mode, please use the "Reverse home/away hold" button. |
| `Home/Away mode`       | `Select` | Please read Flair's documentation regarding [Home/Away Mode](https://support.flair.co/hc/en-us/articles/360044922952-Home-Away-Mode)                                                                                                                                                                                                                                                                                                                                                            |
| `Lock IR device modes` | `Switch` | Turning this on will keep heat/cool mode of all IR devices in your Home in sync. It is recommended for Mini-Split systems that share a common outdoor unit, also known as multi-zone systems. `This entity will only be available if you have any IR devices associated with your account.`                                                                                                                                                                                                     |
| `Reverse home/away hold` | `Button` | Pressing this button removes the current hold for home/away mode and reverts the mode back. For example: If you set your home to away mode, pressing this button sets the mode back to home.                                                                                                                                                                                                                                                                                                    |
| `Structure Mode`       | `Select` | Please read Flair's documentation regarding [Structure mode](https://support.flair.co/hc/en-us/articles/360058466931-Mode)                                                                                                                                                                                                                                                                                                                                                                      |
| `System Mode`          | `Select` | Please read Flair's documentation regarding [Auto mode](https://support.flair.co/hc/en-us/articles/360042659392-System-Auto) and [Manual mode](https://support.flair.co/hc/en-us/articles/360043099291-System-Manual)                                                                                                                                                                                                                                                                           |
| `Home/Away holding until` | `Sensor` | If you have your default hold set to anything other than "Until next scheduled event", whenever setting home/away mode manually, this entity will show how much time if left until the hold ends. `Note:` This entity will only become available if there is home/away hold that is currently active.                                                                                                                                                                                           |
| `Away Mode`  | `Select` | Please read Flair's documentation regarding [Away Settings](https://support.flair.co/hc/en-us/articles/360041109111-Away-Settings)                                                                                                                                                                                                                                                                                                                                                              |
| `Away temperature maximum` | `Number` | Set your max away temperature. `Note:` This entity is only available when your set point controller is set to "Flair App".                                                                                                                                                                                                                                                                                                                                                                      |
| `Away temperature minimum` | `Number` | Set your minimum away temperature. `Note:` This entity is only available when your set point controller is set to "Flair App".                                                                                                                                                                                                                                                                                                                                                                  |
| `Default hold duration` | `Select` | Select your default hold duration.                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `Home set point` | `Number` | Set the set point for your home. `Note:` This entity is only available when your set point controller is set to "Flair App".                                                                                                                                                                                                                                                                                                                                                                    |
| `Home/Away mode set by` | `Select` | Available options inclue App Geolocation, Manual, or (if you have a thermostat linked to Flair) Thermostat.                                                                                                                                                                                                                                                                                                                                                                                     |
| `Set point controller` | `Select` | Select what is being used to set the set point for your home. Options include Flair App and Thermostat (only if you have a thermostat linked to Flair).                                                                                                                                                                                                                                                                                                                                         |


## Puck

Each puck has the following entities:

| Entity               | Entity Type | Additional Comments |
|----------------------|-------------| --- |
| `Lock puck`          | `Switch`    | Locking a puck will prevent someone from rotating the puck to adjust the set point. |
| `Humidity`           | `Sensor`    | |
| `Light`              | `Sensor`    | |
| `Pressure` |  `Sensor`   | Room pressure reported by the puck. |
| `Temperature`        | `Sensor`    | |
| `Background color` | `Select` | Set the puck's background color to either black or white. |
| `Set point lower limit` | `Number` | |
| `Set point upper limit` | `Number` | |
| `Temperature calibration` | `Number` | |
| `Temperature scale` | `Select` | |
| `RSSI`               | `Sensor`    | |
| `Voltage`            | `Sensor`    | Displays the current voltage of the puck. If using batteries to power your puck, this can be used to monitor battery health. |

**Note About Pucks**

Flair statement regarding Puck Light Level sensor:

>  It is not calibrated. The sensor itself, if the nominal reference is 1, can range from 0.3 to 1.6. This also doesn't take into account the mechanical loss in the Puck. In short, this is not an accurate lux sensor.


## Vent

<p align="center">
  <img width="533" height="1000" src="https://github.com/RobertD502/home-assistant-flair/blob/main/images/flair_system_setting_smaller.png?raw=true">
</p>

In order to control vents that are in Flair Rooms that have a temperature sensor, the System setting in the Flair app needs to be set to `Manual` (see image above). If you have it set to `Auto`, you will still be able to control your vents, however, eventually Flair will override your changes. This mode can also be set using a Flair Structure's `System Mode select entity` within Home Assistant.

**Any vents in Flair Rooms that don't report temperature can be controlled regardless of current mode set.**

Each Vent has the following entities:

| Entity | Entity Type | Additional Comments |
| --- | --- | --- |
| `Vent` | `Cover` | Has a state of either `open` or `closed`. If your vent is either `50` or `100` percent open, the state will be `open`. If your vent is `0` percent open, the state will be `closed`. You can manually open the vent halfway (50 percent) by either changing the tilt position to `50` via the UI or by using the service `cover.set_cover_tilt_position` and setting `tilt position` to `50`. Note: Although you can move the slider to any value between 0-100, any tilt position other than `0` or `100` will be interpreted as `50` - this is a Flair vent limitation as it doesn't support any other position aside from 0, 50, or 100. |
| `Duct Pressure` | `Sensor` | |
| `Duct Temperature` | `Sensor` | |
| `RSSI` | `Sensor` | |
| `Voltage` | `Sensor` | Displays the current voltage of the vent. If using batteries to power your vent, this can be used to monitor battery health. |

## Room

Each Room has the following entities:

| Entity                      | Entity Type | Additional Comments                                                                                                                                                                                                                                                               |
|-----------------------------| --- |-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Activity Status`           | `Select` | Rooms can be set to Active or Inactive.                                                                                                                                                                                                                                           |
| `Clear hold`                | `Button` | Clears the current temperature set point change hold time and reverts back to the original set point.                                                                                                                                                                             |
| `Room`                      | `Climate` | Temperature set points can be changed on a room by room basis. Changing HVAC mode for a room propagates that change to all rooms as the HVAC mode is set at the Structure level.                                                                                                  |
| `Temperature holding until` | `Sensor` | If you have the default hold duration set to anything other than "Until next scheduled event", this entity will show you how much time is left until the manual temperature hold expires. `Note:` This entity is only available if there is a currently active hold for the room. |

**Additional Notes**

Changing the temperature for a room climate entity will change the set temperature of the corresponding room. This change will remain for `until next scheduled event`, `3h`, `8h`, `24h`, or `forever`- this depends on the setting in the Flair app under Home Settings > System Settings > Default Hold Duration. This can also be changed using the "Default hold duration" entity in Home Assistant.


## IR HVAC Unit

Each IR HVAC unit has the following entities:

| Entity      | Entity Type | Additional Comments |
|-------------| --- |---------------------|
| `HVAC unit` | `Climate` | SEE NOTE BELOW      |

> To fully control your unit, the associated Flair structure needs to be in `Manual Mode`.
> 
> If your structure is set to `Auto Mode`: you will only be able to control `Fan speed` and `Swing` (if available for your unit). In addition, mini split set points are controlled by rooms if a Flair structure is set to `Auto Mode`. Changing the temperature of this climate entity will result in changing the room set point when in `Auto Mode`. You also cannot change the mode as this is controlled at the Structure level when in auto mode.
> 
> If your structure is set to `Manual Mode`: You can only change the temp, mode, fan speed, and swing when your unit is powered on. If your structure is in manual mode, you can turn your mini split on/off by changing the `Preset` setting to either "On" or "Off".
