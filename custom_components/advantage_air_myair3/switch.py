from homeassistant.components.switch import SwitchEntity
import logging

_LOGGER = logging.getLogger(__name__)

class MySwitch(SwitchEntity):
    def __init__(self):
        self._is_on = False

    @property
    def name(self):
        """Name of the entity."""
        return "My Switch"

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._is_on

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self._is_on = True

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        self._is_on = False

def setup_platform(hass, config, add_devices, discovery_info=None):
    _LOGGER.info("Setting up virtual switch")
    add_devices([MySwitch()])
    return True