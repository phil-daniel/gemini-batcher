import math
import os
import ffmpeg
import tempfile

from .text_chunk_and_batch import TextChunkAndBatch
from ..input_handler.text_inputs import BaseTextInput
from ..input_handler.other_inputs import VideoFileInput
from ..gemini_functions.gemini_api import GeminiApi

from ..utils.json_templates import TranscriptedSentence

class MediaChunkAndBatch():
    """
    Provides a set of functions that can be used to chunk a video file and batch questions against it.
    """
    
    def chunk_sliding_window_by_duration(
        media_input : VideoFileInput,
        output_folder_path : str,
        chunk_duration : int = 100,
        window_duration : int = 0,
    ) -> list[str]:
        """
        Chunks an inputted media files into multiple smaller files using the sliding window approach. 

        Args:
            media_input (VideoFileInput): The content to be chunked, held in a VideoFileInput class.
            output_folder_path (str): The folder that the chunks media file should be saved in. It is useful to use the `tempfile` library to automatically handle removal of this.
            chunk_duration (int): The maximum duration of returned video chunks (in seconds).
            window_duration (int, optional): The duration of the chunk windows (in seconds). This is the overlap between consecutive chunks.
                                This is 0 by default, meaning there is no window.
        
        Returns:
            list[str]: Where each string is the file path of a chunk of the inputted video. Each video is of duration
            'chunk_duration', except for the final video, which may be shorter.
        
        Raises:
            TODO
        """
        chunked_files = []
        chunk_count = math.ceil(MediaChunkAndBatch.get_video_duration(media_input.filepath) / (chunk_duration - window_duration))

        for i in range(chunk_count):
            chunk_start_pos = i * (chunk_duration - window_duration)
            MediaChunkAndBatch.trim_video(media_input.filepath, f'{output_folder_path}/chunk_{i}.mp4', chunk_start_pos, chunk_duration)
            chunked_files.append(f'{output_folder_path}/chunk_{i}.mp4')

        return chunked_files

    def chunk_and_batch_semantically(
        media_input : VideoFileInput,
        questions : list[str],
        gemini_client : GeminiApi,
        min_sentences_per_chunk : int = 5,
        max_sentences_per_chunk : int = 20,
        transformer_model : str = 'all-MiniLM-L6-v2'
    ) -> tuple[list[float], list[str]]:
        transcript_duration = MediaChunkAndBatch.get_video_duration(media_input.filepath)
        timestamps, sentences = MediaChunkAndBatch.generate_transcript(media_input.filepath, gemini_client)

        chunks = TextChunkAndBatch.chunk_semantically(
            text_input = BaseTextInput(" ".join(sentences)), 
            min_sentences_per_chunk = min_sentences_per_chunk,
            max_sentences_per_chunk = max_sentences_per_chunk,
            transformer_model = transformer_model
        )

        batched_questions = TextChunkAndBatch.batch_with_chunks_semantically(
            chunked_content = chunks,
            questions = questions,
            transformer_model = transformer_model
        )

        chunk_timestamps = MediaChunkAndBatch.match_chunks_and_transcript_timings(
            chunks,
            sentences,
            timestamps,
            transcript_duration
        )

        return chunk_timestamps, batched_questions


    def get_video_duration(
        path : str
    ) -> float:
        """
        Returns the duration of the video stored at the inputted file path in seconds.

        Args:
            path (str): The filepath of the video.
        
        Returns:
            float: The duration of the video in seconds.
        
        Raises:
            TODO
        """
        # TODO: Error checking to ensure that the file path exists
        # TODO: Move this to each individual Input class.
        probe = ffmpeg.probe(path)
        duration = float(probe['format']['duration'])
        return duration
    
    def trim_video(
        in_path : str,
        out_path : str,
        start_time : float,
        duration : float
    ) -> None:
        """
        Returns the duration of the video stored at the inputted file path in seconds.

        Args:
            - in_path (str): The filepath of the video to be trimmed.
            - out_path (str): The filepath the trimmed video should be stored at.
            - start_time (float): The timestamp of the original video the trimmed video should start at (in seconds).
            - duration (float): The duration of the trimmed video (in seconds).
        
        Raises:
            TODO
        """
        # TODO: Error checking to ensure that the file path exists
        ffmpeg.input(in_path, ss=start_time).output(out_path, to=duration, c='copy').run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        return
    
    def extract_audio(
        in_path : str,
        out_path : str
    ):
        ffmpeg.input(in_path).output(out_path, ac=1, ar='8000').run(overwrite_output=True)
    
    def generate_transcript(
        filepath : str,
        gemini_client : GeminiApi
    ):
        with tempfile.NamedTemporaryFile(suffix=".wav") as temp_audio_file:
            audio_filepath = temp_audio_file.name

            MediaChunkAndBatch.extract_audio(filepath, audio_filepath)

            prompt = "Transcript the attached file, outputted as JSON. Each entry must be a single sentence with the following fields: start_time (in seconds as float), end_time (in seconds as float) and the sentence itself."

            model_config = gemini_client.create_custom_content_config(
                response_mime_type="application/json",
                response_schema=list[TranscriptedSentence],
            )

            response = gemini_client.generate_content(
                prompt = prompt,
                files = [audio_filepath],
                system_prompt = "",
                content_config = model_config
            )

        timestamps = []
        sentences = []
        
        for sentence_struct in response.content:
            sentences.append(sentence_struct["sentence"])
            timestamps.append(sentence_struct["start_time"])

        return timestamps, sentences
    
    def match_chunks_and_transcript_timings(
        chunks : list[str],
        transcript_sentences : list[str],
        transcript_timings : list[float],
        media_end_time : float
    ) -> list[float]:
        # This makes the assumption that the each chunk consists of entire sentences joined by spaces.
        chunk_times = [0]

        sentence_index = 0
        for i in range(len(chunks)):
            curr_sentence_size = transcript_sentences[sentence_index]
            while curr_sentence_size < len(chunks[i]) and sentence_index + 1 <= len(transcript_sentences):
                sentence_index += 1
                curr_sentence_size += transcript_sentences[sentence_index] + 1
            chunk_times.append(transcript_timings[sentence_index + 1])

        chunk_times.append(media_end_time)
        return chunk_times