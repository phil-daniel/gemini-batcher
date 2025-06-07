from google import genai
from google.genai import types

class GeminiApi:

    def __init__(self, api_key, model):
        # Error handling - Api key not correct
        self.client = genai.Client(api_key=api_key)

        # Error handling - Model not correct, default to a model
        self.model = model

    def make_query(self, prompt):
        response = self.client.models.generate_content(
            model=self.model,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
            contents=prompt
        )
        return response.text