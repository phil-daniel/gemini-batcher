---
title: GeminiConfig
nav_order: 1
parent: Library Documentation
---

# The `GeminiConfig` Class

The `GeminiConfig` is a configuration object for controlling how the Gemini API and batching library is used.

```python
from gemini_batcher.gemini_config import GeminiConfig

config = GeminiConfig(my_api_key, 'gemini-2.5-flash')
```

| *Class Attributes* | |
|------------------|----------------------------------------|
| api_key (str) | The API key used to make requests to the Gemini API. |
| model (str) | The name of the Gemini model to be used. |
| use_previous_responses_for_context (bool, optional) | Controls whether answers from previous queries is used to gain more information. The default value is `false`.|
| use_explicit_caching (bool, optional) | Controls whether Gemini's explicit caching capabilties are used. The default value is `false`. |
| system_prompt (str, optional) | The system-level prompt that guides model behavior. The default prompt is provided as an example for usage with transcript & questions and can be seen in the source code. |
| show_chunks (bool) | Controls whether the chunks generated are returned with the response. This only occurs for text-based chunking. The default value is `false`. |
| show_batches (bool) | Controls whether the batches generated are returned with the response. This only occurs for semantic batching. The default value is `false`.|

**Note: This class is a `dataclass`, therefore, initialisation requires the exact same parameters as those described in the Class Attributes.**
