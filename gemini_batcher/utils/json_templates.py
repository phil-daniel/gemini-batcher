from pydantic import BaseModel

class TranscriptedSentence(BaseModel):
    """
        Represents a single transcribed sentence from an audio or video source. This class is used as an format for JSON responses from the Gemini models.

        Attributes:
            start_time (float): The timestamp (in seconds) where the sentence begins.
            end_time (float): The timestamp (in seconds) where the sentence ends.
            sentence (str): The spoken contents of the sentence.
    """
    start_time: float
    end_time: float
    sentence: str