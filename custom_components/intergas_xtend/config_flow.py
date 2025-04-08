"""Config flow for Intergas Xtend integration."""
import logging
import ipaddress
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, DEFAULT_HOST, DEFAULT_PORT, CONF_HOST, CONF_PORT
from .intergas_api import IntergasXtendApi, ConnectionFailedError

_LOGGER = logging.getLogger(__name__)

def is_valid_ip(address):
    """Check if the given address is a valid IP address."""
    try:
        ipaddress.ip_address(address)
        return True
    except ValueError:
        return False

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
    }
)

async def validate_input(hass: HomeAssistant, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the user input allows us to connect."""
    if not is_valid_ip(data[CONF_HOST]):
        raise InvalidHost
    
    api = IntergasXtendApi(data[CONF_HOST], data[CONF_PORT])
    
    try:
        await api.login()
    except ConnectionFailedError:
        raise CannotConnect
    finally:
        await api.close()
    
    # Return info to be stored in the config entry
    return {"title": f"Intergas Xtend ({data[CONF_HOST]})"}

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Intergas Xtend."""

    VERSION = 1
    
    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidHost:
                errors["host"] = "invalid_host"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
        
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidHost(HomeAssistantError):
    """Error to indicate the host is invalid."""
