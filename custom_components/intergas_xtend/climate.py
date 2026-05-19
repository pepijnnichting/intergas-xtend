"""Climate platform for Intergas Xtend integration."""
import logging

from homeassistant.components.climate import (
    ClimateEntity,
    HVACAction,
    HVACMode,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import IntergasXtendConfigEntry

from .const import (
    DOMAIN,
    MANUFACTURER,
    FIELD_SYSTEM_STATUS,
    FIELD_ROOM_TEMP,
    FIELD_SETPOINT,
    SYSTEM_STATUS_HEATING,
    SYSTEM_STATUS_COOLING,
    XTEND_UNAVAILABLE,
)

_LOGGER = logging.getLogger(__name__)

# Coordinator handles all data updates centrally
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant, entry: IntergasXtendConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Intergas Xtend climate."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities([IntergasXtendThermostat(coordinator, entry.entry_id)])


class IntergasXtendThermostat(CoordinatorEntity, ClimateEntity):
    """Representation of an Intergas Xtend thermostat (read-only)."""

    _attr_has_entity_name = True
    _attr_translation_key = "thermostat"
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.COOL]
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator, entry_id):
        """Initialize the thermostat."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_thermostat"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name="Intergas Xtend",
            manufacturer=MANUFACTURER,
            model="Xtend",
        )

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        if not self.coordinator.data:
            return None
        raw = self.coordinator.data.get(FIELD_ROOM_TEMP)
        if raw is None or raw == XTEND_UNAVAILABLE:
            return None
        return round(raw * 0.01, 2)

    @property
    def target_temperature(self) -> float | None:
        """Return the active setpoint (read-only)."""
        if not self.coordinator.data:
            return None
        raw = self.coordinator.data.get(FIELD_SETPOINT)
        if raw is None or raw == XTEND_UNAVAILABLE:
            return None
        return round(raw * 0.01, 2)

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current operating mode."""
        if not self.coordinator.data:
            return HVACMode.HEAT
        if self.coordinator.data.get(FIELD_SYSTEM_STATUS) in SYSTEM_STATUS_COOLING:
            return HVACMode.COOL
        return HVACMode.HEAT

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return what the system is actively doing right now."""
        if not self.coordinator.data:
            return None
        status = self.coordinator.data.get(FIELD_SYSTEM_STATUS)
        if status in SYSTEM_STATUS_HEATING:
            return HVACAction.HEATING
        if status in SYSTEM_STATUS_COOLING:
            return HVACAction.COOLING
        return HVACAction.IDLE

