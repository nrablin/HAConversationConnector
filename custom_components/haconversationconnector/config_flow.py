"""Config flow for HA Conversation Connector."""
from homeassistant import config_entries

class HAConversationConnectorConfigFlow(config_entries.ConfigFlow, domain="haconversationconnector"):
    """Handle a config flow for HA Conversation Connector."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
            )

        return self.async_create_entry(
            title="HA Conversation Connector",
            data=user_input,
        )