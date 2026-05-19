"""Tests for the Intergas Xtend sensor platform."""
from unittest.mock import MagicMock

import pytest

from custom_components.intergas_xtend.const import (
    FIELD_BURNER_STATUS,
    FIELD_COP,
    FIELD_DHW_FLOW_RATE,
    FIELD_ERROR_CODE,
    FIELD_HP_POWER_THERMAL,
    FIELD_HP_RETURN_TEMP,
    FIELD_HP_SUPPLY_TEMP,
    FIELD_HEATPUMP_MODE,
    FIELD_MODULATION,
    FIELD_NOTIFICATION_CODE,
    FIELD_OUTDOOR_TEMP,
    FIELD_POWER_ELECTRIC,
    FIELD_PRESSURE,
    FIELD_ROOM_TEMP,
    FIELD_SYSTEM_STATUS,
    XTEND_UNAVAILABLE,
)
from custom_components.intergas_xtend.sensor import (
    SENSOR_DESCRIPTIONS,
    IntergasXtendSensor,
    _decode,
    _decode_enum,
    _delta_t,
    _int16,
    _temp,
)

from tests.conftest import FAKE_DATA


def _make_sensor(description, data):
    """Instantiate a sensor entity backed by a MagicMock coordinator."""
    coordinator = MagicMock()
    coordinator.data = data
    return IntergasXtendSensor(coordinator, "test_entry_id", description)


def _desc(key):
    """Look up a SENSOR_DESCRIPTIONS entry by key."""
    return next(d for d in SENSOR_DESCRIPTIONS if d.key == key)


# ---------------------------------------------------------------------------
# Helper: _temp
# ---------------------------------------------------------------------------

def test_temp_valid():
    assert _temp({FIELD_ROOM_TEMP: 2100}, FIELD_ROOM_TEMP) == 21.0


def test_temp_unavailable_sentinel():
    assert _temp({FIELD_ROOM_TEMP: XTEND_UNAVAILABLE}, FIELD_ROOM_TEMP) is None


def test_temp_missing_key():
    assert _temp({}, FIELD_ROOM_TEMP) is None


def test_temp_negative():
    assert _temp({FIELD_OUTDOOR_TEMP: -500}, FIELD_OUTDOOR_TEMP) == -5.0


# ---------------------------------------------------------------------------
# Helper: _int16
# ---------------------------------------------------------------------------

def test_int16_valid():
    assert _int16({FIELD_PRESSURE: 150}, FIELD_PRESSURE, 0.01) == 1.5


def test_int16_unavailable():
    assert _int16({FIELD_PRESSURE: XTEND_UNAVAILABLE}, FIELD_PRESSURE, 0.01) is None


def test_int16_missing():
    assert _int16({}, FIELD_PRESSURE, 0.01) is None


def test_int16_cop():
    # COP field uses factor 0.1 — raw 35 → 3.5
    assert _int16({FIELD_COP: 35}, FIELD_COP, 0.1) == 3.5


# ---------------------------------------------------------------------------
# Helper: _decode
# ---------------------------------------------------------------------------

def test_decode_known_value():
    assert _decode({FIELD_ERROR_CODE: 0}, FIELD_ERROR_CODE, {0: "None"}) == "None"


def test_decode_unknown_value():
    result = _decode({FIELD_ERROR_CODE: 999}, FIELD_ERROR_CODE, {0: "None"})
    assert result == "Unknown (999)"


def test_decode_missing_key():
    assert _decode({}, FIELD_ERROR_CODE, {0: "None"}) is None


# ---------------------------------------------------------------------------
# Helper: _decode_enum
# ---------------------------------------------------------------------------

def test_decode_enum_known():
    mapping = {5: "heating_comfort", 7: "cooling"}
    assert _decode_enum({FIELD_SYSTEM_STATUS: 5}, FIELD_SYSTEM_STATUS, mapping) == "heating_comfort"


def test_decode_enum_unknown():
    mapping = {5: "heating_comfort"}
    assert _decode_enum({FIELD_SYSTEM_STATUS: 99}, FIELD_SYSTEM_STATUS, mapping) is None


def test_decode_enum_missing_key():
    assert _decode_enum({}, FIELD_SYSTEM_STATUS, {5: "heating_comfort"}) is None


