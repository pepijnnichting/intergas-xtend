# Intergas Xtend Integration for Home Assistant

This integration connects your Intergas Xtend enabled heating system to Home Assistant, allowing you to monitor your system's status and readings.

## Features

- Monitor room temperature
- Check boiler temperature
- See tap water temperature
- Monitor water pressure
- Check heating status
- Monitor flame status
- View tap water status

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
4. Enter your Intergas Xtend portal username and password

## Credits

This integration is based on the work by [DSchoutsen](https://github.com/DSchoutsen/HA_connection_Xtend).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
