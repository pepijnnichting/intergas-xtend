"""Intergas Xtend API Client."""
import logging
import aiohttp
import asyncio
import json
from datetime import datetime, timedelta

from .const import LOGIN_URL, DATA_URL

_LOGGER = logging.getLogger(__name__)

class AuthenticationError(Exception):
    """Exception raised for authentication errors."""
    pass

class CommunicationError(Exception):
    """Exception raised for communication errors."""
    pass

class IntergasXtendApi:
    """Intergas Xtend API client."""

    def __init__(self, username, password):
        """Initialize the API client."""
        self.username = username
        self.password = password
        self.session = aiohttp.ClientSession()
        self.token = None
        self.token_expires = None
        self.appliance_id = None
        self.data = {}
        self.last_update = None

    async def login(self):
        """Login to the Intergas Xtend portal."""
        try:
            payload = {
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
                "client_id": "dashboard-intergas",
            }
            
            async with self.session.post(LOGIN_URL, data=payload) as response:
                if response.status != 200:
                    raise AuthenticationError("Failed to authenticate")
                
                result = await response.json()
                self.token = result.get("access_token")
                expires_in = result.get("expires_in", 3600)
                self.token_expires = datetime.now() + timedelta(seconds=expires_in)
                
                # Get appliance ID
                await self.get_appliances()
                
                return True
                
        except aiohttp.ClientError as ex:
            raise CommunicationError(f"Error communicating with API: {ex}")

    async def get_appliances(self):
        """Get list of appliances."""
        await self._ensure_token()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            async with self.session.get(DATA_URL, headers=headers) as response:
                if response.status != 200:
                    raise CommunicationError(f"Failed to get appliances, status: {response.status}")
                
                appliances = await response.json()
                if appliances and len(appliances) > 0:
                    self.appliance_id = appliances[0]["id"]
                    return appliances
                
                return []
                
        except aiohttp.ClientError as ex:
            raise CommunicationError(f"Error communicating with API: {ex}")

    async def get_data(self, force_update=False):
        """Get the latest data from the appliance."""
        # If we have recent data, use it
        if not force_update and self.last_update and (datetime.now() - self.last_update < timedelta(minutes=5)):
            return self.data
            
        await self._ensure_token()
        
        if not self.appliance_id:
            await self.get_appliances()
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            url = f"{DATA_URL}/{self.appliance_id}"
            async with self.session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise CommunicationError(f"Failed to get data, status: {response.status}")
                
                self.data = await response.json()
                self.last_update = datetime.now()
                return self.data
                
        except aiohttp.ClientError as ex:
            raise CommunicationError(f"Error communicating with API: {ex}")

    async def _ensure_token(self):
        """Ensure we have a valid token."""
        if not self.token or (self.token_expires and datetime.now() >= self.token_expires):
            await self.login()

    async def close(self):
        """Close the session."""
        await self.session.close()
