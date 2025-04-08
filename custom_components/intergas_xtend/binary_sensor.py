"""Binary sensor platform for Intergas Xtend integration."""
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, BINARY_SENSOR_TYPES
from .sensor import DataUpdateCoordinator  # Reuse the coordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Intergas Xtend binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id].coordinator
    api = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    
    for sensor_type, sensor_info in BINARY_SENSOR_TYPES.items():
        entities.append(
            IntergasXtendBinarySensor(
                coordinator,
                entry.entry_id,
                sensor_type,
                sensor_info,
                api
            )
        )
    
    async_add_entities(entities)

class IntergasXtendBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Intergas Xtend Binary Sensor."""

    def __init__(self, coordinator, entry_id, sensor_type, sensor_info, api):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._sensor_type = sensor_type
        self._sensor_info = sensor_info
        self._api = api
        self._attr_unique_id = f"{entry_id}_{sensor_type}"
        self._attr_name = sensor_info["name"]
        self._attr_icon = sensor_info.get("icon")
        self._attr_device_class = sensor_info.get("device_class")
        
    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Intergas Xtend",
            "manufacturer": "Intergas",
            "model": self.coordinator.data.get("device_model", "Xtend"),
            "sw_version": self.coordinator.data.get("firmware_version", "Unknown"),
        }
        
    @property
    def is_on(self):
        """Return the state of the binary sensor."""
        if not self.coordinator.data:
            return None
            
        # Map sensor types to data fields
        mapping = {
            "flame": self.coordinator.data.get("flameStatus"),
            "heating": self.coordinator.data.get("heatingEnabled"),
            "tap_water": self.coordinator.data.get("tapWaterEnabled"),
        }
        
        value = mapping.get(self._sensor_type)
        
        if isinstance(value, bool):
            return value
        elif isinstance(value, int) or isinstance(value, float):
            return value > 0
        else:
            return False
