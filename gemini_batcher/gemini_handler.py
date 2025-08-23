import logging
from typing import Any
import os
import tempfile

from .input_handler.text_inputs import BaseInput, BaseTextInput
from .input_handler.other_inputs import VideoFileInput
from .processor.text_chunk_and_batch import TextChunkAndBatch
from .processor.media_chunk_and_batch import MediaChunkAndBatch
from .processor.dynamic_batch import DynamicBatch

from .strategies.text_chunking_strategies import BaseStrategy
from .strategies import text_chunking_strategies
from .strategies import media_chunking_strategies
from .strategies import batching_strategies

from .utils import exceptions

from .gemini_config import GeminiConfig

from .gemini_functions.gemini_api import Response, GeminiApi

class GeminiHandler:

    gemini_api : GeminiApi
    config : GeminiApi

    def __init__(
        self,
        config : GeminiConfig
    ) -> None:
        self.config = config
        self.gemini_api = GeminiApi(
            api_key=config.api_key,
        )
        # TODO: ADD **kwargs back

    def generate_content(
        self,
        content : BaseInput,
        questions : list[str],
        chunking_technique : BaseStrategy,
        batching_technique : BaseStrategy,
        config : GeminiConfig = None
    ) -> Response:
        # Updating the config if it has been changed
        if config != None:
            self.config = config

        # Choosing the method to use based on the content type.
        match content:
            case BaseTextInput():
                return self._generate_content_from_text(
                    config,
                    content,
                    questions,
                    chunking_technique,
                    batching_technique
                )
            case _:
                return self._generate_content_from_media(
                    config,
                    content,
                    questions,
                    chunking_technique,
                    batching_technique
                )
        return None
    
    def _generate_content_from_media(
        self,
        config : GeminiConfig,
        content : VideoFileInput,
        questions : list[str],
        chunking_technique : BaseStrategy,
        batching_technique : BaseStrategy
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generating the chunks based on the inputted technique
            chunks = []
            chunk_transcripts = None
            match chunking_technique:
                case text_chunking_strategies.SlidingWindowChunking | text_chunking_strategies.SemanticChunking:
                    # If we are using a text technique we generate a transcript and then just use that.
                    _, sentences = MediaChunkAndBatch.generate_transcript(content)
                    text_content = BaseTextInput(" ".join(sentences))
                    return self._generate_content_from_text(
                        config=config,
                        content=text_content,
                        questions=questions,
                        chunking_technique=chunking_technique,
                        batching_technique=batching_technique
                    )
                case media_chunking_strategies.SlidingWindowChunking:
                    chunks = MediaChunkAndBatch.chunk_sliding_window_by_duration(
                        content,
                        temp_dir,
                        chunking_technique.chunk_duration,
                        chunking_technique.window_duration
                    )
                case media_chunking_strategies.SemanticChunking:
                    chunks, chunk_transcripts = MediaChunkAndBatch.chunk_semantically(
                        config,
                        content,
                        temp_dir,
                        self.gemini_api,
                        chunking_technique.min_sentences_per_chunk,
                        chunking_technique.max_sentences_per_chunk,
                        chunking_technique.transformer_model
                    )
                case _:
                    raise NotImplementedError("Provided chunking method is not implemented or not suitable for input type.")
            
            # Generating the based on the inputted techniques
            batches = []
            match batching_technique:
                case batching_strategies.FixedBatching():
                    question_batches = DynamicBatch(
                        questions,
                        batching_technique.batch_size
                    )
                    batches = [question_batches for _ in range(len(chunks))]
                case batching_strategies.SemanticBatching():
                    if chunk_transcripts == None:
                        raise NotImplementedError("A transcript has not been generated using the provided chunking technique, so semantic batching is not available.")

                    semantic_batches = TextChunkAndBatch.batch_with_chunks_semantically(
                        chunk_transcripts,
                        questions,
                        batching_technique.transformer_model
                    )
                    batches = [DynamicBatch(batch, batching_technique.batch_size) for batch in semantic_batches]
                case _:
                    raise NotImplementedError("Provided batching method is not implemented or not suitable for input type.")
            
            # TODO: SORT OUT SYSTEM PROMPT & explicit caching
            partial_responses = []
            for i in range(len(chunks)):
                partial_responses.append(
                    self._handle_single_media_chunk_and_batch(
                        config,
                        chunks[i],
                        batches[i],
                    )
                )
        
        response = self._combine_partial_responses(partial_responses)
        return response
        
    def _generate_content_from_text(
        self,
        config : GeminiConfig,
        content : BaseTextInput,
        questions : list[str],
        chunking_technique : BaseStrategy,
        batching_technique : BaseStrategy
    ):
        # Generating the chunks based on the inputted technique
        chunks = []
        match chunking_technique:
            case text_chunking_strategies.SlidingWindowChunking():
                chunks = TextChunkAndBatch.chunk_sliding_window_by_length(
                    text_input=content,
                    chunk_char_size=chunking_technique.chunk_char_size,
                    window_char_size=chunking_technique.window_char_size
                )
            case text_chunking_strategies.SemanticChunking():
                chunks = TextChunkAndBatch.chunk_semantically(
                    text_input=content,
                    min_sentences_per_chunk=chunking_technique.min_sentences_per_chunk,
                    max_sentences_per_chunk=chunking_technique.max_sentences_per_chunk,
                    threshold_factor=chunking_technique.similarity_threashold_factor,
                    transformer_model=chunking_technique.transformer_model
                )
            case text_chunking_strategies.TokenAwareChunkingAndBatching():
                # If TokenAwareChunkingAndBatching is chosen as the chunking method the batching method is ignored.
                return self._token_aware_batching_and_chunking(
                    content=content,
                    questions=questions,
                )
            case _:
                raise NotImplementedError("Provided chunking method is not implemented or not suitable for input type.")
        
        # Generating the based on the inputted techniques
        batches = []
        match batching_technique:
            case batching_strategies.FixedBatching():
                question_batches = DynamicBatch(
                    questions,
                    batching_technique.batch_size
                )
                batches = [question_batches for _ in range(len(chunks))]
            case batching_strategies.SemanticBatching():
                semantic_batches = TextChunkAndBatch.batch_with_chunks_semantically(
                    chunks,
                    questions,
                    batching_technique.transformer_model
                )
                batches = [DynamicBatch(batch, batching_technique.batch_size) for batch in semantic_batches]
            case _:
                raise NotImplementedError("Provided batching method is not implemented or not suitable for chunk type.")

        # TODO: SORT OUT SYSTEM PROMPT
        partial_responses = []
        for i in range(len(chunks)):
            partial_responses.append(
                self._handle_single_text_chunk_and_batch(
                    config,
                    chunks[i],
                    batches[i],
                )
            )
        
        response = self._combine_partial_responses(partial_responses)
        return response

    def _handle_single_media_chunk_and_batch(
        self,
        config : GeminiConfig,
        chunk_filepath : str,
        question_batches : DynamicBatch,
    ) -> Response:
        # TODO: Add explicit caching stuff.
        answers = {}
        total_input_tokens = 0
        total_output_tokens = 0

        batch = question_batches.get_question_batch()
        while len(batch) > 0:
            query_contents = f'Content:\nThe content has been attached as a file.\n\nThere are {len(batch)} questions. The questions are:\n' + '\n\t- '.join(batch)
            
            if config.use_explicit_caching:
                if chunk_filepath not in self.gemini_api.cache.keys():
                    self.gemini_api.add_to_cache(chunk_filepath)
                response = self.gemini_api.generate_content(
                    config.model,
                    query_contents,
                    system_prompt=config.system_prompt,
                    cache_name=chunk_filepath
                )
            else:
                if chunk_filepath not in self.gemini_api.files.keys():
                    self.gemini_api.upload_file(chunk_filepath)
                response = self.gemini_api.generate_content(
                    config.model,
                    query_contents,
                    system_prompt=config.system_prompt,
                    files=[chunk_filepath]
                )

            total_input_tokens += response.input_tokens
            total_output_tokens += response.output_tokens

            for i in range(len(response.content)):
                if batch[i] not in answers.keys() and response.content[i] != 'N/A':
                    answers[batch[i]] = response.content[i]
                    question_batches.mark_answered(batch[i])
            batch = question_batches.get_question_batch()
        
        return Response(
            content = answers,
            input_tokens = total_input_tokens,
            output_tokens = total_output_tokens
        )
    
    def _handle_single_text_chunk_and_batch(
        self,
        config : GeminiConfig,
        chunk : str,
        question_batches : DynamicBatch,
    ) -> Response:
        answers = {}
        total_input_tokens = 0
        total_output_tokens = 0

        batch = question_batches.get_question_batch()
        while len(batch) > 0:
            query_contents = f'Content:\n{chunk}\n\nThere are {len(batch)} questions. The questions are:\n' + '\n\t- '.join(batch)
            response = self.gemini_api.generate_content(
                config.model,
                query_contents,
                system_prompt=config.system_prompt
            )

            total_input_tokens += response.input_tokens
            total_output_tokens += response.output_tokens

            for i in range(len(response.content)):
                if batch[i] not in answers.keys() and response.content[i] != 'N/A':
                    answers[batch[i]] = response.content[i]
                    question_batches.mark_answered(batch[i])
            batch = question_batches.get_question_batch()
        
        return Response(
            content = answers,
            input_tokens = total_input_tokens,
            output_tokens = total_output_tokens
        )

    def _combine_partial_responses(
        partial_responses : list[Response]  
    ) -> Response:
        answers = {}
        total_input_tokens = 0
        total_output_tokens = 0

        for partial_response in partial_responses:
            answers.update(partial_response.content)
            total_input_tokens += partial_response.input_tokens
            total_output_tokens += partial_response.output_tokens

        return Response(
            content=answers,
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens
        )
    
    def _token_aware_batching_and_chunking(
        self,
        config : GeminiConfig,
        content : BaseTextInput,
        questions : list[str],
    ) -> Response:
        # A version of generate_content_fixed() that automatically chunks depending on the token limits of the model being used.
        
        input_token_limit, _ = self.gemini_api.get_model_token_limits(config.model)

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
                contents = [config.system_prompt, query_contents]
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
                    response = self.gemini_api.generate_content(
                        config.model,
                        query_contents,
                        system_prompt=config.system_prompt
                    )
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

