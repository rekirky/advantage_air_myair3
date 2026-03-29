"""Config flow for Advantage Air MyAir3."""
import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import xml.etree.ElementTree as ET
import aiohttp

from .const import DOMAIN, PORT

_LOGGER = logging.getLogger(__name__)

_TIMEOUT = aiohttp.ClientTimeout(total=10)


async def _test_connection(hass, ip_address: str) -> bool:
    """Try to login to the device and confirm it responds."""
    session = async_get_clientsession(hass)
    try:
        async with session.get(
            f"http://{ip_address}:{PORT}/login",
            params={"password": "password"},
            timeout=_TIMEOUT,
        ) as resp:
            text = await resp.text()
        root = ET.fromstring(text)
        return root.findtext("authenticated") == "1"
    except Exception:
        return False


class AdvantageAirMyAir3ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Advantage Air MyAir3."""

    VERSION = 1

    def __init__(self):
        self._discovered_ip: str | None = None
        self._discovered_mac: str | None = None

    async def async_step_user(self, user_input=None):
        """Initial step — try auto-discovery, fall back to manual entry."""
        errors = {}

        if user_input is not None:
            # User submitted the manual IP form
            ip = user_input["ip_address"].strip()
            if await _test_connection(self.hass, ip):
                return self.async_create_entry(
                    title="Advantage Air MyAir3",
                    data={"ip_address": ip},
                )
            errors["ip_address"] = "cannot_connect"

        elif self._discovered_ip is None:
            # First visit — attempt UDP discovery
            try:
                from .find_ip import find_ip_and_mac
                ip, mac = await self.hass.async_add_executor_job(find_ip_and_mac)
                if ip and mac:
                    self._discovered_ip = ip
                    self._discovered_mac = mac
                    _LOGGER.info("MyAir3 discovered: IP=%s MAC=%s", ip, mac)
            except Exception as err:
                _LOGGER.warning("MyAir3 auto-discovery failed: %s", err)

        if self._discovered_ip and not errors:
            # Auto-discovered — confirm and create entry
            await self.async_set_unique_id(self._discovered_mac)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title="Advantage Air MyAir3",
                data={"ip_address": self._discovered_ip},
            )

        # Show manual IP entry form (discovery failed or connection failed)
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("ip_address", default="home19.local"): str,
            }),
            errors=errors,
        )
