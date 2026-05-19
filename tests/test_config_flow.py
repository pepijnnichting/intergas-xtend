"""Tests for the Intergas Xtend config flow."""
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.intergas_xtend.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from custom_components.intergas_xtend.intergas_api import ConnectionFailedError

VALID_INPUT = {CONF_HOST: "10.20.30.1", CONF_PORT: 80}


@pytest.fixture(autouse=True)
def mock_setup_entry():
    """Prevent actual integration setup and unload during flow tests."""
    with (
        patch(
            "custom_components.intergas_xtend.async_setup_entry",
            return_value=True,
        ),
        patch(
            "custom_components.intergas_xtend.async_unload_entry",
            return_value=True,
        ),
    ):
        yield


@pytest.fixture
def mock_api_login():
    """Mock a successful API login."""
    with patch(
        "custom_components.intergas_xtend.config_flow.IntergasXtendApi"
    ) as mock:
        mock.return_value.login = AsyncMock(return_value=True)
        yield mock


# ---------------------------------------------------------------------------
# User step
# ---------------------------------------------------------------------------


async def test_user_step_shows_form(hass: HomeAssistant) -> None:
    """Test that the initial step shows the form with no errors."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}


async def test_user_step_success(hass: HomeAssistant, mock_api_login) -> None:
    """Test a successful config entry creation."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], VALID_INPUT
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == f"Intergas Xtend ({VALID_INPUT[CONF_HOST]})"
    assert result["data"] == VALID_INPUT


async def test_user_step_cannot_connect(hass: HomeAssistant) -> None:
    """Test that a connection failure shows the correct error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.intergas_xtend.config_flow.IntergasXtendApi"
    ) as mock:
        mock.return_value.login = AsyncMock(
            side_effect=ConnectionFailedError("timeout")
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], VALID_INPUT
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_step_invalid_host(hass: HomeAssistant) -> None:
    """Test that a non-IP host value shows an invalid_host error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "not-an-ip", CONF_PORT: 80}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"host": "invalid_host"}


async def test_user_step_unknown_error(hass: HomeAssistant) -> None:
    """Test that an unexpected exception results in a generic error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.intergas_xtend.config_flow.validate_input",
        side_effect=RuntimeError("unexpected"),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], VALID_INPUT
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "unknown"}


async def test_duplicate_entry_aborts(hass: HomeAssistant, mock_api_login) -> None:
    """Test that configuring the same host a second time is aborted."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], VALID_INPUT
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    result2 = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result2["flow_id"], VALID_INPUT
    )

    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "already_configured"


# ---------------------------------------------------------------------------
# Options flow
# ---------------------------------------------------------------------------


async def test_options_flow_shows_form(hass: HomeAssistant, mock_api_login) -> None:
    """Test that the options flow shows the scan interval form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    await hass.config_entries.flow.async_configure(result["flow_id"], VALID_INPUT)
    await hass.async_block_till_done()

    entry = hass.config_entries.async_entries(DOMAIN)[0]
    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"


async def test_options_flow_default_interval(hass: HomeAssistant, mock_api_login) -> None:
    """Test that the options form shows the current scan interval as default."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    await hass.config_entries.flow.async_configure(result["flow_id"], VALID_INPUT)
    await hass.async_block_till_done()

    entry = hass.config_entries.async_entries(DOMAIN)[0]
    result = await hass.config_entries.options.async_init(entry.entry_id)

    schema = result["data_schema"].schema
    assert CONF_SCAN_INTERVAL in schema


async def test_options_flow_saves_interval(hass: HomeAssistant, mock_api_login) -> None:
    """Test that submitting the options form saves the new scan interval."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    await hass.config_entries.flow.async_configure(result["flow_id"], VALID_INPUT)
    await hass.async_block_till_done()

    entry = hass.config_entries.async_entries(DOMAIN)[0]
    result = await hass.config_entries.options.async_init(entry.entry_id)

    with patch.object(hass.config_entries, "async_schedule_reload"):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {CONF_SCAN_INTERVAL: 60}
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_SCAN_INTERVAL] == 60


# ---------------------------------------------------------------------------
# Reconfigure flow
# ---------------------------------------------------------------------------


async def test_reconfigure_shows_form(hass: HomeAssistant, mock_api_login) -> None:
    """Test that the reconfigure step shows the form pre-filled with current data."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    await hass.config_entries.flow.async_configure(result["flow_id"], VALID_INPUT)
    await hass.async_block_till_done()

    entry = hass.config_entries.async_entries(DOMAIN)[0]
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_RECONFIGURE, "entry_id": entry.entry_id},
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "reconfigure"
    assert result["errors"] == {}


async def test_reconfigure_success(hass: HomeAssistant, mock_api_login) -> None:
    """Test that the reconfigure step saves updated host/port."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    await hass.config_entries.flow.async_configure(result["flow_id"], VALID_INPUT)
    await hass.async_block_till_done()

    entry = hass.config_entries.async_entries(DOMAIN)[0]
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_RECONFIGURE, "entry_id": entry.entry_id},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "10.20.30.2", CONF_PORT: 8080}
    )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data[CONF_HOST] == "10.20.30.2"
    assert entry.data[CONF_PORT] == 8080


async def test_reconfigure_cannot_connect(hass: HomeAssistant, mock_api_login) -> None:
    """Test that a connection failure during reconfigure shows an error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    await hass.config_entries.flow.async_configure(result["flow_id"], VALID_INPUT)
    await hass.async_block_till_done()

    entry = hass.config_entries.async_entries(DOMAIN)[0]
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_RECONFIGURE, "entry_id": entry.entry_id},
    )

    with patch(
        "custom_components.intergas_xtend.config_flow.IntergasXtendApi"
    ) as mock:
        mock.return_value.login = AsyncMock(
            side_effect=ConnectionFailedError("timeout")
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_HOST: "10.20.30.2", CONF_PORT: 80}
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}

