"""Light platform for Advantage Air MyAir3 — zone on/off + strength."""
import logging

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MyAirCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a dimmer-style entity for each zone."""
    coordinator: MyAirCoordinator = hass.data[DOMAIN][entry.entry_id]
    num_zones = coordinator.data.get("num_zones", 8)

    async_add_entities(
        ZoneLight(coordinator, zone_id) for zone_id in range(1, num_zones + 1)
    )


class ZoneLight(CoordinatorEntity, LightEntity):
    """Zone represented as a dimmable light — toggle and set strength (0–100%)."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    def __init__(self, coordinator: MyAirCoordinator, zone_id: int) -> None:
        super().__init__(coordinator)
        self._zone_id = zone_id
        self._attr_unique_id = f"{coordinator.ip_address}_zone_{zone_id}_light"

    def _zone(self) -> dict:
        return self.coordinator.data.get("zones", {}).get(self._zone_id, {})

    @property
    def name(self) -> str:
        zone_name = self._zone().get("name", f"Zone {self._zone_id}")
        return f"{zone_name} Strength"

    @property
    def is_on(self) -> bool:
        return self._zone().get("setting") == "1"

    @property
    def brightness(self) -> int:
        """Return current strength as HA brightness (0–255)."""
        return round(self._zone().get("percent", 0) / 100 * 255)

    async def async_turn_on(self, brightness: int | None = None, **kwargs) -> None:
        """Turn zone on, optionally setting strength from brightness value."""
        if brightness is not None:
            zone = self._zone()
            percent = round(brightness / 255 * 100)
            percent = max(zone.get("min_damper", 0), min(zone.get("max_damper", 100), percent))
            await self.coordinator.async_set_zone_percent(self._zone_id, percent)
        await self.coordinator.async_set_zone(self._zone_id, True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_zone(self._zone_id, False)
