---
title: Inputs
nav_order: 8
parent: Library
---

# Inputs

The `gemini-batcher` library supports a variety of different input types as content sources, each of which fall into two main categories: text or video. Each input type requires a corresponding input object, with different methods available depending on the input type category. 

## Text Inputs

The text-based input classes accept different forms of text content are compatible with all of the text-based chunking and batching functions in the library.

### BaseTextInput

The `BaseTextInput` class takes a direct input of a string of text, which contains the full block of text to be processed.

```python
from gemini_batcher.input_handler.textinputs import BaseTextInput

transcript = "Imagine this is a transcript! Ordinarily this would be a lot longer."
text_content = BaseTextInput(transcript)
```

### FileInput

The `FileInput` class allows for text content to be loaded directly for a plain-text file (e.g., `.txt`).

```python
from gemini_batcher.input_handler.textinputs import FileInput

filepath = 'path/to/content/file.txt'
text_content = FileInput(filepath)
```

### WebsiteInput

The `WebsiteInput` class allows for raw text content to be downloaded from a given URL, such as this [example lecture file](https://raw.githubusercontent.com/phil-daniel/gemini-batcher/refs/heads/main/examples/demo_files/content.txt).

```python
from gemini_batcher.input_handler.textinputs import WebsiteInput

url = 'https://raw.githubusercontent.com/phil-daniel/gemini-batcher/refs/heads/main/examples/demo_files/content.txt'
text_content = WebsiteInput(url)
```

## Video Inputs

TODO PLACEHOLDER for once input type structure for media is decided

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

TODO Custom video inputs