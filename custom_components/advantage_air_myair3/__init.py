"""The integration for Advantage Air MyAir3 system."""
import logging
DOMAIN = "advantage_air_myair3"

_LOGGER = logging.getLogger(__name__)

def setup(hass, config):
    hass.states.set("advantage_air_myair3.integration", "Ready")

    _LOGGER.info("Advantage Air MyAir 3 Ready!")

    # Return boolean to indicate that initialization was successful.
    return True