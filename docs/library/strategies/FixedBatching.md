---
title: FixedBatching
nav_order: 7
parent: Strategies
---

# The `FixedBatching` Class

The `FixedBatching` class refers to the strategy of batching items into fixed-size groups.

```python
from gemini_batcher.strategies import FixedBatching

strategy = FixedBatching(batch_size)
```

| *Class Attributes* | |
|------------------|----------------------------------------|
| batch_size (int) | The maximum number of items in each batch. This must be greater than 0.|

**Note: This class is a `dataclass`, therefore, initialisation requires the exact same parameters as those described in the Class Attributes.**

There are also some restrictions on the class attributes:
- `batch_size` > 0