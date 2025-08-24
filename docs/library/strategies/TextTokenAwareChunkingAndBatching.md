---
title: TextTokenAwareChunkingAndBatching
nav_order: 4
parent: Strategies
---

# The `TextTokenAwareChunkingAndBatching` Class

The `TextTokenAwareChunkingAndBatching` class refers to the strategy for chunking and batching text content and questions based on the token limit.

This method repeatedly makes API calls resizing its chunk and batch sizes to find an optimal fit.

```python
from gemini_batcher.strategies import TextTokenAwareChunkingAndBatching

strategy = TextTokenAwareChunkingAndBatching()
```

| *Class Attributes* | |
|------------------|----------------------------------------|
| N/A | |

**Note: This class is a `dataclass`, therefore, initialisation requires the exact same parameters as those described in the Class Attributes.**
