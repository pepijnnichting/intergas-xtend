<p align="center">
  <img src="https://raw.githubusercontent.com/pepijnnichting/intergas-xtend/main/custom_components/intergas_xtend/brand/icon.png" alt="Intergas Xtend" width="160" />
</p>

<h1 align="center">Intergas Xtend — Home Assistant Integration</h1>

<p align="center">
  Local Wi-Fi integration for the Intergas Xtend hybrid heat pump.<br>
  No cloud. No subscription. Full control from Home Assistant.
</p>

<p align="center">
  <a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=pepijnnichting&repository=intergas-xtend&category=integration">
    <img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open in HACS" />
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/HACS-Custom-orange?logo=home-assistant-community-store" alt="HACS Custom" />
  <img src="https://img.shields.io/badge/HA-2026.5%2B-blue?logo=home-assistant" alt="Home Assistant 2026.5+" />
  <img src="https://img.shields.io/github/v/release/pepijnnichting/intergas-xtend" alt="GitHub release" />
  <img src="https://img.shields.io/github/license/pepijnnichting/intergas-xtend" alt="License" />
</p>

---

This integration connects directly to your Intergas Xtend hybrid heat pump over Wi-Fi, allowing you to monitor your heating system from Home Assistant.

## Features

- Room, outdoor, boiler, and heating supply/return temperatures
- Water pressure, flow rate, compressor frequency, and additional boiler/DHW diagnostics
- Heat pump and boiler power (kW) and COP
- Cumulative energy totals for heating and hot water (kWh), plus hot water setpoint and gas volume
- System status and heat pump mode (human-readable)
- Boiler modulation percentage
- Flame, pump, heating, and hot water binary sensors
- Error and notification codes (decoded to plain text)
- Software version and heating hours (diagnostic)
- **Xtore hot water tank** (optional) — tank temperatures, flow rate, pump speed, thermal power, and electric energy

## Requirements

- An Intergas Xtend hybrid heat pump
- Home Assistant host networking:
  - **Direct mode (without proxy):** Ethernet + Wi-Fi adapter (Wi-Fi connects to the Xtend AP)
  - **Proxy mode (with companion proxy):** only a normal network connection to the Raspberry Pi proxy (Wi-Fi on Home Assistant is not required)

## How it works

The Xtend does not connect to your home network. Instead, it acts as its own Wi-Fi access point. Your Home Assistant server uses its Wi-Fi adapter to connect directly to the Xtend network, while staying on your home network and internet via Ethernet.

## Optional companion proxy

If your Home Assistant host cannot stay connected to the Xtend Wi-Fi directly, you can place a Raspberry Pi in between and run the companion proxy:

- Intergas Xtend Proxy (GitHub): https://github.com/pepijnnichting/intergas-xtend-proxy

With this setup, Home Assistant connects to the Raspberry Pi IP instead of directly to `10.20.30.1`.
Home Assistant only needs regular network access to the Raspberry Pi in this mode.

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

> **Using Home Assistant OS or Supervised without a UI network manager?** You can connect via the terminal instead:
>
> ```bash
> # List available Wi-Fi networks
> nmcli device wifi list
>
> # Connect to the Xtend access point
> nmcli device wifi connect "Xtend_xxxxxxxxxx" password "YourPassword"
>
> # Verify the connection is active
> nmcli connection show --active
> ```
>
> Replace `Xtend_xxxxxxxxxx` with the actual network name and use the password printed on the Xtend unit.

## Installation

### HACS (recommended)

