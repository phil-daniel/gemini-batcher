import json
import time
import logging
from typing import Any
from collections import defaultdict
from pathlib import Path
from dataclasses import dataclass

from google import genai
from google.genai import types, errors

from ..utils import exceptions
from ..utils.exception_parser import ExceptionParser

@dataclass
class InternalResponse:
    """
    Represents the response from an API call to a Gemini model, this is a slightly simplified InternalResponse with less attributes.

    Attributes:
        content (Any): The contents of the response, the exact type could depend on the specific API call.
        input_tokens (int): The number of input tokens used by the query to the model.
        output_tokens (int): The number of output tokens used to generate the response.
    """

    content : Any
    input_tokens : int
    output_tokens : int

class GeminiApi:
    """
    A wrapper over the Gemini Python SDK, which provides simplified functionality and additional error handling.

    Attributes:
        client (genai.Client): The gemini client to be used to query the Gemini API.
        cache (defaultdict): A dictionary holding all of the currently cached files.
        files (defaultdict): A dictionary holding all of the currently uploaded files.
    """
    client : genai.Client
    cache : defaultdict
    files : defaultdict

    def __init__(
        self,
        api_key : str,
        **kwargs
    ) -> None:
        """
        Initialises the Gemini API client wrapper. This involves creating a new instance of the `genai.Client` using the provided information.
        It also involves creating dictionaries for storing the references to uploaded files and cached files.

        Args:
            api_key (str): The API used to authenticate requests to the Gemini API.
            **kwargs: Additional keyword arguements passed directly to `genai.Client`, i.e. additional setup options.
        """
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
        """
        Used to upload a provided file to the Gemini API cache. This also involves uploading the file
        to the Gemini API if it has not yet been uploaded.

        Once uploaded to the cache it allows for references to the file to be made in queries without reuploading it.

        Args:
            model (str): The Gemini model to use.
            filepath (str): The path to the local file to cache.
            cache_name (str, optional): A custom name for the cache entry.
                Defaults to the filepath if none is provided.
            ttl (int, optional): Time-to-live for the cache entry in seconds.
                Defaults to 300 seconds.
        """

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
        """
        Uploads a file to the Gemini API for use in later queries.

        Args:
            filepath (str): The path to the local file to be uploaded.
        
        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
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
        """
        Creates a custom content generation configuarion for Gemini API requests.

        This method wraps the `type.GenerateContentConfig` object to allow uses to build flexible and
        reusable request configurations (specifying stuff such as output schema, MIME types, etc).
        
        Args:
            **kwargs: The keyword arguements passed directly to `types.GenerateContentConfig`
        
        Returns:
            types.GenerateContentConfig: A configuration object for requests with the Gemini model.
        """
        config = types.GenerateContentConfig(
            **kwargs
        )
        return config
        

    def make_api_call(
        self,
        model,
        **kwargs
    ) -> types.GenerateContentResponse:
        """
        Makes an API request to the Gemini model and handles errors gracefully.
        
        This method acts as a wrapper around the `generate_content()` function provided in the `google.genai` library.
        It provides additional error handling for rate limiting and token limit failures.

        Args:
            model (str): The name of the Gemini model to use.
            **kwargs: The parameters to pass directly to the API call.

        Returns:
            types.GenerateContentResponse: The raw Gemini API response.

        Raises:
            exceptions.MaxOutputTokensExceeded: If the model stopped because it exceeded the maximum output token limit.
            exceptions.GeminiFinishError: If token generation ended unnatural for a reason other than max tokens (such as safety filters or blocked output).
            exceptions.RateLimitExceeded: If the request was rate-limited (HTTP 429 error)
            exceptions.GeminiAPIError: For generic Gemini API errors caused when using `generate_content`.
            Exception: For any unidentified or unexpected errors. This is reraised.
        """
        try:
            response = self.client.models.generate_content(model=model, **kwargs)

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
    ) -> InternalResponse:
        """
        A high-level wrapper around the `make_api_call()` function that prepares the prompt, attaches additional files,
        applies caching and provides built in retries in case of transient errors. It also returns a simplfiied structured response.
        
        Args:
            model (str): The Gemini model to use for the query.
            prompt (str): The text prompt to provide to the model.
            files (list[str], optional): The filepaths of files to include in the query. These files will be uploaded to the Gemini API
                if they have not yet been. This defaults to [] (i.e. no files to upload).
            cache_name (str, optional): The name of the cache which can be used to reuse pre-uploaded files. This cache must already have been created.
                Defaults to None (i.e. no cached items).
            system_prompt (str, optional): An optional system prompt to help control the model's behaviour.
                This defaults to None. 
            max_retries (int, optional): The number of retry attempt for faillures due to rate limits or transient errors.
                This defaults to 5.
            content_config (types.GenerateContentConfig, optional): A custom content configuration object. If none is provided, a default config
                is created with the following:
                    - JSON response format
                    - `list[str]` schema
            
            Returns:
                InternalResponse: A structured response containing simplified information about the API response. This includes the API's response and 
                    its token usage.
            
            Raises:
                exceptions.MaxOutputTokensExceeded: If then output exceeded the model's token limit.
                exceptions.MaxInputTokensExceeded: If the input exceeded the model's token limit.
                exceptions.RateLimitExceeded: If the API call failed due to the API key's rate limits.
                Exception: Any unknown error during retries.
        """

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

                input_tokens = response.usage_metadata.prompt_token_count
                output_tokens = response.usage_metadata.candidates_token_count

                return InternalResponse(
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
                if i != max_retries:
                    logging.warning(f'Rate limit exceeded, waiting {e.retry_delay} seconds before retrying API call')
                    logging.debug(f'Exception: {e}')
                    time.sleep(e.retry_delay)
                else:
                    logging.warning("Rate limit still exceeeded after retries.")
                    raise e
            except Exception as e:
                logging.warning(f'Unknown expection occured: {e}')
                if i != max_retries:
                    logging.info("Retrying API call in 20 seconds.")
                    time.sleep(20)
                    continue
                else:
                    raise e
        
        return InternalResponse(
            content = [],
            input_tokens = 0,
            output_tokens = 0
        )
