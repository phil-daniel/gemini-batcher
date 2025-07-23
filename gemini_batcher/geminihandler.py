import json
import time
import logging
from typing import Any
import os

from .input_handler.textinputs import BaseTextInput
from .processor.textchunkandbatch import TextChunkAndBatch
from .processor.mediachunkandbatch import MediaChunkAndBatch

from .utils import exceptions

from .geminiapi import Response, GeminiApi

class GeminiHandler:

    def __init__(
        self,
        api_key : str,
        model : str,
        **kwargs
    ):
        self.gemini_api = GeminiApi(
            api_key=api_key,
            model=model,
            **kwargs
        )
        
        
    def generate_content_fixed(
        self,
        content : BaseTextInput,
        questions : list[str],
        chunk_char_length : int = 100000,
        questions_per_batch : int = 50,
        window_char_length : int = 100,
        system_prompt : str = None,
    ) -> Response:
        # TODO: Currently can only handle a text response i.e. not a code block.
 
        chunks = TextChunkAndBatch.chunk_sliding_window_by_length(
            text_input = content,
            chunk_char_size = chunk_char_length,
            window_char_size = window_char_length
        )
        question_batches = TextChunkAndBatch.batch_by_number_of_questions(
            questions = questions, 
            questions_per_batch = questions_per_batch
        )

        answers = {}

        total_input_tokens = 0
        total_output_tokens = 0

        for batch in question_batches:
            for chunk in chunks:
                query_contents = f'Content:\n{chunk}\n\nThere are {len(batch)} questions. The questions are:\n' + '\n\t- '.join(batch)
                response = self.gemini_api.generate_content(query_contents, system_prompt=system_prompt)

                total_input_tokens += response.input_tokens
                total_output_tokens += response.output_tokens

                # TODO: If the question has already been answered in a previous chunk the new answer is disregarded, this can be
                # further optimised so the question is not asked again.
                for i in range(len(response.content)):
                    if batch[i] not in answers.keys() and response.content[i] !=  'N/A':
                        answers[batch[i]] = response.content[i]
        
        return Response(
            content = answers,
            input_tokens = total_input_tokens,
            output_tokens = total_output_tokens
        )
    
    def generate_content_token_aware(
        self,
        content : BaseTextInput,
        questions : list[str],
        system_prompt : str = None
    ) -> Response:
        # A version of generate_content_fixed() that automatically chunks depending on the token limits of the model being used.
        
        input_token_limit, _ = self.gemini_api.get_model_token_limits()

        total_input_tokens = 0
        total_output_tokens = 0

        answers = {}
        queue = [(content.content, questions)]

        while len(queue) > 0:
            curr_content, curr_questions = queue.pop(0)

            input_tokens_used = self.gemini_api.count_tokens(
                contents = [system_prompt, curr_content, curr_questions]
            )

            # Checking if the content is too large for the input token limit, if so splitting the content in half
            # TODO: Add ability to use sliding window
            if input_tokens_used > input_token_limit:
                chunked_content = [curr_content[0 : len(curr_content)//2 + 1], curr_content[len(curr_content)//2 + 1 : len(curr_content)]]

                queue.append((chunked_content[0], curr_questions))
                queue.append((chunked_content[1], curr_questions))

            else:
                query_contents = f'Content:\n{curr_content}\n\nThere are {len(curr_questions)} questions. The questions are:\n' + '\n\t- '.join(curr_questions)
                try:
                    response = self.gemini_api.generate_content(query_contents, system_prompt=system_prompt)
                except exceptions.MaxOutputTokensExceeded as e:
                    # If MaxOutputToken is exceeded then we need to split the number of question in each batch by two.
                    # This will reduce the token size of the output.
                    batched_questions = TextChunkAndBatch.batch_by_number_of_questions(curr_questions, len(curr_questions)//2 + 1)
                    queue.append((curr_content, batched_questions[0]))
                    queue.append((curr_content, batched_questions[1]))
                    continue
                except exceptions.MaxInputTokensExceeded as e:
                    # This exception should never occur as we already check that the input token limit is not exceeded.
                    # TODO: Implement
                    pass
                except Exception as e:
                    # TODO: Generic exception handling
                    raise e
                    
                for i in range(len(response.content)):
                    if curr_questions[i] not in answers.keys() and response.content[i] !=  'N/A':
                        answers[curr_questions[i]] = response.content[i]
                total_input_tokens += response.input_tokens
                total_output_tokens += response.output_tokens

        return Response(
            content = answers,
            input_tokens = total_input_tokens,
            output_tokens = total_output_tokens
        )

    def generate_content_semantic(
        self,
        content : BaseTextInput,
        questions : list[str],
        system_prompt : str = None
    ) -> Response:
        content_chunks, question_batches = TextChunkAndBatch.chunk_and_batch_semantically(content, questions)

        total_input_tokens = 0
        total_output_tokens = 0
        answers = {}
        
        for i in range(len(content_chunks)):
            # If there are no questions in the current chunk's batch, then we don't need to query it.
            if len(question_batches[i]) != 0:
                query_contents = f'Content:\n{content_chunks[i]}\n\nThere are {len(question_batches[i])} questions. The questions are:\n' + '\n\t- '.join(question_batches[i])
                response = self.gemini_api.generate_content(query_contents, system_prompt=system_prompt)

                total_input_tokens += response.input_tokens
                total_output_tokens += response.output_tokens
                
                for j in range(len(response.content)):
                    answers[question_batches[i][j]] = response.content[j]
        
        return Response(
            content = answers,
            input_tokens = total_input_tokens,
            output_tokens = total_output_tokens
        )

    def generate_content_media_fixed(
        self,
        media_path : str,
        questions : list[str],
        chunk_duration : int = 100,
        questions_per_batch : int = 50,
        window_duration : int = 0,
        system_prompt : str = None,
        use_explicit_caching : bool = True
    ):
        chunks = MediaChunkAndBatch.chunk_sliding_window_by_duration(media_path, chunk_duration, window_duration)
        question_batches = TextChunkAndBatch.batch_by_number_of_questions(questions, questions_per_batch)

        answers = {}

        total_input_tokens = 0
        total_output_tokens = 0

        # There is no need to cache the chunks if each chunk is only used once.
        if len(question_batches) == 1 and use_explicit_caching:
            use_explicit_caching = False

        for batch in question_batches:
            for chunk in chunks:
                query_contents = f'Content:\nThis has been attached as a media file, named {chunk}\n\nThere are {len(batch)} questions. The questions are:\n' + '\n\t- '.join(batch)
                
                if use_explicit_caching:
                    if chunk not in self.gemini_api.cache.keys():
                        self.gemini_api.add_to_cache(chunk)
                    response = self.gemini_api.generate_content(query_contents, system_prompt=system_prompt, cache_name=chunk)
                else:
                    if chunk not in self.gemini_api.files.keys():
                        self.gemini_api.upload_file(chunk)
                    response = self.gemini_api.generate_content(query_contents, system_prompt=system_prompt, files=[chunk])

                total_input_tokens += response.input_tokens
                total_output_tokens += response.output_tokens

                # TODO: If the question has already been answered in a previous chunk the new answer is disregarded, this can be
                # further optimised so the question is not asked again.
                for i in range(len(response.content)):
                    if batch[i] not in answers.keys() and response.content[i] !=  'N/A':
                        answers[batch[i]] = response.content[i]


        return Response(
            content = answers,
            input_tokens = total_input_tokens,
            output_tokens = total_output_tokens
        )
    
    def generate_content_media_semantically(
        self,
        media_path : str,
        questions : list[str],
        questions_per_batch : int = 50,
        system_prompt : str = None
    ):
        a, b = MediaChunkAndBatch.chunk_and_batch_semantically(media_path, questions, self.gemini_api)
        print(a)
        print(b)

        return

