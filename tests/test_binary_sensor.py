"""Tests for the Intergas Xtend binary sensor platform."""
from unittest.mock import MagicMock

from custom_components.intergas_xtend.binary_sensor import (
    BINARY_SENSOR_DESCRIPTIONS,
    IntergasXtendBinarySensor,
)
from custom_components.intergas_xtend.const import (
    FIELD_BURNER_STATUS,
    FIELD_HEATPUMP_MODE,
    FIELD_PUMP_SPEED,
    FIELD_SYSTEM_STATUS,
    HEATPUMP_MODE_OFF,
)

from tests.conftest import FAKE_DATA


def _make_sensor(description, data):
    coordinator = MagicMock()
    coordinator.data = data
    return IntergasXtendBinarySensor(coordinator, "test_entry_id", description)


def _desc(key):
    return next(d for d in BINARY_SENSOR_DESCRIPTIONS if d.key == key)


# ---------------------------------------------------------------------------
# Flame (burner)
# ---------------------------------------------------------------------------

def test_flame_on():
    sensor = _make_sensor(_desc(FIELD_BURNER_STATUS), {FIELD_BURNER_STATUS: 1})
    assert sensor.is_on is True


def test_flame_off():
    sensor = _make_sensor(_desc(FIELD_BURNER_STATUS), {FIELD_BURNER_STATUS: 0})
    assert sensor.is_on is False


def test_flame_no_data():
    sensor = _make_sensor(_desc(FIELD_BURNER_STATUS), None)
    assert sensor.is_on is None


# ---------------------------------------------------------------------------
# Heating
# ---------------------------------------------------------------------------

def test_heating_on():
    # Status 5 = Heating Comfort ∈ SYSTEM_STATUS_HEATING
    sensor = _make_sensor(_desc(f"{FIELD_SYSTEM_STATUS}_heating"), {FIELD_SYSTEM_STATUS: 5})
    assert sensor.is_on is True


def test_heating_on_eco():
    # Status 6 = Heating Eco ∈ SYSTEM_STATUS_HEATING
    sensor = _make_sensor(_desc(f"{FIELD_SYSTEM_STATUS}_heating"), {FIELD_SYSTEM_STATUS: 6})
    assert sensor.is_on is True


def test_heating_off():
    sensor = _make_sensor(_desc(f"{FIELD_SYSTEM_STATUS}_heating"), {FIELD_SYSTEM_STATUS: 14})
    assert sensor.is_on is False


# ---------------------------------------------------------------------------
# Tap water
# ---------------------------------------------------------------------------

def test_tapwater_on():
    sensor = _make_sensor(_desc(f"{FIELD_SYSTEM_STATUS}_tapwater"), {FIELD_SYSTEM_STATUS: 4})
    assert sensor.is_on is True


def test_tapwater_off():
    sensor = _make_sensor(_desc(f"{FIELD_SYSTEM_STATUS}_tapwater"), {FIELD_SYSTEM_STATUS: 5})
    assert sensor.is_on is False


# ---------------------------------------------------------------------------
# Pump
# ---------------------------------------------------------------------------

def test_pump_running():
    sensor = _make_sensor(_desc(FIELD_PUMP_SPEED), {FIELD_PUMP_SPEED: 1500})
    assert sensor.is_on is True


def test_pump_stopped():
    sensor = _make_sensor(_desc(FIELD_PUMP_SPEED), {FIELD_PUMP_SPEED: 0})
    assert sensor.is_on is False


def test_pump_missing():
    # Non-empty data without the pump key → lambda returns False (0 > 0)
    sensor = _make_sensor(_desc(FIELD_PUMP_SPEED), {FIELD_BURNER_STATUS: 0})
    assert sensor.is_on is False


# ---------------------------------------------------------------------------
# Heatpump active
# ---------------------------------------------------------------------------

def test_heatpump_active():
    sensor = _make_sensor(_desc(f"{FIELD_HEATPUMP_MODE}_enabled"), {FIELD_HEATPUMP_MODE: 1})
    assert sensor.is_on is True


def test_heatpump_off():
    sensor = _make_sensor(
        _desc(f"{FIELD_HEATPUMP_MODE}_enabled"), {FIELD_HEATPUMP_MODE: HEATPUMP_MODE_OFF}
    )
    assert sensor.is_on is False


def test_heatpump_mode_missing():
    # Non-empty data without heatpump key → get() returns None → not in (off, None) = False
    sensor = _make_sensor(_desc(f"{FIELD_HEATPUMP_MODE}_enabled"), {FIELD_BURNER_STATUS: 1})
    assert sensor.is_on is False


# ---------------------------------------------------------------------------
# device_info
# ---------------------------------------------------------------------------

def test_device_info():
    sensor = _make_sensor(_desc(FIELD_BURNER_STATUS), FAKE_DATA)
    info = sensor.device_info
    assert ("intergas_xtend", "test_entry_id") in info["identifiers"]
    assert info["name"] == "Intergas Xtend"


# ---------------------------------------------------------------------------
# Full integration: async_setup_entry creates all binary sensors
# ---------------------------------------------------------------------------

async def test_binary_sensors_created(setup_integration, hass):
    """async_setup_entry registers 5 binary sensor entities."""
    states = hass.states.async_all("binary_sensor")
    assert len(states) == 5
