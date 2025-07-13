import json

from google.genai import types, errors

class ExceptionParser:

    def parse_rate_limiter_error(
        error : errors.APIError
    ) -> int:
        try:
            for detail in error.details['error']['details']:
                if detail['@type'] == 'type.googleapis.com/google.rpc.RetryInfo':
                    delay = detail['retryDelay']
                    return int(delay[:-1]) + 5
            
            return 30
        except Exception as e:
            print(e)
            return 30