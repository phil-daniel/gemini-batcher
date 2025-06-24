import os
import math
import ffmpeg
import shutil
import whisper


class MediaChunker():
    def sliding_window_chunking_by_duration(
        self,
        filepath : str,
        chunk_duration : int = 100,
        window_duration : int = 25,
    ):
        chunk_count = math.ceil(self.get_video_duration(filepath) / (chunk_duration - window_duration))

        os.mkdir('./temp_output/')

        for i in range(chunk_count):
            chunk_start_pos = i * (chunk_duration - window_duration)
            self.trim_video(filepath, f'./temp_output/chunk_{i}.mp4', chunk_start_pos, chunk_duration)

        return

    def fixed_chunking_by_duration(
        self,
        filepath : str,
        chunk_duration : int = 100,
    ):
        os.mkdir('./temp_output/')

        chunk_count = math.ceil(self.get_video_duration(filepath) / chunk_duration)
        for i in range(chunk_count):
            self.trim_video(filepath, f'./temp_output/chunk_{i}.mp4', i * chunk_duration, chunk_duration)
        return chunk_count

    def semantic_chunking_media(
        self,
        filepath : str,
        whisper_model_size = "base"
    ):
        audio_path = self.extract_audio(filepath)

        model = whisper.load_model(whisper_model_size)
        transcript = model.transcribe(audio_path)

        timestamped_sentences = []
        
        # TODO: Handle transcript



        # Clean up temporary audio
        os.remove(audio_path)

        # TODO: Chunking based on this input
        pass
    
    def extract_audio(self, video_path, audio_path="temp_audio.wav"):
        # Extract audio from video using ffmpeg
        ffmpeg.input(video_path).output(audio_path, ac=1, ar='8000').run(overwrite_output=True)
        return audio_path
    
    def trim_video(in_path, out_path, start_time, duration):
        ffmpeg.input(in_path, ss=start_time).output(out_path, to=duration, c='copy').run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        # TODO: ADD ERROR HANDLING
        return
    
    def get_video_duration(path):
        probe = ffmpeg.probe(path)
        duration = float(probe['format']['duration'])
        return duration

    def clean_up_chunks():
        # Removes the "./temp_output/" directory, which contains the temporarily created chunks.
        shutil.rmtree('./temp_output/')
        pass