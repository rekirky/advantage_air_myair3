# custom_components/myintegration/config_flow.py
from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

from .const import DOMAIN

class MyIntegrationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MyIntegration."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Here you would normally validate the IP address.
            # For simplicity, we'll assume it's always valid.
            # You might want to verify that the device is reachable with the given IP.
            
            # Example validation
            ip_address = user_input.get("ip_address")
            if not self._validate_ip(ip_address):
                errors["base"] = "invalid_ip"
            else:
                await self.async_set_unique_id(ip_address)
                self._abort_if_unique_id_configured()
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
        return MyIntegrationOptionsFlowHandler(config_entry)

class MyIntegrationOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle MyIntegration options."""

    def __init__(self, config_entry):
        """Initialize MyIntegration options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("ip_address", default=self.config_entry.data.get("ip_address")): str,
            })
        )