1. Ensure you have [HACS](https://hacs.xyz/) installed
2. Go to **HACS → three-dot menu → Custom repositories**
3. Add `https://github.com/pepijnnichting/intergas-xtend` as an **Integration**
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

## Removal

1. Go to **Settings → Integrations**
2. Find **Intergas Xtend** and click on it
3. Click the three-dot menu (⋮) and select **Delete**
4. Restart Home Assistant
5. Optionally disconnect from the Xtend Wi-Fi under **Settings → System → Network**

## Usage

After setup you'll have access to the following entities:

- **Sensors:** temperatures, pressure, flow rate, power, energy totals, COP, status, modulation
- **Binary sensors:** flame, heating active, hot water active, pump running
- **Climate entity:** displays current and target temperature and heating/idle state (read-only — control your setpoint via your room thermostat integration)

All sensors use standard Home Assistant device classes, so energy sensors appear in the Energy Dashboard automatically.

In addition to the Xtore-specific sensors below, the integration also exposes generic domestic hot water values that are commonly available across installations, such as hot water setpoint, starts, and gas volume.

### Xtore hot water tank

If you have an Intergas Xtore boiler vessel connected to your Xtend, six additional sensors are created automatically:

| Sensor                        | Description                                |
| ----------------------------- | ------------------------------------------ |
| Hot Water Preheat Temperature | Heat exchanger temperature inside the tank |
| Cold Water Temperature        | Mains cold water inlet temperature         |
| Hot Water Flow Rate           | DHW circuit flow rate (L/min)              |
| Hot Water Pump Speed          | DHW pump modulation (%)                    |
| Hot Water Thermal Power       | Thermal power delivered to the tank (kW)   |
| Electric Energy Hot Water     | Cumulative electric energy for DHW (kWh)   |

When no Xtore is connected, all six sensors show as **unavailable** — they do not affect the rest of the integration.

### Xtend UI field mapping (proxy validation)

If you use the proxy web UI (`http://<PI_IP>:8080/`) to validate values, this quick map helps match on-screen labels to API field codes.

| Xtend UI label (example) | Field code | Notes                               |
| ------------------------ | ---------- | ----------------------------------- |
| Operating Mode           | `77dd`     | System status enum                  |
| DHW Actual               | `8edb`     | Boiler hot water temperature        |
| DHW Setpoint             | `8ecb`     | Boiler hot water setpoint           |
| DHW preheat              | `628d`     | Xtore preheat / heat exchanger temp |
| DHW cold                 | `6256`     | Xtore cold water inlet temp         |
| DHW flow                 | `6290`     | Xtore DHW flow rate                 |
| DHW available (%)        | `622b`     | Xtore pump speed / modulation       |
| DHW thermal power        | `5092`     | Xtore DHW thermal power             |
| DHW electric energy      | `6358`     | Xtore DHW electric energy total     |
| Xtore hot                | `6269`     | Xtore hot water outlet temp         |

UI labels can differ slightly per firmware version. Compare trends and value ranges when matching unknown fields.

## Dashboard

A pre-built Lovelace dashboard is included in [`dashboard.yaml`](dashboard.yaml). It provides two views:

- **Overview** — status indicators, all temperatures, power & efficiency, and energy totals as tile cards
- **History** — 24-hour graphs for temperatures, power, COP/modulation, and a 30-day energy bar chart

To import it:

1. Open [`dashboard.yaml`](https://raw.githubusercontent.com/pepijnnichting/intergas-xtend/main/dashboard.yaml) and copy the contents
2. In Home Assistant, go to **Overview → pencil icon → three-dot menu → Edit in YAML**
3. Replace the contents and click **Save**

> Entity IDs in the dashboard are based on the default device name "Intergas Xtend". If yours differ, find the correct IDs at **Settings → Devices & Services → Intergas Xtend**.

## Credits

Based on the work by [DSchoutsen](https://github.com/DSchoutsen/HA_connection_Xtend).

## Troubleshooting

### Integration is unavailable after a while

The Xtend access point may disconnect Wi-Fi clients due to inactivity. If this happens, keep the scan interval between 5 and 120 seconds (**Settings → Integrations → Intergas Xtend → Configure**) and ensure your Home Assistant Wi-Fi adapter stays connected.

### Sensors show "Unavailable"

If individual sensors show as unavailable, they typically indicate fields that the Xtend hardware does not support in your configuration (for example, Xtore sensors without a connected Xtore tank). This is expected behaviour.

### Diagnostics

To help diagnose issues, download the integration diagnostics:

1. Go to **Settings → Devices & Services → Intergas Xtend**
2. Click the three-dot menu (⋮) on the integration card
3. Select **Download diagnostics**

The file contains the last known sensor values and coordinator status — useful when reporting a bug.

## Supported hardware

| Device              | Supported                                                  |
| ------------------- | ---------------------------------------------------------- |
| Intergas Xtend      | ✅                                                         |
| Intergas Xtore tank | ✅ (optional, sensors show unavailable when not connected) |

## Known limitations

- The climate entity is **read-only**. Setting the target temperature is not supported; use your room thermostat for that.
- The Xtend Wi-Fi access point has a limited number of simultaneous clients. Do not connect additional devices to the Xtend network.
- The integration polls the Xtend on a configurable interval (default 120 s, range 5-300 s). Real-time push updates are not supported, but 5-10 s polling works well for near-real-time dashboards.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
