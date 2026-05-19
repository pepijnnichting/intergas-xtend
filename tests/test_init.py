"""Tests for the Intergas Xtend integration setup."""
from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.config_entries import ConfigEntryState

from custom_components.intergas_xtend import IntergasXtendData
from custom_components.intergas_xtend.intergas_api import (
    ConnectionFailedError,
    IntergasXtendApi,
)

from tests.conftest import FAKE_DATA


# ---------------------------------------------------------------------------
# async_setup_entry
# ---------------------------------------------------------------------------

async def test_setup_entry_success(hass):
    """Integration loads successfully when the API returns data."""
    entry = MockConfigEntry(
        domain="intergas_xtend",
        data={"host": "10.20.30.1", "port": 80},
    )
    entry.add_to_hass(hass)

    with patch.object(IntergasXtendApi, "get_data", new_callable=AsyncMock, return_value=FAKE_DATA):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.LOADED
    assert isinstance(entry.runtime_data, IntergasXtendData)
    assert entry.runtime_data.coordinator.data == FAKE_DATA


async def test_setup_entry_connection_error(hass):
    """Integration goes to SETUP_RETRY when the first API call fails."""
    entry = MockConfigEntry(
        domain="intergas_xtend",
        data={"host": "10.20.30.1", "port": 80},
    )
    entry.add_to_hass(hass)

    with patch.object(
        IntergasXtendApi,
        "get_data",
        new_callable=AsyncMock,
        side_effect=ConnectionFailedError("timeout"),
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.SETUP_RETRY


async def test_setup_entry_uses_scan_interval_option(hass):
    """Coordinator update interval is taken from options when set."""
    entry = MockConfigEntry(
        domain="intergas_xtend",
        data={"host": "10.20.30.1", "port": 80},
        options={"scan_interval": 60},
    )
    entry.add_to_hass(hass)

    with patch.object(IntergasXtendApi, "get_data", new_callable=AsyncMock, return_value=FAKE_DATA):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.LOADED
    assert entry.runtime_data.coordinator.update_interval.seconds == 60


# ---------------------------------------------------------------------------
# async_unload_entry
# ---------------------------------------------------------------------------

async def test_unload_entry_success(hass):
    """Integration unloads cleanly."""
    entry = MockConfigEntry(
        domain="intergas_xtend",
        data={"host": "10.20.30.1", "port": 80},
    )
    entry.add_to_hass(hass)

    with patch.object(IntergasXtendApi, "get_data", new_callable=AsyncMock, return_value=FAKE_DATA):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        result = await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()

    assert result is True
    assert entry.state == ConfigEntryState.NOT_LOADED


async def test_unload_entry_no_runtime_data(hass):
    """Unload with missing runtime_data does not raise."""
    entry = MockConfigEntry(
        domain="intergas_xtend",
        data={"host": "10.20.30.1", "port": 80},
    )
    entry.add_to_hass(hass)

    with patch.object(IntergasXtendApi, "get_data", new_callable=AsyncMock, return_value=FAKE_DATA):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    # Remove runtime_data to simulate teardown edge case
    del entry.runtime_data

    result = await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert result is True
