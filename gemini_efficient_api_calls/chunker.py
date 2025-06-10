import math
import re

from sentence_transformers import SentenceTransformer

class Chunker:

    def sliding_window_chunking_by_size(
        self,
        content : str = "",
        chunk_char_size : int = 400,
        window_char_size : int = 100
    ):
        # TODO: Error handling, add check to ensure window < chunk
        # TODO: Add a sliding_window_chunking_by_num?

        chunked_content = []
        chunk_count = math.ceil(len(content) / (chunk_char_size - window_char_size))

        for i in range(chunk_count):
            chunk_start_pos = i * (chunk_char_size - window_char_size)
            chunk_end_pos = min(chunk_start_pos + chunk_char_size, len(content))
            chunked_content.append(content[chunk_start_pos : chunk_end_pos])

        return chunked_content

    def fixed_chunking_by_size(
        self,
        content : str,
        chunk_char_size : int = 20000
    ):
        # This is the same as using sliding window chunking with no window.

        return self.sliding_window_chunking_by_size(content, chunk_char_size, 0)
    
    def fixed_chunking_by_num(
        self,
        content: str,
        number_of_chunks : int = 5
    ):
        # Rather than defining a specific number of characters in each chunk, the content is distributed evenly across the specified number of chunks.

        # This is the same as using sliding window chunking with no window.
        chars_per_chunk = math.ceil(len(content) / number_of_chunks)

        return self.sliding_window_chunking_by_size(content, chars_per_chunk, 0)
    
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
        transformer_model : str = 'all-MiniLM-L6-v2'
    ):
        content_chunks = []
        question_batches = []

        # TODO: Add error handling in case model doesn't exist -> Try, except
        model = SentenceTransformer(transformer_model)

        # Cleaning up the content to remove any white space and splitting it into sentences
        sentences = re.split(r'(?<=[.!?])\s+', content)
        sentences = [sentence.strip() for sentence in sentences]

        sentence_embeddings = model.encode(sentences)
        
        return content_chunks, question_batches