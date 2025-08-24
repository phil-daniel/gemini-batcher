---
title: Inputs
nav_order: 1
parent: Library Documentation
---

# Inputs

The `gemini-batcher` library supports a variety of different input types as content sources, each of which fall into two main categories: text or video. Each input type requires a corresponding input object, with different chunking and batching methods available depending on the input type category.

The main input types that are used are:
- Text Inputs:
    - `BaseTextInput`
    - `FileInput`
    - `WebsiteInput`
- Media Inputs (such as audio/video):
    - `VideoFileInput`
    - `AudioFileInput`

Two abstract classes are also provided, which help organise the input types into their respective categories:
- `BaseInput`
- `BaseMediaInput`