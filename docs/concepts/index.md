---
title: Concepts
nav_order: 5
---

# Concepts

This section will cover some of the key concepts used to improve the efficiency of API calls to the Gemini API. It also provides various code samples which demonstrate how these techniques can be implemented.

Some of code samples require addition python libraries and boilerplate code, the setup of which is described below.

## Setup

# TO ADD: SETUP API KEY GUIDE

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
```

Throughout this documentation, the usage of these techniques is demonstrated by attempting to answer a series of questions based on the transcript of a lecture. The example resources used in these scenarios can be retrieved as follows: 
```python
import requests

questions = requests.get("https://raw.githubusercontent.com/phil-daniel/gemini-batcher/blob/main/example/demo_files/questions.txt").text.split('\n')
answers = requests.get("https://raw.githubusercontent.com/phil-daniel/gemini-batcher/blob/main/example/demo_files/content.txt").text
```