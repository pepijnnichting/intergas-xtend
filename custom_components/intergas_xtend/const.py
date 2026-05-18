"""Constants for the Intergas Xtend integration."""

DOMAIN = "intergas_xtend"
MANUFACTURER = "Intergas"

# Default values
# The Xtend operates as a WiFi Access Point; its IP is always 10.20.30.1
DEFAULT_HOST = "10.20.30.1"
DEFAULT_PORT = 80
DEFAULT_TIMEOUT = 10  # seconds
# Keep ≤300 s — the Xtend AP disconnects on inactivity
DEFAULT_SCAN_INTERVAL = 120  # seconds

# Config flow keys
CONF_HOST = "host"
CONF_PORT = "port"

# ---------------------------------------------------------------------------
# API field codes — hex keys in the {"stats": {...}} response from:
#   GET /api/stats/values?fields=<comma-separated hex codes>
# Source: https://github.com/DSchoutsen/HA_connection_Xtend
#
# int16 fields return 32767 (0x7FFF) when the reading is unavailable.
# ---------------------------------------------------------------------------
XTEND_UNAVAILABLE = 32767

# Temperatures (int16, °C, ×0.01)
FIELD_ROOM_TEMP        = "79b3"   # room temperature
FIELD_OUTDOOR_TEMP     = "62d1"   # outdoor temperature
FIELD_HP_SUPPLY_TEMP   = "62e7"   # heating circuit water supply
FIELD_HP_RETURN_TEMP   = "6280"   # heating circuit water return
FIELD_TAPWATER_TEMP    = "6269"   # domestic hot water (hot side)
FIELD_SETPOINT         = "7921"   # room thermostat setpoint
FIELD_REQUESTED_TEMP   = "7767"   # calculated circuit target temperature

# Pressure / flow (int16)
FIELD_PRESSURE         = "7ed3"   # bar, ×0.01
FIELD_FLOW_RATE        = "629c"   # L/min, ×0.01

# Power (int16)
FIELD_HP_POWER_THERMAL     = "503e"   # heat pump thermal power, kW, ×0.001
FIELD_BOILER_POWER_THERMAL = "5088"   # gas boiler thermal power, kW, ×0.001
FIELD_POWER_ELECTRIC       = "50f2"   # total electric power, W (×1; 0.001 kW/unit = 1 W/unit)
FIELD_COP                  = "5041"   # current COP, uint8, ×0.1

# Cumulative energy (uint24, kWh, ×1 — no unavailable sentinel)
FIELD_ENERGY_THERMAL_HEATING  = "63f0"
FIELD_ENERGY_ELECTRIC_HEATING = "63b3"
FIELD_ENERGY_THERMAL_BOILER   = "63df"
FIELD_ENERGY_THERMAL_DHW      = "6339"   # domestic hot water energy
FIELD_ENERGY_THERMAL_COOLING  = "63e4"   # cooling energy
FIELD_ENERGY_ELECTRIC_DHW     = "6358"   # Xtore DHW electric energy

# Xtore domestic hot water tank (optional accessory — fields return 32767 when not connected)
FIELD_DHW_COLD_TEMP      = "6256"   # cold water inlet to tank, °C, ×0.01
FIELD_DHW_PREHEAT_TEMP   = "628d"   # preheat / heat exchanger temp, °C, ×0.01
FIELD_DHW_FLOW_RATE      = "6290"   # DHW circuit flow rate, L/min, ×0.01
FIELD_DHW_PUMP_SPEED     = "622b"   # DHW pump modulation, %, ×0.01
FIELD_DHW_POWER_THERMAL  = "5092"   # DHW thermal power, kW, ×0.001

# Boiler OpenTherm modulation
FIELD_MODULATION = "84d1"   # int16, %, ×0.01

# Status / mode enums
FIELD_SYSTEM_STATUS  = "77dd"   # uint8
FIELD_HEATPUMP_MODE  = "777d"   # uint8
FIELD_BURNER_STATUS  = "7e7a"   # uint8, flag byte (non-zero = burner active)
FIELD_PUMP_SPEED     = "701b"   # uint16, rpm

# Diagnostics
FIELD_ERROR_CODE        = "4133"   # uint16
FIELD_NOTIFICATION_CODE = "7940"   # uint8
FIELD_HEATING_HOURS     = "6ac5"   # uint24, hours
FIELD_SOFTWARE_VERSION  = "47e0"   # bytes, version string

# All fields fetched in a single API call
ALL_FIELDS = ",".join([
    FIELD_ROOM_TEMP, FIELD_OUTDOOR_TEMP, FIELD_HP_SUPPLY_TEMP, FIELD_HP_RETURN_TEMP,
    FIELD_TAPWATER_TEMP, FIELD_SETPOINT, FIELD_REQUESTED_TEMP,
    FIELD_PRESSURE, FIELD_FLOW_RATE,
    FIELD_HP_POWER_THERMAL, FIELD_BOILER_POWER_THERMAL, FIELD_POWER_ELECTRIC, FIELD_COP,
    FIELD_ENERGY_THERMAL_HEATING, FIELD_ENERGY_ELECTRIC_HEATING, FIELD_ENERGY_THERMAL_BOILER,
    FIELD_ENERGY_THERMAL_DHW, FIELD_ENERGY_THERMAL_COOLING, FIELD_ENERGY_ELECTRIC_DHW,
    FIELD_DHW_COLD_TEMP, FIELD_DHW_PREHEAT_TEMP, FIELD_DHW_FLOW_RATE,
    FIELD_DHW_PUMP_SPEED, FIELD_DHW_POWER_THERMAL,
    FIELD_MODULATION,
    FIELD_SYSTEM_STATUS, FIELD_HEATPUMP_MODE, FIELD_BURNER_STATUS, FIELD_PUMP_SPEED,
    FIELD_ERROR_CODE, FIELD_NOTIFICATION_CODE, FIELD_HEATING_HOURS, FIELD_SOFTWARE_VERSION,
])

# System status enum values (FIELD_SYSTEM_STATUS = "77dd")
# Used for HVAC action determination and binary sensor logic
SYSTEM_STATUS_HEATING  = {5, 6, 9}   # Heating Comfort, Eco, Floor Heating
SYSTEM_STATUS_TAPWATER = {4, 8}      # DHW, DHW via heat exchanger
SYSTEM_STATUS_COOLING  = {7}

# Heatpump mode enum (FIELD_HEATPUMP_MODE = "777d")
HEATPUMP_MODE_OFF = 254

