# custom_components/AdvantageAirMyAir3/config_flow.py
from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
import asyncio

from .const import DOMAIN
from find_ip import find_ip_and_mac

class AdvantageAirMyAir3ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Advantage Air MyAir3."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            ip_address, mac_address = await self.hass.async_add_executor_job(find_ip_and_mac)
            if ip_address is None or mac_address is None:
                errors["base"] = "discovery_error"
            else:
                await self.async_set_unique_id(mac_address)
                self._abort_if_unique_id_configured()
                user_input["ip_address"] = ip_address  # Automatically populate IP from discovery
                return self.async_create_entry(title="My Device", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({
                vol.Required("ip_address"): str,
            }), errors=errors
        )

    def _validate_ip(self, ip):
        """Validate the IP address format."""
        import ipaddress
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return AdvantageAirMyAir3OptionsFlowHandler(config_entry)

class AdvantageAirMyAir3OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle AdvantageAirMyAir3 options."""

    def __init__(self, config_entry):
        """Initialize AdvantageAirMyAir3 options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("ip_address", default=self.config_entry.data.get("ip_address")): str,
            })
        )
