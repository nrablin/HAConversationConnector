"""The HA Conversation Connector integration."""
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

DOMAIN = "haconva"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the HA Conversation Connector component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up HA Conversation Connector from a config entry."""
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    return True