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
        total_tokens = response.usage_metadata.total_token_count

        print (f'Input tokens: {input_tokens}')
        print (f'Output tokens: {output_tokens}')
        print (f'Total tokens: {total_tokens}')

        return {
            "text" : self.parse_json(response.text),
            "input tokens" : input_tokens,
            "output tokens" : output_tokens,
            "total tokens" : total_tokens
        }

    def generate_content_fixed(
        self,
        content : str,
        questions : list[str],
        chunk_char_length : int = 400,
        enable_sliding_window : bool = False,
        system_prompt : str = None
    ):
        # TODO: Currently can only handle a text response i.e. not a code block.
        # Adding default system prompt if one is not given.
        if system_prompt == None:
            system_prompt = """
                You are an AI assistant tasked with answering questions based on the information provided to you.
                * **Accuracy and Precision:** Provide direct, factual answers, ensuring the question is answered fully.
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
        #  Answer the following questions, in a precise manner, using only the information provided by the attached lecture transcript and ensuring all answers make sense and fully answer the question. If the information is not discussed in the transcript, answer with '-1'.

        
        chunker = Chunker()

        if enable_sliding_window:
            chunks = chunker.sliding_window_chunking(content, chunk_char_length)
        else:
            chunks = chunker.fixed_length_chunking(content, chunk_char_length)
        question_batches = chunker.fixed_question_batching(questions)

        answers = {}

        for batch in question_batches:
            for chunk in chunks:
                response = self.generate_content([chunk, batch], system_prompt)

                # TODO: If the question has already been answered in a previous chunk the new answer is disregarded, this can be
                # further optimised so the question is not asked again.
                if len(response['text']) == len(batch): 
                    print (response['text'])

                for i in range(len(response['text'])):
                    if batch[i] not in answers.keys() and response['text'][f'{i+1}'] != '-1':
                        answers[batch[i]] = response['text'][f'{i+1}']
        
        return answers