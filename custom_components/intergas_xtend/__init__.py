"""The Intergas Xtend integration."""
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from .intergas_api import IntergasXtendApi, ConnectionFailedError

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.CLIMATE]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Intergas Xtend from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    api = IntergasXtendApi(
        entry.data[CONF_HOST],
        entry.data.get(CONF_PORT, DEFAULT_PORT),
        session=async_get_clientsession(hass),
    )

    async def _async_update_data():
        """Fetch data, converting connection errors to UpdateFailed.

        UpdateFailed tells the coordinator to mark all entities unavailable
        and retry automatically on the next interval. The connection is
        re-established transparently once the Xtend Wi-Fi is back.
        """
        try:
            return await api.get_data()
        except ConnectionFailedError as ex:
            raise UpdateFailed(f"Cannot reach Intergas Xtend: {ex}") from ex

    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"Intergas Xtend {entry.data[CONF_HOST]}",
        update_method=_async_update_data,
        update_interval=timedelta(seconds=scan_interval),
    )

    # Fetch initial data — raises ConfigEntryNotReady on failure so HA retries setup
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        await data["api"].close()

    return unload_ok


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
