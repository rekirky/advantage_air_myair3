"""Config flow for Advantage Air MyAir3."""
import logging

import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN
from .find_ip import find_ip_and_mac

_LOGGER = logging.getLogger(__name__)


class AdvantageAirMyAir3ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Advantage Air MyAir3."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            ip_address = user_input["ip_address"].strip()

            ip, mac = await self.hass.async_add_executor_job(
                find_ip_and_mac, ip_address
            )

            if ip and mac:
                await self.async_set_unique_id(mac)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="Advantage Air MyAir3",
                    data={"ip_address": ip},
                )

            errors["ip_address"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("ip_address", default="home19.local"): str,
                }
            ),
            errors=errors,
        )