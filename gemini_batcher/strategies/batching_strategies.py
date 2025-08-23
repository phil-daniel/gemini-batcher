from dataclasses import dataclass

from .text_chunking_strategies import BaseStrategy

@dataclass
class FixedBatching(BaseStrategy):
    batch_size: int

    def __post_init__(self):
        if self.batch_size <= 0:
            raise ValueError("batch_size should be greater than 0")

@dataclass
class SemanticBatching(BaseStrategy):
    transformer_model : str = 'all-MiniLM-L6-v2'
    batch_size: int
    # TODO: In the future might want to be able to batch to second most similar chunk etc.