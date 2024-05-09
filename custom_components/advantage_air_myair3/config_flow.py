from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

from const import (DOMAIN)
from find_ip import find_ip_and_mac

logging.info(f"Const_Flow Hit - {DOMAIN}")

class AdvantageAirMyAir3ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Advantage Air MyAir3."""
    logging.info("Hit 1st class")
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL
    _ip_address = None
    _mac_address = None

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is None:
            if not self._ip_address or not self._mac_address:
                self._ip_address, self._mac_address = await self.hass.async_add_executor_job(find_ip_and_mac)
                logging.info(f"IP & Mac Found. {self._ip_address}")

            if self._ip_address is None or self._mac_address is None:
                errors["base"] = "IP Discovery Error - Make sure system is turned on and connected to the same network"
            else:
                await self.async_set_unique_id(self._mac_address)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Advantage Air IP Address", data=self._ip_address)

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({
                vol.Required("ip_address"): str,
            }), errors=errors
        )

class AdvantageAirMyAir3OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle AdvantageAirMyAir3 options."""
    def __init__(self, config_entry):
        """Initialize AdvantageAirMyAir3 options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        ip_address = self.config_entry.data.get("ip_address") if self.config_entry.data.get("ip_address") else AdvantageAirMyAir3ConfigFlow._ip_address
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("ip_address", default=ip_address): str,
            })
        )
