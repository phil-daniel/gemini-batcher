import math
import ffmpeg
import tempfile
from pathlib import Path

from .text_chunk_and_batch import TextChunkAndBatch
from ..input_handler.text_inputs import BaseTextInput
from ..input_handler.media_inputs import BaseMediaInput, VideoFileInput
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
        """
        chunked_files = []
        chunk_count = math.ceil(MediaChunkAndBatch.get_video_duration(media_input.filepath) / (chunk_duration - window_duration))

        for i in range(chunk_count):
            # TODO: Different file extensions
            chunk_start_pos = i * (chunk_duration - window_duration)
            MediaChunkAndBatch.trim_video(
                in_path=media_input.filepath,
                out_path=f'{output_folder_path}/chunk_{i}.mp4',
                start_time=chunk_start_pos,
                duration=chunk_duration
            )
            chunked_files.append(f'{output_folder_path}/chunk_{i}.mp4')

        return chunked_files
    
    def chunk_semantically(
        media_input : VideoFileInput,
        output_folder_path : str,
        gemini_client : GeminiApi,
        gemini_model : str,
        min_sentences_per_chunk : int,
        max_sentences_per_chunk : int,
        transformer_model : str = 'all-MiniLM-L6-v2'
    ) -> tuple[list[str], list[str]]:
        """
        Splits a media input into chunks based on the semantic similarity of sentences in it's transcript.
        This works by generating a transcript, which is then split into text chunks using SentenceTransformer.
        Text chunks are then aligned with their corresponding video timestamps, and the input is trimmed into its chunks.

        Args:
            media_input (VideoFileInput): The video file input to be chunked.
            output_folder_path (str): The path to the folder where the video chunks should be saved. It can be useful to use `tempfiles` for this.
            gemini_client (GeminiApi): The client instance used to make calls to the Gemini API to generate transcripts.
            gemini_model (str): The Gemini model to use for transcription.
            min_sentences_per_chunk (int): The minimum number of sentences per chunk.
            max_sentences_per_chunk (int): The maximum number of sentences per chunk.
            transformer_model (str, optional): The SentenceTransformer model used to create sentence embeddings.
                The default model is 'all-MiniLM-L6-v2'.
        
        Returns:
            tuple[list[str], list[str]]:
                - A list of the file paths to the generated video chunk files.
                - A llist of the corresponding text chunks from the transcript.
        """

        transcript_duration = MediaChunkAndBatch.get_video_duration(
            path=media_input.filepath
        )
        timestamps, sentences = MediaChunkAndBatch.generate_transcript(
            filepath=media_input,
            gemini_client=gemini_client,
            model=gemini_model
        )

        chunks = TextChunkAndBatch.chunk_semantically(
            text_input=BaseTextInput(" ".join(sentences)), 
            min_sentences_per_chunk=min_sentences_per_chunk,
            max_sentences_per_chunk=max_sentences_per_chunk,
            transformer_model=transformer_model
        )

        chunk_timestamps = MediaChunkAndBatch.match_chunks_and_transcript_timings(
            chunks=chunks,
            transcript_sentences=sentences,
            transcript_timings=timestamps,
            media_end_time=transcript_duration
        )

        file_extension = Path(media_input.filepath).suffix

        chunk_files = []
        for i in range(len(chunk_timestamps)-1):
            MediaChunkAndBatch.trim_video(
                in_path=media_input.filepath,
                out_path=f'{output_folder_path}/chunk_{i}{file_extension}',
                start_time=chunk_timestamps[i],
                duration=chunk_timestamps[i+1]-chunk_timestamps[i]
            )
            chunk_files.append(f'{output_folder_path}/chunk_{i}{file_extension}')
        
        return chunk_files, chunks

    def get_video_duration(
        path : str
    ) -> float:
        """
        Returns the duration of the video stored at the inputted file path in seconds.

        Args:
            path (str): The filepath of the video.
        
        Returns:
            float: The duration of the video in seconds.
        """
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
        """
        ffmpeg.input(
            in_path,
            ss=start_time
        ).output(
            out_path,
            to=duration,
            c='copy'
        ).run(
            overwrite_output=True,
            capture_stdout=True,
            capture_stderr=True
        )
        return
    
    def generate_transcript(
        input_file : BaseMediaInput,
        gemini_client : GeminiApi,
        model : str
    ) -> tuple[list[float], list[str]]:
        """
        Generates a transcript for a video or audio file using the Gemini API.

        Args:
            filepath(str): Path to the input media file.
            gemini_client (GeminiApi): The Gemini client to be used for transcription.
            model (str): The Gemini model to use.
        
        Returns:
            tuple[list[float], list[str]]:
                - List of the start time (in seconds) for each transcribed sentence.
                - List of the corresponding sentences.
        """
        with tempfile.NamedTemporaryFile(suffix=".wav") as temp_audio_file:
            audio_filepath = temp_audio_file.name

            audio_filepath = input_file.get_audio_file(audio_filepath)

            prompt = (
                "Transcript the attached file, outputted as JSON. Each entry must be a single sentence with the following fields:"
                "start_time (in seconds as float), end_time (in seconds as float) and the sentence itself."
            )

            model_config = gemini_client.create_custom_content_config(
                response_mime_type="application/json",
                response_schema=list[TranscriptedSentence],
            )

            response = gemini_client.generate_content(
                model=model,
                prompt=prompt,
                files=[audio_filepath],
                system_prompt="",
                content_config=model_config
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
        """
        Aligns chunked transcript text with the timestamps from the original media input.

        This function assumes that:
        - Each chunk is formed by concatenating full transcript sentences.
        - Transcript timings are aligned at the sentence level.

        Args:
            chunks (list[str]): List of text chunks created during chunking.
            transcript_sentences (list[str]): List of the sentences generated during transcription.
            transcript_timings (list[float]): The start times for each transcripted sentence.
            media_end_time (float): The duration of the original media file (in seconds).
        
        Returns:
            list[float]: A list of timestamps corresponding to the chunk boundaries.
                Chunk `i`'s timestamp is between `i` and `i+1`
        """
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