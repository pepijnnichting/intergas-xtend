"""Sensor platform for Intergas Xtend integration."""
from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, SENSOR_TYPES, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Intergas Xtend sensors."""
    api = hass.data[DOMAIN][entry.entry_id]
    
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="intergas_xtend",
        update_method=api.get_data,
        update_interval=timedelta(seconds=UPDATE_INTERVAL),
    )
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    entities = []
    
    for sensor_type, sensor_info in SENSOR_TYPES.items():
        entities.append(
            IntergasXtendSensor(
                coordinator,
                entry.entry_id,
                sensor_type,
                sensor_info,
                api
            )
        )
    
    async_add_entities(entities)

class IntergasXtendSensor(CoordinatorEntity, SensorEntity):
    """Intergas Xtend Sensor."""

    def __init__(self, coordinator, entry_id, sensor_type, sensor_info, api):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._sensor_type = sensor_type
        self._sensor_info = sensor_info
        self._api = api
        self._attr_unique_id = f"{entry_id}_{sensor_type}"
        self._attr_name = sensor_info["name"]
        self._attr_native_unit_of_measurement = sensor_info.get("unit")
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
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
            
        # Map sensor types to data fields
        mapping = {
            "room_temp": self.coordinator.data.get("roomTemperature"),
            "tap_temp": self.coordinator.data.get("tapWaterTemperature"),
            "boiler_temp": self.coordinator.data.get("boilerTemperature"),
            "pressure": self.coordinator.data.get("waterPressure"),
            "setpoint": self.coordinator.data.get("setpoint"),
        }
        
        value = mapping.get(self._sensor_type)
        
        # Handle special cases or conversions if needed
        if value is not None and self._sensor_type in ["room_temp", "tap_temp", "boiler_temp", "setpoint"]:
            # Convert from Kelvin to Celsius if needed
            if value > 100:  # Likely Kelvin
                value = round(value - 273.15, 1)
                
        return value
