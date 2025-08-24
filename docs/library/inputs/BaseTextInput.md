---
title: BaseTextInput
nav_order: 2
parent: Inputs
---

# The `BaseTextInput` Class

The `BaseTextInput` class is the simplest of the inputted classes and represents the text content provided during initialisation.

```python
from gemini_batcher.input_handler.textinputs import BaseTextInput

transcript = "Imagine this is a transcript! Ordinarily this would be a lot longer."
text_content = BaseTextInput(transcript)
```

| *Class Attributes* | |
|------------------|----------------------------------------|
| content (str) | The text contents to be processed. |

## Initialisation

Initialises a `BaseTextInput` instance storing the provided content argument as a object attribute.

```python
__init__(content)
```

| *Arguments* | |
|------------------|----------------------------------------|
| content (str) | The text contents to be stored within the object for processing. |
