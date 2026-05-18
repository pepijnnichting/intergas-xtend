"""Sensor platform for Intergas Xtend integration."""
import logging
from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    EntityCategory,
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import IntergasXtendConfigEntry

from .const import (
    DOMAIN,
    MANUFACTURER,
    XTEND_UNAVAILABLE,
    FIELD_ROOM_TEMP,
    FIELD_OUTDOOR_TEMP,
    FIELD_HP_SUPPLY_TEMP,
    FIELD_HP_RETURN_TEMP,
    FIELD_BOILER_DHW_TEMP,
    FIELD_XTORE_HOT_TEMP,
    FIELD_SETPOINT,
    FIELD_REQUESTED_TEMP,
    FIELD_PRESSURE,
    FIELD_FLOW_RATE,
    FIELD_HP_POWER_THERMAL,
    FIELD_BOILER_POWER_THERMAL,
    FIELD_POWER_ELECTRIC,
    FIELD_COP,
    FIELD_ENERGY_THERMAL_HEATING,
    FIELD_ENERGY_ELECTRIC_HEATING,
    FIELD_ENERGY_THERMAL_BOILER,
    FIELD_ENERGY_THERMAL_DHW,
    FIELD_ENERGY_THERMAL_COOLING,
    FIELD_ENERGY_ELECTRIC_DHW,
    FIELD_DHW_COLD_TEMP,
    FIELD_DHW_PREHEAT_TEMP,
    FIELD_DHW_FLOW_RATE,
    FIELD_DHW_PUMP_SPEED,
    FIELD_DHW_POWER_THERMAL,
    FIELD_MODULATION,
    FIELD_SYSTEM_STATUS,
    FIELD_HEATPUMP_MODE,
    FIELD_ERROR_CODE,
    FIELD_NOTIFICATION_CODE,
    FIELD_HEATING_HOURS,
    FIELD_COOLING_HOURS,
    FIELD_DHW_HOURS,
    FIELD_SOFTWARE_VERSION,
)

_LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Enum → human-readable string mappings
# ---------------------------------------------------------------------------

_SYSTEM_STATUS: dict[int, str] = {
    0: "monitor_lockout",  1: "pump_venting",    2: "service",
    3: "defrost",          4: "hot_water",        5: "heating_comfort",
    6: "heating_eco",      7: "cooling",          8: "hot_water_hx",
    9: "floor_heating",   12: "anti_freeze",     13: "pump_maintenance",
    14: "idle",          255: "standby",
}

_HEATPUMP_MODE: dict[int, str] = {
    0: "hot_water", 1: "heating", 2: "cooling",
    253: "pumpdown", 254: "off", 255: "undefined",
}

_ERROR_CODES: dict[int, str] = {
    0: "None", 255: "No Error", 65535: "Unconnected",
    1: "Defrost Failed",                2: "Low Pressure",
    3: "High Pressure",                 4: "Compressor Outside Range",
    5: "Exhaust Temp Too High",         6: "Condenser Temp Too High",
    7: "Outdoor Unit Auto Restart",     8: "Outdoor Unit Locked",
    9: "Outdoor Unit Control Guard",   10: "Water Flow Too Low",
    11: "Water Flow Too Low (Defrost)", 12: "Condenser Gas Too Low",
    13: "No Outdoor Sensor",           14: "Pumpdown Failed",
    15: "DSH Too Low",                 16: "SSH Too Low",
    17: "SSH Too High",                18: "Cooling Mode Temps",
    19: "Condenser Liquid Sensor",     20: "Water Inlet Sensor",
    21: "Water Outlet Sensor",         22: "Refrigerant Liquid Sensor",
    23: "Refrigerant Gas Sensor",     128: "AC Bus Voltage High",
    129: "AC Bus Voltage Low",        130: "DC Bus Overvoltage",
    131: "Compressor Overcurrent (HW)", 132: "Compressor Overcurrent (FW)",
    133: "AC Input Overcurrent (HW)",  134: "AC Input Overcurrent (FW)",
    135: "Compressor Current Overload", 136: "Phase Loss",
    137: "IPM Temp Protection",        138: "Outdoor DC Fan Fault",
    139: "Suction Temp Sensor",        140: "Discharge Temp Sensor",
    141: "Coil Temp Sensor",           142: "Ambient Temp Sensor",
    143: "Discharge Temp High",        144: "Condensing Temp High",
    145: "Outdoor-Indoor Comms Error", 146: "DC Bus Undervoltage",
}

