from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
import asyncio
import logging

from .const import DOMAIN
from .find_ip import find_ip_and_mac

_LOGGER = logging.getLogger(__name__)
_LOGGER.info(f"Const_Flow Hit - {DOMAIN}")

class AdvantageAirMyAir3ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Advantage Air MyAir3."""
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize the config flow."""
        self._ip_address = None
        self._mac_address = None
        _LOGGER.info("AdvantageAirMyAir3ConfigFlow initialized")

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is None:
            if not self._ip_address or not self._mac_address:
                try:
                    self._ip_address, self._mac_address = await self.hass.async_add_executor_job(find_ip_and_mac)
                    _LOGGER.info(f"IP & MAC Found: IP={self._ip_address}, MAC={self._mac_address}")
                except Exception as e:
                    _LOGGER.error(f"Error finding IP and MAC: {e}")
                    errors["base"] = "ip_discovery_error"
                    return self.async_show_form(
                        step_id="user", 
                        data_schema=vol.Schema({
                            vol.Required("ip_address"): str,
                        }), 
                        errors=errors
                    )

            if not self._ip_address or not self._mac_address:
                errors["base"] = "ip_discovery_error"
            else:
                await self.async_set_unique_id(self._mac_address)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Advantage Air IP Address", data={"ip_address": self._ip_address})

        return self.async_show_form(
            step_id="user", 
            data_schema=vol.Schema({
                vol.Required("ip_address"): str,
            }), 
            errors=errors
        )

class AdvantageAirMyAir3OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Advantage Air MyAir3 options."""

    def __init__(self, config_entry):
        """Initialize AdvantageAirMyAir3 options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        ip_address = self.config_entry.data.get("ip_address", AdvantageAirMyAir3ConfigFlow._ip_address)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("ip_address", default=ip_address): str,
            })
        )
