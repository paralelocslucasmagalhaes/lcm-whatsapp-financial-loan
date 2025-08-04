from langchain_google_vertexai import VertexAI
import os

class VertexAIService:

    def __init__(self, model_name: str = "gemini-2.5-pro") -> None:
        self.model_name = os.getenv("MODEL_NAME", model_name)
        self.llm = VertexAI(
            model_name=self.model_name,
            project=os.getenv("PROJECT_ID"),    
            location=os.getenv("REGION"),   
        )

    async def ask(self, message: str):

        """Send a message to the Vertex AI model and get a response."""
        general_instruction = """You are a helpful assistant that extracts information from bills.
        Your goals is to receive a OCR text from a bill and extract the following information:
            - Bill date
            - Bill due date        
            - Bill issuer
            - Bill owner
            - Bill identification number (CPF, RG, CNPJ)
            - Bill address       
        
        You will return a JSON with the following structure:
        {
            "bill_date": "2023-10-01",
            "due_date": "2023-10-15",
            "issuer": "Company Name", 
            "owner": "User Name",
            "identification_number": "12345678900",
            "address": "123 Main St, City, State, Zip"
        }

        If unable to extract the information, return an empty JSON object {}.
            
        Here the OCR text you need to analyze:

        """

        result = await self.llm.ainvoke([general_instruction + message])
        return result
