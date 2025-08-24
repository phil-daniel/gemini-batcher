---
title: Custom Inputs
nav_order: 8
parent: Inputs
---

# Custom Inputs

The built-in input classes represent only a small subset of the possible input types. For more specific use cases, it may be useful to create a custom input class, such as for access to a database.

For text-based inputs, custom classes should inherit from the `BaseTextInput` class, storing the content as a `content` attribute.

```python
from gemini_batcher.input_handler.textinputs import BaseTextInput

class CustomTextInput(BaseTextInput):
    def __init__(self, ...):
        # Custom logic here...
        self.content = ...
```

For media-based inputs, custom classes should inherit from the `BaseMediaInput` class, provide a `filepath` attribute and an implementation of the `get_audio_file()` function.