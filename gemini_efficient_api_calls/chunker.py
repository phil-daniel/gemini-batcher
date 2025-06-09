import math

class Chunker:

    def fixed_length_chunking(
        self,
        content : str = "",
        chunk_char_size : int = 400
    ):
        chunked_content = []
        chunk_count = math.ceil(len(content) / chunk_char_size)

        for i in range(chunk_count):
            chunk_start_pos = i * chunk_char_size
            chunk_end_pos = min(chunk_start_pos + chunk_char_size, len(content))
            chunked_content.append(content[chunk_start_pos : chunk_end_pos])

        return chunked_content

    def sliding_window_chunking(
        self,
        content : str = "",
        chunk_char_size : int = 400,
        window_char_size : int = 100
    ):
        # TODO: Error handling, add check to ensure window < chunk

        chunked_content = []
        chunk_count = math.ceil(len(content) / (chunk_char_size - window_char_size))

        for i in range(chunk_count):
            chunk_start_pos = i * (chunk_char_size - window_char_size)
            chunk_end_pos = min(chunk_start_pos + chunk_char_size, len(content))
            chunked_content.append(content[chunk_start_pos : chunk_end_pos])

        return chunked_content
    
    def fixed_question_batching(
        self,
        questions : list[str],
        questions_per_batch : int = 50
    ): 
        # TODO: Error handling, no questions
        batches = []
        batch_count = math.ceil(len(questions) / questions_per_batch)

        for i in range(batch_count):
            batches.append(questions[i : min(i + questions_per_batch, len(questions))])
        return batches

    def semantic_chunk_and_batch(
        self,
        content : str,
        questions : list[str],
    ):
        pass