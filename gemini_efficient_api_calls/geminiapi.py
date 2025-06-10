import json

from google import genai
from google.genai import types

from .chunker import Chunker

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
        # TODO: NEED TO HANDLE API RATE LIMITS, CHECK INPUT OUTPUT TOKENS ARE UNDER THE LIMIT.

        response = self.client.models.generate_content(
            model=self.model,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                system_instruction=system_prompt
            ),
            contents=prompt
        )

        # TODO: Add retry if API failure occurs

        # TODO: Information about token usage, this can be used to compare performance between different designs
        input_tokens = response.usage_metadata.prompt_token_count
        output_tokens = response.usage_metadata.candidates_token_count

        return {
            "text" : self.parse_json(response.text),
            "input tokens" : input_tokens,
            "output tokens" : output_tokens,
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
        # Adding default system prompt if one is not given.
        if system_prompt == None:
            system_prompt = """
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
            for chunk in chunks:
                response = self.generate_content([chunk, batch], system_prompt)

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