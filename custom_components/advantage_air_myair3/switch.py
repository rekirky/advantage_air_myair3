from homeassistant.components.switch import SwitchEntity
import logging

_LOGGER = logging.getLogger(__name__)

SWITCH_NAME = "My Switch"

class MySwitch(SwitchEntity):
    """Representation of a custom switch."""

    def __init__(self):
        """Initialize the switch."""
        self._is_on = False

    @property
    def name(self):
        """Return the name of the switch."""
        return SWITCH_NAME

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._is_on

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self._is_on = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        self._is_on = False
        self.schedule_update_ha_state()

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the switch platform."""
    _LOGGER.info("Setting up virtual switch")
    add_entities([MySwitch()])
