import json
import time
import logging
from typing import Any
from collections import defaultdict

from google import genai
from google.genai import types, errors


DEFAULT_SYSTEM_PROMPT = """
    You are an AI assistant tasked with answering questions based on the information provided to you, with each answer being a **single** string in the JSON response.
    There should be the **exactly** same number of answers as inputted questions, no more, no less.
    * **Accuracy and Precision:** Provide direct, factual answers. **Do not** create or merge any of the questions.
    * **Source Constraint:** Use *only* information explicitly present in the transcript. Do not infer, speculate, or bring in outside knowledge.
    * **Completeness:** Ensure each answer fully addresses the question, *to the extent possible with the given transcript*.
    * **Missing Information:** If the information required to answer a question is not discussed or cannot be directly derived from the transcript, respond with "N/A".
"""

class Response:
    content : Any
    input_tokens : int
    output_tokens : int

    def __init__(
        self,
        content : Any,
        input_tokens : int,
        output_tokens : int
    ):
        self.content = content
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens

class GeminiApi:

    def __init__(
        self,
        api_key : str,
        model : str,
        **kwargs
    ):
        # Error handling - Api key not correct
        self.client = genai.Client(api_key=api_key, **kwargs)

        self.cache = defaultdict(lambda : None)
        self.files = defaultdict(lambda : None)

        # Error handling - Model not correct, default to a model
        self.model = model
    
    def parse_json(
        self,
        to_parse : str,
    ):
        # TODO: Error handling - incorrect json formatting.
        parsed = json.loads(to_parse)
        return parsed
    
    def get_model_token_limits(
        self
    ):
        model_info = self.client.models.get(model=self.model)
        input_token_limit = model_info.input_token_limit
        output_token_limit = model_info.output_token_limit

        return input_token_limit, output_token_limit

    def count_tokens(
            self,
            contents : Any
        ):

        return self.client.models.count_tokens(
            model=self.model,
            contents = contents
        )

    def add_to_cache(
        self,
        filepath : str,
        cache_name : str = None,
        ttl : str = "300s",
    ):
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
            model = self.model,
            config = types.CreateCachedContentConfig(
                display_name = cache_name,
                contents = [uploaded_file],
                ttl = ttl
            )
        )

        self.cache[cache_name] = cached_file
        return

    def upload_file(
        self,
        filepath : str,
    ):
        uploaded_file = self.client.files.upload(file=filepath)
        while uploaded_file.state.name == "PROCESSING" or uploaded_file.state.name == "PENDING":
            logging.info(f'Waiting for file {filepath} to upload, current state is {uploaded_file.state.name}')
            time.sleep(5)
        self.files[filepath] = uploaded_file
        return

    def generate_content(
        self,
        prompt : str,
        files : list[str] = [],
        cache_name : str = None,
        system_prompt : str = None,
        max_retries : int = 5,
    ):
        # TODO: Check input and output tokens are below limits.
        # TODO: Improve retry if API failure occurs

        # Adding default system prompt if one is not given.
        if system_prompt == None:
            system_prompt = DEFAULT_SYSTEM_PROMPT
        
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
            

        for i in range(max_retries):
            try:
                # Making the API call to Gemini
                response = self.client.models.generate_content(
                    model = self.model,
                    config = config_type,
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
            except errors.APIError as e:
                print(e)
                if e.code == 429:
                    # TODO: Is it possible to identify how long we have to way instead of just doing 10 seconds?
                    logging.info(f'Rate limit exceeded, waiting 20 seconds before retrying API call')
                    logging.debug(f'Gemini API Error Code: {e.code}\nGemini API Error Message: {e.message}')
                    time.sleep(20)
                    continue
                else:
                    logging.info(f'Unknown API Error occured, Error Code: {e.code}\nError Message: {e.message}')
            except Exception as e:
                print(e)
                logging.info(f'Unkown expection occured: {e}')
                logging.info("Retrying API call in 20 seconds.")
                time.sleep(20)
                continue
        
        # TODO: Handle failure better
        return Response(
            content = [],
            input_tokens = 0,
            output_tokens = 0
        )