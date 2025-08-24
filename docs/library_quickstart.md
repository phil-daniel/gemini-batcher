---
title: Library Quickstart
nav_order: 5
---

# Gemini-Batcher Library Quickstart Guide

## Install Library

Clone the repository and install the package as follows:
```
git clone https://github.com/phil-daniel/gemini-batcher.git
cd ./gemini-batcher
pip install -e .
```
This will install the package in addition to all of its required dependencies.

You will also have to generate a Gemini API key. Instructions for this can be found [here](https://phil-daniel.github.io/gemini-batcher/concepts/setup.html#api-key-setup). In our examples this API key is stored in the `GEMINI_API_KEY` constant.

## Create Configuration

With the package installed, you can now begin. We start by initialising a [`GeminiConfig`](https://phil-daniel.github.io/gemini-batcher/concepts/setup.html#api-key-setup) object, which stores information about our Gemini API key, model and other information. 

```python
from gemini_batcher.gemini_config import GeminiConfig

config = GeminiConfig(
    api_key=GEMINI_API_KEY,
    model="gemini-2.5-flash",
)
```

Additional arguements for the `GeminiConfig` object can be found in its respective documentation.

## Create Input Object

We can then define an "input object", which holds the content which is used to query the Gemini API. There are various different input types, depending on the format and source of the input, which are described in the [Inputs section](https://phil-daniel.github.io/gemini-batcher/library/inputs/). For this example, we will use a simple text input from a website.

```python
from gemini_batcher.input_handler.text_inputs import WebsiteInput

content = WebsiteInput(
    "https://raw.githubusercontent.com/phil-daniel/gemini-batcher/refs/heads/main/examples/demo_files/content.txt"
)
```

## Create Strategy Objects

We can define the strategies we would like to use for chunking and batching. Once again, the techniques available are dependant on the input type, with more information available in the [Strategies section](https://phil-daniel.github.io/gemini-batcher/library/strategies/).

For this example, we will chunk the text content semantically and then use fixed batching to split up the questions.

```python
from gemini_batcher.strategies import TextSemanticChunking, FixedBatching

chunking_strategy = TextSemanticChunking(
    min_sentences_per_chunk=25,
    max_sentences_per_chunk=50
)

batching_strategy = FixedBatching(
    batch_size=15
)
```

## Create the GeminiBatcher Object and Get Response

We can now finish by creating a `GeminiBatcher` object and calling the `generate_content()` function to make the relevant API calls to the Gemini models.

```python
from gemini_batcher.gemini_batcher import GeminiBatcher

client = GeminiBatcher(
    config=config
)

response = client.generate_content(
    content=content,
    questions=questions,
    chunking_strategy=chunking_strategy,
    batching_strategy=batching_strategy,
)

print('Answers:', response.content)
```