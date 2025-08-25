from dataclasses import dataclass

from .gemini_functions.gemini_api import InternalResponse

@dataclass
class Response:
    """
    Represents the response to a call to the Gemini-Batcher library.

    Attributes:
        content (dict): The contents of the response, the exact type could depend on the specific API call.
        input_tokens (int): The number of input tokens used by the query to the model.
        output_tokens (int): The number of output tokens used to generate the response.
        chunks (list[str], optional): Shows the chunks of the text transcript used in the API calls.
        batches (list[str], optional): Shows the question batches used in API calls. This is only relevant for semantic batching.
    """

    content : dict = {}
    input_tokens : int = 0
    output_tokens : int = 0
    chunks : list[str] = None
    batches : list[str] = None

    def add_internal_response(
        self,
        internal_response : InternalResponse
    ) -> None:
        """
        Merges an InternalRepsonse object into the current Response, updating each of the Response fields contained within the InternalResponse.

        Args:
            internal_response (InternalResponse): The InternalResponse object containing the information to merge.
        """
        if len(self.content.keys()) == 0:
            self.content = internal_response.content
        else:
            self.content.update(internal_response.content)
        self.input_tokens += internal_response.input_tokens
        self.output_tokens += internal_response.output_tokens
        return

    def add_internal_response_only_token_info(
        self,
        internal_response : InternalResponse
    ) -> None:
        """
        Merges the token information contained within an InternalRepsonse object into the current Response.

        Args:
            internal_response (InternalResponse): The InternalResponse object containing the information to merge.
        """
        self.input_tokens += internal_response.input_tokens
        self.output_tokens += internal_response.output_tokens
        return