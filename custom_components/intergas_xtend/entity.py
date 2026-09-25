"""Shared entity helpers for Intergas Xtend."""

from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, MANUFACTURER


def device_info(entry_id: str) -> DeviceInfo:
    """Return the shared Intergas Xtend device metadata."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry_id)},
        name="Intergas Xtend",
        manufacturer=MANUFACTURER,
        model="Xtend",
    )
