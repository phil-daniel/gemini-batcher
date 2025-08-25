---
title: TextSlidingWindowChunking
nav_order: 2
parent: Strategies
---

# The `TextSlidingWindowChunking` Class

The `TextSlidingWindowChunking` class refers to the strategy for chunking text based on overlapping windows of characters, also known as a "sliding window".

Although it is a text-based method, it can also be used by media input types by generating a transcript which is used as the content rather of the media itself.

```python
from gemini_batcher.strategies import TextSlidingWindowChunking

strategy = TextSlidingWindowChunking(chunk_char_size, window_char_size)
```

| *Class Attributes* | |
|------------------|----------------------------------------|
| chunk_char_size (int) | The number of characters per chunk. |
| window_char_size (int, optional)| The number of characters that overlap between consecutive chunks. The default value is 0, meaning no overlap. |

**Note: This class is a `dataclass`, therefore, initialisation requires the exact same parameters as those described in the Class Attributes.**

There are also some restrictions on the class attributes:
-`chunk_char_size` <= `window_char_size`
-`window_char_size` < 0