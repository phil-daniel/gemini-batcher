---
title: Batching
nav_order: 7
parent: Concepts
---

# Batching

Batching describes the process of combining multiple individual API calls together into a single API call. A real-life analogy would be shopping - imagine you need to buy three items, instead of making three separate trips to the shop where you buy a single item at a time, it would be far more efficient to just make a single trip and buy everything at the same time.

Batching API calls together can provide several benefits, including:
- Reduced latency - Rather than having to make repeated HTTP calls, only a single one must be made, reducing latency. In addition, since many LLM APIs have rate limits, the number of requests which can be made may be limited. 
- Improved cost efficiency - In some situations, combining your inputs into a single API call can reduce the number of tokens required. For example, given a paragraph costing 400 tokens to process, and 5 questions each costing 10 tokens, asking the questions one at a time would take ≈ (400 + 10) * 5 = 2050 tokens, whereas batching the questions would only take ≈ 400 + (10 * 5) = 450 tokens, giving a signficant improvement. An example of this is shown below.

There are, however, some considerations which need to be made during implementation, including:i 
- Response parsing - The Gemini API will return the answers to each of the queries together so you must then be able to separate each of these answers and match them to their original queries. This problem can be simplified using prompt engineering and enforcing a JSON output which can be easily parsed.
- Token limits - All LLM models have both input and output token limits which must be taken into account during batching as they may be exceed. Too many questions batched together many cause the input token limit to be exceeded and too large of a response from the API can cause the output token limit to be exceeded, so it is best to experiment with the batch size used for your specific scenario.

## Examples

The following examples demonstrate the efficiency gains achieved when using batching and can be tested yourself by following the [setup information](https://phil-daniel.github.io/gemini-batcher/concepts/setup.html) or accessing the Google Colab:
<a target="_blank" href="https://colab.research.google.com/github/phil-daniel/gemini-batcher/blob/main/examples/batching.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" height=30/></a>

### 1. No Batching

In the first example, no batching is used and questions are instead answered sequentially using on the content, with a custom system prompt used to ensure response accuracy. The response is returned in JSON format for easier comparison to the batched example.

```python
system_prompt = "Answer the questions using *only* the content provided, with each answer being a different string in the JSON response."

total_input_tokens_no_batching = 0
total_output_tokens_no_batching = 0

for question in questions[:5]:
    response = client.models.generate_content(
        model=MODEL_ID,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[str],
            system_instruction=system_prompt,
        ),
        contents=[f'Content:\n{content}', f'\nQuestion:\n{question}']
    )
    total_input_tokens_no_batching += response.usage_metadata.prompt_token_count
    total_output_tokens_no_batching += response.usage_metadata.candidates_token_count

print (f'Total input tokens used with no batching: {total_input_tokens_no_batching}')
print (f'Total output tokens used with no batching: {total_output_tokens_no_batching}')
```

### 2. Fixed Batching

In this second example, rather than asking each question one at a time, simple batching logic is used to group the questions into a batch of 5, which is passed to the API all at the same time. This results in a significant reduction in the number of input tokens used as the model is only provided with the large content once rather than five times.

The response is returned in JSON format to allow for easier separation of each question's answer.

```python
system_prompt = "Answer the questions using *only* the content provided, with each answer being a different string in the JSON response."

batched_questions = ("\n").join(questions[:5])

batched_response = client.models.generate_content(
    model=MODEL_ID,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=list[str],
        system_instruction=system_prompt,
        thinking_config=types.ThinkingConfig(thinking_budget=0,)
    ),
    contents=[f'Content:\n{content}', f'\nQuestions:\n{batched_questions}']
)

answers = batched_response.text
batched_answers = json.loads(answers.strip())

total_input_tokens_with_batching = batched_response.usage_metadata.prompt_token_count
total_output_tokens_with_batching = batched_response.usage_metadata.candidates_token_count

print (f'Total input tokens used with batching: {total_input_tokens_with_batching}')
print (f'Total output tokens used with batching: {total_output_tokens_with_batching}')
```

In the above example, only simple batching logic is used, however there are also more advanced techniques which also be implemented to provide increased efficiency. Many of these techniques also have to be combined with chunking, a technique for breaking down content into small parts.