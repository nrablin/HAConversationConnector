import requests
import json
import logging


class NodeRedConnector:
    """A connector for sending data to Node-RED."""

    def __init__(self, url):
        self.url = url
        self.logger = logging.getLogger(__name__)
    
    def send_data(self, data):
        headers = {'Content-Type': 'application/json'}
        _LOGGER = logging.getLogger(__name__)

        response = requests.post(self.url, headers=headers, data=json.dumps(data))
        

        # Log the response
        _LOGGER.info(f"Received response: {response.status_code} {response.text}")

        # Parse the response
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            _LOGGER.error("Failed to parse response from Node-RED")
            return response.status_code, None

        # Extract the message from the response data
        message = response_data.get('message', {}).get('content')

        return response.status_code, message