# Intergas Xtend — Copilot Instructions

This is a Home Assistant custom integration for the **Intergas Xtend hybrid heat pump**.
Target: **HA 2026.5+**, Python 3.12, distributed via HACS.

---

## Project structure

```
custom_components/intergas_xtend/
  __init__.py          # Setup, coordinator, IntergasXtendData, IntergasXtendConfigEntry
  intergas_api.py      # Async HTTP API client (no cloud, direct Wi-Fi)
  sensor.py            # 29 sensor entities
  binary_sensor.py     # 5 binary sensor entities
  climate.py           # Read-only climate entity
  config_flow.py       # Config flow + options flow
  const.py             # All field codes, constants
  strings.json         # Source strings (HA convention)
  manifest.json        # Integration manifest
translations/
  en.json              # English translations (loaded by HA)
  nl.json              # Dutch translations
dashboard.yaml         # Pre-built Lovelace dashboard (sections layout)
```

---

## API

- The Xtend acts as its own **Wi-Fi access point** at `10.20.30.1` — never connects to home network.
- HA must have both Ethernet (home network) and Wi-Fi (Xtend AP) active simultaneously.
- Endpoint: `GET http://10.20.30.1:80/api/stats/values?fields=<comma-separated hex codes>`
- Response: `{"stats": {"<hex_code>": <raw_int>, ...}}`
- Scaling: most fields are **int16 × 0.01**. See `const.py` for per-field factors.
- Unavailable sentinel: raw value `32767` (0x7FFF) means the field is not available.
- All field hex codes are defined in `const.py` with inline comments explaining unit and scale.
- All fields are fetched in **one API call** using `ALL_FIELDS` (comma-joined string).

---

## Architecture decisions

### `entry.runtime_data` (HA 2024.4+)

Runtime data is stored on `entry.runtime_data` as a typed `IntergasXtendData` dataclass.
Never use `hass.data[DOMAIN]`.

```python
# __init__.py
@dataclass
class IntergasXtendData:
    api: IntergasXtendApi
    coordinator: DataUpdateCoordinator

type IntergasXtendConfigEntry = ConfigEntry[IntergasXtendData]
```

All platform `async_setup_entry` functions use `IntergasXtendConfigEntry` as type and access data via `entry.runtime_data.coordinator`.

### `DataUpdateCoordinator`

- `always_update=False` — avoids unnecessary recorder writes when data hasn't changed.
- `async_config_entry_first_refresh()` — raises `ConfigEntryNotReady` on first failure.
- `UpdateFailed` from `ConnectionFailedError` → entities go unavailable, coordinator retries.

### Options flow

- Uses `async_update_reload_and_abort` (HA 2024.4+) — no `add_update_listener` needed.
- Only option: `scan_interval` (30–300 s, default 120 s).

### `DeviceInfo`

All platforms return typed `DeviceInfo(...)` from `homeassistant.helpers.device_registry`.
Never return a raw `dict` for `device_info`.

```python
return DeviceInfo(
    identifiers={(DOMAIN, self._entry_id)},
    name="Intergas Xtend",
    manufacturer=MANUFACTURER,
    model="Xtend",
)
```

### Enum sensors

`system_status` and `heatpump_mode` use `SensorDeviceClass.ENUM` with `translation_key`.
State values are slug strings (e.g. `"heating_comfort"`), translated in `translations/en.json` and `translations/nl.json` under `entity.sensor.<key>.state`.

`error_code` and `notification_code` use plain text strings via `_decode()` — too many values for a static `options` list.

### Xtore optional sensors

The Xtore hot water tank is optional. Its fields return `32767` when not connected. All 6 Xtore sensors always exist — they show as unavailable, not missing.

---

## Code style

- **Python 3.12** — use `X | None` not `Optional[X]`, `dict[str, int]` not `Dict[str, int]`.
- Use `from collections.abc import Callable` not `from typing import Callable`.
- No `from typing import` at all — all needed types are either builtins or `collections.abc`.
- Import order: stdlib → HA → local (`.` imports always last in the HA block).
- No `hass.data` usage anywhere.
- No `add_update_listener` pattern.
- No `FlowResult` from `data_entry_flow` — use `ConfigFlowResult` from `config_entries`.
- `OptionsFlowHandler` has no `__init__` — HA injects `self.config_entry` automatically.
- `raise SomeException()` always with parentheses.
- `suggested_display_precision` on all measurement sensors (temp=1, pressure=2, flow=1, kW=2, W=0, COP=1, %=0).

