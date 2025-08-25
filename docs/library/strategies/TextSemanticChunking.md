---
title: TextSemanticChunking
nav_order: 3
parent: Strategies
---
# The `TextSemanticChunking` Class

The `TextSemanticChunking` class refers to the strategy for chunking text based on the similarity of its sentences.

Although it is a text-based method, it can also be used by media input types by generating a transcript which is used as the content rather of the media itself.

```python
from gemini_batcher.strategies import TextSemanticChunking

strategy = TextSemanticChunking(min_sentences_per_chunk, max_sentences_per_chunk, similarity_threshold_factor, transformer_model)
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