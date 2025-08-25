---
title: BaseMediaInput
nav_order: 5
parent: Inputs
---

# The `BaseMediaInput` Class

The `BaseMediaInput` class is abstract base class for all of the media input types. It provides a common interface which allows various media input types to be used interchangably.

```python
from gemini_batcher.input_handler.media_inputs import BaseMediaInput
```

| *Class Attributes* | |
|------------------|----------------------------------------|
| filepath (str) | Path to the relevant media file. |

## Methods

### @abstract `get_audio_file()`

An abstract method implemented by child classes used to provide an audio file corresponding to the media file.


| *Arguments* | |
|------------------|----------------------------------------|
| out_path (str) | The filepath of the output, where possible. |

| *Returns* | |
|------------------|----------------------------------------|
| str | The file path to the audio file. In most cases, this is just the inputted `out_path` parameter.|