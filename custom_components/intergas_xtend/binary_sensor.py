"""Binary sensor platform for Intergas Xtend integration."""
import logging
from dataclasses import dataclass
from typing import Callable, Dict, Optional

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    KEY_FLAME,
    KEY_HEATING,
    KEY_HEATING_ENABLED,
    KEY_PUMP,
    KEY_TAPWATER,
    KEY_TAPWATER_ENABLED,
    KEY_COOLING_ENABLED,
)

_LOGGER = logging.getLogger(__name__)

@dataclass
class IntergasXtendBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing Intergas Xtend binary sensor entities."""

    is_on_fn: Optional[Callable[[Dict], bool]] = None


BINARY_SENSOR_DESCRIPTIONS: tuple[IntergasXtendBinarySensorEntityDescription, ...] = (
    IntergasXtendBinarySensorEntityDescription(
        key=KEY_FLAME,
        name="Flame",
        device_class=BinarySensorDeviceClass.HEAT,
        icon="mdi:fire",
        is_on_fn=lambda data: data.get(KEY_FLAME, False),
    ),
    IntergasXtendBinarySensorEntityDescription(
        key=KEY_HEATING,
        name="Heating",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:radiator",
        is_on_fn=lambda data: data.get(KEY_HEATING, False),
    ),
    IntergasXtendBinarySensorEntityDescription(
        key=KEY_TAPWATER,
        name="Tap Water",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:water",
        is_on_fn=lambda data: data.get(KEY_TAPWATER, False),
    ),
    IntergasXtendBinarySensorEntityDescription(
        key=KEY_PUMP,
        name="Pump",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:water-pump",
        is_on_fn=lambda data: data.get(KEY_PUMP, False),
    ),
    IntergasXtendBinarySensorEntityDescription(
        key=KEY_HEATING_ENABLED,
        name="Heating Enabled",
        device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:radiator",
        is_on_fn=lambda data: data.get(KEY_HEATING_ENABLED, False),
    ),
    IntergasXtendBinarySensorEntityDescription(
        key=KEY_TAPWATER_ENABLED,
        name="Tap Water Enabled",
        device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:water",
        is_on_fn=lambda data: data.get(KEY_TAPWATER_ENABLED, False),
    ),
    IntergasXtendBinarySensorEntityDescription(
        key=KEY_COOLING_ENABLED,
        name="Cooling Enabled",
        device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:snowflake",
        is_on_fn=lambda data: data.get(KEY_COOLING_ENABLED, False),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Intergas Xtend binary sensors."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    
    sensors = []
    
    for description in BINARY_SENSOR_DESCRIPTIONS:
        sensors.append(IntergasXtendBinarySensor(coordinator, entry.entry_id, description))
    
    async_add_entities(sensors)


class IntergasXtendBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of an Intergas Xtend binary sensor."""

    def __init__(
        self, coordinator, entry_id, description: IntergasXtendBinarySensorEntityDescription
    ):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._entry_id = entry_id
        self._attr_has_entity_name = True
        
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
    def is_on(self):
        """Return true if the binary sensor is on."""
        if not self.coordinator.data:
            return None
            
        is_on_fn = self.entity_description.is_on_fn
        if is_on_fn is not None:
            return is_on_fn(self.coordinator.data)
            
        return None
