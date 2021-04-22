# Flair Home Assistant Integration
<a href="https://www.buymeacoffee.com/RobertD502" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs) ![GitHub manifest version (path)](https://img.shields.io/github/manifest-json/v/RobertD502/home-assistant-flair?filename=custom_components%2Fflair%2Fmanifest.json)

Custom component for Home Assistant Core for controlling Flair vents/rooms and monitoring pucks/vents/rooms. This integration DOES NOT control or pull in information about mini-splits.

Donations aren't required, but are always appreciated. If you enjoy this integration, consider buying me a coffee by clicking on the link above.

**Prior To Installation**

You will need credentials consisting of client_id and client_secret. If you don't already have these, for API access, please [contact Flair Support](https://support.flair.co/hc/en-us/requests/new) with the email address associated with your registered Flair account.

## Installation

### With HACS
1. Open HACS Settings and add this repository (https://github.com/RobertD502/home-assistant-flair)
as a Custom Repository (use **Integration** as the category).
2. The `Flair` page should automatically load (or find it in the HACS Store)
3. Click `Install`

### Manual
Copy the `flair` directory from `custom_components` in this repository,
and place inside your Home Assistant Core installation's `custom_components` directory.


## Setup
1. Install this integration.
2. Use Config Flow to configure the integration with your Flair API client_id and client_secret.
    * Initiate Config Flow by navigating to Configuration > Integrations > click the "+" button > find "Flair" (restart Home Assistant and / or clear browser cache if you can't find it)

## Features

### Puck
Pucks are exposed as `sensor` entities and have a `state` that displays `current temperature` obtained by the puck.

Available attributes:

| Attribute | Description |
| --- | --- |
| `humidity` | This is the current humidity as measured by your puck |
| `is_active` | If puck is active or not. Can be either `true` or `false` |
| `is_gateway` | If puck is set up to be a gateway. Can be either `true` or `false` |
| `voltage` | Displays the current voltage of the puck. If it is plugged in, this value will be constant (3.41 for me). If using batteries to power your puck, this can be used to monitor battery health. |
| `rssi` | Displays puck connection strength. |

### Vent
![alt text](https://github.com/RobertD502/home-assistant-flair/blob/main/images/flair_system_setting_smaller.png?raw=true)

In order to control vents, the System setting in the Flair app needs to be set to `Manual` (see image above). If you have it set to `Auto`, you will still be able to control your vents, however, eventually Flair will override your changes.

Vents are exposed as `fan` entities and have a `state` of either `on` or `off`. If your vent is either `50` or `100` percent open, the state will be `on`. If your vent is `0` percent open, the state will be `off`. Turning the vent fan entity `on` manually will fully open the vent (100 percent). Turning the vent fan entity `off` manually will completely close the vent (0 percent). You are also able to manually open the vent halfway (50 percent) by either changing the speed to `50` via the UI or by using the service `fan.set_percentage` and setting `percentage` to `50`- the same goes for fully open with `100` or fully closed with `0`.

Available attributes:

| Attribute | Description |
| --- | --- |
| `percent_open` | The amount of percent the vent is open. This can be `100`, `50`, or `0` |
| `voltage` | Displays the current voltage of the vent. If using batteries to power your vent, this can be used to monitor battery health. |
| `is_active` | If puck is active or not. Can be either `true` or `false`. Helpful in determining if a vent has gone offline as this will result in `false` being displayed for the `is_active` attribute |
| `rssi` | Connection strength of vent to puck |

### Room

Rooms are exposed as `climate` entities and have a `state` that displays the type of mode your house is in (`heat`, `cool`, `heat_cool`, or `off`). Note, you cannot change this state as it is a limitation of the official flair python API. Changing the temperature for a room climate entity will change the set temperature of the corresponding room. This change will remain for `until next scheduled event`, `3h`, `8h`, `24h`, or `forever`- this depends on the setting in the Flair app under Home Settings > System Settings > Default Hold Duration.

Available attributes:

| Attribute | Description |
| --- | --- |
| `is_active` | If room is active or not. Can be either `true` or `false`. |
