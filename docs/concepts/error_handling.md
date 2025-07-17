---
title: Error Handling
nav_order: 10
parent: Concepts
---

# Error Handling

In this section we will cover some of the many errors that occur during calls to the Python Gemini SDK and now they can be resolved.

## API Errors

These errors are typically triggered by bad requests, quota limits or server errors. In this documentation, we will cover some of the most frequently found errors, however more information about these errors can be found in the [Gemini error code documentation](https://ai.google.dev/gemini-api/docs/troubleshooting#error-codes). 

### HTTP Code 429, Status RESOURCE_EXHAUSTED
When using a free tier Gemini API it is very likely that you will face this error which occurs when too many requests are made in a short period of time. It is also possible that you may face this error with paid tiers, however this is unlikely as the limits are vastly higher. The exact limits can be found [here](https://ai.google.dev/gemini-api/docs/rate-limits#current-rate-limits).

This error can be identified by wrapping any `generate_content()` calls within a `try-except` clause and then checking the error code. An example of this is shown below:

```python
from google.genai import types, errors

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        ),
        contents=[f'Content:\n{content}', f'\nQuestion:\n{question}']
    )
except errors.APIError as e:
    if e.code == 429:
        print('Error 429 - Resource Exhausted')
        # Here we know that the error has occured and relative logic can be added to resolve the issue.
    else:
        print(f'Error {e.code} occured')
        # Similar logic can be applied to identify the specific error in other cases.
```

If you are repeatedly facing this error it may be useful to upgrade the Gemini tier being used, however if this is not possible there are various other techinques that can be used to help reduce it's occurence.



It is also possible to parse the error message provided by the Gemini API to retrieve the suggested retryDelay. This can be done as follows:

```python
time_to_wait = 0

for detail in error.details['error']['details']:
    if detail['@type'] == 'type.googleapis.com/google.rpc.RetryInfo':
        delay = detail['retryDelay']
        time_to_wait = int(delay[:-1])
        break
```

how to reoslve the error - fixed time or parsing the error
what does the error look like