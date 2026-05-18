"""API client for Intergas Xtend."""
import asyncio
import aiohttp
import logging
from typing import Any, Dict, Optional

from .const import DEFAULT_TIMEOUT, ALL_FIELDS

_LOGGER = logging.getLogger(__name__)

class IntergasXtendError(Exception):
    """General Intergas Xtend exception."""
    pass

class ConnectionFailedError(IntergasXtendError):
    """Exception when connection fails."""
    pass

class IntergasXtendApi:
    """API Client for Intergas Xtend."""

    def __init__(self, host: str, port: int = 80, session: Optional[aiohttp.ClientSession] = None):
        """Initialize the API client."""
        self.host = host
        self.port = port
        self._own_session = session is None
        self.session = session if session is not None else aiohttp.ClientSession()
        self._stats_url = f"http://{host}:{port}/api/stats/values"
        self._timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)

    async def login(self) -> bool:
        """Test connection to the Intergas Xtend."""
        try:
            await self.get_data()
            return True
        except Exception as ex:
            _LOGGER.error("Failed to connect to Intergas Xtend: %s", ex)
            raise ConnectionFailedError(
                f"Failed to connect to Intergas Xtend at http://{self.host}:{self.port}"
            ) from ex

    async def get_data(self) -> Dict[str, int]:
        """Get current stats from the Intergas Xtend.

        The Xtend API endpoint is:
            GET /api/stats/values?fields=<comma-separated hex codes>

        It returns JSON in the form:
            {"stats": {"<hex_code>": <raw_int>, ...}}

        Raw integer values must be scaled by the field-specific factor (usually 0.01).
        A raw value of 32767 means "not available" for int16 fields.
        """
        try:
            async with self.session.get(
                self._stats_url,
                params={"fields": ALL_FIELDS},
                timeout=self._timeout,
            ) as response:
                if response.status != 200:
                    raise ConnectionFailedError(
                        f"Failed to get data: HTTP {response.status}"
                    )
                payload = await response.json(content_type=None)
                stats: Dict[str, int] = payload.get("stats", {})
                return stats
        except asyncio.TimeoutError:
            raise ConnectionFailedError(
                f"Connection to {self._stats_url} timed out"
            )
        except aiohttp.ClientError as ex:
            raise ConnectionFailedError(
                f"Error communicating with Intergas Xtend: {ex}"
            )

    async def close(self) -> None:
        """Close the session if we own it."""
        if self._own_session and self.session:
            await self.session.close()

