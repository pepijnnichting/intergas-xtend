"""Climate platform for Intergas Xtend integration."""
import logging
from typing import Any, Dict, List, Optional

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    KEY_HEATING,
    KEY_ROOMTEMP,
    KEY_SETPOINT,
    KEY_HEATING_ENABLED,
)

_LOGGER = logging.getLogger(__name__)

MIN_TEMP = 5.0
MAX_TEMP = 30.0
PRECISION = 0.5

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Intergas Xtend climate."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]
    
    async_add_entities([IntergasXtendThermostat(coordinator, entry.entry_id, api)])


class IntergasXtendThermostat(CoordinatorEntity, ClimateEntity):
    """Representation of an Intergas Xtend thermostat."""

    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_temperature_unit = TEMP_CELSIUS
    _attr_min_temp = MIN_TEMP
    _attr_max_temp = MAX_TEMP
    _attr_target_temperature_step = PRECISION

    def __init__(self, coordinator, entry_id, api):
        """Initialize the thermostat."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._api = api
        self._attr_unique_id = f"{entry_id}_thermostat"
        self._attr_name = "Thermostat"
        
    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Intergas Xtend",
            "manufacturer": "Intergas",
            "model": "Xtend",
        }
        
    @property
    def current_temperature(self) -> Optional[float]:
        """Return the current temperature."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(KEY_ROOMTEMP)
        
    @property
    def target_temperature(self) -> Optional[float]:
        """Return the temperature we try to reach."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(KEY_SETPOINT)
        
    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac operation mode."""
        if not self.coordinator.data:
            return HVACMode.OFF
            
        if self.coordinator.data.get(KEY_HEATING_ENABLED, False):
            return HVACMode.HEAT
        return HVACMode.OFF
        
    @property
    def hvac_action(self) -> Optional[HVACAction]:
        """Return the current HVAC action."""
        if not self.coordinator.data:
            return HVACAction.OFF
            
        if not self.coordinator.data.get(KEY_HEATING_ENABLED, False):
            return HVACAction.OFF
            
        if self.coordinator.data.get(KEY_HEATING, False):
            return HVACAction.HEATING
        return HVACAction.IDLE
        
    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is not None:
            await self._api.set_temperature(temp)
            await self.coordinator.async_request_refresh()
            
    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        # This would require implementing mode control in the API
        # For now, we'll just set a reasonable temperature based on mode
        if hvac_mode == HVACMode.HEAT:
            await self._api.set_temperature(21.0)  # Default comfort temperature
        else:  # HVACMode.OFF
            await self._api.set_temperature(MIN_TEMP)  # Minimal temperature for OFF mode
            
        await self.coordinator.async_request_refresh()
