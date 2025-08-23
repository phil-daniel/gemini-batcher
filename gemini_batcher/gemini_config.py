from dataclasses import dataclass

DEFAULT_SYSTEM_PROMPT = """
    Answer each of the inputted questions using the information provided to you in the prompt. Each answer should be a **single** string in the JSON response.
    There should be **exactly** one answer for each inputted question, no more, no less. 
    * **Accuracy and Precision:** Provide direct, factual answers. **Do not** create or merge any of the questions.
    * **Source Constraint:** Use *only* information explicitly present in the transcript. Do not infer, speculate, or bring in outside knowledge.
    * **Completeness:** Ensure each answer fully addresses the question, *to the extent possible with the given transcript*.
    * **Missing Information:** If the information required to answer a question is not discussed or cannot be directly derived from the transcript, respond with "N/A".
"""

@dataclass
class GeminiConfig():
    """
    Configuration object for controlling how the Gemini API and batching library is used.

    Attributes:
        api_key (str): The API key used to make requests to the Gemini API.
        model (str): The name of the Gemini model to be used.
        use_previous_responses_for_context (bool, optional): Controls whether answers from previous queries is used to gain more information.
            The default value is `false`.
        use_explicit_caching (bool, optional): Controls whether Gemini's explicit caching capabilties are used.
            The default value is `false`.
        system_prompt (str, optional): The system-level prompt that guides model behavior.
            The default is provided as an example for usage with transcript & questions.
        show_chunks (bool): Controls whether the chunks generated are returned with the response. This only occurs for text-based chunking.
            The default value is `false`.
        show_batches (bool): Controls whether the batches generated are returned with the response. This only occurs for semantic batching.
            The default value is `false`.
    """
    api_key : str
    model : str
    use_previous_responses_for_context : bool = False
    use_explicit_caching : bool = False
    system_prompt : str = DEFAULT_SYSTEM_PROMPT
    show_chunks : bool = False
    show_batches : bool = False

