---
title: Using Previous Responses
nav_order: 11
parent: Concepts
---

# Using Previous Responses

In some cases, providing a model with its previous responses along with additional questions and context enables it to build on its earlier answers and incorporate details that may not be provided in the current input.

In the Python SDK, this conversation-like functionality is implemented using `clients.chat.create()` rather than ``generate_content()`, as it manages the conversation state internally. This works as `chat` automatically includes the entire conversation history in each request, which allows the model to stay aware of previous exchanges. 

```python
chat = client.chats.create(model="gemini-2.5-flash")

response = chat.send_message(
    ...
)

response = chat.send_message(
    ...
)
```
`chat.send_message()` can then be used the same as `generate_content()` which

## Using a Summary

As explained in the previous section, the `Chat` functionality in the Python SDK works by sending the entire conversation history to the model with each API call. This can become problematic when working with large inputs that are already close to the token limit, as including the full history may exceed the token limit whilst also adding irrelevant context.

In such cases, instead of relying on the built-in `Chat` object, it may be more effect to use the `generate_content()` function directly, prepending only the answers to previously answered questions to the content.

To further reduce the token size of the previous context, you could also make a separate API call - potentially to a less expensive model - to generate a summary of the earlier answers, which can then be included instead.