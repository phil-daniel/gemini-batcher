from dataclasses import dataclass

from abc import ABC

class BaseStrategy(ABC):
    pass

@dataclass
class SlidingWindowChunking(BaseStrategy):
    chunk_char_size: int
    window_char_size: int = 0

@dataclass
class SemanticChunking(BaseStrategy):
    min_sentences_per_chunk: int
    max_sentences_per_chunk: int
    similarity_threashold_factor: float = 0.5
    transformer_model : str = 'all-MiniLM-L6-v2'

    def __post_init__(self):
        if not (0 < self.similarity_threashold_factor <= 1):
            raise ValueError("similarity_threashold_factor should be between 0 and 1.")

@dataclass
class TokenAwareChunkingAndBatching(BaseStrategy):
    pass