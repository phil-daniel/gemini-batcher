---
title: SemanticBatching
nav_order: 8
parent: Strategies
---

# The `SemanticBatching` Class

The `SemanticBatching` class refers to the strategy of batching items into groups based on their semantic similarity to the text chunks.

```python
from gemini_batcher.strategies import FixedBatching

strategy = SemanticBatching(batch_size, transformer_model)
```

| *Class Attributes* | |
|------------------|----------------------------------------|
| batch_size (int) | The maximum number of items in each batch. This must be greater than 0.|
| transformer_model (str, optional) | The SentenceTransformer model used to create sentence embeddings. The default model is `all-MiniLM-L6-v2`.|

**Note: This class is a `dataclass`, therefore, initialisation requires the exact same parameters as those described in the Class Attributes.**

There are also some restrictions on the class attributes:
- `batch_size` > 0