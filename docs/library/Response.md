---
title: Response
nav_order: 5
parent: Library Documentation
---

# The `Response` Class

The `Response` class is used to represent the returned information from a call to `GeminiBatcher.generate_content`. It contains the answers retrieved from queries to the Gemini API in addition to other relevant information.

```python
from gemini_batcher.response import Response

response = Response(content, input_tokens, output_tokens, chunks, batches)
```

| *Class Attributes* | |
|------------------|----------------------------------------|
| content (dict)| The API key used to make requests to the Gemini API. |
| input_tokens (int)| The number of input tokens used by the query to the model. |
| output_tokens (int)| The number of output tokens used to generate the response. |
| chunks (list[str], optional) | Shows the chunks of the text transcript used in the API calls. |
| batches (list[str], optional) | Shows the question batches used in API calls. This is only relevant for semantic batching. |

**Note: Although the `Response` class is not a `dataclass`, initialisation requires the exact same parameters as those described in the Class Attributes**

The class isn't a `dataclass` as it has internal functions used to combine singular responses from Gemini API calls together to produce the result.