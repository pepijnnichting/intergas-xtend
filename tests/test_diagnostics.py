"""Tests for the Intergas Xtend diagnostics platform."""
from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.intergas_xtend.intergas_api import IntergasXtendApi

pytestmark = pytest.mark.usefixtures("auto_enable_custom_integrations")

FAKE_DATA = {
    "79b3": 2100,
    "62d1": 800,
}


async def test_diagnostics_returns_entry_data(hass, hass_client) -> None:
    """Test that diagnostics returns entry data and coordinator status."""
    from homeassistant.components.diagnostics import async_redact_data

    entry = MockConfigEntry(
        domain="intergas_xtend",
        data={"host": "10.20.30.1", "port": 80},
    )
    entry.add_to_hass(hass)

    with patch.object(IntergasXtendApi, "get_data", new_callable=AsyncMock, return_value=FAKE_DATA):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        from custom_components.intergas_xtend.diagnostics import async_get_config_entry_diagnostics
        result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["entry_data"] == {"host": "10.20.30.1", "port": 80}
    assert result["coordinator_last_update_success"] is True
    assert result["coordinator_data"] == FAKE_DATA

    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()


async def test_diagnostics_coordinator_data_reflects_api(hass) -> None:
    """Test that coordinator_data in diagnostics matches the latest API response."""
    from tests.conftest import FAKE_DATA as FULL_DATA

    entry = MockConfigEntry(
        domain="intergas_xtend",
        data={"host": "10.20.30.1", "port": 80},
    )
    entry.add_to_hass(hass)

    with patch.object(IntergasXtendApi, "get_data", new_callable=AsyncMock, return_value=FULL_DATA):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        from custom_components.intergas_xtend.diagnostics import async_get_config_entry_diagnostics
        result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["coordinator_data"] == FULL_DATA

    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
