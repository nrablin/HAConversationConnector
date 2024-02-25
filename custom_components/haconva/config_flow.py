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
    CONF_TRY_HA_FIRST,
    DEFAULT_NODE_RED_HTTP,
    DEFAULT_NODE_RED_API,
    DEFAULT_STORE_HISTORY,
    DEFAULT_HISTORY_CONVERSATIONS,
    DEFAULT_TRY_HA_FIRST,
    DOMAIN,
)
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TemplateSelector,
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
            # Populate form with existing values or default/suggested values
            config_entry = self.hass.config_entries.async_get_entry(self.context["entry_id"]) if "entry_id" in self.context else None
            existing_data = dict(self.config_entry.data) if config_entry else {}
            data_schema = vol.Schema({
                vol.Required(CONF_NODE_RED_HTTP, default=existing_data.get(CONF_NODE_RED_HTTP, DEFAULT_NODE_RED_HTTP)): str,
                vol.Required(CONF_NODE_RED_API, default=existing_data.get(CONF_NODE_RED_API, DEFAULT_NODE_RED_API)): str,
                vol.Optional(CONF_STORE_HISTORY, default=existing_data.get(CONF_STORE_HISTORY, DEFAULT_STORE_HISTORY)): BooleanSelector(),
                vol.Optional(CONF_TRY_HA_FIRST, default=existing_data.get(CONF_TRY_HA_FIRST, DEFAULT_TRY_HA_FIRST)): BooleanSelector(),
                vol.Required(CONF_HISTORY_CONVERSATIONS, default=existing_data.get(CONF_HISTORY_CONVERSATIONS, DEFAULT_HISTORY_CONVERSATIONS)): int,
            })
            # Show the form
            return self.async_show_form(
                step_id="user",
                data_schema=data_schema,
                errors=errors,
            )



