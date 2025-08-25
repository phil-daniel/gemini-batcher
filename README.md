# Gemini Batcher

This is a project for Google Summer of Code 2025 under the Google Deepmind organisation. More details about the project can be found [here](https://summerofcode.withgoogle.com/programs/2025/projects/QwrjzUxs).

## Overview

Large language models, such as the Gemini family of models, are often limited by their context window - the number of input and output tokens they can process. Input tokens are produced when a model ingest any context, such as a prompt, and output tokens are generated when the model produces its response.

This repository provides code samples, documentation and a code library implementing various techniques that can be used to ensure context window constraints are followed while also improving token usage efficiency.

## Documentation

Documentation for this repository is available on its GitHub Pages site, [here](https://phil-daniel.github.io/gemini-batcher/). It is split into two separate parts, 'Concepts' and 'Library'.
- The [Concepts](https://phil-daniel.github.io/gemini-batcher/concepts/) section explains the techniques used in the library and provides simple code samples for each.
- The [Library](https://phil-daniel.github.io/gemini-batcher/library/) section covers the setup and usage instructions for our implementation of each techniques.

## Library Setup

1. Clone the repository.
```
git clone https://github.com/phil-daniel/gemini-batcher.git
cd gemini-batcher
```

2. Install the package and its required dependencies.
```
pip install -e .
```

3. Generate a Gemini API Key.
    Visit [Google AI Studio](https://aistudio.google.com/apikey), click 'Create API Key' and follow the instructions.

4. Save the API key as an environment variable called `GEMINI_API_KEY`. It is important that you do not share this key in any publicly available code.
    - If you are using Google Colab, save the API key as a secret.
    - If you are developing locally, save it as an environment variable using `export GEMINI_API_KEY=<your_key>`. Alternatively you can store the key in an `.env` file as follows. `GEMINI_API_KEY="<your_key>"`

5. You are free to use the library as required! Documentation can be found [here](https://phil-daniel.github.io/gemini-batcher/library/).

## Additional Code Samples

Additional code samples demonstrating the techniques covered, along with examples of how to use library can be found in the `./examples` subdirectory ([here](https://github.com/phil-daniel/gemini-batcher/tree/main/examples). Each notebook also includes a link to a corresponding Google Colab version for easy, online exploration.