# ---------------------------------------------------------------------------
# Helper: _delta_t
# ---------------------------------------------------------------------------

def test_delta_t_valid():
    data = {FIELD_HP_SUPPLY_TEMP: 4500, FIELD_HP_RETURN_TEMP: 4000}
    assert _delta_t(data) == 5.0


def test_delta_t_supply_unavailable():
    data = {FIELD_HP_SUPPLY_TEMP: XTEND_UNAVAILABLE, FIELD_HP_RETURN_TEMP: 4000}
    assert _delta_t(data) is None


def test_delta_t_return_unavailable():
    data = {FIELD_HP_SUPPLY_TEMP: 4500, FIELD_HP_RETURN_TEMP: XTEND_UNAVAILABLE}
    assert _delta_t(data) is None


# ---------------------------------------------------------------------------
# IntergasXtendSensor.native_value
# ---------------------------------------------------------------------------

def test_native_value_room_temp():
    sensor = _make_sensor(_desc(FIELD_ROOM_TEMP), FAKE_DATA)
    assert sensor.native_value == 21.0


def test_native_value_no_data():
    sensor = _make_sensor(_desc(FIELD_ROOM_TEMP), None)
    assert sensor.native_value is None


def test_native_value_empty_data():
    sensor = _make_sensor(_desc(FIELD_ROOM_TEMP), {})
    assert sensor.native_value is None


def test_native_value_unavailable_sentinel():
    data = {**FAKE_DATA, FIELD_ROOM_TEMP: XTEND_UNAVAILABLE}
    sensor = _make_sensor(_desc(FIELD_ROOM_TEMP), data)
    assert sensor.native_value is None


def test_native_value_enum_system_status():
    sensor = _make_sensor(_desc(FIELD_SYSTEM_STATUS), {FIELD_SYSTEM_STATUS: 5})
    assert sensor.native_value == "heating_comfort"


def test_native_value_enum_unknown():
    sensor = _make_sensor(_desc(FIELD_SYSTEM_STATUS), {FIELD_SYSTEM_STATUS: 99})
    assert sensor.native_value is None


def test_native_value_heatpump_mode():
    sensor = _make_sensor(_desc(FIELD_HEATPUMP_MODE), {FIELD_HEATPUMP_MODE: 1})
    assert sensor.native_value == "heating"


def test_native_value_error_code_known():
    sensor = _make_sensor(_desc(FIELD_ERROR_CODE), {FIELD_ERROR_CODE: 0})
    assert sensor.native_value == "None"


def test_native_value_error_code_unknown():
    sensor = _make_sensor(_desc(FIELD_ERROR_CODE), {FIELD_ERROR_CODE: 999})
    assert sensor.native_value == "Unknown (999)"


def test_native_value_notification_code():
    sensor = _make_sensor(_desc(FIELD_NOTIFICATION_CODE), {FIELD_NOTIFICATION_CODE: 255})
    assert sensor.native_value == "None"


def test_native_value_power_sensor():
    # HP thermal power: raw 5000, factor 0.001 → 5.0 kW
    sensor = _make_sensor(_desc(FIELD_HP_POWER_THERMAL), {FIELD_HP_POWER_THERMAL: 5000})
    assert sensor.native_value == 5.0


def test_native_value_modulation():
    # FIELD_MODULATION: int16 × 0.01 → raw 7000 = 70.00%
    sensor = _make_sensor(_desc(FIELD_MODULATION), {FIELD_MODULATION: 7000})
    assert sensor.native_value == 70.0


# ---------------------------------------------------------------------------
# device_info
# ---------------------------------------------------------------------------

def test_device_info():
    sensor = _make_sensor(_desc(FIELD_ROOM_TEMP), FAKE_DATA)
    info = sensor.device_info
    assert ("intergas_xtend", "test_entry_id") in info["identifiers"]
    assert info["name"] == "Intergas Xtend"
    assert info["manufacturer"] == "Intergas"


# ---------------------------------------------------------------------------
# Full integration: async_setup_entry creates all sensors
# ---------------------------------------------------------------------------

async def test_sensors_created(setup_integration, hass):
    """async_setup_entry registers exactly as many sensors as SENSOR_DESCRIPTIONS."""
    states = hass.states.async_all("sensor")
    assert len(states) == len(SENSOR_DESCRIPTIONS)
