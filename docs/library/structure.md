---
title: Library Structure
nav_order: 6
parent: Library Documentation
---

# Library Structure

The source code of the library is available on GitHub within the [gemini-batcher repository](https://github.com/phil-daniel/gemini-batcher/tree/main/gemini_batcher) and consists of the following file structure.

```
gemini-batcher/
├── gemini_batcher/
│   ├── gemini_functions/
│   │    └── gemini_api.py
│   ├── input_handler/
│   │    ├── text_inputs.py
│   │    └── media_inputs.py
│   ├── processor/
│   │    ├── dynamic_batch.py
│   │    ├── media_chunk_and_batch.py
│   │    └── text_chunk_and_batch.py
│   └── utils/
│   │    ├── exceptions.py
│   │    └── exception_parser.py
│   ├── __init__.py
│   ├── gemini_batcher.py
│   ├── gemini_config.py
│   ├── response.py
│   └── strategies.py
├── docs/*
└── *
```

A short description of each of the files is also provided below:
- `gemini_api.py` - Provides code which creates a wrapper over the Gemini Python SDK, giving additional error handling functionality and simplified response information.
- `text_inputs.py`, `media_inputs.py` - Provides code for the various input types, as described in the [Inputs chapter](https://phil-daniel.github.io/gemini-batcher/library/inputs/).
- `dynamic_batch.py` - Provides logic for handling fixed batching, which is also used when a large batch is created during semantic batching.
- `media_chunk_and_batch.py`, `text_chunk_and_batch.py` - Provides logic for creating the various types of chunks and batches for each input type.
- `exceptions.py` - Provides additional exceptions used throughout the library.
- `exception_parser.py` Provides code used to parse errors occuring during API calls to Gemini models, in particular, for parsing the rate limiting information.
- `gemini_batcher.py` - Provides the high level logic of the library, including select the correct methodology depending on the input type and strategies provided. More information about this is provided in the [GeminiBatch chapter](https://phil-daniel.github.io/gemini-batcher/library/GeminiBatcher.html).
- `response.py` - Provides the format for a response from the library. More information can be found in the [Response chapter](https://phil-daniel.github.io/gemini-batcher/library/Response.html).
- `strategies.py` - Provides a way to define the various strategies used for chunking and batching. More information can be found in the [Strategies chapter](https://phil-daniel.github.io/gemini-batcher/library/strategies/).

The source code of the library also provides additional information about some of the functions and classes which were not documented within this section.