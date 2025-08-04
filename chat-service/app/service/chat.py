import os
import uuid
from google.cloud import dialogflowcx_v3 as dialogflowcx

class ChatService:
    def __init__(self,):
        self.project_id = os.getenv("DIALOGFLOW_PROJECT_ID")
        self.region = os.getenv("REGION", "us-central1")
        self.agent_id = os.getenv("AGENT_ID")
        self.language_code = os.getenv("LANGUAGE_CODE", "pt-br")    

    def get_answer(self, user: str, user_message: str, file: dict = {}):
        """Send a message to Dialogflow CX and get a response."""
        # agent = f"projects/{self.project_id}/locations/{self.region}/agents/{self.agent_id}"
        # session_path = f"{agent}/sessions/{session_id}"
        # client_options = None
        # agent_components = dialogflowcx.AgentsClient.parse_agent_path(agent)
        # location_id = agent_components["location"]

        api_endpoint = f"{self.region}-dialogflow.googleapis.com:443"
        client_options = {"api_endpoint": api_endpoint}
        client = dialogflowcx.SessionsClient(client_options=client_options)

        session_path = client.session_path(self.project_id, self.region, self.agent_id, user)
        # Create the text input
        text_input = dialogflowcx.TextInput(text=user_message)
        query_input = dialogflowcx.QueryInput(text=text_input, language_code=self.language_code)
        query_parameters = dialogflowcx.QueryParameters(parameters={"user": user, "file": file})


        request_obj = dialogflowcx.DetectIntentRequest(
            session=session_path,
            query_input=query_input,
            query_params=query_parameters,
        )

        response = client.detect_intent(request=request_obj)
        fulfillment_messages = [
            msg.text.text[0]
            for msg in response.query_result.response_messages
            if msg.text and msg.text.text
        ]

        return fulfillment_messages