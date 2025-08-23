from dataclasses import dataclass

from abc import ABC

class BaseStrategy(ABC):
    pass

@dataclass
class TextSlidingWindowChunking(BaseStrategy):
    chunk_char_size: int
    window_char_size: int = 0

@dataclass
class TextSemanticChunking(BaseStrategy):
    min_sentences_per_chunk: int
    max_sentences_per_chunk: int
    similarity_threashold_factor: float = 0.5
    transformer_model : str = 'all-MiniLM-L6-v2'

    def __post_init__(self):
        if not (0 < self.similarity_threashold_factor <= 1):
            raise ValueError("similarity_threashold_factor should be between 0 and 1.")

@dataclass
class TextTokenAwareChunkingAndBatching(BaseStrategy):
    pass

@dataclass
class MediaSlidingWindowChunking(BaseStrategy):
    chunk_duration: int
    window_duration: int = 0

@dataclass
class MediaSemanticChunking(BaseStrategy):
    min_sentences_per_chunk: int
    max_sentences_per_chunk: int
    similarity_threashold_factor: float = 0.5
    transformer_model : str = 'all-MiniLM-L6-v2'

    def __post_init__(self):
        if not (0 < self.similarity_threashold_factor <= 1):
            raise ValueError("similarity_threashold_factor should be between 0 and 1.")

@dataclass
class FixedBatching(BaseStrategy):
    batch_size: int

    def __post_init__(self):
        if self.batch_size <= 0:
            raise ValueError("batch_size should be greater than 0")

@dataclass
class SemanticBatching(BaseStrategy):
    batch_size: int
    transformer_model : str = 'all-MiniLM-L6-v2'
    # TODO: In the future might want to be able to batch to second most similar chunk etc.