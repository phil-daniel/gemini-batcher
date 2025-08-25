---
title: MediaSemanticChunking
nav_order: 6
parent: Strategies
---
# The `MediaSemanticChunking` Class

The `MediaSemanticChunking` class refers to the strategy of chunking media based on the similarity of its spoken content. This is done by generating a transcript and then using a similar method to `TextSemanticChunking`.

```python
from gemini_batcher.strategies import MediaSemanticChunking

strategy = MediaSemanticChunking(min_sentences_per_chunk, max_sentences_per_chunk, similarity_threshold_factor, transformer_model)
```

| *Class Attributes* | |
|------------------|----------------------------------------|
| min_sentences_per_chunk (int) | The minimum number of sentences in each chunk. |
| max_sentences_per_chunk (int)| The maximum number of sentences in each chunk. |
| similarity_threshold_factor (float, optional)| The threshold factor determining whether sentences are similar enough to one another. Any provided value must be between 0 and 1. The default value is 0.5. |
| transformer_model (str, optional)| The `SentenceTransformer` model used to create sentence embeddings. The default model is `all-MiniLM-L6-v2`. |

**Note: This class is a `dataclass`, therefore, initialisation requires the exact same parameters as those described in the Class Attributes.**

There are also some restrictions on the class attributes:
    -`similarity_threshold_factor` is within 0 and 1
    -`max_sentences_per_chunk` > 0
    -`max_sentences_per_chunk` > `min_sentences_per_chunk`