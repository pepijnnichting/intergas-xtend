"""Sensor platform for Intergas Xtend integration."""
import logging
from dataclasses import dataclass
from typing import Callable, Dict, Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    TEMP_CELSIUS,
    PRESSURE_BAR,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    KEY_HEATING_TEMP,
    KEY_MODULATION,
    KEY_OUTSIDE_TEMP,
    KEY_PRESSURE,
    KEY_ROOMTEMP,
    KEY_SETPOINT,
    KEY_STATUS,
    KEY_TAPWATERTEMP,
)

_LOGGER = logging.getLogger(__name__)

@dataclass
class IntergasXtendSensorEntityDescription(SensorEntityDescription):
    """Class describing Intergas Xtend sensor entities."""

    value_fn: Optional[Callable[[Dict], float]] = None


SENSOR_DESCRIPTIONS: tuple[IntergasXtendSensorEntityDescription, ...] = (
    IntergasXtendSensorEntityDescription(
        key=KEY_ROOMTEMP,
        name="Room Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(KEY_ROOMTEMP),
    ),
    IntergasXtendSensorEntityDescription(
        key=KEY_HEATING_TEMP,
        name="Heating Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(KEY_HEATING_TEMP),
    ),
    IntergasXtendSensorEntityDescription(
        key=KEY_OUTSIDE_TEMP,
        name="Outside Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(KEY_OUTSIDE_TEMP),
    ),
    IntergasXtendSensorEntityDescription(
        key=KEY_TAPWATERTEMP,
        name="Tap Water Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(KEY_TAPWATERTEMP),
    ),
    IntergasXtendSensorEntityDescription(
        key=KEY_PRESSURE,
        name="Water Pressure",
        native_unit_of_measurement=PRESSURE_BAR,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(KEY_PRESSURE),
    ),
    IntergasXtendSensorEntityDescription(
        key=KEY_SETPOINT,
        name="Temperature Setpoint",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(KEY_SETPOINT),
    ),
    IntergasXtendSensorEntityDescription(
        key=KEY_MODULATION,
        name="Modulation",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:percent",
        value_fn=lambda data: data.get(KEY_MODULATION),
    ),
    IntergasXtendSensorEntityDescription(
        key=KEY_STATUS,
        name="Status",
        icon="mdi:information",
        value_fn=lambda data: data.get(KEY_STATUS),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Intergas Xtend sensors."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    
    sensors = []
    
    for description in SENSOR_DESCRIPTIONS:
        sensors.append(IntergasXtendSensor(coordinator, entry.entry_id, description))
    
    async_add_entities(sensors)


class IntergasXtendSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Intergas Xtend sensor."""

    def __init__(
        self, coordinator, entry_id, description: IntergasXtendSensorEntityDescription
    ):
        """Initialize the sensor."""
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
    def native_value(self):
        """Return the sensor value."""
        if not self.coordinator.data:
            return None
            
        value_fn = self.entity_description.value_fn
        if value_fn is not None:
            return value_fn(self.coordinator.data)
            
        return None
