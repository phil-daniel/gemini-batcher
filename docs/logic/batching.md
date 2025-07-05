---
title: Batching
nav_order: 6
parent: Concepts
---

# Batching

Batching describes the process of combining multiple individual API calls together into a single API call. A real-life analogy would be shopping - imagine you need to buy three items, instead of making three separate trips to the shop where you buy a single item at a time, it would be far more efficient to just make a single trip and buy everything at the same time.

Batching API calls together can provide several benefits, including:
- Reduced latency - Rather than having to make repeated HTTP calls, only a single one must be made, reducing latency. In addition, since many LLM APIs have rate limits, the number of requests which can be made may be limited. 
- Improved cost efficiency - In some situations, combining your inputs into a single API call can reduce the number of tokens required. For example, given a paragraph costing 400 tokens to process, and 5 questions each costing 10 tokens, asking the questions one at a time would take ≈ (400 + 10) * 5 = 2050 tokens, whereas batching the questions would only take ≈ 400 + (10 * 5) = 450 tokens, giving a signficant improvement. An example of this is shown below.

There are, however, some considerations which need to be made during implementation, including:
- Response parsing - The Gemini API will return the answers to each of the queries together so you must then be able to separate each of these answers and match them to their original queries. This problem can be simplified using prompt engineering and enforcing a JSON output which can be easily parsed.
- Token limits - All LLM models have both input and output token limits which must be taken into account during batching as they may be exceed. Too many questions batched together many cause the input token limit to be exceeded and too large of a response from the API can cause the output token limit to be exceeded, so it is best to experiment with the batch size used for your specific scenario.

## Examples

[Link to Google Colab when created]

In the first example, no batching is used and questions are instead answered sequentially using on the content, with a custom system prompt used to ensure response accuracy.

```python
input_tokens = 0
output_tokens = 0

system_prompt = """
    Answer the question using the content provided.
    Provide direct, factual answers, using only information explicitly present in the content. Do not infer, speculate or bring in outside knowledge.
"""

for question in questions:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        ),
        contents=[f'Content:\n{content}', f'\nQuestion:\n{question}']
    )
    input_tokens += response.usage_metadata.prompt_token_count
    output_tokens += response.usage_metadata.candidates_token_count

print (f'Input tokens used: {input_tokens}')
print (f'Output tokens used: {output_tokens}')
```

In this second example, simple batching logic is used to group the questions into batches of 8, with each batch of questions being passed to the API one at a time. A slightly modified system prompt is also used, which requires the API to response in JSON format, which allows for every individual answer to be retrieved easily.

```python
# Batching the questions together, where each batch is of size 'questions_per_batch'
questions_per_batch = 8
batched_questions = []
for i in range(len(questions), questions_per_batch):
    batch = "\n".join(questions[i * questions_per_batch : min((i+1) * questions_per_batch, len(questions))])
    batched_questions.append(batch)

input_tokens = 0
output_tokens = 0

system_prompt = """
    Answer the questions using the content provided, with each answer being a different string in the JSON response.
    Provide direct, factual answers, using only information explicitly present in the content. Do not infer, speculate or bring in outside knowledge.
"""

for batch in batched_questions:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            # Setting 'response_mime_type' and 'response_schema' to ensure response is a parsable JSON format.
            response_mime_type="application/json",
            response_schema=list[str],
            system_instruction=system_prompt,
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        ),
        contents=[f'Content:\n{content}', f'\nQuestions:\n{batch}']
    )

    answers = response.text
    batched_answers = json.loads(answers.strip())
    # For question X in a batch (i.e. batch[X]), the answer can now be accessed from batched_answers[X]

    input_tokens += response.usage_metadata.prompt_token_count
    output_tokens += response.usage_metadata.candidates_token_count

print (f'Input tokens used: {input_tokens}')
print (f'Output tokens used: {output_tokens}')
```
