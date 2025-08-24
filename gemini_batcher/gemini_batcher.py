import logging
import tempfile

from .input_handler.text_inputs import BaseInput, BaseTextInput
from .input_handler.media_inputs import BaseMediaInput
from .processor.text_chunk_and_batch import TextChunkAndBatch
from .processor.media_chunk_and_batch import MediaChunkAndBatch
from .processor.dynamic_batch import DynamicBatch

from .strategies import *

from .utils import exceptions

from .gemini_config import GeminiConfig

from .gemini_functions.gemini_api import InternalResponse, GeminiApi

from .response import Response

class GeminiBatcher:
    """
    Provides the main functionalitys of the gemini-batcher library.

    Attributes:
        gemini_api (GeminiApi): The GeminiApi object provides a wrapper around the Gemini Python SDK, allowing for additional error handling.
        config (GeminiConfig): The default config settings to be used when querying the Gemini API. This can be replaced when calling `generate_content()`.
    """

    gemini_api : GeminiApi
    config : GeminiConfig

    def __init__(
        self,
        config : GeminiConfig
    ) -> None:
        """
        Initializes the GeminiBatcher object with a given Gemini configuration. This involves creating the GeminiApi object which allows for API calls to Gemini models to be made.

        Args:
            config (GeminiConfig): The configuration settings for the query (such as model name, system prompt, caching options, etc).
        """
        self.config = config
        self.gemini_api = GeminiApi(
            api_key=config.api_key,
        )
        # TODO: ADD **kwargs back

    def generate_content(
        self,
        content : BaseInput,
        questions : list[str],
        chunking_strategy : BaseStrategy,
        batching_strategy : BaseStrategy,
        config : GeminiConfig = None
    ) -> Response:
        """
        The base function used to generate the responses from the Gemini API. This function selects the relevant sub-function to generate the response
        depending on the input type.

        Args:
            content (BaseTextInput): The input to be chunked.
            questions (list[str]): The list of questions to be answered from the content.
            chunking_strategy (BaseStrategy): The chunking strategy to be used to split the input into chunks.
            batching_strategy (BaseStrategy): The strategy used to group questions into batches.
            config (GeminiConfig, optional): The configuration settings for the query (such as model name, system prompt, caching options, etc).

        Returns:
            Response: An object containing all of the relevant information about the queries reponse. Including its answers and token usage.
                Optional information such as the chunks/batches generated can also be provided depending on the provided. `config` parameter.  

        Raises:
            NotImplemenentedError: If an unsupported chunking or batching strategy is provided.
        """

        # Updating the config if it has been changed
        if config != None:
            self.config = config
        else:
            config = self.config

        # Choosing the method to use based on the content type.
        match content:
            case BaseTextInput():
                return self._generate_content_from_text(
                    config=config,
                    content=content,
                    questions=questions,
                    chunking_strategy=chunking_strategy,
                    batching_strategy=batching_strategy
                )
            case BaseMediaInput():
                return self._generate_content_from_media(
                    config=config,
                    content=content,
                    questions=questions,
                    chunking_strategy=chunking_strategy,
                    batching_strategy=batching_strategy
                )
        return None
    
    def _generate_content_from_media(
        self,
        config : GeminiConfig,
        content : BaseMediaInput,
        questions : list[str],
        chunking_strategy : BaseStrategy,
        batching_strategy : BaseStrategy
    ) -> Response:
        """
        Generates answers to a set of questions from a media input using the provided chunking and batching strategies.
        This function handles calling the relevant chunking and batching functions to generate the required information.
        It then handles queries the Gemini API and combining the answers to produce the response.

        Args:
            config (GeminiConfig): The configuration settings for the query (such as model name, system prompt, caching options, etc).
            content (BaseTextInput): The video input to be chunked.
            questions (list[str]): The list of questions to be answered from the content.
            chunking_strategy (BaseStrategy): The chunking strategy to be used to split the media into chunks.
                Supported strategies:
                    - `TextSlidingWindowChunking`
                    - `TextSemanticChunking`
                    - `MediaSlidingWindowChunking`
                    - `MediaSemanticChunking`
            batching_strategy (BaseStrategy): The strategy used to group questions into batches.
                Supported strategies:
                    - `FixedBatching`
                    - `SemanticBatching`

        Returns:
            Response: An object containing all of the relevant information about the queries reponse. Including its answers and token usage.
                Optional information such as the chunks/batches generated can also be provided depending on the provided. `config` parameter.  

        Raises:
            NotImplemenentedError: If an unsupported chunking or batching strategy is provided.            
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            response = Response()
            # Generating the chunks based on the inputted technique
            chunks = []
            chunk_transcripts = None
            match chunking_strategy:
                case TextSlidingWindowChunking() | TextSemanticChunking():
                    # If we are using a text technique we generate a transcript and then just use that.
                    _, sentences = MediaChunkAndBatch.generate_transcript(content)
                    text_content = BaseTextInput(" ".join(sentences))
                    return self._generate_content_from_text(
                        config=config,
                        content=text_content,
                        questions=questions,
                        chunking_strategy=chunking_strategy,
                        batching_strategy=batching_strategy
                    )
                case MediaSlidingWindowChunking():
                    chunks = MediaChunkAndBatch.chunk_sliding_window_by_duration(
                        media_input=content,
                        output_folder_path=temp_dir,
                        chunk_duration=chunking_strategy.chunk_duration,
                        window_duration=chunking_strategy.window_duration
                    )
                case MediaSemanticChunking():
                    chunks, chunk_transcripts = MediaChunkAndBatch.chunk_semantically(
                        media_input=content,
                        output_folder_path=temp_dir,
                        gemini_client=self.gemini_api,
                        gemini_model=config.model,
                        min_sentences_per_chunk=chunking_strategy.min_sentences_per_chunk,
                        max_sentences_per_chunk=chunking_strategy.max_sentences_per_chunk,
                        transformer_model=chunking_strategy.transformer_model
                    )
                case _:
                    raise NotImplementedError("Provided chunking method is not implemented or not suitable for input type.")
            
            if config.show_chunks:
                logging.warning("Showing chunks in the response is not enabled for media chunking. This will not be returned.")
            
            # Generating the based on the inputted techniques
            batches = []
            match batching_strategy:
                case FixedBatching():
                    question_batches = DynamicBatch(
                        questions=questions,
                        batch_size=batching_strategy.batch_size
                    )
                    batches = [question_batches for _ in range(len(chunks))]
                    if config.show_batches:
                        logging.warning("Showing batches in the response is not enabled for fixed batching. This will not be returned.")
                case SemanticBatching():
                    if chunk_transcripts == None:
                        raise NotImplementedError("A transcript has not been generated using the provided chunking technique, so semantic batching is not available.")

                    semantic_batches = TextChunkAndBatch.batch_with_chunks_semantically(
                        chunk_transcripts,
                        questions,
                        batching_strategy.transformer_model
                    )
                    batches = [DynamicBatch(batch, batching_strategy.batch_size) for batch in semantic_batches]
                    if config.show_batches:
                        response.batches = batches
                case _:
                    raise NotImplementedError("Provided batching method is not implemented or not suitable for input type.")
            
            for i in range(len(chunks)):
                previous_context = ""
                if config.use_previous_responses_for_context:
                    previous_context_response = self._generate_summary_of_previous_answers(
                        config=config,
                        current_response=response
                    )
                    previous_context = previous_context_response.content
                    response.add_internal_response_only_token_info(previous_context_response)

                chunk_response = self._handle_single_media_chunk_and_batch(
                    config=config,
                    chunk_filepath=chunks[i],
                    question_batches=batches[i],
                    previous_context=previous_context
                )
                response.add_internal_response(chunk_response)
        
        return response
        
    def _generate_content_from_text(
        self,
        config : GeminiConfig,
        content : BaseTextInput,
        questions : list[str],
        chunking_strategy : BaseStrategy,
        batching_strategy : BaseStrategy
    ) -> Response:
        """
        Generates answers to a set of questions from a text input using the provided chunking and batching strategies.
        This function handles calling the relevant chunking and batching functions to generate the required information.
        It then handles queries the Gemini API and combining the answers to produce the response.

        Args:
            config (GeminiConfig): The configuration settings for the query (such as model name, system prompt, caching options, etc).
            content (BaseTextInput): The text input to be chunked.
            questions (list[str]): The list of questions to be answered from the content.
            chunking_strategy (BaseStrategy): The chunking strategy to be used to split the text into chunks.
                Supported strategies:
                    - `TextSlidingWindowChunking`
                    - `TextSemanticChunking`
                    - `TextTokenAwareChunkingAndBatching`
            batching_strategy (BaseStrategy): The strategy used to group questions into batches.
                Supported strategies:
                    - `FixedBatching`
                    - `SemanticBatching`

        Returns:
            Response: An object containing all of the relevant information about the queries reponse. Including its answers and token usage.
                Optional information such as the chunks/batches generated can also be provided depending on the provided. `config` parameter.  

        Raises:
            NotImplemenentedError: If an unsupported chunking or batching strategy is provided.            
        """

        response = Response()
        # Generating the chunks based on the inputted technique
        chunks = []
        match chunking_strategy:
            case TextSlidingWindowChunking():
                chunks = TextChunkAndBatch.chunk_sliding_window_by_length(
                    text_input=content,
                    chunk_char_size=chunking_strategy.chunk_char_size,
                    window_char_size=chunking_strategy.window_char_size
                )
            case TextSemanticChunking():
                chunks = TextChunkAndBatch.chunk_semantically(
                    text_input=content,
                    min_sentences_per_chunk=chunking_strategy.min_sentences_per_chunk,
                    max_sentences_per_chunk=chunking_strategy.max_sentences_per_chunk,
                    threshold_factor=chunking_strategy.similarity_threshold_factor,
                    transformer_model=chunking_strategy.transformer_model
                )
            case TextTokenAwareChunkingAndBatching():
                # If TokenAwareChunkingAndBatching is chosen as the chunking method the batching method is ignored.
                return self._token_aware_batching_and_chunking(
                    content=content,
                    questions=questions,
                )
            case _:
                raise NotImplementedError("Provided chunking method is not implemented or not suitable for input type.")
        if config.show_chunks:
            response.chunks = chunks

        # Generating the based on the inputted techniques
        batches = []
        match batching_strategy:
            case FixedBatching():
                question_batches = DynamicBatch(
                    questions,
                    batching_strategy.batch_size
                )
                batches = [question_batches for _ in range(len(chunks))]
                if config.show_batches:
                    logging.warning("Showing batches in the response is not enabled for fixed batching. This will not be returned.")
            case SemanticBatching():
                semantic_batches = TextChunkAndBatch.batch_with_chunks_semantically(
                    chunks,
                    questions,
                    batching_strategy.transformer_model
                )
                batches = [DynamicBatch(batch, batching_strategy.batch_size) for batch in semantic_batches]
                if config.show_batches:
                    response.batches = batches
            case _:
                raise NotImplementedError("Provided batching method is not implemented or not suitable for chunk type.")

        for i in range(len(chunks)):
            previous_context = ""
            if config.use_previous_responses_for_context:
                previous_context_response = self._generate_summary_of_previous_answers(
                    config=config,
                    current_response=response
                )
                previous_context = previous_context_response.content
                response.add_internal_response_only_token_info(previous_context_response)

            chunk_response = self._handle_single_text_chunk_and_batch(
                config=config,
                chunk=chunks[i],
                batches=batches[i],
                previous_context=previous_context
            )
            response.add_internal_response(chunk_response)
        
        return response

    def _handle_single_media_chunk_and_batch(
        self,
        config : GeminiConfig,
        chunk_filepath : str,
        question_batches : DynamicBatch,
        previous_context : str = ""
    ) -> InternalResponse:
        """
        Processes a single chunk of media and its batched questions to query the Gemini model and retrieve answers.
        This function uploads the relevant chunk to the model and then queries it with all the questions in the batch.

        Args:
            config (GeminiConfig): The configuration settings for the query (such as model name, system prompt, caching options, etc).
            chunk_filepath (str): The filepath to the chunk of media to be uploaded to the Gemini model.
            question_batches (DynamicBatch): The object managing the queue of questions to be asked to the chunk.
            previous_context (str, optional): Additional context from previous responses which are prepended to the query.
                This defaults to "" (i.e.) no previous context.
        
        Returns:
            InternalResponse: Contains the questions and answers provided by the model in addition to information about token usage.     
        """
        answers = {}
        total_input_tokens = 0
        total_output_tokens = 0

        batch = question_batches.get_question_batch()
        while len(batch) > 0:
            query_contents = previous_context + f'Content:\nThe content has been attached as a file.\n\nThere are {len(batch)} questions. The questions are:\n' + '\n\t- '.join(batch)
            
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
        
        return InternalResponse(
            content = answers,
            input_tokens = total_input_tokens,
            output_tokens = total_output_tokens
        )
    
    def _handle_single_text_chunk_and_batch(
        self,
        config : GeminiConfig,
        chunk : str,
        question_batches : DynamicBatch,
        previous_context : str = ""
    ) -> InternalResponse:
        """
        Processes a single chunk of text and its batched questions to query the Gemini model and retrieve answers.

        Args:
            config (GeminiConfig): The configuration settings for the query (such as model name, system prompt, etc).
            chunk (str): The text content chunk to be processed.
            question_batches (DynamicBatch): The object managing the queue of questions to be asked to the chunk.
            previous_context (str, optional): Additional context from previous responses which are prepended to the query.
                This defaults to "" (i.e.) no previous context.
        
        Returns:
            InternalResponse: Contains the questions and answers provided by the model in addition to information about token usage.        
        """
        answers = {}
        total_input_tokens = 0
        total_output_tokens = 0

        batch = question_batches.get_question_batch()
        while len(batch) > 0:
            query_contents = previous_context + f'Content:\n{chunk}\n\nThere are {len(batch)} questions. The questions are:\n' + '\n\t- '.join(batch)
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
        
        return InternalResponse(
            content = answers,
            input_tokens = total_input_tokens,
            output_tokens = total_output_tokens
        )
    
    def _token_aware_batching_and_chunking(
        self,
        config : GeminiConfig,
        content : BaseTextInput,
        questions : list[str],
    ) -> InternalResponse:
        """
        This function repeated resizes the chunks and batches it queries the Gemini API with to ensure token usage is maximised whilst
        also maintaining the token limits. This is done in a binary-search type pattern, where if the input token limit is exceeded the
        chunk size will be halved, and if the output token limit is exceeded, the batch size will be halved.

        Args:
            config (GeminiConfig): The configuration settings for the query (such as model name, system prompt, etc).
            content (BaseTextInput): The text content to process.
            questions (list[str]): The list of questions to be answered by the content.
        
            Returns:
                Response: Contains the answers provided by the model, in addition to information about token usage.
        """
        
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
            if input_tokens_used > input_token_limit:
                chunked_content = [curr_content[0 : len(curr_content)//2 + 1], curr_content[len(curr_content)//2 + 1 : len(curr_content)]]

                queue.append((chunked_content[0], curr_batch_size))
                queue.append((chunked_content[1], curr_batch_size))
                question_batcher.add_questions(curr_batch)

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
                    question_batcher.add_questions(curr_batch)
                    continue
                    
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

    def _generate_summary_of_previous_answers(
        self,
        config : GeminiConfig,
        current_response : Response
    ) -> InternalResponse:
        """
        Generates a summary of the previously answered questions to provide additional context for subsequent queries.

        Args:
            config (GeminiConfig): Config object containing the config settings for the gemini model.
            current_response (Response): The reponse object containing the previously answered questions.
        
        Returns:
            InternalResponse: A summarisation of the previously answered questions and the tokens used to generate it.
        """
        if len(current_response.content.keys) == 0:
            # No previous answers to summarise
            return ""
        
        previous_answers = []
        for question in current_response.content.keys():
            previous_answers.append(f'Question: {question}\nAnswer:{current_response.content[question]}')
        
        summary_response = self.gemini_api.generate_content(
            model=config.model,
            query="\n".join(previous_answers),
            system_prompt="Summarise the provided questions and answers as briefly as possible whilst maintaing as much information as possible. This will then be used in following queries."
        )

        summary_response.content = f"Context from previous answers:\n{summary_response.content}"
        return summary_response
