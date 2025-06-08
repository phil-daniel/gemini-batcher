import json

from google import genai
from google.genai import types

class GeminiApi:

    def __init__(
            self,
            api_key : str,
            model : str
        ):
        # Error handling - Api key not correct
        self.client = genai.Client(api_key=api_key)

        # Error handling - Model not correct, default to a model
        self.model = model
    
    def parse_json(
            self,
            to_parse : str,
        ):
        # TODO: Error handling - incorrect json formatting.
        parsed = json.loads(to_parse)
        return parsed

    def generate_content(
            self,
            prompt : str,
            system_prompt : str = None
        ):
        
        response = self.client.models.generate_content(
            model=self.model,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                system_instruction=system_prompt
            ),
            contents=prompt
        )

        # TODO: Add retry if API failure occurs

        input_tokens = response.usage_metadata.prompt_token_count
        output_tokens = response.usage_metadata.candidates_token_count
        total_tokens = response.usage_metadata.total_token_count

        print (f'{input_tokens} {output_tokens} {total_tokens}')

        return {
            "text" : self.parse_json(response.text),
            "input tokens" : input_tokens,
            "output tokens" : output_tokens,
            "total_tokens" : total_tokens
        }
    