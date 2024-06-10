# Flair Home Assistant Integration
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration) ![GitHub manifest version (path)](https://img.shields.io/github/manifest-json/v/RobertD502/home-assistant-flair?filename=custom_components%2Fflair%2Fmanifest.json)

<a href="https://www.buymeacoffee.com/RobertD502" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="100" width="424"></a>
<a href="https://liberapay.com/RobertD502/donate"><img alt="Donate using Liberapay" src="https://liberapay.com/assets/widgets/donate.svg" height="100" width="300"></a>

### A lot of work has been put into creating the backend and this integration. If you enjoy this integration, consider donating by clicking on one of the supported methods above.

***All proceeds go towards helping a local animal rescue.**

___

Custom Home Assistant component for controlling and monitoring Flair structures, bridges, pucks, vents, rooms, and IR HVAC units.

## **Prior To Installation**

**Starting with version `0.1.1` and above**: You will need credentials consisting of **OAuth 2.0** `client_id` and `client_secret`.

If you don't already have these, please [contact Flair Support](https://forms.gle/VohiQjWNv9CAP2ASA) with the email address associated with your registered Flair account.

# Installation

## With HACS

Click on the button below to automatically navigate to the repository within HACS:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=RobertD502&repository=home-assistant-flair&category=integration)

Alternatively, follow the steps below:

1. Click on the `Explore & Download Repositories` button and search for Flair.
2. On the Flair page, click on the `Download` button.

## Manual
Copy the `flair` directory, from `custom_components` in this repository,
and place it inside your Home Assistant Core installation's `custom_components` directory.

`Note`: If installing manually, in order to be alerted about new releases, you will need to subscribe to releases from this repository. 

## Setup

Click on the button below to add the integration:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=flair)

Alternatively, follow the steps below:

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
| `Active Schedule`      | `Select` | Schedules are only available if the Flair System Mode is set to "Auto". All schedules created within the Flair app will appear here. To turn off a schedule, select "No Schedule". `Note:` By default, this entity is disabled if Flair system mode is set to manual.                                                                                                                                                                                                                                                                                                              |
| `Clear home/away hold` | `Button` | If you have a hold duration other than "Until next scheduled event", setting the home/away mode manually will result in your setting being held for the defined period of time. Pressing this button will remove the hold. `Note:` Pressing this button will only remove the time period hold, but will keep the home/away mode set to whatever you switched it to. In order to remove the hold and revert back to the original home/away mode, please use the "Reverse home/away hold" button. `Note:` By default, this entity is disabled if Flair system mode is set to manual. `Note:` By default, this entity is disabled if Flair system mode is set to manual. |
| `Home/Away`       | `Select` | Please read Flair's documentation regarding [Home/Away Mode](https://support.flair.co/hc/en-us/articles/360044922952-Home-Away-Mode). `Note:` By default, this entity is disabled if Flair system mode is set to manual.                                                                                                                                                                                                                                                                                                                                                            |
| `Lock IR device modes` | `Switch` | Turning this on will keep heat/cool mode of all IR devices in your Home in sync. It is recommended for Mini-Split systems that share a common outdoor unit, also known as multi-zone systems. `This entity will only be available if you have any IR devices associated with your account.`                                                                                                                                                                                                     |
| `Network repair mode` | `Switch` | Turn this on to temporarily allow Sensor Pucks and Vents to connect to different gatways. `Network repair mode will turn itself off after 30 minutes, if not turned off by the user.`                                                                                                                                                                                                     |
| `Reverse home/away hold` | `Button` | Pressing this button removes the current hold for home/away mode and reverts the mode back. For example: If you set your home to away mode, pressing this button sets the mode back to home. `Note:` By default, this entity is disabled if Flair system mode is set to manual.                                                                                                                                                                                                                                                                                                 |
| `Structure`       | `Climate` | Entity to set Flair Structure mode and Structure Set point. `Target temperature is only available when Set point controller is set to Flair app`. Please read Flair's documentation regarding [Structure mode](https://support.flair.co/hc/en-us/articles/360058466931-Mode). `Note:` By default, this entity is disabled if Flair system mode is set to manual.                                                                                                                                                                                                                                                                                                                                                                     |
| `System Mode`          | `Select` | Please read Flair's documentation regarding [Auto mode](https://support.flair.co/hc/en-us/articles/360042659392-System-Auto) and [Manual mode](https://support.flair.co/hc/en-us/articles/360043099291-System-Manual)                                                                                                                                                                                                                                                                           |
| `Home/Away holding until` | `Sensor` | If you have your default hold set to anything other than "Until next scheduled event", whenever setting home/away mode manually, this entity will show how much time if left until the hold ends. `Note:` This entity will only become available if there is home/away hold that is currently active. `Note:` By default, this entity is disabled if Flair system mode is set to manual.                                                                                                                                                                                          |
| `Away Mode`  | `Select` | Please read Flair's documentation regarding [Away Settings](https://support.flair.co/hc/en-us/articles/360041109111-Away-Settings). `Note:` By default, this entity is disabled if Flair system mode is set to manual.                                                                                                                                                                                                                                                                                                                                                              |
| `Away temperature maximum` | `Number` | Set your max away temperature. `Note:` This entity is only available when your set point controller is set to "Flair App". By default, this entity is disabled if Flair system mode is set to manual.                                                                                                                                                                                                                                                                                                                                                                      |
| `Away temperature minimum` | `Number` | Set your minimum away temperature. `Note:` This entity is only available when your set point controller is set to "Flair App". By default, this entity is disabled if Flair system mode is set to manual.                                                                                                                                                                                                                                                                                                                                                                  |
| `Default hold duration` | `Select` | Select your default hold duration. `Note:` By default, this entity is disabled if Flair system mode is set to manual.                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `Home/Away mode set by` | `Select` | Available options inclue App Geolocation, Manual, or (if you have a thermostat linked to Flair) Thermostat. `Note:` By default, this entity is disabled if Flair system mode is set to manual.                                                                                                                                                                                                                                                                                                                                                                                     |
| `Set point controller` | `Select` | Select what is being used to set the set point for your home. Options include Flair App and Thermostat (only if you have a thermostat linked to Flair). `Note:` By default, this entity is disabled if Flair system mode is set to manual.                                                                                                                                                                                                                                                                                                                                         |

