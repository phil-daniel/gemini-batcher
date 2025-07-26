---
title: Other Batching and Chunking Techniques
nav_order: 9
parent: Concepts
---

# Other Batching and Chunking Techniques

In previous sections, basic techniques for batching and chunking (such as fixed batching) were demonstrated. These methods are incredibly easy to implement however there are alternative methods that may perform better. In this section we will discuss some of these methods.

## Token Awareness

As previously mentioned, one of the primary limitations of large language models is their token limit, which restricts the number of input and output tokens that can be processed or generated in a single API call. To improve the efficiency of API calls, it is important to make the best possible use of the available context window. One way of doing this is by dynamically adjusting the size of the input and expected output depending on the task and the model being used. This can be done using the chunking and batching techniques discussed earlier.

Revisiting our example use case - where we had a large block of text (a lecture transcript) and a list of questions relating to that text, we can use a binary search-style algorithm to find the largest input sizes that will produce queries fitting within the model's token limit. This can be done by iteratively making API calls to the model, chunking (to reduce the input size) and batching (to control the number of questions and hence reduce the output size) as needed to stay within the token limits.

To check whether the API call is within the token limits, we can do the following:
- Check the input token size and comparing it to the token limit. This can be done before making the API call:

```python
model_name = "gemini-2.5-flash"
input_token_limit = client.models.get(model = model_name).input_token_limit # Retrieving the input token limit of the specified model
input_tokens_required = client.count_tokens(
    model = model_name,
    contents = [content, questions]
)
if input_tokens_required > input_token_limit:
    # In this case we know that an API call with the current content will exceed the input token limit for the current model.
```

- Check whether the output token limit has been exceeded. It is important to note that we can not predict this before making the API call, and intead have to make the API call and then check whether it succeeded. This is discussed more in the [Error Handling section](https://phil-daniel.github.io/gemini-batcher/concepts/error_handling.html#max_tokens-finish-reason) of this guide.
```python
# Making the API call to Gemini
response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
    system_instruction=system_prompt,
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    ),
    contents=[f'Content:\n{content}', f'\nQuestion:\n{question}']
)

# Checking the finish reason of token generation, anything other than 'STOP' is unnatural.
if response.candidates[0].finish_reason == types.FinishReason.MAX_TOKENS:
    # In this case we know that token generation finished due to max token limit being exceeded.
```

Combining these checks together with a binary-search style approach gives us the following:

```python
model_name = "gemini-2.5-flash"
input_token_limit = client.models.get(model = model_name).input_token_limit # Retrieving the input token limit of the specified model

# Beginning with attempting to make an API call with the entire content & questions, if this fails we can break it up as appropriate.
queue = [(content, questions)]

while len(queue) > 0:
    curr_content, curr_questions = queue.pop(0)

    # Checking whether the input token limit is exceeded.
    input_tokens_required = client.count_tokens(
        model = model_name,
        contents = [curr_content, curr_content]
    )
    if input_tokens_required > input_token_limit:
        # In this case we know that an API call with the current content will exceed the input token limit for the current model.
        # If this is the case, we split the content in half so each API call processes half of the content.
        chunked_content = [curr_content[0 : len(curr_content)//2 + 1], curr_content[len(curr_content)//2 + 1 : len(curr_content)]]
        queue.append((chunked_content[0], curr_questions))
        queue.append((chunked_content[1], curr_questions))
        continue

    # Making the API call to the Gemini model
    reponse = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        ),
        contents=[f'Content:\n{curr_content}', f'\nQuestion:\n{curr_questions}']
    )

    # Checking the finish reason of token generation, anything other than 'STOP' is unnatural.
    if response.candidates[0].finish_reason == types.FinishReason.MAX_TOKENS:
        # In this case we know that token generation finished due to max token limit being exceeded, therefore we likely have not recieved a full answer.
        # We will therefore retry the API call but split the questions into batches of half the sizes to reduce the output.
        batch1, batch2 = curr_questions[0 : len(curr_questions)//2 + 1], curr_content[len(curr_questions)//2 + 1 : len(curr_questions)]
        queue.append((curr_content, batch1))
        queue.append((curr_content, batch2))
        continue

    # Add logic for handling valid responses here...
```


## Semantic Chunking and Batchingz