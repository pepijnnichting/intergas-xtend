"""Constants for the Intergas Xtend integration."""

DOMAIN = "intergas_xtend"
MANUFACTURER = "Intergas"

# API endpoints
BASE_URL = "https://portal.intergas-verwarming.nl"
LOGIN_URL = f"{BASE_URL}/oauth/token"
DATA_URL = f"{BASE_URL}/api/appliances"

# Data update interval in seconds (5 minutes)
UPDATE_INTERVAL = 300

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
