"""API client for Intergas Xtend."""
import logging
from collections.abc import Mapping

import aiohttp

from .const import DEFAULT_TIMEOUT, ALL_FIELDS

_LOGGER = logging.getLogger(__name__)

class IntergasXtendError(Exception):
    """General Intergas Xtend exception."""


class ConnectionFailedError(IntergasXtendError):
    """Exception when connection fails."""


class IntergasXtendApi:
    """API Client for Intergas Xtend."""

    def __init__(
        self,
        host: str,
        port: int = 80,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Initialize the API client."""
        self.host = host
        self.port = port
        self._own_session = session is None
        self.session = session if session is not None else aiohttp.ClientSession()
        # Square brackets are required around an IPv6 literal in a URL.
        url_host = f"[{host}]" if ":" in host else host
        self._stats_url = f"http://{url_host}:{port}/api/stats/values"
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

    async def get_data(self) -> dict[str, int]:
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
        except TimeoutError as ex:
            raise ConnectionFailedError(
                f"Connection to {self._stats_url} timed out"
            ) from ex
        except aiohttp.ClientError as ex:
            raise ConnectionFailedError(
                f"Error communicating with Intergas Xtend: {ex}"
            ) from ex
        except ValueError as ex:
            raise ConnectionFailedError("Intergas Xtend returned invalid JSON") from ex

        if not isinstance(payload, Mapping):
            raise ConnectionFailedError("Intergas Xtend returned an invalid response")

        stats = payload.get("stats", {})
        if not isinstance(stats, Mapping) or not all(
            isinstance(key, str) and isinstance(value, int)
            for key, value in stats.items()
        ):
            raise ConnectionFailedError("Intergas Xtend returned invalid statistics")

        return dict(stats)

    async def close(self) -> None:
        """Close the session if we own it."""
        if self._own_session and self.session:
            await self.session.close()
