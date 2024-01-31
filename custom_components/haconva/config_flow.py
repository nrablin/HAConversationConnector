# config_flow.py
import logging
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
import voluptuous as vol
from homeassistant.exceptions import HomeAssistantError
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import (
    CONF_NODE_RED_HTTP,
    CONF_NODE_RED_API,
    CONF_STORE_HISTORY,
    CONF_HISTORY_CONVERSATIONS,
    DEFAULT_NODE_RED_HTTP,
    DEFAULT_NODE_RED_API,
    DEFAULT_STORE_HISTORY,
    DEFAULT_HISTORY_CONVERSATIONS,
    DOMAIN,
)
    
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NODE_RED_HTTP, description={"suggested_value": DEFAULT_NODE_RED_HTTP}): str,
        vol.Required(CONF_NODE_RED_API, default=DEFAULT_NODE_RED_API): str,
        vol.Optional(CONF_STORE_HISTORY, default=DEFAULT_STORE_HISTORY): bool,
        vol.Optional(CONF_HISTORY_CONVERSATIONS, default=DEFAULT_HISTORY_CONVERSATIONS): int,
    }
)



_LOGGER = logging.getLogger(__name__)

class APIConnectionError(HomeAssistantError):
    """Error to indicate we can't connect to the API."""

class AuthenticationError(HomeAssistantError):
    """Error to indicate there is an authentication issue."""

#class HAConversationConnectorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):


async def validate_input(hass: HomeAssistant, data: dict) -> None:
    # Replace with your own validation function
    pass

class HAConversationConnectorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
            except APIConnectionError:
                errors["base"] = "cannot_connect"
            except AuthenticationError:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title="HA Conversation Connector",
                    data=user_input
                )
        else:
            # Show the form
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                errors=errors,
            )
    def async_get_options_flow(self):
        return HAConversationConnectorOptionsFlow(self)

class HAConversationConnectorOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_flow):
        self.config_flow = config_flow

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            # Update the config entry options
            return self.async_create_entry(title="HA Conversation Connector", data=user_input)
        else:
            # Show the form
            return self.async_show_form(
                step_id="init",
                data_schema=STEP_USER_DATA_SCHEMA,
            )

