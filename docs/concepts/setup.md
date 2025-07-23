---
title: Setup
nav_order: 6
parent: Concepts
---

# Setup

Many of the code samples throughout this guide require additional python libraries and boilerplate code to use. Instructions to set this up can be found below.

## API Key Setup

In order to make use of the Gemini models, an API key must first be generated. Instructions for generating an API key can be found below, taking notes from [Patrick Loeber's Build with Gemini Workshop](https://github.com/patrickloeber/workshop-build-with-gemini/tree/main).

1. Visit [Google AI Studio](https://aistudio.google.com/apikey) to create or retrieve an API key.
2. Copy the API Key and save it called `GEMINI_API_KEY` for use in your project. In Google Colab this can be saved as a secret or in local development it can be saved as an environment variable using `export GEMINI_API_KEY=<your_key>`. In this guide the key is stored in a `.env` file as follows:
`GEMINI_API_KEY="<your_key>"`
It is important that you do not share this key in publicly available code.

### TODO: Mention changing the type of API key (billed/non-billed) 

## Package Installation

The code samples in this guide require various python libraries, which can all be installed using the following command:
```
pip install google-generativeai numpy sentence-transformers scikit-learn ffmpeg-python python-dotenv
```

These packages are used as follows:
- `google-generativeai` - This is an SDK provided by google which provides access to Google's LLM APIs.
- `numpy` - This is a widely used mathematical library.
- `sentence-transformers` - This is a python wrapper over Hugging Face's transformers, it provides pretrained models that can be used to compute semantic embeddings of sentences.
- `scikit-learn` - This is a widely used machine learning library. During this examples we will in particular be using its `consine_similarity` function, which computes can compute the simalarity between different embeddings.
- `ffmpeg-python` - A python wrapper over the FFmpeg CLI, which provides tools for audio and video processing.
- `python-dotenv` - A package which allows for environment variables to be easily read from `.env` files.

## Boilerplate Start Code

This code sample provides all the `import` and setup required to use the various libraries used in this guide. A key point to notice is that the Gemini API key for these code samples is stored in a `.env` file, which is then retrieved using the `load_dotenv` library. In the Google Colab variants of these code samples is instead stored as a secret.

```python
# Built-in Python Libaries
import os
import json
import math

# Google Generative AI SDK library
from google import genai
from google.genai import types

# Third-party libraries
import numpy as np # Provides useful numerical opertions for vectors, arrays and matrices.
from sentence_transformers import SentenceTransformer # Provides transformer models to calculate vector embeddings for text.
from sklearn.metrics.pairwise import cosine_similarity # Used for computing the similarity of vectors.
import ffmpeg # A wrapper library for the FFmpeg CLI used for audio & video processing.
from dotenv import load_dotenv # Used to load environment variables from '.env' files.

load_dotenv() # Loading the environment variables from the '.env' file.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # Retrieving the 'GEMINI_API_KEY' environment variable.
client = genai.Client(api_key=GEMINI_API_KEY) # Creates an instance of the Gemini API client, this can be used to make API calls.
```

Throughout this documentation, the usage of these techniques is demonstrated by attempting to answer a series of questions based on the transcript of a lecture. The example resources used in these scenarios can be retrieved as follows.

```python
import requests

questions = requests.get("https://raw.githubusercontent.com/phil-daniel/gemini-batcher/blob/main/examples/demo_files/questions.txt").text.split('\n')
answers = requests.get("https://raw.githubusercontent.com/phil-daniel/gemini-batcher/blob/main/examples/demo_files/content.txt").text
```