"""Config flow for Intergas Xtend integration."""
import logging
import ipaddress
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
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
    
    api = IntergasXtendApi(data[CONF_HOST], data[CONF_PORT], session=async_get_clientsession(hass))
    
    try:
        await api.login()
    except ConnectionFailedError:
        raise CannotConnect
    
    # Return info to be stored in the config entry
    return {"title": f"Intergas Xtend ({data[CONF_HOST]})"}

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Intergas Xtend."""

    VERSION = 1
    
    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            try:
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
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

    @staticmethod
    @config_entries.callback
    def async_get_options_flow(config_entry: "config_entries.ConfigEntry") -> "OptionsFlowHandler":
        """Return the options flow."""
        return OptionsFlowHandler()


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Intergas Xtend."""

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_update_reload_and_abort(
                self.config_entry,
                data_updates={},
                options=user_input,
            )
        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=current_interval
                    ): vol.All(int, vol.Range(min=30, max=300)),
                }
            ),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidHost(HomeAssistantError):
    """Error to indicate the host is invalid."""
