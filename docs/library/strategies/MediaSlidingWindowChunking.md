---
title: MediaSlidingWindowChunking
nav_order: 5
parent: Strategies
---

# The `MediaSlidingWindowChunking` Class

The `MediaSlidingWindowChunking` class refers to the strategy for chunking media input types based on overlapping windows of time durations.

```python
from gemini_batcher.strategies import MediaSlidingWindowChunking

strategy = MediaSlidingWindowChunking(chunk_duration, window_duration)
```

| *Class Attributes* | |
|------------------|----------------------------------------|
| chunk_duration (int) | The duration (in seconds) of each chunk. |
| window_duration (int, optional)| The duration (in seconds) that overlap between consecutive chunks. The default value is 0, meaning no overlap. |

**Note: This class is a `dataclass`, therefore, initialisation requires the exact same parameters as those described in the Class Attributes.**

There are also some restrictions on the class attributes:
-`chunk_duration` > `window_duration`
-`window_duration` >= 0