_NOTIFICATION_CODES: dict[int, str] = {
    255: "None",              0: "Parameter Out of Bounds",
    1: "Low Pressure",        2: "No Pressure",
    8: "Heatpump Fault",      9: "Heatpump Phase Select",
    10: "Heatpump Remote Off", 11: "Heatpump Failed",
    12: "kWh Meter",          13: "Condenser Overheat",
    14: "Room Thermostat Failed", 15: "Crank Heater",
    16: "Water Temp Sensors", 18: "EEPROM Broken",
    19: "BMM Broken",         20: "No Flow DHW Circuit",
    21: "No Flow CH Circuit", 22: "Flow Control Disabled",
    23: "Commissioning Low Flow", 26: "RTC Time Invalid",
    27: "RTC Clock",          31: "Unknown",
    32: "Defrost Timeout",    33: "Defrost Monitor Timeout",
    37: "HP Return Sensor",   38: "HP Supply Sensor",
    39: "System Supply Sensor", 40: "Outdoor Sensor",
    41: "Condenser Liquid Sensor", 42: "Condenser Gas Sensor",
    46: "Boiler Return Sensor", 47: "Boiler Supply Sensor",
    48: "Boiler Flow Too High", 49: "Boiler Flow Too Low",
    50: "Boiler Flow Reversed", 51: "Boiler Fault",
    52: "Boiler OpenTherm Fault", 53: "Boiler Max Setting",
    54: "Boiler No CH Response", 60: "Thermostat Version",
    73: "Refrigerant Low",
}

# ---------------------------------------------------------------------------
# Value helper functions
# ---------------------------------------------------------------------------

def _temp(data: dict, key: str) -> float | None:
    """Temperature in °C (int16 ×0.01); None when unavailable (32767)."""
    raw = data.get(key)
    if raw is None or raw == XTEND_UNAVAILABLE:
        return None
    return round(raw * 0.01, 2)


def _int16(data: dict, key: str, factor: float) -> float | None:
    """Scaled int16 value; None when unavailable (32767)."""
    raw = data.get(key)
    if raw is None or raw == XTEND_UNAVAILABLE:
        return None
    return round(raw * factor, 2)


def _decode(data: dict, key: str, mapping: dict) -> str | None:
    """Decode an integer enum field to a human-readable string."""
    raw = data.get(key)
    if raw is None:
        return None
    return mapping.get(raw, f"Unknown ({raw})")


def _decode_enum(data: dict, key: str, mapping: dict) -> str | None:
    """Decode an integer enum field to a translation-key slug; None for unknown values."""
    raw = data.get(key)
    if raw is None:
        return None
    return mapping.get(raw)


def _delta_t(data: dict) -> float | None:
    """Supply minus return temperature in °C; None when either is unavailable."""
    supply = _temp(data, FIELD_HP_SUPPLY_TEMP)
    ret = _temp(data, FIELD_HP_RETURN_TEMP)
    if supply is None or ret is None:
        return None
    return round(supply - ret, 2)


# ---------------------------------------------------------------------------
# Entity descriptions
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class IntergasXtendSensorEntityDescription(SensorEntityDescription):
    """Sensor description with a value extraction function."""

    value_fn: Callable[[dict], object] | None = None


