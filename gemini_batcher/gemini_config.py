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
    api_key : str
    model : str
    use_previous_repsonses_for_context : bool = False
    use_explicit_caching : bool = False
    system_prompt : str = DEFAULT_SYSTEM_PROMPT
    show_chunks : bool = False
    show_batches : bool = False

