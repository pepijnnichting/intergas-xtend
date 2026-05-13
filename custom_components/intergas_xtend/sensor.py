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
    UnitOfTemperature,
    UnitOfPressure,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    FIELD_ROOM_TEMP,
    FIELD_OUTDOOR_TEMP,
    FIELD_HP_SUPPLY_TEMP,
    FIELD_TAPWATER_TEMP,
    FIELD_PRESSURE,
    FIELD_SETPOINT,
    FIELD_MODULATION,
    FIELD_SYSTEM_STATUS,
    XTEND_UNAVAILABLE,
)

_LOGGER = logging.getLogger(__name__)


def _temp(data: Dict, key: str) -> Optional[float]:
    """Return a temperature in °C (scale ×0.01), or None if unavailable."""
    raw = data.get(key)
    if raw is None or raw == XTEND_UNAVAILABLE:
        return None
    return round(raw * 0.01, 2)


def _scaled(data: Dict, key: str, factor: float) -> Optional[float]:
    """Return a value scaled by factor, or None if unavailable."""
    raw = data.get(key)
    if raw is None or raw == XTEND_UNAVAILABLE:
        return None
    return round(raw * factor, 2)


@dataclass
class IntergasXtendSensorEntityDescription(SensorEntityDescription):
    """Class describing Intergas Xtend sensor entities."""

    value_fn: Optional[Callable[[Dict], float]] = None


SENSOR_DESCRIPTIONS: tuple[IntergasXtendSensorEntityDescription, ...] = (
    IntergasXtendSensorEntityDescription(
        key=FIELD_ROOM_TEMP,
        name="Room Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: _temp(data, FIELD_ROOM_TEMP),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_HP_SUPPLY_TEMP,
        name="Heating Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: _temp(data, FIELD_HP_SUPPLY_TEMP),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_OUTDOOR_TEMP,
        name="Outside Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: _temp(data, FIELD_OUTDOOR_TEMP),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_TAPWATER_TEMP,
        name="Tap Water Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: _temp(data, FIELD_TAPWATER_TEMP),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_PRESSURE,
        name="Water Pressure",
        native_unit_of_measurement=UnitOfPressure.BAR,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: _scaled(data, FIELD_PRESSURE, 0.01),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_SETPOINT,
        name="Temperature Setpoint",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: _temp(data, FIELD_SETPOINT),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_MODULATION,
        name="Modulation",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:percent",
        value_fn=lambda data: _scaled(data, FIELD_MODULATION, 0.01),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_SYSTEM_STATUS,
        name="Status",
        icon="mdi:information",
        value_fn=lambda data: data.get(FIELD_SYSTEM_STATUS),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Intergas Xtend sensors."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    async_add_entities(
        IntergasXtendSensor(coordinator, entry.entry_id, description)
        for description in SENSOR_DESCRIPTIONS
    )


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

