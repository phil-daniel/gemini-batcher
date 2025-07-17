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

When this error occurs, you see an error message such as:
```
{'error': {'code': 429, 'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits.', 'status': 'RESOURCE_EXHAUSTED', 'details': [{'@type': 'type.googleapis.com/google.rpc.QuotaFailure', 'violations': [{'quotaMetric': 'generativelanguage.googleapis.com/generate_content_free_tier_requests', 'quotaId': 'GenerateRequestsPerMinutePerProjectPerModel-FreeTier', 'quotaDimensions': {'location': 'global', 'model': 'gemini-2.0-flash'}, 'quotaValue': '15'}]}, {'@type': 'type.googleapis.com/google.rpc.Help', 'links': [{'description': 'Learn more about Gemini API quotas', 'url': 'https://ai.google.dev/gemini-api/docs/rate-limits'}]}, {'@type': 'type.googleapis.com/google.rpc.RetryInfo', 'retryDelay': '20s'}]}}
```

A `try-except` cause can be used to catch the error by wrapping around any `generate_content()` calls and then checking for the specific error code. An example of this is show below:

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
        # Here we know that the error has occured and relative logic can be added to resolve the issue.
        print('Error 429 - Resource Exhausted')
    else:
        # Similar logic can be applied to identify the specific error in other cases.
        print(f'Error {e.code} occured')
```

If you are repeatedly facing this error it may be useful to upgrade the Gemini tier being used, however if this is not possible a common technique for reducing the error is to add a retry timeout. Continuing with the previous code block, this would look as follows:

```python
import time

max_retries = 5 # Number of times to attempt the API call before stopping.
delay_time = 10 # The time to wait before retrying the API call if a 429 error occurs.

successful = False
for i in range(max_retries):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            ),
            contents=[f'Content:\n{content}', f'\nQuestion:\n{question}']
        )
        successful = True
        break
    except errors.APIError as e:
        if e.code == 429:
            # Here we know that the error has occured and relative logic can be added to resolve the issue.
            print('Error 429 - Resource Exhausted')
            time.sleep(delay_time) # Before retrying we wait `delay_time` seconds, this can avoid the rate limiting.
        else:
            print(f'Error {e.code} occured')
            # Add separate logic here to handle other errors.

if not successful:
    print ('Unable to complete the API call')
```

In the previous example a fixed delay time was used, however there are various other techniques which can be used. The first of which is to exponentially increase the delay time every time failure occurs. This could work as follows:

```python
max_retries = 5

for i in range(max_retries):
    try:
        # API call logic here
    except errors.APIError as e:
        if e.code == 429:
            time.sleep(2 ** i)
        else:
            # Add logic for other errors here
```

Finally it is also possible to use information from the error message provided by the Gemini API. In particularly, looking back at the error message shown above, the `retryDelay` value says how long to wait before retrying, therefore it is possible to parse this information to use. An example of the parsing is shown below:

```python
except errors.APIError as e:
    if e.code == 429:
        time_to_wait = 30 # Setting a default time to wait in case the information cannot be parsed.
        for detail in error.details['error']['details']:
            if detail['@type'] == 'type.googleapis.com/google.rpc.RetryInfo':
                delay = detail['retryDelay']
                time_to_wait = int(delay[:-1])
                break
        time.sleep(time_to_wait)
```