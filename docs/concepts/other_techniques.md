---
title: Other Batching and Chunking Techniques
nav_order: 9
parent: Concepts
---

# Other Batching and Chunking Techniques

In previous sections, basic techniques for batching and chunking (such as fixed batching) were demonstrated. These methods are incredibly easy to implement however there are alternative methods that may perform better. In this section we will discuss some of these methods.

Interactive examples demonstrating the techniques mentioned in this page can be found in following Google Colab:

<a target="_blank" href="https://colab.research.google.com/github/phil-daniel/gemini-batcher/blob/main/examples/other_techniques.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" height=30/></a>

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

## Semantic Chunking and Batching

### Semantic Chunking

Up until now, all of the chunking techniques discussed have broken up the content purely based on its length, rather than considering the meaning and structure of the content itself. Semantic chunking takes a different approach. Instead of breaking up the text arbitrarily, content is split at meaningful boundaries, such as topic shifts. This increases the likelihood that the answer to a question is entirely contained within a single chunk, which can result in improved responses.

TO perform semantic chunking, we begin by splitting the transcript into individual sentences, and then converting these sentences into embeddings (high dimensional vectors), similar to the steps required for LLMs. We can then calculate the consine similarity between adjacent sentence embeddings, where a large change indicates a potential boundary position for chunking.

```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Splitting sentences and stripping excess detail
sentences = re.split(r'(?<=[.!?])\s+', content)
sentences = [sentence.strip() for sentence in sentences]

model = SentenceTransformer(transformer_model)

# Creating sentence embeddings using the SentenceTransformer model
sentence_embeddings = model.encode(sentences)

# Calculating the similarity between adjacent embeddings
similarities = []
for i in range(len(sentence_embeddings) - 1):
    # Reshape for cosine_similarity: (1, n_features) for each vector
    s1 = sentence_embeddings[i].reshape(1, -1)
    s2 = sentence_embeddings[i+1].reshape(1, -1)
    similarity = cosine_similarity(s1, s2)[0][0]
    similarities.append(similarity)

# Calculating a threshold value for cosine similarity.
mean = np.mean(similarities)
std_dev = np.std(similarities)
similarity_threshold = mean - (std_dev * threshold_factor)

boundaries = [0]
current_chunk_start_pos = 0
for i in range(len(similarities)):
    # Checking if there is a natural boundary.
    if similarities[i] < similarity_threshold and (i + 1) - current_chunk_start_pos >= min_sentences_per_chunk:
        boundaries.append(i+1)
        current_chunk_start_pos = i + 1
    elif (i+1) - current_chunk_start_pos >= max_sentences_per_chunk:
        boundaries.append(i+1)
        current_chunk_start_pos = i + 1
        
# Adding the end point if it has not already been added
if boundaries[-1] != len(similarities) + 1:
    boundaries.append(len(similarities) + 1)

# Creating the chunks based on the boundaries.
content_chunks = []
for i in range(len(boundaries) - 1):
    content_chunks.append(" ".join(sentences[boundaries[i] : boundaries[i+1]]))
```

### Semantic Batching

We can continue with the semantic approach by also batching questions based on their meanings. There are two main approaches to this:
1. Questions can be batched together based on their similarity to one another.
2. Questions can be batched to chunks based on their similarity the chunk's contents. The advantage of this technique is that the model doesn't need to be queried with irrelvant question-chunk pairs, further improving the efficiency and token usage.

```python
# Creating a batch for each chunk. Each batch only contains the questions for its respective chunks.
question_batches = [[] for _ in range(len(content_chunks))]

# Creating embeddings for each question.
question_embeddings = model.encode(questions)
# Creating an embeddings for each chunk - not each sentence in a chunk.
chunk_embeddings = model.encode(content_chunks)

for i in range(len(question_embeddings)):
    # Calculating the similarity to each chunk.
    chunk_similarity = cosine_similarity(question_embeddings[i].reshape(1, -1), chunk_embeddings)[0]
    # Finding the most similar chunk and adding the question to its batch.
    most_similar_chunk = np.argmax(chunk_similarity)
    question_batches[most_similar_chunk].append(questions[i])
```

It is worth noting that while semantic chunking and batching can improve performance and reduce token usage, it does require additional computation (such as calculating embeddings) that the fixed techniques do not, meaning that the best approach will depend on your specific use case and constraints.