# __init__.py
import logging
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from .conversation_agent import ConversationAgent
from homeassistant.components import conversation

from .const import DOMAIN, CONF_NODE_RED_HTTP, CONF_NODE_RED_API, CONF_STORE_HISTORY, CONF_HISTORY_CONVERSATIONS
from .config_flow import HAConversationConnectorConfigFlow

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry) -> bool:
    _LOGGER.info("Setting up HA Conversation Connector from a config entry.")
    
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data

    # Initialize the ConversationAgent and register it with the conversation service
    agent = ConversationAgent(hass, entry)
    conversation.async_set_agent(hass, entry, agent)

    return True

#config_entries.HANDLERS.register(DOMAIN)(HAConversationConnectorConfigFlow)

async def async_setup(hass, config):
    """Set up the HA Conversation Connector component."""
    return True

async def async_unload_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry) -> bool:
    hass.data[DOMAIN].pop(entry.entry_id)

    #conversation.async_unset_agent(hass, entry, agent)
    return True