"""Switch platform for Advantage Air MyAir3."""
import logging

from homeassistant.components.switch import SwitchEntity
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
    """Set up switches from a config entry."""
    coordinator: MyAirCoordinator = hass.data[DOMAIN][entry.entry_id]
    num_zones = coordinator.data.get("num_zones", 8)

    entities = [AirConSwitch(coordinator)]
    for zone_id in range(1, num_zones + 1):
        entities.append(ZoneSwitch(coordinator, zone_id))

    async_add_entities(entities)


class AirConSwitch(CoordinatorEntity, SwitchEntity):
    """Main air con on/off switch."""

    def __init__(self, coordinator: MyAirCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_name = "Air Con Power"
        self._attr_unique_id = f"{coordinator.ip_address}_power"

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("aircon_on_off") == "1"

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_set_system(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_system(False)


class ZoneSwitch(CoordinatorEntity, SwitchEntity):
    """On/off switch for a single zone."""

    def __init__(self, coordinator: MyAirCoordinator, zone_id: int) -> None:
        super().__init__(coordinator)
        self._zone_id = zone_id
        self._attr_unique_id = f"{coordinator.ip_address}_zone_{zone_id}"

    @property
    def name(self) -> str:
        zone = self.coordinator.data.get("zones", {}).get(self._zone_id, {})
        return zone.get("name", f"Zone {self._zone_id}")

    @property
    def is_on(self) -> bool:
        zone = self.coordinator.data.get("zones", {}).get(self._zone_id, {})
        return zone.get("setting") == "1"

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_set_zone(self._zone_id, True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_zone(self._zone_id, False)
