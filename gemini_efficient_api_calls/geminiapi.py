import json
import time
import logging

from google import genai
from google.genai import types, errors

from .chunker import Chunker

DEFAULT_SYSTEM_PROMPT = """
    You are an AI assistant tasked with answering questions based on the information provided to you.
    * **Accuracy and Precision:** Provide direct, factual answers.
    * **Source Constraint:** Use *only* information explicitly present in the transcript. Do not infer, speculate, or bring in outside knowledge.
    * **Completeness:** Ensure each answer fully addresses the question, *to the extent possible with the given transcript*.
    * **Missing Information:** If the information required to answer a question is not discussed or cannot be directly derived from the transcript, respond with '-1'.
    Respond in valid JSON of the form, only using text:
    ```
    {
        "1" : "Answer to question 1",
        "2" : "Answer to question 2",
    }
    ```
"""

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
        system_prompt : str = None,
        max_retries : int = 3,
    ):
        # TODO: Check input and output tokens are below limits.
        # TODO: Improve retry if API failure occurs

        # Adding default system prompt if one is not given.
        if system_prompt == None:
            system_prompt = DEFAULT_SYSTEM_PROMPT

        for i in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        system_instruction=system_prompt
                    ),
                    contents=prompt
                )

                # TODO: Information about token usage, this can be used to compare performance between different designs
                input_tokens = response.usage_metadata.prompt_token_count
                output_tokens = response.usage_metadata.candidates_token_count

                return {
                    "text" : self.parse_json(response.text),
                    "input tokens" : input_tokens,
                    "output tokens" : output_tokens,
                }
            except errors.APIError as e:
                if e.code == 429:
                    # TODO: Is it possible to identify how long we have to way instead of just doing 10 seconds?
                    logging.info(f'Rate limit exceeded, waiting 10 seconds before retrying API call')
                    logging.debug(f'Gemini API Error Code: {e.code}\nGemini API Error Message: {e.message}')
                    time.sleep(10)
                    continue
                else:
                    logging.info(f'Unknown API Error occured, Error Code: {e.code}\nError Message: {e.message}')
            except Exception as e:
                logging.info(f'Unkown expection occured: {e}')
                logging.info("Retrying API call in 10 seconds.")
                time.sleep(10)
                continue
        
        # TODO: Handle failure better
        return {
            'text' : [],
            'input tokens' : 0,
            'output tokens' : 0
        }

    def generate_content_fixed(
        self,
        content : str,
        questions : list[str],
        chunk_char_length : int = 100000,
        questions_per_batch : int = 50,
        enable_sliding_window : bool = False,
        window_char_length : int = 100,
        system_prompt : str = None
    ):
        # TODO: Currently can only handle a text response i.e. not a code block.
        
        # Chunking and Batching the questions
        chunker = Chunker()
        if enable_sliding_window:
            chunks = chunker.sliding_window_chunking_by_size(content, chunk_char_length, window_char_length)
        else:
            chunks = chunker.fixed_chunking_by_size(content, chunk_char_length)
        question_batches = chunker.fixed_question_batching(questions, questions_per_batch)

        answers = {}

        total_input_tokens = 0
        total_output_tokens = 0

        for batch in question_batches:
            # TODO: Changed where the questions are numbered but this would cause problems if the questions are already numbered
            # Get the API to output the responses in a json list instead of a dictionary?
            numbered_batch = [f'{i+1}: {batch[i]}' for i in range(len(batch))]
            for chunk in chunks:
                response = self.generate_content([chunk, numbered_batch], system_prompt=system_prompt)

                total_input_tokens += response["input tokens"]
                total_output_tokens += response["output tokens"]

                # TODO: If the question has already been answered in a previous chunk the new answer is disregarded, this can be
                # further optimised so the question is not asked again.

                for i in range(len(response['text'])):
                    if batch[i] not in answers.keys() and response['text'][f'{i+1}'] != '-1':
                        answers[batch[i]] = response['text'][f'{i+1}']
        

        # TODO: Better way of returning? Tuple?
        return {
            "text" : answers,
            "input tokens" : total_input_tokens,
            "output tokens" : total_output_tokens
        }
    
    def generate_content_token_aware(
        self,
        content : str,
        questions : list[str],
        system_prompt : str = None
    ):
        
        # Adding default system prompt if one is not given.
        if system_prompt == None:
            system_prompt = DEFAULT_SYSTEM_PROMPT
        
        # A version of generate_content_fixed() that automatically chunks depending on the token limits of the model being used.
        
        model_info = self.client.models.get(model=self.model)
        input_token_limit = model_info.input_token_limit
        output_token_limit = model_info.output_token_limit

        total_input_tokens = 0
        total_output_tokens = 0

        chunker = Chunker()

        answers = {}
        queue = [(content, questions)]

        while len(queue) > 0:
            curr_content, curr_questions = queue.pop(0)

            input_tokens_used = self.client.models.count_tokens(
                model=self.model, contents = [system_prompt, curr_content, curr_questions]
            )

            # Checking if the content is too large for the input token limit, if so splitting the content in half
            # TODO: Add ability to use sliding window
            if input_tokens_used > input_token_limit:
                chunked_content = chunker.fixed_chunking_by_num(curr_content, 2)

                queue.append((chunked_content[0], curr_questions))
                queue.append((chunked_content[1], curr_questions))

            else:
                response = self.generate_content([curr_content, curr_questions], system_prompt=system_prompt)

                # TODO: This doesn't seem to actually occur, need a better way of doing this, checking if the output limit has been reached
                if response["output tokens"] > output_token_limit:
                    batched_questions = chunker.fixed_question_batching(curr_questions, len(curr_questions)//2 + 1)
                    queue.append((curr_content, batched_questions[0]))
                    queue.append((curr_content, batched_questions[1]))
                else:
                    for i in range(len(response['text'])):
                        if curr_questions[i] not in answers.keys() and response['text'][f'{i+1}'] != '-1':
                            answers[curr_questions[i]] = response['text'][f'{i+1}']
                    total_input_tokens += response["input tokens"]
                    total_output_tokens += response["output tokens"]

        return {
            "text" : answers,
            "input tokens" : total_input_tokens,
            "output tokens" : total_output_tokens
        }

    def generate_content_semantic(
        self,
        content : str,
        questions : list[str],
    ):
        chunker = Chunker()
        content_chunks, question_batches = chunker.semantic_chunk_and_batch(content, questions)

        total_input_tokens = 0
        total_output_tokens = 0
        answers = {}
        
        for i in range(len(content_chunks)):
            # If there are no questions in the current chunk's batch, then we don't need to query it.
            if len(question_batches[i]) != 0:
                response = self.generate_content([content_chunks[i], question_batches[i]])

                total_input_tokens += response["input tokens"]
                total_output_tokens += response["output tokens"]
                
                for j in range(len(response["text"])):
                    answers[question_batches[i][j]] = response["text"][f'{j+1}']
        
        # TODO: Better way of returning? Tuple?
        return {
            "text" : answers,
            "input tokens" : total_input_tokens,
            "output tokens" : total_output_tokens
        }