## Bridge

Each bridge has the following entities:

| Entity               | Entity Type | Additional Comments |
|----------------------|-------------| --- |
| `LED brightness`          | `Number`    | Brightness between 20-100. |
| `Connection status`          | `Binary Sensor`    | Used to show if the bridge is reported as being online by Flair. |
| `RSSI`               | `Sensor`    | If your bridge is connected via ethernet, this sensor will always report 0.0 |

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
| `Associated gateway`            | `Sensor`    | Displays the name of the gateway (as named in the Flair app) the puck is using. If the puck is a gateway itself, this sensor will read "Self". |
| `Connection status`          | `Binary Sensor`    | Used to show if the puck is reported as being online by Flair. |
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
| `Reported state` | `Sensor` | This entity is disabled by default. Value corresponds to the percent open of the vent as last reported by the sensor on the vent itself. Can be used in automations to determine if puck failed to open/close a vent by comparing if the state of this sensor is equal to the position of the related vent cover entity (for example checking 5 minutes after the current position of the vent cover entity changed). |
| `Associated gateway`            | `Sensor`    | Displays the name of the bridge or puck (as named in the Flair app) the vent is using as a gateway. |
| `Connection status`          | `Binary Sensor`    | Used to show if the vent is reported as being online by Flair. |
| `RSSI` | `Sensor` | |
| `Voltage` | `Sensor` | Displays the current voltage of the vent. If using batteries to power your vent, this can be used to monitor battery health. |

## Room

Each Room has the following entities:

| Entity                      | Entity Type | Additional Comments                                                                                                                                                                                                                                                               |
|-----------------------------| --- |-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Activity Status`           | `Select` | Rooms can be set to Active or Inactive. `Note:` By default, this entity is disabled if Flair system mode is set to manual.                                                                                                                                                                                                                                           |
| `Clear hold`                | `Button` | Clears the current temperature set point change hold time and reverts back to the original set point. `Note:` By default, this entity is disabled if Flair system mode is set to manual.                                                                                                                                                                             |
| `Room`                      | `Climate` | Temperature set points can be changed on a room by room basis. Changing HVAC mode for a room propagates that change to all rooms as the HVAC mode is set at the Structure level. `Note:` By default, this entity is disabled if Flair system mode is set to manual.                                                                                                  |
| `Temperature holding until` | `Sensor` | If you have the default hold duration set to anything other than "Until next scheduled event", this entity will show you how much time is left until the manual temperature hold expires. `Note:` This entity is only available if there is a currently active hold for the room. By default, this entity is disabled if Flair system mode is set to manual. |

**Additional Notes**

Changing the temperature for a room climate entity will change the set temperature of the corresponding room. This change will remain for `until next scheduled event`, `3h`, `8h`, `24h`, or `forever`- this depends on the setting in the Flair app under Home Settings > System Settings > Default Hold Duration. This can also be changed using the "Default hold duration" entity in Home Assistant.


## IR HVAC Unit

Each IR HVAC unit has the following entities:

| Entity      | Entity Type | Additional Comments |
|-------------| --- |---------------------|
| `HVAC unit` | `Climate` | SEE NOTE BELOW      |

> To fully control your unit, the associated Flair structure needs to be in `Manual Mode`.
> 
> If your structure is set to `Auto Mode`: you will only be able to control `Fan speed` and `Swing` (if available for your unit). In addition, mini split temperature set point is controlled by rooms if a Flair structure is set to `Auto Mode`. Changing the temperature of this climate entity will result in changing the room set point when in `Auto Mode`. You also cannot change the HVAC mode as this is controlled at the Structure level when in auto mode.
> 
> If your structure is set to `Manual Mode`: Setting the HVAC mode to `Off` will turn your HVAC unit off. In order to turn the unit on, set the HVAC mode to your desired HVAC mode (Heat, Cool, Fan Only, etc).

### If your HVAC unit only has standalone buttons in the Flair app:

For these HVAC units `button` entities are created depending on what control is available (Temp +, Temp -, Fan +, Fan -, etc).
In addition, a `Last button pressed` `sensor` entity is created showing the last command sent to the HVAC unit by Flair. By default, if the Flair API doesn't return a value for the last button pressed, the sensor will have a state of `No button pressed`.
