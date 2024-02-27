import json
from datetime import datetime
from homeassistant.components import conversation
from homeassistant.helpers import intent,entity_registry as er, device_registry as dr, area_registry as ar
from homeassistant.components.homeassistant.exposed_entities import async_should_expose
from homeassistant.util import ulid
from .nodered_connector import NodeRedConnector
from .const import CONF_NODE_RED_HTTP, CONF_NODE_RED_API, CONF_STORE_HISTORY, CONF_HISTORY_CONVERSATIONS, CONF_TRY_HA_FIRST
class ConversationAgent:
    """A conversation agent for HA Conversation Connector."""

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self.supported_languages = ["en"]
        self.conversation_history = []
        self.history_length = self.entry.options.get('history_length', 10)  # Use entry.options to access config flow options
        self.node_red = NodeRedConnector(f"{self.entry.data[CONF_NODE_RED_HTTP]}/{self.entry.data[CONF_NODE_RED_API]}")

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
        context = utterance.context
        va_device = utterance.device_id

        def get_area_of_device(hass, device_id):
            # Get device registry
            dev_registry = dr.async_get(hass)
            # Get area registry
            area_registry = ar.async_get(hass)
            
            # Find the device
            device = dev_registry.async_get(device_id)
            if device is None:
                return None
            
            # Get area_id from the device
            area_id = device.area_id
            if area_id is None:
                return None
            
            # Find the area using area_id
            area = area_registry.async_get_area(area_id)
            if area is None:
                return None
            
            return area.name  # or return area as needed

        va_area = get_area_of_device(self.hass, va_device)

        if self.entry.data[CONF_TRY_HA_FIRST]:
            # Generate a unique conversation ID or use the existing one
            conversation_id = utterance.conversation_id or ulid.ulid_now()

            conversation_result = await conversation.async_converse(self.hass, text, self.supported_languages, context)

            # Check if the response is an IntentResponse object
            if isinstance(conversation_result.response, intent.IntentResponse):
                # If it is, extract the speech text from it
                response_text = conversation_result.response.speech['plain']['speech']
            else:
                response_text = conversation_result.response

            if not conversation_result.response.response_type == intent.IntentResponseType.ERROR:
                # Create an IntentResponse and set the speech
                intent_response = intent.IntentResponse(language="en")
                intent_response.async_set_speech(response_text)
            
                # Return a ConversationResult with the intent response
                return conversation.ConversationResult(
                    response=intent_response, 
                    conversation_id=conversation_result.conversation_id  # Use the conversation_id from the result
                )

       
        def context_to_dict(context):
            # Replace with the actual attributes of the Context object
            return {
                'user_id': context.user_id,
                'parent_id': context.parent_id,
                'id': context.id,
                'device': va_device,
                'area': va_area
                #'language': context.language,
                #'device_id': context.device_id,
                #'device_type': context.device_type,
                #'room_id': context.room_id,
                #'room_name': context.room_name,
                #'user': context.user,
                #'home': context.home,
                #'app': context.app
                         
                # Add more attributes as needed
            }

         # Generate a unique conversation ID or use the existing one
        conversation_id = utterance.conversation_id or ulid.ulid_now()

        # Prepare the content for the POST request
        content = {
            'content': utterance.text,
            'chatid': conversation_id,
            'history': json.dumps(self.conversation_history),
            'exposed_entities': json.dumps(self.get_exposed_entities()),
            'context': json.dumps(context_to_dict(context)) 
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
