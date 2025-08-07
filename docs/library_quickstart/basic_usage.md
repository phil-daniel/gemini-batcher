---
title: Basic Usage
nav_order: 7
parent: Library Quickstart
---

# Basic Usage

The basic functionality of the library is provided within the `GeminiHandler` class, which serves a wrapper around the Gemini API and implements the various chunking and batching techniques.

Each of the techniques is implemented as its own dedicated function, supported by various other helper functions which are also available in the library. More information about these functions can be found in the detailed documentation.

In order to use these functions you must first create a `GeminiHandler` object, which requires an API key and the name of the model you wish to use (this can be changed later).
```python
from gemini_batcher.geminihandler import GeminiHandler
transcript = "This is your transcript or large block of content that needs chunking."
questions = ["This is your list of questions", "about the content"]

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
model = "gemini-2.5-flash"
client = GeminiHandler(GEMINI_API_KEY, model)
```

An input object for the inputted transcript then needs to be defined, the exact type of this object will depend on the input itself, more information about the various options can be found at [TODO ADD link](). In this example, the simplest text input is used.

```python
from gemini_batcher.input_handler.textinputs import BaseTextInput
text_content = BaseTextInput(transcript)
```

You can then use the various functions provided by class to make chunked and batched API calls, such as `generate_content_fixed()`, which uses fixed-size sliding window chunking and batching. A brief description of the various functions is provided below.
```
answers = client.generate_content_fixed(content = content, questions = questions)
print (f'Answers: {answers.content}')
print (f'Input tokens: {answers.input_tokens}, output tokens: {answers.output_tokens}')
```

There are several optional parameters that can be added to the function call to tweak the way the chunking and batching occur. These include:
- chunk_char_length (int) - The number of characters in each chunk, this defaults to 100000.
- question_per_batch (int) - The number of questions in each batch, this defaults to 50.
- window_char_length (int) - The number of characters in each sliding window, this defaults to 100.
- system_prompt (string) - A custom string prompt can be added if you don't want to use the default one.

A brief list of the main API wrapper functions provided within the `GeminiHandler` class can be found below:
- `generate_content_fixed(content : BaseTextInput, questions : list[str], chunk_char_length = 100000, questions_per_batch = 50, window_char_length = 100, system_prompt = None)`
    - Sliding window batching on a text input.
- `generate_content_token_aware(content : BaseTextInput, questions : list[str], system_prompt = None)`
    - A token aware text input technique, automatically alters the batch and chunk sizes to ensure token limits are followed.
- `generate_content_semantic(content : BaseTextInput, questions : list[str], system_prompt = None)`
    - A text input technique that chunks the content semantically and then batches semantically based on the chunks created.
- generate_content_media_fixed() - TODO
- generate_content_media_semantically() - TODO
    
