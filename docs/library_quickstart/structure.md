---
title: Library Structure
nav_order: 20
parent: Library Quickstart
---

# Library Structure

{: .warning } This library is still in development and is subject to change.

The source code of the library is available on GitHub within the [gemini-batcher repository](https://github.com/phil-daniel/gemini-batcher/tree/main/gemini_batcher) and consists of the following file structure.

```
gemini-batcher/
├── gemini_batcher/
│   ├── __init__.py
│   ├── geminiapi.py
│   ├── geminihandler.py
│   ├── input_handler/
│   │    ├── textinputs.py
│   │    └── otherinputs.py
│   ├── output_handler/
│   │    └── 
│   ├── processor/
│   │    ├── mediachunkandbatch.py
│   │    └── textchunkandbatch.py
│   └── utils/
│   │    ├── exceptions.py
│   │    └── exceptionparser.py
├── docs/*
└── *
```

TODO: Add brief descriptions of the main folders once completed.