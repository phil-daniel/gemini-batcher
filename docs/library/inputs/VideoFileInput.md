---
title: VideoFileInput
nav_order: 6
parent: Inputs
---

# The `VideoFileInput` Class

The `VideoFileInput` class represents a video file that is to be used as the input for the chunking and batching functions.

```python
from gemini_batcher.input_handler.media_inputs import VideoFileInput

filepath = 'path/to/content/file.mp4'
text_content = VideoFileInput(filepath)
```

| *Class Attributes* | |
|------------------|----------------------------------------|
| filepath (str) | The filepath to the video file. |

## Initialisation

Initialises a `VideoFileInput` instance.

```python
__init__(filepath)
```

| *Arguments* | |
|------------------|----------------------------------------|
| filepath (str) | The path to the media file. |

## Methods

### `get_audio_file()`
Extracts the audio from a video file, saving is as a `.wav` file. The function uses FFmpeg, and converts the audio track into a single channel, sampled at 8 kHz.

```python
get_audio_file(in_path, out_path)
```

| *Arguments* | |
|------------------|----------------------------------------|
| in_path (str) | The path to input media file. |
| out_path (str) | The path to save the extracted audio file at. |

 | *Returns* | |
|------------------|----------------------------------------|
| str | The output path, this is the same as the out_path arguement.|