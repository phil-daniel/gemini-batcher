import json
import time
import logging
from typing import Any
from collections import defaultdict
from pathlib import Path
from dataclasses import dataclass

from google import genai
from google.genai import types, errors
from google.genai.chats import Chat

from ..utils import exceptions
from ..utils.exception_parser import ExceptionParser

@dataclass
class Response:
    """
    Represents the response from an API call to a Gemini model, this is a slightly simplified response with less attributes.

    Attributes:
        content (Any): The contents of the response, the exact type could depend on the specific API call.
        input_tokens (int): The number of input tokens used by the query to the model.
        output_tokens (int): The number of output tokens used to generate the response.
    """

    content : Any
    input_tokens : int
    output_tokens : int

class GeminiApi:

    def __init__(
        self,
        api_key : str,
        **kwargs
    ) -> None:
        # TODO: Error handling - Api key not correct
        self.client = genai.Client(api_key=api_key, **kwargs)

        self.cache = defaultdict(lambda : None)
        self.files = defaultdict(lambda : None)
    
    def parse_json(
        self,
        to_parse : str,
    ) -> dict | list | str | int | float | bool | None:
        """
        Parses a JSON-formatted string string into it's corresponding Python object.

        Args:
            to_parse (str): A string containing JSON data.

        Returns:
            Various: The Python representation of the JSON input. The exact type returned depends on the JSON input.

        Raises:
            json.JSONDecodeError: This occurs if the input string is not valid JSON.
        """
        try:
            parsed = json.loads(to_parse)
        except json.JSONDecodeError as e: 
            logging.error(f"Error whilst decoding the inputted json. Further information: {e}")
            raise
        return parsed
    
    def get_model_token_limits(
        self,
        model : str
    ) -> tuple[int, int]:
        """
        Retrieves the input and output token limit of the current model.

        Args:
            model (str): The name of the Gemini model.
        
        Returns:
            tuple[int, int]: A tuple, where the first element is the maximum number of input tokens and the second element is the maximum number of output tokens.
        """
        model_info = self.client.models.get(model=model)
        input_token_limit = model_info.input_token_limit
        output_token_limit = model_info.output_token_limit

        return input_token_limit, output_token_limit

    def count_tokens(
            self,
            model : str,
            contents : Any
        ) -> int:
        """
        Returns the number of tokens a content block contains.

        Args:
            model (str): The name of the Gemini model.
            contents (Any): The content to be tokenised and counted.
        
        Returns:
            int: The number of tokens contained within the input object.
        """

        return self.client.models.count_tokens(
            model=model,
            contents = contents
        )

    def add_to_cache(
        self,
        model : str,
        filepath : str,
        cache_name : str = None,
        ttl : int = 300,
    ) -> None:
        # TODO: Error handling if there is an issue with caching on the specified model.

        # cache_name defaults to the filepath if it has not explicitly been defined
        if cache_name == None:
            cache_name = filepath

        if filepath not in self.files.keys():
            self.upload_file(filepath)
        
        # Retrieving the uploaded file obejct
        uploaded_file = self.files[filepath]

        # Adding the file to the cache
        cached_file = self.client.caches.create(
            model = model,
            config = types.CreateCachedContentConfig(
                display_name = cache_name,
                contents = [uploaded_file],
                ttl = f'{ttl}s'
            )
        )

        self.cache[cache_name] = cached_file
        return

    def upload_file(
        self,
        filepath : str,
    ) -> None:
        path = Path(filepath)
        if not path.exists():
            logging.error(f"File {filepath} not found.")
            raise FileNotFoundError(f"File {filepath} not found.")

        uploaded_file = self.client.files.upload(file=filepath)
        while uploaded_file.state.name == "PROCESSING" or uploaded_file.state.name == "PENDING":
            logging.info(f'Waiting for file {filepath} to upload, current state is {uploaded_file.state.name}')
            time.sleep(5)
        # TODO: Add error handling if upload was not successful
        self.files[filepath] = uploaded_file
        return
    
    def create_custom_content_config(
        self,
        **kwargs 
    ) -> types.GenerateContentConfig:
        config = types.GenerateContentConfig(
            **kwargs
        )
        return config
        

    def make_api_call(
        self,
        model : str,
        **kwargs
    ):
        # TODO: Other errors to handle - any network problems? Input token limit exceeded
        try:
            response = self.client.models.generate_content(**kwargs)

            if response.candidates[0].finish_reason != types.FinishReason.STOP:
                # If 'finish_reason != STOP' then the token generation did not finish naturally.
                if response.candidates[0].finish_reason == types.FinishReason.MAX_TOKENS:
                    # If 'finish_reason == MAX_TOKENS' then token generation ended as the output token limit was exceeded.
                    logging.error("Token generation finished unnatural as output token limit was exceeded.")
                    _, output_token_limit = self.get_model_token_limits(model)
                    raise exceptions.MaxOutputTokensExceeded("Token generation finished unnaturally as output token limit was exceeded. "
                                                  f"Limit for the {model} model is {output_token_limit}.")
                else:
                    # There are various other reasons for token generation to end unnaturally, including 'SAFETY', 'RECITATION', etc...
                    # A full list of these can be found at https://ai.google.dev/api/generate-content#FinishReason
                    logging.error(f"Token generation finished unnaturally. The finish reason was {response.candidates[0].finish_reason}")
                    raise exceptions.GeminiFinishError(f"Token generation finished unnaturally. The finish reason was {response.candidates[0].finish_reason}")
                
        except errors.APIError as e:
            if e.code == 429:
                # Error code 429 occurs when API calls to the Gemini model have been rate limited.
                
                time_to_delay = ExceptionParser.parse_rate_limiter_error(e)

                logging.warning(f"API call to Gemini failed due to rate limiting, wait {time_to_delay} seconds before retrying. "
                            f"Error code: {e.code}, error message: {e.message}")
                raise exceptions.RateLimitExceeded(
                    f"API call to Gemini failed due to rate limiting. Error code: {e.code}, error message: {e.message}",
                    time_to_delay
                )
            else:
                # Generic exception for any unidentified error codes.
                logging.error(f"Error occured during API call to Gemini model. Error code: {e.code}, error message: {e.message}")
                raise exceptions.GeminiAPIError("Error occured during API call to Gemini model. "
                                     f"Error code: {e.code}, error message: {e.message}")
    
        except Exception as e:
            logging.error(f"Unidentified error occured during API call. Error details: {e}")
            raise e
        return response

    def generate_content(
        self,
        model : str,
        prompt : str,
        files : list[str] = [],
        cache_name : str = None,
        system_prompt : str = None,
        max_retries : int = 5,
        content_config : types.GenerateContentConfig = None
    ) -> Response:
        # TODO: Check input tokens are below limits.
        # TODO: Improve retry if API failure occurs
        
        if len(files) != 0:
            prompt = [prompt]
            for file in files:
                if file in self.files.keys():
                    uploaded_file = self.files[file]
                else:
                    # TODO: Error handling if the file does not exist.
                    self.upload_file(file)
                    uploaded_file = self.files[file]
                prompt.append(uploaded_file)
        
        if content_config == None:
            # If no custom GenerateContentConfig object has been supplied we create an empty one and add the relavant information.
            content_config = types.GenerateContentConfig()

            content_config.response_mime_type = "application/json"
            content_config.response_schema = list[str]
            content_config.system_instruction = system_prompt
            if cache_name != None:
               content_config.cached_content = self.cache[cache_name]

        for i in range(max_retries):
            try:
                # Making the API call to Gemini
                response = self.make_api_call(
                    model = model,
                    config = content_config,
                    contents = prompt
                )

                # TODO: Information about token usage, this can be used to compare performance between different designs
                input_tokens = response.usage_metadata.prompt_token_count
                output_tokens = response.usage_metadata.candidates_token_count

                return Response(
                    content = self.parse_json(response.text),
                    input_tokens = input_tokens,
                    output_tokens = output_tokens
                )
            except exceptions.MaxOutputTokensExceeded as e:
                # Reraising to be handled by function caller.
                raise e
            except exceptions.MaxInputTokensExceeded as e:
                # Reraising to be handled by function caller.
                raise e
            except exceptions.RateLimitExceeded as e:
                logging.info(f'Rate limit exceeded, waiting {e.retry_delay} seconds before retrying API call')
                logging.debug(f'Exception: {e}')
                time.sleep(e.retry_delay)
            except Exception as e:
                logging.info(f'Unknown expection occured: {e}')
                logging.info("Retrying API call in 20 seconds.")
                time.sleep(20)
                continue
        
        # TODO: Handle failure better
        return Response(
            content = [],
            input_tokens = 0,
            output_tokens = 0
        )
    
    def multi_turn_conversation(
        self,
        model : str,
        prompt : str,
        gemini_chat : Chat = None,
        files : list[str] = [],
        cache_name : str = None,
        system_prompt : str = None,
        max_retries : int = 5,
    ):
        
        # If no chat is provided a new one is created. This chat is returned along with the response allowing for it
        # to be reused.
        if gemini_chat == None:
            gemini_chat = self.client.chats.create(
                model=model
            )
                
        if len(files) != 0:
            prompt = [prompt]
            for file in files:
                if file in self.files.keys():
                    uploaded_file = self.files[file]
                else:
                    # TODO: Error handling if the file does not exist.
                    self.upload_file(file)
                    uploaded_file = self.files[file]
                prompt.append(uploaded_file)

        # TODO: Can this be simplified to just being 'cached_content = None'
        # Adding the cache to the config where neccessary
        if cache_name == None:
            config_type = types.GenerateContentConfig(
                response_mime_type = "application/json",
                response_schema = list[str],
                system_instruction = system_prompt,
            )
        else:
            config_type = types.GenerateContentConfig(
                response_mime_type = "application/json",
                response_schema = list[str],
                system_instruction = system_prompt,
                cached_content = self.cache[cache_name]
            )

        return _, gemini_chat


