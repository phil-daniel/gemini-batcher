---
title: Strategies
nav_order: 3
parent: Library Documentation
---

# Strategies

Strategies are interchangeable objects which describe how content should be chunked and batched. Different media types are compatible with different strategies, as described below:

- Chunking strategies for text inputs:
    - `TextSlidingWindowChunking`
    - `TextSemanticChunking`
    - `TextTokenAwareChunkingAndBatching`
- Chunking strategies for media inputs:
    - `TextSlidingWindowChunking` (by using the transcript only)
    - `TextSemanticChunking` (by using the transcript only)
    - `MediaSlidingWindowChunking`
    - `MediaSemanticChunking`
