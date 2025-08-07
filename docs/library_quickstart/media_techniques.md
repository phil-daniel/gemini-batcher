---
title: Media Techniques
nav_order: 10
parent: Library Quickstart
---

# Media Techniques

The `GeminiHandler` class provides various video and audio compatible functions, which are listed below:

- generate_content_media_fixed() - TODO, information about parameters once finalised
- generate_content_media_semantically() - TODO

Each of the above functions use specific help functions provided by the `MediaChunkAndBatch` class, which can also be used directly in your code if required. These include:

TODO: Add the various functions once finalised.

A full list of these functions is provided in the detailed documentation.

## Using Text Methods Directly via Transcripts

It is also possible to use the text-based functions provided within `TextChunkAndBatch` by firstly generating a transcript of the media input which can then be passed as text to the required functions.

```python
from gemini_batcher.input_handler.textinputs import BaseTextInput
from gemini_batcher.input_handler.otherinputs import VideoFileInput
from gemini_batcher.processor.mediachunkandbatch import MediaChunkAndBatch
from gemini_batcher.processor.textchunkandbatch import TextChunkAndBatch

video_file_path = "path/to/file.mp4"

# Generating a transcript to use as the text input.
video_content = VideoFileInput(video_file_path)
_, transcript = MediaChunkAndBatch.generate_transcript(video_content, client)
content = BaseTextInput(transcript)

# The methods for text-based content can now be used
client.generate_content_fixed(content, questions)
```