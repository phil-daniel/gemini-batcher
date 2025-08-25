from abc import abstractmethod
import ffmpeg

from .text_inputs import BaseInput

class BaseMediaInput(BaseInput):
    """
    Abstract base class for media inputs, this is used to gather all the media input types under a single umbrella.
    """

    filepath : str

    @abstractmethod
    def get_audio_file(
        self,
        out_path : str
    ) -> str:
        """
        Retrieve the path to the audio file associated with this media input.

        Args:
            out_path (str): The filepath of the output, where possible.

        Returns:
            str: The file path to the audio file.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        pass

class VideoFileInput(BaseMediaInput):
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

    def get_audio_file(
        self,
        out_path : str
    ) -> str:
        """
        Extracts the audio from a video file, saving is as a `.wav` file.
        The function uses FFmpeg, and converts the audio track into a single channel, sampled at 8 kHz.

        Args:
            in_path (str): The path to input media file.
            out_path (str): The path to save the extracted audio file at.
        
        Returns:
            str: The output path, this is the same as the out_path arguement.
        """
        ffmpeg.input(
            self.filepath
        ).output(
            out_path,
            ac=1,
            ar='8000'
        ).run(
            overwrite_output=True
        )
        return out_path
    
class AudioFileInput(BaseMediaInput):
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
    
    def get_audio_file(
        self,
        out_path : str
    ) -> str:
        """
        Provides the path to the audio file. This function is inheritted from `BaseMediaInput`.

        Returns:
            str: The filepath of the audio file.
        """
        return self.filepath
