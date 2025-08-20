import logging

from google.genai import errors

class ExceptionParser:

    def parse_rate_limiter_error(
        error : errors.APIError,
        default_delay : int = 30
    ) -> int:
        """
        Parses the content of a 'google.genai.errors.APIError' to retrieve the 'retryDelay' value.
        This is specifically for when API calls are being ratelimited, which can be identified by the '429' error code.
        If the error code is not '429' then only a small delay will be returned.

        Args:
            error (errors.APIError): The APIError produced during the API call.
            default_delay (int, optional): The delay time returned if the error cannot be parsed to retrieve the 'retryDelay' value.
        
        Returns:
            int: The time delay described in the 'retryDelay' value of the APIError's description in seconds. 5 seconds is also added to provide leeway.
            If the contents is unable to be parsed, a default delay time of 30 seconds is returned.
        """
        try:
            # If the error code is not 429 (which is caused by rate limiting) then there will be no retry info and the API call can be retried immediately.
            # A 5 second delay is returned just in case.
            if error.code != 429:
                return 5

            for detail in error.details['error']['details']:
                if detail['@type'] == 'type.googleapis.com/google.rpc.RetryInfo':
                    delay = detail['retryDelay']
                    # 5 seconds is added to the provided time just in case.
                    return int(delay[:-1]) + 5
            
            # If no value can be found, then a default delay time is returned. This also occurs if there is an exception.
            return default_delay
        except Exception as e:
            # If an exception occurs the default delay time is returned
            logging.warning(f"Exception occured whilst parsing the APIError for the retryDelay value. The default value will be returned instead. More info: {e}")
            return default_delay