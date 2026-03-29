"""DataUpdateCoordinator for Advantage Air MyAir3."""
import logging
import xml.etree.ElementTree as ET
from datetime import timedelta

import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, PORT, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

_TIMEOUT = aiohttp.ClientTimeout(total=10)


class MyAirCoordinator(DataUpdateCoordinator):
    """Polls the MyAir3 device and exposes system + zone state."""

    def __init__(self, hass, ip_address: str) -> None:
        self.ip_address = ip_address
        self.base_url = f"http://{ip_address}:{PORT}/"
        self.mac: str | None = None
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _login(self, session: aiohttp.ClientSession) -> None:
        """Login to the device and verify authentication."""
        async with session.get(
            f"{self.base_url}login",
            params={"password": "password"},
            timeout=_TIMEOUT,
        ) as resp:
            text = await resp.text()

        root = ET.fromstring(text)
        if root.findtext("authenticated") != "1":
            raise UpdateFailed("MyAir3 login failed — device returned not authenticated")

        if self.mac is None:
            self.mac = root.findtext("mac")

    # ------------------------------------------------------------------
    # Coordinator update
    # ------------------------------------------------------------------

    async def _async_update_data(self) -> dict:
        """Fetch system state and all zone states in one cycle."""
        session = async_get_clientsession(self.hass)
        try:
            await self._login(session)

            # Get system data
            async with session.get(
                f"{self.base_url}getSystemData", timeout=_TIMEOUT
            ) as resp:
                sys_text = await resp.text()

            sys_root = ET.fromstring(sys_text)
            aircon_on_off = sys_root.findtext(".//airconOnOff") or "0"
            num_zones = int(sys_root.findtext(".//numberOfZones") or "8")

            # Get zone data — try all zones in one request first
            zones = await self._fetch_zones(session, num_zones)

            return {
                "aircon_on_off": aircon_on_off,
                "num_zones": num_zones,
                "zones": zones,
            }

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Communication error with MyAir3: {err}") from err
        except ET.ParseError as err:
            raise UpdateFailed(f"Failed to parse MyAir3 response: {err}") from err

    async def _fetch_zones(
        self, session: aiohttp.ClientSession, num_zones: int
    ) -> dict:
        """Fetch zone data. Tries zone=* first, falls back to individual requests."""
        async with session.get(
            f"{self.base_url}getZoneData",
            params={"zone": "*"},
            timeout=_TIMEOUT,
        ) as resp:
            text = await resp.text()

        root = ET.fromstring(text)
        zones = self._parse_zones(root, num_zones)

        # If zone=* isn't supported (returns empty), fetch individually
        if not zones:
            _LOGGER.debug("zone=* returned no data, fetching zones individually")
            for i in range(1, num_zones + 1):
                async with session.get(
                    f"{self.base_url}getZoneData",
                    params={"zone": i},
                    timeout=_TIMEOUT,
                ) as resp:
                    text = await resp.text()
                zone_root = ET.fromstring(text)
                zones.update(self._parse_zones(zone_root, num_zones))

        return zones

    @staticmethod
    def _parse_zones(root: ET.Element, num_zones: int) -> dict:
        zones = {}
        for i in range(1, num_zones + 1):
            zone_el = root.find(f"zone{i}")
            if zone_el is not None:
                name = zone_el.findtext("name") or f"Zone {i}"
                zones[i] = {
                    "name": name.title(),
                    "setting": zone_el.findtext("setting") or "0",
                }
        return zones

    # ------------------------------------------------------------------
    # Control commands
    # ------------------------------------------------------------------

    async def async_set_system(self, on: bool) -> None:
        """Turn the air con on or off."""
        session = async_get_clientsession(self.hass)
        await self._login(session)
        async with session.get(
            f"{self.base_url}setSystemData",
            params={"airconOnOff": "1" if on else "0"},
            timeout=_TIMEOUT,
        ) as resp:
            await resp.text()
        await self.async_request_refresh()

    async def async_set_zone(self, zone_id: int, on: bool) -> None:
        """Turn a zone on or off."""
        session = async_get_clientsession(self.hass)
        await self._login(session)
        async with session.get(
            f"{self.base_url}setZoneData",
            params={"zone": zone_id, "zoneSetting": "1" if on else "0"},
            timeout=_TIMEOUT,
        ) as resp:
            await resp.text()
        await self.async_request_refresh()
