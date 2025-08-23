from .text_inputs import BaseInput

class VideoFileInput(BaseInput):
    """
    Represents a video file that is to be used as the input for the chunking and batching functions.

    Attributes:
        filepath (str): The filepath to the video file.
    """
    
    filepath : str

    def __init__(
        self,
        filepath : str
    ) -> None:
        """
        Initialises a VideoFileInput.

        Args:
            filepath (str): The filepath to the video file.
        """
        self.filepath = filepath
        return
    
class AudioFileInput(BaseInput):
    """
    Represents an audio file that is to be used as the input for the chunking and batching functions.

    Attributes:
        filepath (str): The filepath to the audio file.
    """

    filepath : str

    def __init__(
        self,
        filepath : str
    ) -> None:
        """
        Initialises an AudioFileInput.

        Args:
            filepath (str): The filepath to the audio file.
        """
        self.filepath = filepath
        return
