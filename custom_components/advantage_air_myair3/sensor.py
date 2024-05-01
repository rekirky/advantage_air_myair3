"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import ( # type: ignore
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature   # type: ignore
from homeassistant.core import HomeAssistant        # type: ignore
from homeassistant.helpers.entity_platform import AddEntitiesCallback   # type: ignore
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType # type: ignore
from homeassistant.helpers.entity import generate_entity_id # type: ignore

from homeassistant.components.binary_sensor import ( # type: ignore
BinarySensorEntity,
BinarySensorDeviceClass
)

from homeassistant.helpers.aiohttp_client import async_get_clientsession # type: ignore

import requests
import xml.etree.ElementTree as ET
import aiohttp

global url
url = "http://192.168.86.56/"

async def async_login(session):
    params = {"password": "password"}
    await session.get(url, params=params)  # Assume this logs you in for subsequent requests

async def async_get_on_off(hass):
    site = f"{url}getSystemData"
    session = async_get_clientsession(hass)  # Use Home Assistant's session management

    try:
        async with session.get(site) as response:
            response_text = await response.text()
            root = ET.fromstring(response_text)
            aircon_on_off = root.find(".//airconOnOff").text
            return aircon_on_off
    except Exception as e:
        print(f"Error fetching system status: {e}")
        return None

async def async_get_zone_on_off(hass, zone):
    """Asynchronously get the on/off status of a zone."""
    await async_login(hass)  # Ensure you're logged in before making the request
    site = f"{url}getZoneData?zone={zone}"
    session = async_get_clientsession(hass)
    
    try:
        async with session.get(site) as response:
            response_text = await response.text()
            root = ET.fromstring(response_text)
            zone_on_off = root.find(".//setting").text
            return zone_on_off
    except Exception as e:
        print(f"Error fetching zone status: {e}")
        return None

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    # Set up the sensor platform asynchronously
    sensors = [ZonePowerSensor(i) for i in range(1, 7)]
    async_add_entities(sensors)


async def async_get_zone_name(hass, zone):
    async_login()
    site = f"{url}getZoneData?zone={zone}"
    session = async_get_clientsession(hass)  # Use Home Assistant's aiohttp session
    try:
        async with session.get(site) as response:
            response_text = await response.text()
            root = ET.fromstring(response_text)
            zone_name = root.find(".//name").text
            return zone_name
    except Exception as e:
        print(f"Error fetching zone name: {e}")
        return None

class PowerSensor(SensorEntity):
    _attr_name = "Air Con Power"
    def update(self) -> None:
        self._attr_native_value = async_get_on_off()
    
class ZonePowerSensor(SensorEntity):
    def __init__(self, zone):
        self.zone = zone
        self._attr_name = f"Zone {zone} Power Sensor"  # Default name until updated

    async def async_update(self):
        """Asynchronously update the sensor status."""
        self._attr_name = await async_get_zone_name(self.hass, self.zone)
        self._attr_native_value = await async_get_zone_on_off(self.hass, self.zone)