---

## Quality Scale — Bronze & Silver (required)

All code must comply with the **HA Integration Quality Scale** Bronze and Silver tiers.
Every change must keep the integration passing both levels.

### Bronze requirements (all met)

- `config_flow` with unique ID and `_abort_if_unique_id_configured()` outside `try/except`
- `DataUpdateCoordinator` with `always_update=False`
- `entry.runtime_data` — never `hass.data[DOMAIN]`
- `async_config_entry_first_refresh()` → `ConfigEntryNotReady` on first failure
- `OptionsFlowWithReload` — no `add_update_listener`
- `has_entity_name = True` on all entities
- Typed `DeviceInfo(...)` — never a raw `dict`
- `suggested_display_precision` on all measurement sensors
- `EntityCategory.DIAGNOSTIC` on diagnostic sensors
- `strings.json` + `translations/en.json` + `translations/nl.json` in sync

### Silver requirements (all met)

- `PARALLEL_UPDATES = 0` on every coordinator-based platform (`sensor.py`, `binary_sensor.py`, `climate.py`)
- **Test coverage ≥ 95%** — run `pytest --cov=custom_components/intergas_xtend`
- `log-when-unavailable` — handled automatically by `DataUpdateCoordinator`
- `reauthentication-flow` — EXEMPT (no authentication required)

### Gold requirements (all met)

- `diagnostics` — `diagnostics.py` with `async_get_config_entry_diagnostics`
- `reconfiguration-flow` — `async_step_reconfigure` in `ConfigFlow`; uses `async_update_reload_and_abort`
- `entity-translations` — `translation_key=` on all entities; names in `strings.json` + translation files under `entity.<platform>.<key>.name`
- `icon-translations` — `icons.json` (separate file) under `entity.<platform>.<key>.default`; only non-device-class icons (temperature/pressure/energy sensors use device class icon)
- `exception-translations` — `exceptions` section in `strings.json` with `message` per key
- `entity-disabled-by-default` — `entity_registry_enabled_default=False` on Xtore sensors + diagnostic sensors (13 total)
- `devices`, `entity-category`, `entity-device-class` — already satisfied by DeviceInfo, EntityCategory.DIAGNOSTIC, and device_class fields
- `discovery`, `discovery-update-info`, `dynamic-devices`, `stale-devices`, `repair-issues` — all **EXEMPT** (single static device, local polling)
- 7 docs rules met in `README.md`: troubleshooting, diagnostics, supported hardware, known limitations, removal, installation, usage

### Testing rules

- All new code paths must have matching tests in `tests/`.
- Tests use `pytest-homeassistant-custom-component`; `asyncio_mode = auto`.
- `conftest.py` must keep `auto_enable_custom_integrations` autouse fixture.
- Use `MockConfigEntry` + `patch.object(IntergasXtendApi, "get_data", ...)` for integration tests.
- Use direct entity instantiation with a `MagicMock` coordinator for unit tests.
- Coverage must stay ≥ 95% after every change.

---

## Manifest

```json
{
  "domain": "intergas_xtend",
  "iot_class": "local_polling",
  "homeassistant": "2026.5.0"
}
```

Version follows **semver**. Bump patch for bugfixes, minor for new sensors/features, major for breaking changes.
Current: see `manifest.json`.

---

## Dashboard

`dashboard.yaml` uses `type: sections` layout throughout (both views).
Overview contains:

1. **Thermostat** section — `type: thermostat` widget (`column_span: 2`) + status binaries
2. **Live Performance** — 3× `type: gauge` with needle and color segments (COP, Modulation, Pressure)
3. **Temperatures** — tile cards
4. **Power** — tile cards
5. **Energy Totals** — tile cards
6. **Xtore Hot Water Tank** — 2× gauge + tile cards

History view: `type: sections`, each graph in its own section. Statistics graph for energy (30-day bar chart).

---

## Translations

Three files must always be kept in sync:

- `strings.json` — source (HA convention)
- `translations/en.json` — English (what HA actually loads)
- `translations/nl.json` — Dutch

Enum sensor states live under `entity.sensor.<translation_key>.state.<slug>`.

---

## HACS

- `hacs.json` with `{"name": "Intergas Xtend", "render_readme": true}`
- GitHub repo: `https://github.com/pepijnnichting/intergas-xtend`
- Install as custom repository → Integration category
