"""Constants for the Intergas Xtend integration."""

DOMAIN = "intergas_xtend"
MANUFACTURER = "Intergas"

# Default values
# The Xtend operates as a WiFi Access Point; its IP is always 10.20.30.1
DEFAULT_HOST = "10.20.30.1"
DEFAULT_PORT = 80
DEFAULT_TIMEOUT = 10  # Timeout in seconds
# Xtend AP disconnects on inactivity — keep interval ≤ 300 s (5 min)
DEFAULT_SCAN_INTERVAL = 120  # Update interval in seconds

# Config flow
CONF_HOST = "host"
CONF_PORT = "port"

# ---------------------------------------------------------------------------
# API field codes — hex keys returned in {"stats": {...}} by the Xtend API.
# Endpoint: GET /api/stats/values?fields=<comma-separated hex codes>
# Source: https://github.com/DSchoutsen/HA_connection_Xtend
# ---------------------------------------------------------------------------

FIELD_ROOM_TEMP = "79b3"          # int16, °C, ×0.01
FIELD_OUTDOOR_TEMP = "62d1"       # int16, °C, ×0.01
FIELD_HP_SUPPLY_TEMP = "62e7"     # int16, °C, ×0.01  (heating circuit supply)
FIELD_TAPWATER_TEMP = "6269"      # int16, °C, ×0.01  (DHW hot)
FIELD_PRESSURE = "7ed3"           # int16, bar, ×0.01
FIELD_SETPOINT = "7921"           # int16, °C, ×0.01  (room thermostat setpoint)
FIELD_REQUESTED_TEMP = "7767"     # int16, °C, ×0.01  (requested temperature)
FIELD_MODULATION = "84d1"         # int16,  %, ×0.01  (boiler OT modulation)
FIELD_SYSTEM_STATUS = "77dd"      # uint8, system status enum
FIELD_HEATDEMAND_STATUS = "7e51"  # uint8, heatdemand status enum
FIELD_HEATPUMP_MODE = "777d"      # uint8, heatpump mode enum
FIELD_BURNER_STATUS = "7e7a"      # uint8, burner status flags
FIELD_PUMP_SPEED = "701b"         # uint16, rpm
FIELD_ERROR_CODE = "4133"         # uint16
FIELD_NOTIFICATION_CODE = "7940"  # uint8

# Raw value returned by the Xtend when a reading is unavailable (max int16)
XTEND_UNAVAILABLE = 32767

# All fields requested in a single API call
ALL_FIELDS = ",".join([
    FIELD_ROOM_TEMP,
    FIELD_OUTDOOR_TEMP,
    FIELD_HP_SUPPLY_TEMP,
    FIELD_TAPWATER_TEMP,
    FIELD_PRESSURE,
    FIELD_SETPOINT,
    FIELD_REQUESTED_TEMP,
    FIELD_MODULATION,
    FIELD_SYSTEM_STATUS,
    FIELD_HEATDEMAND_STATUS,
    FIELD_HEATPUMP_MODE,
    FIELD_BURNER_STATUS,
    FIELD_PUMP_SPEED,
    FIELD_ERROR_CODE,
    FIELD_NOTIFICATION_CODE,
])

# System status enum values (FIELD_SYSTEM_STATUS = "77dd")
SYSTEM_STATUS_HEATING = {5, 6, 9}   # Roomheating Comfort, Eco, Floor heating
SYSTEM_STATUS_TAPWATER = {4, 8}     # DHW, DHW Heatexchanger
SYSTEM_STATUS_COOLING = {7}         # Roomcooling
SYSTEM_STATUS_IDLE = {14, 255}      # Idle, No task

# Heatpump mode enum values (FIELD_HEATPUMP_MODE = "777d")
HEATPUMP_MODE_DHW = 0
HEATPUMP_MODE_HEATING = 1
HEATPUMP_MODE_COOLING = 2
HEATPUMP_MODE_OFF = 254

