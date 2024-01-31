import json
from datetime import datetime
from homeassistant.components import conversation
from homeassistant.helpers import intent,entity_registry as er
from homeassistant.components.homeassistant.exposed_entities import async_should_expose
from homeassistant.util import ulid
from .nodered_connector import NodeRedConnector
from .const import CONF_NODE_RED_HTTP, CONF_NODE_RED_API, CONF_STORE_HISTORY, CONF_HISTORY_CONVERSATIONS

class ConversationAgent:
    """A conversation agent for HA Conversation Connector."""

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        # Add the supported_languages attribute
        self.supported_languages = ["en"]  # Replace None with a list of languages if your agent only supports specific languages
        self.conversation_history = []
        self.history_length = self.entry.data.get('history_length', 10)  # Default to 10 messages
        self.node_red = NodeRedConnector(f"{self.entry.data[CONF_NODE_RED_HTTP]}/{self.entry.data[CONF_NODE_RED_API]}")

    async def async_process(self, utterance, context=None):
        """Handle a conversation utterance."""
        text = utterance.text

#PLACEHOLDER to try and process with HomeAssistant first
        # Try to process the utterance with Home Assistant
        #conversation_result = await conversation.async_converse(self.hass, text, self.supported_languages, context)

        #if conversation_result != "Sorry, I couldn't understand that":
            # The utterance matches a registered intent
            #https://developers.home-assistant.io/docs/intent_conversation_api#response-types
            # Return the ConversationResult from Home Assistant
        #    return conversation_result
# End Placeholder


        # Generate a unique conversation ID or use the existing one
        conversation_id = utterance.conversation_id or ulid.ulid_now()

        # Prepare the content for the POST request
        content = {
            'content': utterance.text,
            'chatid': conversation_id,
            'history': json.dumps(self.conversation_history),
            'exposed_entities': json.dumps(self.get_exposed_entities())
        }

        status_code, message = await self.hass.async_add_executor_job(
            self.node_red.send_data, content
        )
        if self.entry.data[CONF_STORE_HISTORY]:
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_input": text,
                "response": message,
            })
            self.conversation_history = self.conversation_history[-self.entry.data[CONF_HISTORY_CONVERSATIONS]:]
        # Handle the response from Node-RED
        if status_code == 200:
            response_message = message
        else:
            response_message = "There was an error sending your message to Node-RED."

        # Create an IntentResponse and set the speech
        intent_response = intent.IntentResponse(language="en")
        intent_response.async_set_speech(response_message)
        # Return a ConversationResult with the intent response
        return conversation.ConversationResult(
            response=intent_response, 
            conversation_id="your-conversation-id"  # Replace with your actual conversation ID
        )
    
    def get_exposed_entities(self):
        states = [
            state
            for state in self.hass.states.async_all()
            if async_should_expose(self.hass, conversation.DOMAIN, state.entity_id)
        ]
        entity_registry = er.async_get(self.hass)
        exposed_entities = []
        for state in states:
            entity_id = state.entity_id
            entity = entity_registry.async_get(entity_id)

            aliases = []
            if entity and entity.aliases:
                aliases = list(entity.aliases)  # Convert aliases to a list

            # Get the area_id from the entity
            area_id = entity.area_id if entity else None

            exposed_entities.append(
                {
                    "entity_id": entity_id,
                    "name": state.name,
                    "state": self.hass.states.get(entity_id).state,
                    "aliases": aliases,
                    "area_id": area_id,
                }
            )
        return exposed_entities