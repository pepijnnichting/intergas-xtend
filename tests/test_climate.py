"""Tests for the Intergas Xtend climate platform."""
from unittest.mock import MagicMock

from homeassistant.components.climate import HVACAction, HVACMode

from custom_components.intergas_xtend.climate import IntergasXtendThermostat
from custom_components.intergas_xtend.const import (
    FIELD_ROOM_TEMP,
    FIELD_SETPOINT,
    FIELD_SYSTEM_STATUS,
    XTEND_UNAVAILABLE,
)

from tests.conftest import FAKE_DATA


def _make_thermostat(data):
    coordinator = MagicMock()
    coordinator.data = data
    return IntergasXtendThermostat(coordinator, "test_entry_id")


# ---------------------------------------------------------------------------
# current_temperature
# ---------------------------------------------------------------------------

def test_current_temperature_valid():
    thermostat = _make_thermostat({FIELD_ROOM_TEMP: 2100})
    assert thermostat.current_temperature == 21.0


def test_current_temperature_unavailable_sentinel():
    thermostat = _make_thermostat({FIELD_ROOM_TEMP: XTEND_UNAVAILABLE})
    assert thermostat.current_temperature is None


def test_current_temperature_missing():
    thermostat = _make_thermostat({})
    assert thermostat.current_temperature is None


def test_current_temperature_no_data():
    thermostat = _make_thermostat(None)
    assert thermostat.current_temperature is None


# ---------------------------------------------------------------------------
# target_temperature
# ---------------------------------------------------------------------------

def test_target_temperature_valid():
    thermostat = _make_thermostat({FIELD_SETPOINT: 2100})
    assert thermostat.target_temperature == 21.0


def test_target_temperature_unavailable():
    thermostat = _make_thermostat({FIELD_SETPOINT: XTEND_UNAVAILABLE})
    assert thermostat.target_temperature is None


def test_target_temperature_no_data():
    thermostat = _make_thermostat(None)
    assert thermostat.target_temperature is None


# ---------------------------------------------------------------------------
# hvac_mode
# ---------------------------------------------------------------------------

def test_hvac_mode_heat():
    # Status 5 = Heating Comfort → HEAT
    thermostat = _make_thermostat({FIELD_SYSTEM_STATUS: 5})
    assert thermostat.hvac_mode == HVACMode.HEAT


def test_hvac_mode_cool():
    # Status 7 ∈ SYSTEM_STATUS_COOLING → COOL
    thermostat = _make_thermostat({FIELD_SYSTEM_STATUS: 7})
    assert thermostat.hvac_mode == HVACMode.COOL


def test_hvac_mode_no_data():
    thermostat = _make_thermostat(None)
    assert thermostat.hvac_mode == HVACMode.HEAT


# ---------------------------------------------------------------------------
# hvac_action
# ---------------------------------------------------------------------------

def test_hvac_action_heating():
    # Status 5 ∈ SYSTEM_STATUS_HEATING → HEATING
    thermostat = _make_thermostat({FIELD_SYSTEM_STATUS: 5})
    assert thermostat.hvac_action == HVACAction.HEATING


def test_hvac_action_heating_floor():
    # Status 9 = Floor heating ∈ SYSTEM_STATUS_HEATING
    thermostat = _make_thermostat({FIELD_SYSTEM_STATUS: 9})
    assert thermostat.hvac_action == HVACAction.HEATING


def test_hvac_action_cooling():
    # Status 7 ∈ SYSTEM_STATUS_COOLING → COOLING
    thermostat = _make_thermostat({FIELD_SYSTEM_STATUS: 7})
    assert thermostat.hvac_action == HVACAction.COOLING


def test_hvac_action_idle():
    # Status 14 = idle → IDLE
    thermostat = _make_thermostat({FIELD_SYSTEM_STATUS: 14})
    assert thermostat.hvac_action == HVACAction.IDLE


def test_hvac_action_no_data():
    thermostat = _make_thermostat(None)
    assert thermostat.hvac_action is None


# ---------------------------------------------------------------------------
# device_info
# ---------------------------------------------------------------------------

def test_device_info():
    thermostat = _make_thermostat(FAKE_DATA)
    info = thermostat.device_info
    assert ("intergas_xtend", "test_entry_id") in info["identifiers"]
    assert info["name"] == "Intergas Xtend"
    assert info["manufacturer"] == "Intergas"


# ---------------------------------------------------------------------------
# Full integration: async_setup_entry creates climate entity
# ---------------------------------------------------------------------------

async def test_climate_entity_created(setup_integration, hass):
    """async_setup_entry registers 1 climate entity."""
    states = hass.states.async_all("climate")
    assert len(states) == 1
