from dataclasses import dataclass

from abc import ABC

@dataclass
class BaseStrategy(ABC):
    """
    Abstract base class for all batching and chunking strategies.
    This provides a common interfact which allows strategies to be used interchangably.
    """
    pass

@dataclass
class TextSlidingWindowChunking(BaseStrategy):
    """
    Strategy for chunking text based on overlapping windows of characters.
    This can also be used in media content by generating a transcript which is used instead of the nedia.

    Attributes:
        chunk_char_size (int): The number of characters per chunk.
        window_char_size (int, optional): The number of characters that overlap between consecutive chunks.
            The default value is 0, meaning no overlap.
    """
    chunk_char_size: int
    window_char_size: int = 0

    def __post_init__(self):
        """
        Validates:
            -`chunk_char_size` <= `window_char_size`
            -`window_char_size` < 0
        """
        if self.chunk_char_size <= self.window_char_size:
            raise ValueError("chunk_char_size must be greater than window_char_size")
        if self.window_char_size < 0:
            raise ValueError("window_char_size must be non-negative")

@dataclass
class TextSemanticChunking(BaseStrategy):
    """
    Strategy for chunking text based on the similarity of sentences.
    This can also be used in media content by generating a transcript which is used instead of the nedia.

    Attributes:
        min_sentences_per_chunk (int): The minimum number of sentences in each chunk.
        max_sentences_per_chunk (int): The maximum number of sentences in each chunk.
        similarity_threshold_factor (float, optional): The threshold factor determining whether sentences are similar enough to one another.
            Any provided value must be between 0 and 1. The default value is 0.5.
        transformer_model (str, optional): The SentenceTransformer model used to create sentence embeddings.
            The default model is `all-MiniLM-L6-v2`.
    """

    min_sentences_per_chunk: int
    max_sentences_per_chunk: int
    similarity_threshold_factor: float = 0.5
    transformer_model : str = 'all-MiniLM-L6-v2'

    def __post_init__(self):
        """
        Validates:
            -`similarity_threshold_factor` is within (0,1]
            -`max_sentences_per_chunk` > 0
            -`max_sentences_per_chunk` > `min_sentences_per_chunk`
        """
        if not (0 < self.similarity_threshold_factor <= 1):
            raise ValueError("similarity_threshold_factor should be between 0 and 1.")
        if self.max_sentences_per_chunk < 0:
            raise ValueError("max_sentences_per_chunk should be a positive integer.")
        if self.max_sentences_per_chunk < self.min_sentences_per_chunk:
            raise ValueError("max_sentences_per_chunk should be a greater than min_sentences_per_chunk.")

@dataclass
class TextTokenAwareChunkingAndBatching(BaseStrategy):
    """
    Strategy for chunking and batching text content and questions based on the token limit.
    This method repeatedly makes API calls resizing its chunk and batch sizes to find an optimal fit.
    """

    pass

@dataclass
class MediaSlidingWindowChunking(BaseStrategy):
    """
    Strategy for chunking media based on overlapping windows of time durations.

    Attributes:
        chunk_duration (int): The duration (in seconds) of each chunk.
        window_duration (int, optional): The duration (in seconds) that overlap between consecutive chunks.
            The default value is 0, meaning no overlap.
    """

    chunk_duration: int
    window_duration: int = 0

    def __post_init__(self):
        """
        Validates:
            -`chunk_duration` > `window_duration`
            -`window_duration` >= 0
        """
        if self.chunk_duration <= self.window_duration:
            raise ValueError("chunk_duration must be greater than window_duration")
        if self.window_duration < 0:
            raise ValueError("window_duration must be non-negative")

@dataclass
class MediaSemanticChunking(BaseStrategy):
    """
    Strategy for chunking media based on the similarity of its spoken content.
    This is done by generating a transcript and then using a similar method to `TextSemanticChunking`.

    Attributes:
        min_sentences_per_chunk (int): The minimum number of sentences in each chunk.
        max_sentences_per_chunk (int): The maximum number of sentences in each chunk.
        similarity_threshold_factor (float, optional): The threshold factor determining whether sentences are similar enough to one another.
            Any provided value must be between 0 and 1. The default value is 0.5.
        transformer_model (str, optional): The SentenceTransformer model used to create sentence embeddings.
            The default model is `all-MiniLM-L6-v2`.
    """

    min_sentences_per_chunk: int
    max_sentences_per_chunk: int
    similarity_threshold_factor: float = 0.5
    transformer_model : str = 'all-MiniLM-L6-v2'

    def __post_init__(self):
        """
        Validates:
            -`similarity_threshold_factor` is within (0,1]
            -`max_sentences_per_chunk` > 0
            -`max_sentences_per_chunk` > `min_sentences_per_chunk`
        """
        if not (0 < self.similarity_threshold_factor <= 1):
            raise ValueError("similarity_threshold_factor should be between 0 and 1.")
        if self.max_sentences_per_chunk < 0:
            raise ValueError("max_sentences_per_chunk should be a positive integer.")
        if self.max_sentences_per_chunk < self.min_sentences_per_chunk:
            raise ValueError("max_sentences_per_chunk should be a greater than min_sentences_per_chunk.")

@dataclass
class FixedBatching(BaseStrategy):
    """
    Strategy that batches items into fixed-size groups.

    Attributes:
        batch_size (int): The maximum number of items in each batch. This must be greater than 0.
    """

    batch_size: int

    def __post_init__(self):
        """
        Validates that a positive `batch_size` has been provided.
        """
        if self.batch_size <= 0:
            raise ValueError("batch_size should be greater than 0")

@dataclass
class SemanticBatching(BaseStrategy):
    """
    Strategy that batches items based on their semantic similarity to chunks.

    Attributes:
        batch_size (int): The maximum number of items in each batch. This must be greater than 0.
        transformer_model (str, optional): The SentenceTransformer model used to create sentence embeddings.
            The default model is `all-MiniLM-L6-v2`.
    """

    batch_size: int
    transformer_model : str = 'all-MiniLM-L6-v2'
    # TODO: In the future might want to be able to batch to second most similar chunk etc.

    def __post_init__(self):
        """
        Validates that a positive `batch_size` has been provided.
        """
        if self.batch_size <= 0:
            raise ValueError("batch_size should be greater than 0")