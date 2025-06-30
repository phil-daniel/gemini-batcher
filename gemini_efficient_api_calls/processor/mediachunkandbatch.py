import math
import os
import ffmpeg

from .textchunkandbatch import TextChunkAndBatch
from ..input_handler.textinputs import BaseTextInput
from ..input_handler.otherinputs import VideoFileInput
from ..geminiapi import GeminiApi

class MediaChunkAndBatch():
    
    def batch_by_number_of_questions(
        questions : list[str],
        questions_per_batch : int = 50
    ) -> list[list[str]]:
        """
        Easy access to the 'batch_by_number_of_questions' function provided by 'TextChunkAndBatch'.
        Groups a list of strings into multiple sublists, based on the maximum number of questions per batch.

        Args:
            - questions : The list of questions to be batched
            - questions_per_batch : The maximum number of questions that can be grouped together.
        
        Returns:
            - A list of a list of questions, where each sublist contains 'questions_per_batch' questions, other than the final
              sublist which may contain less.
        """
        return TextChunkAndBatch.batch_by_number_of_questions(questions, questions_per_batch)
    
    def chunk_sliding_window_by_duration(
        media_input : VideoFileInput,
        chunk_duration : int = 100,
        window_duration : int = 0,
    ) -> list[str]:
        """
        Chunks an inputted media files into multiple smaller files using the sliding window approach. 

        Args:
            - media_input: The content to be chunked, held in a VideoFileInput class
            - chunk_duration: The maximum duration of returned video chunks (in seconds).
            - window_duration: The duration of the chunk windows (in seconds). This is the overlap between consecutive chunks.
                                This is 0 by default.
        
        Returns:
            - A list of strings, where each string is the file path of a chunk of the inputted video. Each video is of duration
            'chunk_duration', except for the final video, which may be shorter.
        
        Raises:
            TODO
        """
        chunked_files = []
        chunk_count = math.ceil(MediaChunkAndBatch.get_video_duration(media_input.filepath) / (chunk_duration - window_duration))

        # TODO: Better method for creating temporary files?
        os.mkdir('./temp_output/')

        for i in range(chunk_count):
            chunk_start_pos = i * (chunk_duration - window_duration)
            MediaChunkAndBatch.trim_video(media_input.filepath, f'./temp_output/chunk_{i}.mp4', chunk_start_pos, chunk_duration)
            chunked_files.append(f'./temp_output/chunk_{i}.mp4')

        return chunked_files

    def chunk_and_batch_semantically(
        media_input : VideoFileInput,
        questions : list[str],
        gemini_client : GeminiApi,
        min_sentences_per_chunk : int = 5,
        max_sentences_per_chunk : int = 20,
        transformer_model : str = 'all-MiniLM-L6-v2'
    ):
        
        timestamps, sentences = MediaChunkAndBatch.generate_transcript(media_input.filepath, gemini_client)

        # TODO: Tidy up the basetextinput part
        chunked_text = TextChunkAndBatch.chunk_semantically(
            text_input = BaseTextInput(" ".join(sentences)), 
            min_sentences_per_chunk = min_sentences_per_chunk,
            max_sentences_per_chunk = max_sentences_per_chunk,
            transformer_model = transformer_model
        )

        batched_questions = TextChunkAndBatch.batch_with_chunks_semantically(
            chunked_content = chunked_text,
            questions = questions,
            transformer_model = transformer_model
        )

        # Handle same sentence twice in a transcript
        chunk_timestamps = []
        for chunk in chunked_text:
            final_sentence = chunk.split('. ')[-1].strip()
            index = sentences.index(final_sentence)

            if index != 0:
                start_time = timestamps[index]
            else:
                start_time = 0
            
            if index == len(sentences) - 1:
                end_time = MediaChunkAndBatch.get_video_duration(media_input.filepath)
            else:
                end_time = timestamps[index + 1]
            
            chunk_timestamps.append((start_time, end_time))

        for chunk in chunked_text:
            print(chunk)


        return chunk_timestamps, batched_questions


    def get_video_duration(
        path : str
    ) -> float:
        """
        Returns the duration of the video stored at the inputted file path in seconds.

        Args:
            - path: The filepath of the video.
        
        Returns:
            - The duration of the video in seconds.
        
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
    ):
        """
        Returns the duration of the video stored at the inputted file path in seconds.

        Args:
            - in_path: The filepath of the video to be trimmed.
            - out_path: The filepath the trimmed video should be stored at.
            - start_time: The timestamp of the original video the trimmed video should start at (in seconds).
            - duration: The duration of the trimmed video (in seconds).
        
        Raises:
            TODO
        """
        # TODO: Move this to each individual Input class.
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
        # TODO: Handle the transcript being over the API token limit.

        # TODO: Need to remove the file once done and tidy up.
        MediaChunkAndBatch.extract_audio(filepath, "temp_sound.wav")
        filepath = "temp_sound.wav"

        prompt = "Create a transcript of the provided media, in the format of: start time of sentence in seconds, caption."
        response = gemini_client.generate_content(
            prompt = prompt,
            files = [filepath],
            system_prompt = ""
        )

        timestamps = []
        sentences = []
        # Update prompt to simplify this
        for line in response.content:
            first_comma = line.find(',')
            timestamps.append(line[:first_comma])
            sentences.append(line[first_comma+2:].strip())

        return timestamps, sentences