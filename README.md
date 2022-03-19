# Flair Home Assistant Integration
<a href="https://www.buymeacoffee.com/RobertD502" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs) ![GitHub manifest version (path)](https://img.shields.io/github/manifest-json/v/RobertD502/home-assistant-flair?filename=custom_components%2Fflair%2Fmanifest.json)

Custom component for Home Assistant Core for controlling and monitoring Flair structures, pucks, vents, rooms, and mini split units.

**Donations aren't required, but are always appreciated. If you enjoy this integration, consider buying me a coffee by clicking on the logo above.**

## **Prior To Installation**

You will need credentials consisting of **OAuth1** `client_id` and `client_secret`. If you don't already have these, for API access, please [contact Flair Support](https://support.flair.co/hc/en-us/requests/new) with the email address associated with your registered Flair account.

## **IMPORTANT**
If you handle external access to Home Assistant yourself (i.e., You don't use NabuCasa), you need to access Home Assistant via the **LOCAL** URL when setting up this integration. 

# Table of Contents
* [Installation](#installation)
   * [With HACS](#with-hacs)
   * [Manual](#manual)
* [Setup](#setup)
* [Devices](#devices)
   * [Structure](#structure)
   * [Puck](#puck)
   * [Vent](#vent)
   * [Room](#room)
   * [Mini Split](#mini-split)

# Installation

## With HACS
1. Open HACS Settings and add this repository (https://github.com/RobertD502/home-assistant-flair)
as a Custom Repository (use **Integration** as the category).
2. The `Flair` page should automatically load (or find it in the HACS Store)
3. Click `Install`

## Manual
Copy the `flair` directory from `custom_components` in this repository,
and place inside your Home Assistant Core installation's `custom_components` directory.


# Setup
1. Use Config Flow to configure the integration with your Flair API client_id and client_secret.
    * Initiate Config Flow by navigating to Configuration > Integrations > click the "+" button > find "Flair" (restart Home Assistant and / or clear browser cache if you can't find it)

# Devices

Each Flair mini-split, puck, room, structure, and vent is represented as a device in Home Assistant. Within each device
are several entities described below.

## Structure

Each structure has the following entities:

| Entity | Entity Type | Additional Comments |
| --- | --- | --- |
| `Home/Away Mode` | `Select` | Please read  Flair's documentation regarding [Home/Away Mode](https://support.flair.co/hc/en-us/articles/360044922952-Home-Away-Mode) |
| `Schedules` | `Select` | Schedules and this entity are only available if the Flair System Mode is set to "Auto". All schedules created within the Flair app will appear here. To turn off a schedule, select "No Schedule" |
| `Structure Mode` | `Select` | Please read Flair's documentation regarding [Structure mode](https://support.flair.co/hc/en-us/articles/360058466931-Mode) |
| `System Mode` | `Select` | Please read Flair's documentation regarding [Auto mode](https://support.flair.co/hc/en-us/articles/360042659392-System-Auto) and [Manual mode](https://support.flair.co/hc/en-us/articles/360043099291-System-Manual) |


## Puck

Each puck has the following entities:

| Entity | Entity Type | Additional Comments |
| --- | --- | --- |
| `Humidity` | `Sensor` | |
| `Light Level` | `Sensor` | |
| `Temperature` | `Sensor` | |
| `RSSI` | `Sensor` | |
| `Voltage` | `Sensor` | Displays the current voltage of the puck. If using batteries to power your puck, this can be used to monitor battery health. |

**Note About Pucks**

Flair statement regarding Puck Light Level sensor:

>  It is not calibrated. The sensor itself, if the nominal reference is 1, can range from 0.3 to 1.6. This also doesn't take into account the mechanical loss in the Puck. In short, this is not an accurate lux sensor.


## Vent

<p align="center">
  <img width="533" height="1000" src="https://github.com/RobertD502/home-assistant-flair/blob/main/images/flair_system_setting_smaller.png?raw=true">
</p>

In order to control vents that are in Flair Rooms that have a temperature sensor, the System setting in the Flair app needs to be set to `Manual` (see image above). If you have it set to `Auto`, you will still be able to control your vents, however, eventually Flair will override your changes. This mode can also be set using a Flair Structure's `System Mode select entity` within Home Assistant. Any vents in Flair Rooms that don't report temperature can be controlled regardless of current mode set.

Each Vent has the following entities:

| Entity | Entity Type | Additional Comments |
| --- | --- | --- |
| `Vent` | `Fan` | Has a state of either `on` or `off`. If your vent is either `50` or `100` percent open, the state will be `on`. If your vent is `0` percent open, the state will be `off`. Turning the vent fan entity `on` manually will fully open the vent (100 percent). Turning the vent fan entity `off` manually will completely close the vent (0 percent). You are also able to manually open the vent halfway (50 percent) by either changing the speed to `50` via the UI or by using the service `fan.set_percentage` and setting `percentage` to `50`- the same goes for fully open with `100` or fully closed with `0`. |
| `Duct Pressure` | `Sensor` | |
| `Duct Temperature` | `Sensor` | |
| `RSSI` | `Sensor` | |
| `Voltage` | `Sensor` | Displays the current voltage of the vent. If using batteries to power your vent, this can be used to monitor battery health. |


## Room

Each Room has the following entities:

| Entity | Entity Type | Additional Comments |
| --- | --- | --- |
| `Activity Status` | `Select` | Rooms can be set to Active or Inactive. |
| `Room` | `Climate` | Temperature set points can be changed on a room by room basis. Changing HVAC mode on a room by room basis is not supported as room HVAC mode (for all rooms) is controlled by a Flair structure. Changing HVAC mode for all rooms can be done using a structure's `Structure Mode` entity. |
| `Duct Temperature` | `Sensor` | |
| `RSSI` | `Sensor` | |
| `Voltage` | `Sensor` | Displays the current voltage of the vent. If using batteries to power your vent, this can be used to monitor battery health. |

**Additional Notes**

Changing the temperature for a room climate entity will change the set temperature of the corresponding room. This change will remain for `until next scheduled event`, `3h`, `8h`, `24h`, or `forever`- this depends on the setting in the Flair app under Home Settings > System Settings > Default Hold Duration.


## Mini Split

Each Mini Split has the following entities:

| Entity | Entity Type | Additional Comments |
| --- | --- | --- |
| `Mini Split` | `Climate` | To fully control your mini split unit, the associated Flair structure needs to be in `Manual Mode`. If your structure is set to `Auto Mode` you will only be able to control `Fan speed` and `Swing` (if available for your unit). In addition, mini split set points are controlled by rooms if a Flair structure is set to `Auto Mode`. Changing the temperature of this climate entity will result in changing the room set point when in `Auto Mode`.  |
