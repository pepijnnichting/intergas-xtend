# Intergas Xtend Integration for Home Assistant

This integration connects directly to your Intergas Xtend enabled heating system over Wi-Fi, allowing you to monitor and control your system from Home Assistant.

## Features

- Monitor room temperature
- Check boiler temperature
- See tap water temperature
- Monitor water pressure
- Check heating status
- Monitor flame status
- View tap water status
- Control temperature setpoint via Home Assistant

## Requirements

- An Intergas boiler with an Xtend controller
- The Xtend controller must be connected to your local network
- You need to know the IP address of the Xtend controller

## Installation

### HACS (recommended)

1. Ensure you have [HACS](https://hacs.xyz/) installed
2. Go to HACS > Integrations
3. Add this repository URL as a custom repository
4. Search for "Intergas Xtend" and install it
5. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/intergas_xtend` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Configuration > Integrations in Home Assistant
2. Click the "+ Add Integration" button
3. Search for "Intergas Xtend" and select it
4. Enter the IP address of your Intergas Xtend controller (typically 192.168.178.120)
5. The integration will automatically discover and set up all available entities

## Usage

After setup, you'll have access to the following entities:

- **Climate entity**: Control your heating setpoint
- **Sensors**: Monitor temperatures, pressure, and modulation percentage
- **Binary Sensors**: Check flame status, pump status, heating status, etc.

You can use these entities in automations, scripts, and dashboards like any other Home Assistant entity.

## Credits

This integration is based on the work by [DSchoutsen](https://github.com/DSchoutsen/HA_connection_Xtend).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
