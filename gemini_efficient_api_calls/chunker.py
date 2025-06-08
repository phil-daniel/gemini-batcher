import math

from .geminiapi import GeminiApi

class Chunker:

    def fixed_length_chunking(
            self,
            content : str = "",
            chunk_char_size : int = 400
        ):
        chunked_content = []
        chunk_count = math.ceil(len(content) / chunk_char_size)

        for i in range(chunk_count):
            chunk_start_pos = i * chunk_char_size
            chunk_end_pos = min(chunk_start_pos + chunk_char_size, len(content))
            chunked_content.append(content[chunk_start_pos : chunk_end_pos])

        return chunked_content

    def sliding_window_chunking(
            self,
            content : str = "",
            chunk_char_size : int = 400,
            window_char_size : int = 100
        ):
        # TODO: Error handling, add check to ensure window < chunk

        chunked_content = []
        chunk_count = math.ceil(len(content) / (chunk_char_size - window_char_size))

        for i in range(chunk_count):
            chunk_start_pos = i * (chunk_char_size - window_char_size)
            chunk_end_pos = min(chunk_start_pos + chunk_char_size, len(content))
            chunked_content.append(content[chunk_start_pos : chunk_end_pos])

        return chunked_content
    
    def fixed_question_batching(
        self,
        questions : list[str],
        questions_per_batch : int = 10
    ): 
        # TODO: Error handling, no strings
        batches = []
        batch_count = math.ceil(len(questions) / questions_per_batch)

        for i in range(batch_count):
            batches.append(questions[i : min(i + questions_per_batch, len(questions))])
        return batches
    
    def generate_content_fixed(
        self,
        api_key : str,
        model : str,
        content : str,
        questions : list[str],
        chunk_char_length : int = 400,
        enable_sliding_window : bool = False,
        system_prompt : str = None
    ):
        
        # Adding default system prompt if one is not given.
        if system_prompt == None:
            system_prompt = """
                Answer the following questions, in a brief and precise manner, using only the information provided by the attached content. If the information is not provided by the video, answer with '-1'.
                Respond in valid JSON of the form:
                ```
                {
                    "1" : "Answer to question 1",
                    "2" : "Answer to question 2",
                }
                ```
            """
        
        client = GeminiApi(api_key=api_key, model=model)

        if enable_sliding_window:
            chunks = self.sliding_window_chunking(content, chunk_char_length)
        else:
            chunks = self.fixed_length_chunking(content, chunk_char_length)
        question_batches = self.fixed_question_batching(questions)

        # TODO: Add system prompt
        # TODO: Handle question batches better, what if one question has already been answered?

        for batch in question_batches:
            for chunk in chunks:
                response = client.generate_content([chunk, question_batches[0]], system_prompt)
                print(response['text'])