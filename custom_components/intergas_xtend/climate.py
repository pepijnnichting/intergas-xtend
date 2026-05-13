"""Climate platform for Intergas Xtend integration."""
import logging
from typing import Optional

from homeassistant.components.climate import (
    ClimateEntity,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    FIELD_SYSTEM_STATUS,
    FIELD_ROOM_TEMP,
    FIELD_SETPOINT,
    SYSTEM_STATUS_HEATING,
    XTEND_UNAVAILABLE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Intergas Xtend climate."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([IntergasXtendThermostat(coordinator, entry.entry_id)])


class IntergasXtendThermostat(CoordinatorEntity, ClimateEntity):
    """Representation of an Intergas Xtend thermostat (read-only)."""

    _attr_hvac_modes = [HVACMode.HEAT]
    _attr_supported_features = 0
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator, entry_id):
        """Initialize the thermostat."""
        super().__init__(coordinator)
        self._entry_id = entry_id
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
        raw = self.coordinator.data.get(FIELD_ROOM_TEMP)
        if raw is None or raw == XTEND_UNAVAILABLE:
            return None
        return round(raw * 0.01, 2)

    @property
    def target_temperature(self) -> Optional[float]:
        """Return the active setpoint (read-only)."""
        if not self.coordinator.data:
            return None
        raw = self.coordinator.data.get(FIELD_SETPOINT)
        if raw is None or raw == XTEND_UNAVAILABLE:
            return None
        return round(raw * 0.01, 2)

    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac operation mode."""
        return HVACMode.HEAT

    @property
    def hvac_action(self) -> Optional[HVACAction]:
        """Return the current HVAC action."""
        if not self.coordinator.data:
            return None
        if self.coordinator.data.get(FIELD_SYSTEM_STATUS) in SYSTEM_STATUS_HEATING:
            return HVACAction.HEATING
        return HVACAction.IDLE


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

    _attr_hvac_modes = [HVACMode.HEAT]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
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
        raw = self.coordinator.data.get(FIELD_ROOM_TEMP)
        if raw is None or raw == XTEND_UNAVAILABLE:
            return None
        return round(raw * 0.01, 2)

    @property
    def target_temperature(self) -> Optional[float]:
        """Return the temperature we try to reach."""
        if not self.coordinator.data:
            return None
        raw = self.coordinator.data.get(FIELD_SETPOINT)
        if raw is None or raw == XTEND_UNAVAILABLE:
            return None
        return round(raw * 0.01, 2)

    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac operation mode."""
        return HVACMode.HEAT

    @property
    def hvac_action(self) -> Optional[HVACAction]:
        """Return the current HVAC action."""
        if not self.coordinator.data:
            return None
        system_status = self.coordinator.data.get(FIELD_SYSTEM_STATUS)
        if system_status in SYSTEM_STATUS_HEATING:
            return HVACAction.HEATING
        return HVACAction.IDLE
        
    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is not None:
            await self._api.set_temperature(temp)
            await self.coordinator.async_request_refresh()
            
    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode.
        
        Note: The Intergas Xtend API does not expose an explicit on/off endpoint.
        HEAT mode restores a default comfort temperature; OFF mode is not truly
        supported and is intentionally not implemented to avoid unexpected behaviour.
        """
        if hvac_mode == HVACMode.HEAT:
            await self._api.set_temperature(21.0)  # Default comfort temperature
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.warning(
                "Setting HVAC mode to %s is not supported by the Intergas Xtend API",
                hvac_mode,
            )
