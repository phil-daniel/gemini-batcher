---
title: Using Previous Responses
nav_order: 11
parent: Concepts
---

# Using Previous Responses

In some cases, providing a model with its previous responses along with additional questions and context enables it to build on its earlier answers and incorporate details that may not be provided in the current input.

In the Python SDK, this conversation-like functionality is implemented using `clients.chat.create()` which 

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

As mentioned in the previous section, the `Chat` functionality in the Python SDK works by sending the model the entire conversation history in each API call. However, when working with large chunks already approach the input token limit, including the full history may not be possible or may contain some sections that are not relevant. To resolve this, rather than using the provided `Chat` object, it may be more appropriate to just use the `generate_content()` function, adding all of the answers to the previously asked questions to the content.

To further reduce the number of tokens used for the previous answers, it may also be beneficial to make an separate API call to the model 