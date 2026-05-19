"""pytest configuration for Intergas Xtend tests."""
from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations in all tests."""
    yield


# ---------------------------------------------------------------------------
# Shared test data — representative raw values from the Xtend API
# ---------------------------------------------------------------------------
FAKE_DATA = {
    # Temperatures (int16, raw = °C × 100)
    "79b3": 2100,   # FIELD_ROOM_TEMP        21.00 °C
    "62d1": 800,    # FIELD_OUTDOOR_TEMP      8.00 °C
    "62e7": 4500,   # FIELD_HP_SUPPLY_TEMP   45.00 °C
    "6280": 4000,   # FIELD_HP_RETURN_TEMP   40.00 °C
    "8edb": 6000,   # FIELD_BOILER_DHW_TEMP  60.00 °C
    "7921": 2100,   # FIELD_SETPOINT         21.00 °C
    "7767": 4500,   # FIELD_REQUESTED_TEMP   45.00 °C
    # Xtore temperatures
    "6269": 5500,   # FIELD_XTORE_HOT_TEMP   55.00 °C
    "6256": 1000,   # FIELD_DHW_COLD_TEMP    10.00 °C
    "628d": 3500,   # FIELD_DHW_PREHEAT_TEMP 35.00 °C
    # Pressure / flow
    "7ed3": 150,    # FIELD_PRESSURE          1.50 bar
    "629c": 1200,   # FIELD_FLOW_RATE        12.00 L/min
    "6290": 800,    # FIELD_DHW_FLOW_RATE     8.00 L/min
    # Power (kW × 1000 raw)
    "503e": 5000,   # FIELD_HP_POWER_THERMAL      5.00 kW
    "5088": 3000,   # FIELD_BOILER_POWER_THERMAL  3.00 kW
    "50f2": 1500,   # FIELD_POWER_ELECTRIC     1500 W
    "5092": 2000,   # FIELD_DHW_POWER_THERMAL    2.00 kW
    # COP (uint8, raw = COP × 10)
    "5041": 35,     # FIELD_COP  3.5
    # Energy (kWh raw × 1)
    "63f0": 1500,   # FIELD_ENERGY_THERMAL_HEATING
    "63b3": 500,    # FIELD_ENERGY_ELECTRIC_HEATING
    "63df": 300,    # FIELD_ENERGY_THERMAL_BOILER
    "6339": 200,    # FIELD_ENERGY_THERMAL_DHW
    "63e4": 0,      # FIELD_ENERGY_THERMAL_COOLING
    "6358": 100,    # FIELD_ENERGY_ELECTRIC_DHW
    # Pump / modulation
    "622b": 5000,   # FIELD_DHW_PUMP_SPEED  50.00 %
    "84d1": 7000,   # FIELD_MODULATION      70.00 %
    # Status / mode enums
    "77dd": 5,      # FIELD_SYSTEM_STATUS   heating_comfort
    "777d": 1,      # FIELD_HEATPUMP_MODE   heating
    "7e7a": 1,      # FIELD_BURNER_STATUS   burner active
    "701b": 1500,   # FIELD_PUMP_SPEED      pump running
    # Diagnostics
    "4133": 0,      # FIELD_ERROR_CODE      "None"
    "7940": 255,    # FIELD_NOTIFICATION_CODE "None"
    "6ac5": 1200,   # FIELD_HEATING_HOURS
    "6a78": 50,     # FIELD_COOLING_HOURS
    "6a6c": 300,    # FIELD_DHW_HOURS
    "47e0": 123,    # FIELD_SOFTWARE_VERSION
}


@pytest.fixture
async def setup_integration(hass):
    """Set up the Intergas Xtend integration with mocked API data."""
    from custom_components.intergas_xtend.intergas_api import IntergasXtendApi

    entry = MockConfigEntry(
        domain="intergas_xtend",
        data={"host": "10.20.30.1", "port": 80},
    )
    entry.add_to_hass(hass)

    with patch.object(IntergasXtendApi, "get_data", new_callable=AsyncMock, return_value=FAKE_DATA):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        yield entry
        await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
