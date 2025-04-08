"""API client for Intergas Xtend."""
import asyncio
import aiohttp
import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional

from .const import DEFAULT_TIMEOUT

_LOGGER = logging.getLogger(__name__)

class IntergasXtendError(Exception):
    """General Intergas Xtend exception."""
    pass

class ConnectionFailedError(IntergasXtendError):
    """Exception when connection fails."""
    pass

class IntergasXtendApi:
    """API Client for Intergas Xtend."""

    def __init__(self, host: str, port: int = 80):
        """Initialize the API client."""
        self.host = host
        self.port = port
        self.data = {}
        self.session = aiohttp.ClientSession()
        self.base_url = f"http://{host}:{port}"
        
    async def login(self) -> bool:
        """Test connection to the Intergas Xtend."""
        try:
            await self.get_data()
            return True
        except Exception as ex:
            _LOGGER.error("Failed to connect to Intergas Xtend: %s", ex)
            raise ConnectionFailedError(f"Failed to connect to Intergas Xtend at {self.base_url}") from ex

    async def get_data(self) -> Dict[str, Any]:
        """Get the current data from the Intergas Xtend."""
        try:
            url = f"{self.base_url}/data.json"
            async with self.session.get(url, timeout=DEFAULT_TIMEOUT) as response:
                if response.status != 200:
                    raise ConnectionFailedError(f"Failed to get data: HTTP {response.status}")
                
                data = await response.json()
                self.data = data
                return data
        except asyncio.TimeoutError:
            raise ConnectionFailedError(f"Connection to {self.base_url} timed out")
        except aiohttp.ClientError as ex:
            raise ConnectionFailedError(f"Error communicating with Intergas Xtend: {ex}")
            
    async def set_temperature(self, temperature: float) -> bool:
        """Set the temperature setpoint."""
        try:
            url = f"{self.base_url}/data.json"
            data = {"setpoint": temperature}
            async with self.session.post(url, json=data, timeout=DEFAULT_TIMEOUT) as response:
                if response.status != 200:
                    raise ConnectionFailedError(f"Failed to set temperature: HTTP {response.status}")
                return True
        except Exception as ex:
            _LOGGER.error("Failed to set temperature: %s", ex)
            raise ConnectionFailedError(f"Failed to set temperature: {ex}")
            
    async def close(self) -> None:
        """Close the session."""
        if self.session:
            await self.session.close()
