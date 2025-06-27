import math
import os
import ffmpeg

from .textchunkandbatch import TextChunkAndBatch

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
        self,
        filepath : str,
        chunk_duration : int = 100,
        window_duration : int = 25,
    ) -> list[str]:
        chunked_files = []
        chunk_count = math.ceil(MediaChunkAndBatch.get_video_duration(filepath) / (chunk_duration - window_duration))

        os.mkdir('./temp_output/')

        for i in range(chunk_count):
            chunk_start_pos = i * (chunk_duration - window_duration)
            self.trim_video(filepath, f'./temp_output/chunk_{i}.mp4', chunk_start_pos, chunk_duration)
            chunked_files.append(f'./temp_output/chunk_{i}.mp4')

        return chunked_files

    def get_video_duration(path):
        # TODO: Error checking to ensure that the file path exists
        probe = ffmpeg.probe(path)
        duration = float(probe['format']['duration'])
        return duration