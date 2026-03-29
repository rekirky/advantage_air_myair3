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

import xml.etree.ElementTree as ET
import aiohttp
import logging

try:
    from .find_ip import find_ip_and_mac
except:
    logging.error(f".find didn't work")
    try:
        from find_ip import find_ip_and_mac
    except:
        logging.error(f"find didn't work")

logger = logging.getLogger(__name__)

global url
url,mac = find_ip_and_mac()
#url = "home19.local"

# Functions to get data
async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
    ) -> None:
    # Set up the sensor platform asynchronously
    sensorpower = [ZonePowerSensor(i) for i in range(1, 7)]
    sensorname = [ZoneNameSensor(i) for i in range (1,7)]
    async_add_entities([PowerSensor()] + sensorpower + sensorname, True)    

async def async_login(hass,session):
    site = f"{url}login"
    params = {"password": "password"}
    try:
        await session.get(site, params=params)
    except aiohttp.ClientError as e:
        logging.error(f"Login failed: {e}")
        # Consider a retry mechanism here

async def async_get_on_off(hass):
    site = f"{url}getSystemData"
    session = async_get_clientsession(hass)  # Use Home Assistant's session management
    await async_login(hass, session)  # Ensure login uses the same session if needed
    try:
        async with session.get(site) as response:
            response_text = await response.text()
            root = ET.fromstring(response_text)
            aircon_on_off = root.find(".//airconOnOff").text
            return aircon_on_off
    except Exception as e:
        logging.error(f"Error fetching system status: {e}")
        return None

async def async_get_zone_on_off(hass, zone):
    """Asynchronously get the on/off status of a zone."""
    site = f"{url}getZoneData?zone={zone}"
    session = async_get_clientsession(hass)  # Get HA's managed session
    await async_login(hass, session)  # Ensure login uses the same session if needed
    try:
        async with session.get(site) as response:
            response_text = await response.text()
            root = ET.fromstring(response_text)
            zone_on_off = root.find(".//setting").text
            return zone_on_off
    except Exception as e:
        logging.error(f"Error fetching zone {zone} status: {e}")
        return None

async def async_get_zone_name(hass, zone):
    site = f"{url}getZoneData?zone={zone}"
    session = async_get_clientsession(hass)
    await async_login(hass, session)  # Ensure login uses the same session if needed
    try:
        async with session.get(site, timeout=10) as response:  # 10 seconds timeout
            response_text = await response.text()
            root = ET.fromstring(response_text)
            zone_name = root.find(".//name").text
            return zone_name.title()
    except Exception as e:
        logging.error(f"Error fetching zone {zone} name: {e}")
        return None

# Classes
class PowerSensor(SensorEntity):
    _attr_name = "Air Con Power"

    async def async_update(self) -> None:
        """Asynchronously update the sensor value."""
        self._attr_native_value = await async_get_on_off(self.hass)
    
class ZonePowerSensor(SensorEntity):
    def __init__(self, zone):
        self.zone = zone
        self._attr_name = f"Air Con Zone {zone} Power" 

    async def async_update(self):
        """Asynchronously update the sensor status."""
        try:
            self._attr_native_value = await async_get_zone_on_off(self.hass, self.zone)
        except Exception as e:
            # Log an error message or handle the exception in a way that's appropriate for your setup
            logging.error(f"Failed to update Zone {self.zone}: {e}")

class ZoneNameSensor(SensorEntity):
    def __init__(self, zone):
        self.zone = zone
        self._attr_name = f"Air Con Zone {zone} Name"

    async def async_update(self):
        try:
            self._attr_native_value = await async_get_zone_name(self.hass,self.zone)
        except Exception as e:
            logging.error(f"Failed to set zone {self.zone} name")
