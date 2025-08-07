---
title: Setup
nav_order: 6
parent: Library
---

# Setup

## API Key Setup

In order to make use of the Gemini models, an API key must first be generated. Instructions for generating an API key can be found below and more detail can be found at [Patrick Loeber's Build with Gemini Workshop](https://github.com/patrickloeber/workshop-build-with-gemini/tree/main).

1. Visit [Google AI Studio](https://aistudio.google.com/apikey) to create or retrieve an API key.
2. Copy the API Key and save it called `GEMINI_API_KEY` for use in your project. In Google Colab this can be saved as a secret or in local development it can be saved as an environment variable using `export GEMINI_API_KEY=<your_key>`. In this guide the key is stored in a `.env` file as follows:
`GEMINI_API_KEY="<your_key>"`
It is important that you do not share this key in publicly available code.

Gemini API are classed as either non-billed (free) and billed (paid), with billed API keys allowing higher usage limits and access to additional features. For smaller projects a non-billed API key may suffice however for larger projects it may benefit from a billed API key to accomodate increased usage. More information about billed API keys can be found at the following links:
- [Pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Rate Limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Billing & Upgrading](https://ai.google.dev/gemini-api/docs/billing)

## Library Setup

Download the repository and install the package using:
```
pip install -e .
```
This will install the package in addition to all of its required dependencies.
