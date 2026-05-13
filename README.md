# Intergas Xtend Integration for Home Assistant

This integration connects directly to your Intergas Xtend hybrid heat pump over Wi-Fi, allowing you to monitor your heating system from Home Assistant.

## Features

- Room, outdoor, heating supply/return, and hot water temperatures
- Water pressure and flow rate
- Heat pump and boiler power (kW) and COP
- Cumulative energy totals for heating and hot water (kWh) — integrates with the Energy Dashboard
- System status and heat pump mode (human-readable)
- Boiler modulation percentage
- Flame, pump, heating, and hot water binary sensors
- Error and notification codes (decoded to plain text)
- Software version and heating hours (diagnostic)

## Requirements

- An Intergas Xtend hybrid heat pump
- A Home Assistant server with both an **Ethernet** port (for your home network) and a **Wi-Fi** adapter (to connect to the Xtend)

## How it works

The Xtend does not connect to your home network. Instead, it acts as its own Wi-Fi access point. Your Home Assistant server uses its Wi-Fi adapter to connect directly to the Xtend network, while staying on your home network and internet via Ethernet.

## Network setup

> **Before you begin:** Make sure your Home Assistant server is connected to your home network via **Ethernet**. The Wi-Fi adapter will be dedicated to the Xtend — without Ethernet, Home Assistant will lose internet access.

1. **Activate the Xtend access point** — press the button on the Xtend unit until the LED blinks purple.
2. **Connect Home Assistant to the Xtend Wi-Fi:**
   - Go to **Settings → System → Network** in Home Assistant
   - Select your Wi-Fi adapter
   - Click **Scan for access points** and select the network named **Xtend_xxxxxxxxxx**
   - Choose **WPA-PSK** and enter the password (printed on the Xtend unit)
   - Save — the IP range `10.20.30.0/24` must not overlap with your home LAN
3. The Xtend is always reachable at **10.20.30.1** on this network.

## Installation

### HACS (recommended)

1. Ensure you have [HACS](https://hacs.xyz/) installed
2. Go to HACS > Integrations
3. Add this repository as a custom repository
4. Search for "Intergas Xtend" and install it
5. Restart Home Assistant

### Manual

1. Copy the `custom_components/intergas_xtend` directory into your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings → Integrations**
2. Click **+ Add Integration** and search for "Intergas Xtend"
3. Follow the on-screen instructions — the config flow will walk you through the Wi-Fi setup if you haven't done it yet
4. The default IP (`10.20.30.1`) and port (`80`) are correct for all Xtend units

## Usage

After setup you'll have access to the following entities:

- **Sensors:** temperatures, pressure, flow rate, power, energy totals, COP, status, modulation
- **Binary sensors:** flame, heating active, hot water active, pump running
- **Climate entity:** displays current and target temperature and heating/idle state (read-only — control your setpoint via your room thermostat integration)

All sensors use standard Home Assistant device classes, so energy sensors appear in the Energy Dashboard automatically.

## Credits

Based on the work by [DSchoutsen](https://github.com/DSchoutsen/HA_connection_Xtend).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
