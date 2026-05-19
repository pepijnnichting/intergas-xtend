"""Diagnostics support for Intergas Xtend."""
from __future__ import annotations

from homeassistant.core import HomeAssistant

from . import IntergasXtendConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: IntergasXtendConfigEntry,
) -> dict:
    """Return diagnostics for a config entry.

    No sensitive data to redact — the Xtend has no authentication.
    """
    coordinator = entry.runtime_data.coordinator
    return {
        "entry_data": dict(entry.data),
        "coordinator_last_update_success": coordinator.last_update_success,
        "coordinator_data": coordinator.data,
    }
