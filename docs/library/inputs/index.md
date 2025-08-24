---
title: Inputs
nav_order: 1
parent: Library Documentation
---

# Inputs

The `gemini-batcher` library supports a variety of different input types as content sources, each of which fall into two main categories: text or video. Each input type requires a corresponding input object, with different chunking and batching methods available depending on the input type category.

The main input types that are used are:
- Text Inputs:
    - `BaseTextInput`
    - `FileInput`
    - `WebsiteInput`
- Media Inputs (such as audio/video):
    - `VideoFileInput`
    - `AudioFileInput`

Two abstract classes are also provided, which help organise the input types into their respective categories:
- `BaseInput`
- `BaseMediaInput`






<!-- # Inputs

The `gemini-batcher` library supports a variety of different input types as content sources, each of which fall into two main categories: text or video. Each input type requires a corresponding input object, with different chunking and batching methods available depending on the input type category.

The main input types that are used are:
- Text Inputs:
    - `BaseTextInput`
    - `FileInput`
    - `WebsiteInput`
- Media Inputs (such as audio/video):
    - `VideoFileInput`
    - `AudioFileInput`

Two abstract classes are also provided, which help organise the input types into their respective categories:
- `BaseInput`
- `BaseMediaInput`

## Custom Inputs

These built-in classes represent only a small subset of the possible input types. For more specific use cases, it may be useful to create a custom input class, such as for access to a database.

For text-based inputs, custom classes should inherit from the `BaseTextInput` class, storing the content as a `content` attribute.

```python
from gemini_batcher.input_handler.textinputs import BaseTextInput

class CustomTextInput(BaseTextInput):
    def __init__(self, ...):
        # Custom logic here...
        self.content = ...
```

For media-based inputs, custom classes should inherit from the `BaseMediaInput` class, provide a `filepath` attribute and an implementation of the `get_audio_file()` function.

## Text Inputs

The text-based input classes accept different forms of text content are compatible with all of the text-based chunking and batching functions in the library.

### `BaseTextInput`

#### Methods


## Parameters




### `FileInput`

### `WebsiteInput`

## Media Inputs

### `VideoFileInput`

### `AudioFileInput`

## Abstract Inputs

### `BaseInput`

### `BaseMediaInput` -->