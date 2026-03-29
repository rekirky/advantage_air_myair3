"""Number platform for Advantage Air MyAir3 — zone damper percentage."""
import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
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
    """Set up zone percentage sliders from a config entry."""
    coordinator: MyAirCoordinator = hass.data[DOMAIN][entry.entry_id]
    num_zones = coordinator.data.get("num_zones", 8)

    entities = []
    for zone_id in range(1, num_zones + 1):
        zone = coordinator.data.get("zones", {}).get(zone_id, {})
        if zone.get("percent_avail", True):
            entities.append(ZonePercentNumber(coordinator, zone_id))

    async_add_entities(entities)


class ZonePercentNumber(CoordinatorEntity, NumberEntity):
    """Damper opening percentage slider for a single zone."""

    _attr_mode = NumberMode.SLIDER
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_native_step = 5

    def __init__(self, coordinator: MyAirCoordinator, zone_id: int) -> None:
        super().__init__(coordinator)
        self._zone_id = zone_id
        self._attr_unique_id = f"{coordinator.ip_address}_zone_{zone_id}_percent"

    @property
    def name(self) -> str:
        zone = self.coordinator.data.get("zones", {}).get(self._zone_id, {})
        return f"{zone.get('name', f'Zone {self._zone_id}')} Damper"

    @property
    def native_min_value(self) -> float:
        zone = self.coordinator.data.get("zones", {}).get(self._zone_id, {})
        return float(zone.get("min_damper", 0))

    @property
    def native_max_value(self) -> float:
        zone = self.coordinator.data.get("zones", {}).get(self._zone_id, {})
        return float(zone.get("max_damper", 100))

    @property
    def native_value(self) -> float:
        zone = self.coordinator.data.get("zones", {}).get(self._zone_id, {})
        return float(zone.get("percent", 0))

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_zone_percent(self._zone_id, int(value))
