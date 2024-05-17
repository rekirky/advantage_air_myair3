"""The integration for Advantage Air MyAir3 system."""
import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

DOMAIN = "advantage_air_myair3"
INTEGRATION_STATE = "advantage_air_myair3.integration"
IP_ADDRESS_KEY = "ip_address"

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Advantage Air MyAir3 from a config entry."""
    try:
        # Store the configuration entry in hass.data to make it accessible to the platform
        ip_address = entry.data.get(IP_ADDRESS_KEY)
        if not ip_address:
            raise ValueError("IP address is missing in the configuration entry")

        hass.data[DOMAIN] = {
            IP_ADDRESS_KEY: ip_address
        }

        # Set an example state, this can be changed or removed as necessary
        hass.states.async_set(INTEGRATION_STATE, "Ready")
        _LOGGER.info("Advantage Air MyAir3 Ready!")

        # Forward the setup to the sensor platform
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, "sensor")
        )

        return True
    except Exception as e:
        _LOGGER.error(f"Error setting up Advantage Air MyAir3: {e}")
        return False

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    try:
        # Remove the config entry from hass.data
        hass.data.pop(DOMAIN)
        await hass.config_entries.async_forward_entry_unload(entry, "sensor")
        return True
    except Exception as e:
        _LOGGER.error(f"Error unloading Advantage Air MyAir3: {e}")
        return False
