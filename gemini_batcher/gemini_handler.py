import logging
from typing import Any
import os
from enum import Enum, auto
import tempfile

from .input_handler.text_inputs import BaseTextInput
from .processor.text_chunk_and_batch import TextChunkAndBatch
from .processor.media_chunk_and_batch import MediaChunkAndBatch
from .processor.dynamic_batch import DynamicBatch

from .utils import exceptions

from .gemini_functions.gemini_api import Response, GeminiApi

class GeminiHandler:

    gemini_api : GeminiApi

    def __init__(
        self,
        api_key : str,
        model : str,
        **kwargs
    ) -> None:
        self.gemini_api = GeminiApi(
            api_key=api_key,
            model=model,
            **kwargs
        )
    
    def change_model(
        self,
        model_name : str
    ) -> None:
        self.model = model_name
        
    def generate_content_fixed(
        self,
        content : BaseTextInput,
        questions : list[str],
        chunk_char_length : int = 100000,
        questions_per_batch : int = 50,
        window_char_length : int = 100,
        system_prompt : str = None,
    ) -> Response:
 
        chunks = TextChunkAndBatch.chunk_sliding_window_by_length(
            text_input = content,
            chunk_char_size = chunk_char_length,
            window_char_size = window_char_length
        )

        question_batches = DynamicBatch(questions)

        answers = {}

        total_input_tokens = 0
        total_output_tokens = 0

        for chunk in chunks:
            batch = question_batches.get_question_batch(questions_per_batch)
            while len(batch) > 0:
                query_contents = f'Content:\n{chunk}\n\nThere are {len(batch)} questions. The questions are:\n' + '\n\t- '.join(batch)
                response = self.gemini_api.generate_content(query_contents, system_prompt=system_prompt)

                total_input_tokens += response.input_tokens
                total_output_tokens += response.output_tokens

                for i in range(len(response.content)):
                    if batch[i] not in answers.keys() and response.content[i] != 'N/A':
                        answers[batch[i]] = response.content[i]
                        question_batches.mark_answered(batch[i])
                batch = question_batches.get_question_batch(questions_per_batch)

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

        start_batch_size = len(questions)
        question_batcher = DynamicBatch(questions)

        answers = {}
        queue = [(content.content, start_batch_size)]

        while len(queue) > 0:
            curr_content, curr_batch_size = queue.pop(0)

            curr_batch = question_batcher.get_question_batch(curr_batch_size)

            query_contents = f'Content:\n{curr_content}\n\nThere are {len(curr_batch)} questions. The questions are:\n' + '\n\t- '.join(curr_batch)

            input_tokens_used = self.gemini_api.count_tokens(
                contents = [system_prompt, query_contents]
            )

            # Checking if the content is too large for the input token limit, if so splitting the content in half
            # TODO: Add ability to use sliding window
            if input_tokens_used > input_token_limit:
                chunked_content = [curr_content[0 : len(curr_content)//2 + 1], curr_content[len(curr_content)//2 + 1 : len(curr_content)]]

                queue.append((chunked_content[0], curr_batch_size))
                queue.append((chunked_content[1], curr_batch_size))
                DynamicBatch.add_questions(curr_batch)

            else:
                try:
                    response = self.gemini_api.generate_content(query_contents, system_prompt=system_prompt)
                except exceptions.MaxOutputTokensExceeded as e:
                    # If MaxOutputToken is exceeded then we need to split the number of question in each batch by two.
                    # This will reduce the token size of the output.
                    queue.append((curr_content, curr_batch_size // 2 + 1))
                    queue.append((curr_content, curr_batch_size // 2 + 1))
                    DynamicBatch.add_questions(curr_batch)
                    continue
                except exceptions.MaxInputTokensExceeded as e:
                    # This exception should never occur as we already check that the input token limit is not exceeded.
                    # TODO: Implement
                    pass
                    
                for i in range(len(response.content)):
                    if curr_batch[i] not in answers.keys() and response.content[i] !=  'N/A':
                        answers[curr_batch[i]] = response.content[i]
                    question_batcher.mark_answered(curr_batch[i])

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
        with tempfile.TemporaryDirectory() as temp_dir:
            chunks = MediaChunkAndBatch.chunk_sliding_window_by_duration(media_path, temp_dir, chunk_duration, window_duration)

            question_batches = DynamicBatch(questions)

            answers = {}

            total_input_tokens = 0
            total_output_tokens = 0

            for chunk in chunks:
                batch = question_batches.get_question_batch(questions_per_batch)
                while len(batch) > 0:
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

                    for i in range(len(response.content)):
                        if batch[i] not in answers.keys() and response.content[i] != 'N/A':
                            answers[batch[i]] = response.content[i]
                            question_batches.mark_answered(batch[i])
                    batch = question_batches.get_question_batch(questions_per_batch)

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
        chunked_timestamps, batches = MediaChunkAndBatch.chunk_and_batch_semantically(media_path, questions, self.gemini_api)

        answers = {}

        total_input_tokens = 0
        total_output_tokens = 0
        
        for i in range(len(chunked_timestamps) - 1):
            if len(batches[i]) == 0:
                continue

            with tempfile.NamedTemporaryFile() as temp_file:
                chunk_filepath = temp_file.name
                MediaChunkAndBatch.trim_video(
                    media_path,
                    chunk_filepath,
                    chunked_timestamps[i],
                    chunked_timestamps[i+1]
                )

                if chunk_filepath not in self.gemini_api.files.keys():
                    self.gemini_api.upload_file(chunk_filepath)
                query_contents = f'Content:\nThis has been attached as a media file, named {chunk_filepath}\n\nThere are {len(batch)} questions. The questions are:\n' + '\n\t- '.join(batches[i])
                response = self.gemini_api.generate_content(query_contents, system_prompt=system_prompt, files=[chunk])

                total_input_tokens += response.input_tokens
                total_output_tokens += response.output_tokens

                for i in range(len(response.content)):
                    if batches[i] not in answers.keys() and response.content[i] != 'N/A':
                        answers[batches[i]] = response.content[i]

        return Response(
            content = answers,
            input_tokens = total_input_tokens,
            output_tokens = total_output_tokens
        )
    
    def generate_content_fixed_with_previous_answers(
        self,
        content : BaseTextInput,
        questions : list[str],
        previous_answers : str = None,
        chunk_char_length : int = 100000,
        questions_per_batch : int = 50,
        window_char_length : int = 100,
        system_prompt : str = None,
    ) -> Response:
        
        if previous_answers == None:
            query = "Summarise the following information as briefly as possible whilst maintaing as much information as possible: " + previous_answers
            previous_answer_summary = self.gemini_api.generate_content(query).content
        else:
            previous_answer_summary = "No previous answers"
 
        chunks = TextChunkAndBatch.chunk_sliding_window_by_length(
            text_input = content,
            chunk_char_size = chunk_char_length,
            window_char_size = window_char_length
        )

        question_batches = DynamicBatch(questions)

        answers = {}

        total_input_tokens = 0
        total_output_tokens = 0

        for chunk in chunks:
            batch = question_batches.get_question_batch(questions_per_batch)
            while len(batch) > 0:
                query_contents = f'Content:\n{chunk}\nAdditional Information:\n{previous_answer_summary}\nThere are {len(batch)} questions. The questions are:\n' + '\n\t- '.join(batch)
                response = self.gemini_api.generate_content(query_contents, system_prompt=system_prompt)

                total_input_tokens += response.input_tokens
                total_output_tokens += response.output_tokens

                for i in range(len(response.content)):
                    if batch[i] not in answers.keys() and response.content[i] != 'N/A':
                        answers[batch[i]] = response.content[i]
                        question_batches.mark_answered(batch[i])
                batch = question_batches.get_question_batch(questions_per_batch)
        
        return Response(
            content = answers,
            input_tokens = total_input_tokens,
            output_tokens = total_output_tokens
        )

