---
title: Caching
nav_order: 10
parent: Concepts
---

# Caching

Very simply put, large language models (such as Gemini) work by processing the input to generate tokens, which are then transformed into embeddings (high dimensional vectors that can represent the structure and meaning of the text). These embeddings are then used by the model to predict the most likely next output token. Computing embeddings can be computationally expensive and time-consuming, especially when dealing with long, repetitive prompts.

Caching helps to optimise this process by storing the computed embeddings so that they can reused in future API calls. This means that instead of having to reprocess the entire input every time, the model can accessed the cache embeddings and only needs to compute embeddings for the new parts of the prompt.

Returning to our example, where we have a large transcript and a list of questions about the transcript, it is obvious that caching can be useful. If we want to ask multiple questions about a specific section of the transcript, we can cache that portion once and reuse it for each subsequent question, which can significantly improve the efficiency of these queries.

The Gemini family of models provide two methods of caching, 'implicit caching' and 'explicit caching'. This guide will give a quick overview of the two methods, with more detail available in the [Gemini Context Caching Documentation](https://ai.google.dev/gemini-api/docs/caching?lang=python).

TODO: Talk about how caching can reduce billed tokens.

Implicit caching is enabled by default and works automatically. It is more likely that an implicit cache hit will occur if similar prompts are made within a short amount of time with the common contents at the beginning of each prompt.

TODO: Add how to check whether implicit cache hits occur

Explicit caching on the other hand has to be completed manually. In this case, content is uploaded to the model and saved in a cache, with a link to the cache then being passed to the model during API queries. This can be done as follows:

```python
# Adding the content (the transcript) to the cache.
cache = client.caches.create(
    model="gemini-2.5-flash",
    config=types.CreateCachedContentConfig(
        display_name='transcript_content', # This allows for the cache to easily be accessed and referred to.
        system_instruction=system_prompt,
        contents=[content], # The actual contents of the cache. This could also contain other media types, such as videos and photos.
        ttl="300s", # The TTL (time to live) of the cache, this limits how long the cache is accessible for.
    )
)

# An API call can then be made using the cache rather than providing the content directly.
response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
    system_instruction=system_prompt,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        cached_content = cache.name # Here we referred to the previously cached transcript.
    ),
    contents=[f'\nQuestion:\n{question}'] # Only the questions are passed here and not the transcript.
)
```

A similar code sample demonstrating how caching can be used for other content types, such as videos, can be found in the Gemini documentation, [here](https://ai.google.dev/gemini-api/docs/caching?lang=python#generate-content).

TODO: Show performance difference, graph etc

## Additional Links
- [Gemini Context Caching Documentation](https://ai.google.dev/gemini-api/docs/caching?lang=python)