---
title: Multimedia Chunking
nav_order: 13
parent: Concepts
---

# Multimedia Chunking

Up until now, our examples have focused on applying chunking and batching techniques to simple text inputs. However, these strategies can also be extended to other media types, such as audio and video. In this section, we focus on how these techniques can be adapted for other input types, and also introduce other methods that are unique to specific media types.

## Duration Chunking

In the [Fixed Chunking](https://phil-daniel.github.io/gemini-batcher/concepts/fixed_chunking.html) section of this guide, we introduced straightforward techniques for splitting large blocks of text into smaller chunks based on character count. In media inputs (such as video and audio), we can instead break the content up by fixed time intervals (i.e. every 30 seconds), to produce smaller clips which contain fewer tokens and can therefore fit within the model's context window. This is demonstrated in the code sample below, which shows how sliding window chunking can be implemented.

TODO: Add example video which can be downloaded similar to the text files.

In this code sample, the input video file is chunked into multiple 100 second clips, each of which overlaps by 10 seconds using a sliding window
```python
input_file_path = "TODO"

chunk_duration = 100 # The duration (in seconds) of each chunk.
window_duration = 10 # The duration (in seconds) of the sliding window.

video_duration = float((ffmpeg.probe(path))['format']['duration']) # using the FFmpeg tool to retrieve the duration of the video in seconds.
number_of_chunks = math.ceil(video_duration / (chunk_duration - window_duration))

chunked_files = [] # This will hold an all of the file name of the chunked inputted so they can be easily accessed.

for i in range(number_of_chunks):
    chunk_start_time = i * (chunk_duration - window_duration)
    # Using the FFmpeg tool to trim each video into chunks, saving each as a file named 'chunk_i' where 'i' is the chunk number.
    ffmpeg.input(input_file_path, ss=chunk_start_time).output(f'chunk_{i}.mp4', to=chunk_duration, c='copy').run(overwrite_output=True, capture_stdout=True, capture_stderr=True) 
    chunked_files.append(f'chunk_{i}.mp4')
```

These chunks can then be used to query the Gemini API as followa:
```python
uploaded_file = client.files.upload(file=chunked_files[0]) # Uploading the 1st chunk of the video to the Gemini API.

# It can take time for the file to be uploaded, so we busy wait until it is available.
while uploaded_file.state.name == "PROCESSING" or uploaded_file.state.name == "PENDING":
    logging.info(f'Waiting for file {filepath} to upload, current state is {uploaded_file.state.name}')
    time.sleep(5)

# The uploaded file can now be included in the prompt as part of the contents.
response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    ),
    contents=[f'\nQuestion:\n{question}', f'Contents (attached as file named {chunked_files[0]})', uploaded_file]
)

```

## Transcript-based Chunking

TODO: Add how we can generate a transcript

## Other Chunking Methods

So far in this section, we have just demonstrated how a transcript can be generated from a video or audio file, which then allows for perform text-based chunking and batching techniques to be applied. However, video and audio inputs have additional features which can also be used to create chunks, either by themselves or in combiniation with the text-based methods.

### Audio Methods

Speaker diarization is the proceess of identifying and separating inidivdual speakers in an audio recording. It can also be used to determine natural breaks in speech, both of which act as good chunking points. One useful library for this is `pyannote.audio`, which provides pretrained models for speaker diarization models and voice detection.

### Video Methods

In the same way that we can extract the transcript of a video or audio for text proccessing, we can also extract the audio track of a video to apply the audio specific techniques such as speaker diarization, which was previously mentioned. The code sample in TODO: ADD LINK demonstrates how audio can be extracted with the `ffmpeg-python` package. 

Finally, video content also provides visual cues for chunking, such as scene changes or camera cuts. Another method would be to detect changes in the video, for example a change in scene or a camera cut, which could both provide a good chunking position. One useful tool for this is `PySceneDetect`, which is a python package that can be used to automatically detect shot changes in videos and to create separate clips.