---
title: AudioFileInput
nav_order: 7
parent: Inputs
---

# The `AudioFileInput` Class

The `AudioFileInput` class represents an audio file that is to be used as the input for the chunking and batching functions.

```python
from gemini_batcher.input_handler.media_inputs import AudioFileInput

filepath = 'path/to/content/file.mp3'
text_content = AudioFileInput(filepath)
```

| *Class Attributes* | |
|------------------|----------------------------------------|
| filepath (str) | The filepath to the audio file. |

## Initialisation

Initialises a `AudioFileInput` instance.

```python
__init__(filepath)
```

| *Arguments* | |
|------------------|----------------------------------------|
| filepath (str) | The path to the audio file. |

## Methods

### `get_audio_file()`
Returns the filepath of the audio file (as the input file is already an audio file so no additional processing is needed.)

```python
get_audio_file(in_path, out_path)
```

| *Arguments* | |
|------------------|----------------------------------------|
| in_path (str) | The path to input media file. |
| out_path (str) | This is ignored.|

 | *Returns* | |
|------------------|----------------------------------------|
| str | The output path, this is the filepath of the audio file.|