SENSOR_DESCRIPTIONS: tuple[IntergasXtendSensorEntityDescription, ...] = (
    # --- Temperatures -------------------------------------------------------
    IntergasXtendSensorEntityDescription(
        key=FIELD_ROOM_TEMP,
        name="Room Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: _temp(data, FIELD_ROOM_TEMP),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_OUTDOOR_TEMP,
        name="Outdoor Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: _temp(data, FIELD_OUTDOOR_TEMP),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_HP_SUPPLY_TEMP,
        name="Heating Supply Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: _temp(data, FIELD_HP_SUPPLY_TEMP),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_HP_RETURN_TEMP,
        name="Heating Return Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: _temp(data, FIELD_HP_RETURN_TEMP),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_BOILER_DHW_TEMP,
        name="Hot Water Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: _temp(data, FIELD_BOILER_DHW_TEMP),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_SETPOINT,
        name="Temperature Setpoint",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: _temp(data, FIELD_SETPOINT),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_REQUESTED_TEMP,
        name="Requested Circuit Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:thermometer-auto",
        value_fn=lambda data: _temp(data, FIELD_REQUESTED_TEMP),
    ),
    IntergasXtendSensorEntityDescription(
        key="delta_t",
        name="Delta T",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:thermometer-plus",
        value_fn=_delta_t,
    ),
    # --- Pressure / Flow ----------------------------------------------------
    IntergasXtendSensorEntityDescription(
        key=FIELD_PRESSURE,
        name="Water Pressure",
        native_unit_of_measurement=UnitOfPressure.BAR,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: _int16(data, FIELD_PRESSURE, 0.01),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_FLOW_RATE,
        name="Flow Rate",
        native_unit_of_measurement=UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: _int16(data, FIELD_FLOW_RATE, 0.01),
    ),
    # --- Power --------------------------------------------------------------
    IntergasXtendSensorEntityDescription(
        key=FIELD_HP_POWER_THERMAL,
        name="Heat Pump Thermal Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: _int16(data, FIELD_HP_POWER_THERMAL, 0.001),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_BOILER_POWER_THERMAL,
        name="Boiler Thermal Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: _int16(data, FIELD_BOILER_POWER_THERMAL, 0.001),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_POWER_ELECTRIC,
        name="Electric Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: _int16(data, FIELD_POWER_ELECTRIC, 1.0),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_COP,
        name="COP",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:gauge",
        value_fn=lambda data: round(data[FIELD_COP] * 0.1, 1)
        if data.get(FIELD_COP) is not None
        else None,
    ),
    # --- Energy totals ------------------------------------------------------
    IntergasXtendSensorEntityDescription(
        key=FIELD_ENERGY_THERMAL_HEATING,
        name="Thermal Energy Heating",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get(FIELD_ENERGY_THERMAL_HEATING),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_ENERGY_ELECTRIC_HEATING,
        name="Electric Energy Heating",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get(FIELD_ENERGY_ELECTRIC_HEATING),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_ENERGY_THERMAL_BOILER,
        name="Thermal Energy Boiler",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get(FIELD_ENERGY_THERMAL_BOILER),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_ENERGY_THERMAL_DHW,
        name="Thermal Energy Hot Water",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get(FIELD_ENERGY_THERMAL_DHW),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_ENERGY_THERMAL_COOLING,
        name="Thermal Energy Cooling",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get(FIELD_ENERGY_THERMAL_COOLING),
    ),
    # --- Xtore domestic hot water tank (optional) ---------------------------
    # All fields return 32767 (unavailable) when the Xtore is not connected.
    IntergasXtendSensorEntityDescription(
        key=FIELD_XTORE_HOT_TEMP,
        name="Tank Hot Water Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-boiler",
        value_fn=lambda data: _temp(data, FIELD_XTORE_HOT_TEMP),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_DHW_PREHEAT_TEMP,
        name="Hot Water Preheat Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-thermometer",
        value_fn=lambda data: _temp(data, FIELD_DHW_PREHEAT_TEMP),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_DHW_COLD_TEMP,
        name="Cold Water Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-thermometer-outline",
        value_fn=lambda data: _temp(data, FIELD_DHW_COLD_TEMP),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_DHW_FLOW_RATE,
        name="Hot Water Flow Rate",
        native_unit_of_measurement=UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: _int16(data, FIELD_DHW_FLOW_RATE, 0.01),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_DHW_PUMP_SPEED,
        name="Hot Water Pump Speed",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:pump",
        value_fn=lambda data: _int16(data, FIELD_DHW_PUMP_SPEED, 0.01),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_DHW_POWER_THERMAL,
        name="Hot Water Thermal Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: _int16(data, FIELD_DHW_POWER_THERMAL, 0.001),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_ENERGY_ELECTRIC_DHW,
        name="Electric Energy Hot Water",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get(FIELD_ENERGY_ELECTRIC_DHW),
    ),
    # --- Status (decoded to human-readable text) ----------------------------
    IntergasXtendSensorEntityDescription(
        key=FIELD_SYSTEM_STATUS,
        name="System Status",
        device_class=SensorDeviceClass.ENUM,
        translation_key="system_status",
        options=list(_SYSTEM_STATUS.values()),
        icon="mdi:information",
        value_fn=lambda data: _decode_enum(data, FIELD_SYSTEM_STATUS, _SYSTEM_STATUS),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_HEATPUMP_MODE,
        name="Heat Pump Mode",
        device_class=SensorDeviceClass.ENUM,
        translation_key="heatpump_mode",
        options=list(_HEATPUMP_MODE.values()),
        icon="mdi:heat-pump",
        value_fn=lambda data: _decode_enum(data, FIELD_HEATPUMP_MODE, _HEATPUMP_MODE),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_MODULATION,
        name="Boiler Modulation",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:percent",
        value_fn=lambda data: _int16(data, FIELD_MODULATION, 0.01),
    ),
    # --- Diagnostics --------------------------------------------------------
    IntergasXtendSensorEntityDescription(
        key=FIELD_ERROR_CODE,
        name="Error",
        icon="mdi:alert-circle-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: _decode(data, FIELD_ERROR_CODE, _ERROR_CODES),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_NOTIFICATION_CODE,
        name="Notification",
        icon="mdi:bell-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: _decode(data, FIELD_NOTIFICATION_CODE, _NOTIFICATION_CODES),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_HEATING_HOURS,
        name="Heating Hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get(FIELD_HEATING_HOURS),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_COOLING_HOURS,
        name="Cooling Hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get(FIELD_COOLING_HOURS),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_DHW_HOURS,
        name="Hot Water Hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get(FIELD_DHW_HOURS),
    ),
    IntergasXtendSensorEntityDescription(
        key=FIELD_SOFTWARE_VERSION,
        name="Software Version",
        icon="mdi:chip",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get(FIELD_SOFTWARE_VERSION),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: IntergasXtendConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Intergas Xtend sensors."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        IntergasXtendSensor(coordinator, entry.entry_id, description)
        for description in SENSOR_DESCRIPTIONS
    )


class IntergasXtendSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Intergas Xtend sensor."""

    def __init__(
        self,
        coordinator,
        entry_id: str,
        description: IntergasXtendSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._entry_id = entry_id
        self._attr_has_entity_name = True

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
    def native_value(self):
        """Return the sensor value."""
        if not self.coordinator.data:
            return None
        value_fn = self.entity_description.value_fn
        if value_fn is not None:
            return value_fn(self.coordinator.data)
        return None


