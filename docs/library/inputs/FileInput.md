---
title: FileInput
nav_order: 3
parent: Inputs
---

# The `FileInput` Class

The `FileInput` class represents a text input taken from a plain-text file (such as a '.txt' file). 

```python
from gemini_batcher.input_handler.textinputs import FileInput

filepath = 'path/to/content/file.txt'
text_content = FileInput(filepath)
```

| *Class Attributes* | |
|------------------|----------------------------------------|
| content (str) | The text contents to be processed. |

## Initialisation

Initialises a FileInput instance by retrieving the text contents of a file and storing it in the `content` attribute.

```python
__init__(filepath)
```

| *Arguments* | |
|------------------|----------------------------------------|
| filepath (str) | The path to the file to be read. |

| *Raises* | |
|------------------|----------------------------------------|
| FileNotFoundError | Occurs if the inputted file does not exist. |
| Exception | For unexpected errors occuring during file reading (these exceptions are reraised). |
