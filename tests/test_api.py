"""Tests for the Intergas Xtend API client."""
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from custom_components.intergas_xtend.intergas_api import (
    ConnectionFailedError,
    IntergasXtendApi,
)


def _make_session(status: int = 200, json_data: dict | None = None, side_effect=None):
    """Build a MagicMock aiohttp session."""
    mock_response = AsyncMock()
    mock_response.status = status
    if json_data is not None:
        mock_response.json = AsyncMock(return_value=json_data)

    mock_cm = MagicMock()
    if side_effect is not None:
        mock_cm.__aenter__ = AsyncMock(side_effect=side_effect)
    else:
        mock_cm.__aenter__ = AsyncMock(return_value=mock_response)
    mock_cm.__aexit__ = AsyncMock(return_value=False)

    session = MagicMock()
    session.get.return_value = mock_cm
    return session


# ---------------------------------------------------------------------------
# get_data
# ---------------------------------------------------------------------------

async def test_get_data_success():
    """Successful data fetch returns the stats dict."""
    fake_stats = {"79b3": 2100, "62d1": 800}
    session = _make_session(json_data={"stats": fake_stats})

    api = IntergasXtendApi("10.20.30.1", 80, session=session)
    result = await api.get_data()

    assert result == fake_stats


async def test_get_data_http_error():
    """Non-200 response raises ConnectionFailedError."""
    session = _make_session(status=500)

    api = IntergasXtendApi("10.20.30.1", 80, session=session)
    with pytest.raises(ConnectionFailedError, match="HTTP 500"):
        await api.get_data()


async def test_get_data_timeout():
    """TimeoutError is converted to ConnectionFailedError."""
    session = _make_session(side_effect=TimeoutError())

    api = IntergasXtendApi("10.20.30.1", 80, session=session)
    with pytest.raises(ConnectionFailedError, match="timed out"):
        await api.get_data()


async def test_get_data_client_error():
    """aiohttp.ClientError is converted to ConnectionFailedError."""
    session = _make_session(side_effect=aiohttp.ClientError("network error"))

    api = IntergasXtendApi("10.20.30.1", 80, session=session)
    with pytest.raises(ConnectionFailedError, match="network error"):
        await api.get_data()


async def test_get_data_missing_stats_key():
    """Response without 'stats' key returns empty dict."""
    session = _make_session(json_data={})

    api = IntergasXtendApi("10.20.30.1", 80, session=session)
    result = await api.get_data()
    assert result == {}


# ---------------------------------------------------------------------------
# login
# ---------------------------------------------------------------------------

async def test_login_success():
    """login() returns True when get_data() succeeds."""
    fake_stats = {"79b3": 2100}
    session = _make_session(json_data={"stats": fake_stats})

    api = IntergasXtendApi("10.20.30.1", 80, session=session)
    result = await api.login()
    assert result is True


async def test_login_failure():
    """login() re-raises ConnectionFailedError when get_data fails."""
    session = _make_session(status=500)

    api = IntergasXtendApi("10.20.30.1", 80, session=session)
    with pytest.raises(ConnectionFailedError):
        await api.login()


# ---------------------------------------------------------------------------
# close
# ---------------------------------------------------------------------------

async def test_close_owned_session():
    """close() calls session.close() when the session was created internally."""
    mock_session = AsyncMock()
    api = IntergasXtendApi.__new__(IntergasXtendApi)
    api.session = mock_session
    api._own_session = True

    await api.close()
    mock_session.close.assert_awaited_once()


async def test_close_borrowed_session():
    """close() does nothing when the session was injected from outside."""
    mock_session = AsyncMock()
    session = _make_session(json_data={"stats": {}})
    api = IntergasXtendApi("10.20.30.1", 80, session=session)

    await api.close()
    # The injected session must not be closed
    mock_session.close.assert_not_called()


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------

def test_init_creates_own_session():
    """Constructor creates its own session when none is provided."""
    from unittest.mock import patch
    with patch("aiohttp.ClientSession", return_value=MagicMock()) as mock_cls:
        api = IntergasXtendApi("192.168.1.1", 8080)
        assert api._own_session is True
        mock_cls.assert_called_once()
        assert api._stats_url == "http://192.168.1.1:8080/api/stats/values"


def test_init_uses_injected_session():
    """Constructor marks session as borrowed when one is provided."""
    mock_session = MagicMock()
    api = IntergasXtendApi("10.20.30.1", 80, session=mock_session)
    assert api._own_session is False
    assert api.session is mock_session
