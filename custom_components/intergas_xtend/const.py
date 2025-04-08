"""Constants for the Intergas Xtend integration."""

DOMAIN = "intergas_xtend"
MANUFACTURER = "Intergas"

# Default values
DEFAULT_HOST = "192.168.178.120"  # Default IP address of the Intergas Xtend
DEFAULT_PORT = 80
DEFAULT_TIMEOUT = 10  # Timeout in seconds
DEFAULT_SCAN_INTERVAL = 60  # Update interval in seconds

# Config flow
CONF_HOST = "host"
CONF_PORT = "port"

# Data keys
KEY_STATUS = "status"
KEY_STATUS_CODE = "statusCode"
KEY_ROOMTEMP = "roomTemp"
KEY_OUTSIDE_TEMP = "outsideTemp"
KEY_PRESSURE = "pressure"
KEY_TAPWATERTEMP = "tapwaterTemp"
KEY_HEATING_TEMP = "heatingTemp"
KEY_SETPOINT = "setpoint"
KEY_MANUAL_SETPOINT = "manualSetpoint"
KEY_FLAME = "flame"
KEY_PUMP = "pump"
KEY_HEATING = "heating"
KEY_TAPWATER = "tapwater"
KEY_MODULATION = "modulation"
KEY_INTERNAL_SETPOINT = "internalSetpoint"
KEY_HEATING_ENABLED = "heatingEnabled"
KEY_TAPWATER_ENABLED = "tapwaterEnabled"
KEY_COOLING_ENABLED = "coolingEnabled"

# Sensors
SENSOR_TYPES = {
    "room_temp": {
        "name": "Room Temperature",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
    },
    "tap_temp": {
        "name": "Tap Water Temperature",
        "unit": "°C",
        "icon": "mdi:water-thermometer",
        "device_class": "temperature",
    },
    "boiler_temp": {
        "name": "Boiler Temperature",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
    },
    "pressure": {
        "name": "Water Pressure",
        "unit": "bar",
        "icon": "mdi:gauge",
        "device_class": "pressure",
    },
    "setpoint": {
        "name": "Temperature Setpoint",
        "unit": "°C",
        "icon": "mdi:thermostat",
        "device_class": "temperature",
    },
}

BINARY_SENSOR_TYPES = {
    "flame": {
        "name": "Flame",
        "icon": "mdi:fire",
        "device_class": "heat",
    },
    "heating": {
        "name": "Central Heating",
        "icon": "mdi:radiator",
        "device_class": "running",
    },
    "tap_water": {
        "name": "Tap Water",
        "icon": "mdi:water",
        "device_class": "running",
    },
}
