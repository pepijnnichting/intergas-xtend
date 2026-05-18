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
    MANUFACTURER,
    FIELD_BURNER_STATUS,
    FIELD_SYSTEM_STATUS,
    FIELD_PUMP_SPEED,
    FIELD_HEATPUMP_MODE,
    SYSTEM_STATUS_HEATING,
    SYSTEM_STATUS_TAPWATER,
    HEATPUMP_MODE_OFF,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class IntergasXtendBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing Intergas Xtend binary sensor entities."""

    is_on_fn: Optional[Callable[[Dict], bool]] = None


BINARY_SENSOR_DESCRIPTIONS: tuple[IntergasXtendBinarySensorEntityDescription, ...] = (
    IntergasXtendBinarySensorEntityDescription(
        key=FIELD_BURNER_STATUS,
        name="Flame",
        device_class=BinarySensorDeviceClass.HEAT,
        icon="mdi:fire",
        # Burner status is a flag byte; any non-zero value means burner is active
        is_on_fn=lambda data: bool(data.get(FIELD_BURNER_STATUS, 0)),
    ),
    IntergasXtendBinarySensorEntityDescription(
        key=f"{FIELD_SYSTEM_STATUS}_heating",
        name="Heating",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:radiator",
        # System status 5=Roomheating Comfort, 6=Roomheating Eco, 9=Floor heating
        is_on_fn=lambda data: data.get(FIELD_SYSTEM_STATUS) in SYSTEM_STATUS_HEATING,
    ),
    IntergasXtendBinarySensorEntityDescription(
        key=f"{FIELD_SYSTEM_STATUS}_tapwater",
        name="Tap Water",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:water",
        # System status 4=DHW, 8=DHW Heatexchanger
        is_on_fn=lambda data: data.get(FIELD_SYSTEM_STATUS) in SYSTEM_STATUS_TAPWATER,
    ),
    IntergasXtendBinarySensorEntityDescription(
        key=FIELD_PUMP_SPEED,
        name="Pump",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:water-pump",
        is_on_fn=lambda data: (data.get(FIELD_PUMP_SPEED) or 0) > 0,
    ),
    IntergasXtendBinarySensorEntityDescription(
        key=f"{FIELD_HEATPUMP_MODE}_enabled",
        name="Heatpump Active",
        device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:heat-pump",
        # Heatpump mode 254 means Off; any other value means it is active
        is_on_fn=lambda data: data.get(FIELD_HEATPUMP_MODE) not in (HEATPUMP_MODE_OFF, None),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Intergas Xtend binary sensors."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    async_add_entities(
        IntergasXtendBinarySensor(coordinator, entry.entry_id, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


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
            "manufacturer": MANUFACTURER,
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

