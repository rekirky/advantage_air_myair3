"""Platform for sensor integration."""
from __future__ import annotations

import aiohttp
import xml.etree.ElementTree as ET
import logging
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .find_ip import find_ip_and_mac
from .const import DOMAIN

logger = logging.getLogger(__name__)

# Global variable for URL and MAC address
url, mac = find_ip_and_mac()

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform asynchronously."""
    sensors = [PowerSensor()] + [ZonePowerSensor(i) for i in range(1, 7)] + [ZoneNameSensor(i) for i in range(1, 7)]
    async_add_entities(sensors, True)

async def async_login(hass, session):
    """Log in to the system asynchronously."""
    site = f"{url}login"
    params = {"password": "password"}
    try:
        await session.get(site, params=params)
    except aiohttp.ClientError as e:
        logger.error(f"Login failed: {e}")
        # Consider a retry mechanism here

async def async_get_on_off(hass):
    """Fetch system on/off status asynchronously."""
    site = f"{url}getSystemData"
    session = async_get_clientsession(hass)
    await async_login(hass, session)  # Ensure login uses the same session if needed
    try:
        async with session.get(site, timeout=10) as response:
            response_text = await response.text()
            root = ET.fromstring(response_text)
            return root.find(".//setting").text
    except Exception as e:
        logger.error(f"Error fetching system status: {e}")
        return None

async def async_get_zone_on_off(hass, zone):
    """Fetch zone on/off status asynchronously."""
    site = f"{url}getZoneData?zone={zone}"
    session = async_get_clientsession(hass)
    await async_login(hass, session)  # Ensure login uses the same session if needed
    try:
        async with session.get(site, timeout=10) as response:
            response_text = await response.text()
            root = ET.fromstring(response_text)
            return root.find(".//setting").text
    except Exception as e:
        logger.error(f"Error fetching zone {zone} status: {e}")
        return None

async def async_get_zone_name(hass, zone):
    """Fetch zone name asynchronously."""
    site = f"{url}getZoneData?zone={zone}"
    session = async_get_clientsession(hass)
    await async_login(hass, session)  # Ensure login uses the same session if needed
    try:
        async with session.get(site, timeout=10) as response:
            response_text = await response.text()
            root = ET.fromstring(response_text)
            return root.find(".//name").text.title()
    except Exception as e:
        logger.error(f"Error fetching zone {zone} name: {e}")
        return None

class PowerSensor(SensorEntity):
    """Representation of a Power Sensor."""
    _attr_name = "Air Con Power"

    async def async_update(self) -> None:
        """Asynchronously update the sensor value."""
        self._attr_native_value = await async_get_on_off(self.hass)

class ZonePowerSensor(SensorEntity):
    """Representation of a Zone Power Sensor."""
    def __init__(self, zone):
        self.zone = zone
        self._attr_name = f"Air Con Zone {zone} Power"

    async def async_update(self):
        """Asynchronously update the sensor status."""
        try:
            self._attr_native_value = await async_get_zone_on_off(self.hass, self.zone)
        except Exception as e:
            logger.error(f"Failed to update Zone {self.zone}: {e}")

class ZoneNameSensor(SensorEntity):
    """Representation of a Zone Name Sensor."""
    def __init__(self, zone):
        self.zone = zone
        self._attr_name = f"Air Con Zone {zone} Name"

    async def async_update(self):
        """Asynchronously update the sensor name."""
        try:
            self._attr_native_value = await async_get_zone_name(self.hass, self.zone)
        except Exception as e:
            logger.error(f"Failed to set zone {self.zone} name: {e}")
