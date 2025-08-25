---
title: WebsiteInput
nav_order: 4
parent: Inputs
---

# The `WebsiteInput` Class

The `FileInput` class represents a text input taken from a the raw-text of a website.

```python
from gemini_batcher.input_handler.textinputs import WebsiteInput

url = 'https://raw.githubusercontent.com/phil-daniel/gemini-batcher/refs/heads/main/examples/demo_files/content.txt'
text_content = WebsiteInput(url)
```

| *Class Attributes* | |
|------------------|----------------------------------------|
| content (str) | The text contents to be processed. |

## Initialisation

Initialises a `WebsiteInput` instance by retrieving the website's text content and storing it in the `content` attribute.
It also contains a retry mechanism if a connection error or timeout occured during the request.

```python
__init__(url)
```

| *Arguments* | |
|------------------|----------------------------------------|
| url (str) | The URL of the webpage to fetch content from. |

| *Raises* | |
|------------------|----------------------------------------|
| httpx.RequestError | If a network-related error occurs. |
| httpx.HTTPStatusError | If the response contains an error HTTP status code. |
