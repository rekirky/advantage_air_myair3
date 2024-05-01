"""Platform for sensor integration."""
from __future__ import annotations

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

from homeassistant.components.binary_sensor import (
BinarySensorEntity,
BinarySensorDeviceClass
)


import requests
import xml.etree.ElementTree as ET

url = "http://192.168.86.56/"

def login():
    global url
    site = f"{url}login"
    params = {"password": "password"}
    response = requests.get(site, params=params)

def get_on_off():
    global url
    login()
    site = f"{url}getSystemData"
    response = requests.get(site)
    root = ET.fromstring(response.text)
    aircon_on_off = root.find(".//airconOnOff").text
    return(aircon_on_off)

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    sensors = [ZonePowerSensor(i) for i in range(1,7)]
    add_entities(sensors, PowerSensor())

def get_zone_on_off(zone):
    global url
    login()
    site = f"{url}getZoneData?zone={zone}"
    response = requests.get(site)
    root = ET.fromstring(response.text)
    zone_on_off = root.find(".//setting").text
    return(zone_on_off)

def get_zone_name(zone):
    global url
    login()
    site = f"{url}getZoneData?zone={zone}"
    root = ET.fromstring(response.text)
    zone_name = root.find(".//name").text
    return(zone_name)

class PowerSensor(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Air Con Power"
    
    def update(self) -> None:
        self._attr_native_value = get_on_off()
    

class ZonePowerSensor(SensorEntity):
    def __init__(self,zone):
        self.zone = zone
        self.name = get_zone_name(zone)
        self._attr_name = f"{name} (Zone {zone}) Power"

    def update(self) -> None:
        self._attr_native_value = get_zone_on_off(self.zone)


