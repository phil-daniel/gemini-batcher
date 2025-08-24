---
title: GeminiBatcher
nav_order: 4
parent: Library Documentation
---

# The `GeminiBatcher` Class

The `GeminiBatcher` is the core component of the gmeini-batcher library, serving as its primary interface. It integrates the logic of all the internal classes to efficiently chunk and batch content before querying the Gemini API.

```python
from gemini_batcher.gemini_batcher import GeminiBatcher

config = GeminiBatcher(config)
```

    Attributes:
        gemini_api (GeminiApi): The GeminiApi object provides a wrapper around the Gemini Python SDK, allowing for additional error handling.
        config (GeminiConfig): The default config settings to be used when querying the Gemini API. This can be replaced when calling `generate_content()`.
    """

| *Class Attributes* | |
|------------------|----------------------------------------|
| gemini_api (GeminiApi) | The GeminiApi object provides a wrapper around the Gemini Python SDK, allowing for additional error handling. |
| config (GeminiConfig) | The default config settings to be used when querying the Gemini API. This can, optionally, be replaced when calling `generate_content()`. |

## Initialisation

Initializes the `GeminiBatcher` object with a given Gemini configuration. This involves creating the GeminiApi object which allows for API calls to Gemini models to be made.

```python
__init__(config)
```

| *Arguments* | |
|------------------|----------------------------------------|
| config (GeminiConfig) | The configuration settings for the query (such as model name, system prompt, caching options, etc). |

## Methods

### `generate_content()`
The base function responsible for generating responses from the Gemini API. It determines which sub-functions to used based on the type of the input, ensuring that the response is generated appropriately.

```
generate_content(content, questions, chunking_strategy, batching_strategy, config)
```

| *Arguments* | |
|------------------|----------------------------------------|
| content (BaseTextInput) | The input to be chunked. |
| questions (list[str]) | he list of questions to be answered from the content. |
| chunking_strategy (BaseStrategy) | The chunking strategy to be used to split the input into chunks. |
| batching_strategy (BaseStrategy) | The strategy used to group questions into batches. |
| config (GeminiConfig, optional) | The configuration settings for the query (such as model name, system prompt, caching options, etc). This only needs to be provided if you'd like to make changes to the original config provided when initialises the `GeminiBatcher` object. |

 | *Returns* | |
|------------------|----------------------------------------|
| Response | An object containing all of the relevant information about the queries reponse. Including its answers and token usage. Optional information such as the chunks/batches generated can also be provided depending on the provided. `config` parameter.  |

 | *Raises* | |
|------------------|----------------------------------------|
| NotImplemenentedError | If an unsupported chunking or batching strategy for the given input type is provided.|
