"""The integration for Advantage Air MyAir3 system."""
import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

DOMAIN = "advantage_air_myair3"

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Advantage Air MyAir3 from a config entry."""
    # Store the configuration entry in hass.data to make it accessible to the platform
    hass.data[DOMAIN] = {
        "ip_address": entry.data["ip_address"]
    }

    # Set an example state, this can be changed or removed as necessary
    hass.states.set("advantage_air_myair3.integration", "Ready")

    _LOGGER.info("Advantage Air MyAir3 Ready!")

    # Forward the setup to the sensor platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    # Return boolean to indicate that initialization was successful.
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Remove the config entry from hass.data
    hass.data.pop(DOMAIN)
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")

    # Return boolean to indicate the unload was successful
    return True
