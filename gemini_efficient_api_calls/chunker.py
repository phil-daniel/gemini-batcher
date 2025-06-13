import math
import re

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

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
                start = i * questions_per_batch
                end = min((i+1) * questions_per_batch, len(questions))
                batches.append(questions[start:end])
        return batches
    
    def get_similarity_chunk_boundaries(
        self,
        similarities : list[float],
        min_sentences_per_chunk : int = 10,
        max_sentences_per_chunk : int = 100,
        threashold_factor : int = 0.6
    ):
        # TODO: Testing using a dynamic threashold, could also try just using a fixed value.
        mean = np.mean(similarities)
        std_dev = np.std(similarities)
        similarity_threashold = mean - (std_dev * threashold_factor)

        boundaries = [0]
        current_chunk_start_pos = 0
        for i in range(len(similarities)):
            # Checking if there is a natural boundary.
            if similarities[i] < similarity_threashold and (i + 1) - current_chunk_start_pos >= min_sentences_per_chunk:
                boundaries.append(i+1)
                current_chunk_start_pos = i + 1
            elif (i+1) - current_chunk_start_pos >= max_sentences_per_chunk:
                boundaries.append(i+1)
                current_chunk_start_pos = i + 1
        
        # Adding the end point if it has not already been added
        if boundaries[-1] != len(similarities) + 1:
            boundaries.append(len(similarities) + 1)
        return boundaries

    def semantic_chunk_and_batch(
        self,
        content : str,
        questions : list[str],
        min_sentences_per_chunk : int = 5,
        max_sentences_per_chunk : int = 100,
        transformer_model : str = 'all-MiniLM-L6-v2'
    ):
        content_chunks = []

        # TODO: Add error handling in case model doesn't exist -> Try, except
        model = SentenceTransformer(transformer_model)

        # Cleaning up the content to remove any white space and splitting it into sentences
        sentences = re.split(r'(?<=[.!?])\s+', content)
        sentences = [sentence.strip() for sentence in sentences]

        # Creating sentence embeddings using the SentenceTransformer model
        sentence_embeddings = model.encode(sentences)

        # Calculating the similarity between adjacent embeddings
        similarities = []
        for i in range(len(sentence_embeddings) - 1):
            # Reshape for cosine_similarity: (1, n_features) for each vector
            s1 = sentence_embeddings[i].reshape(1, -1)
            s2 = sentence_embeddings[i+1].reshape(1, -1)
            similarity = cosine_similarity(s1, s2)[0][0]
            similarities.append(similarity)
        
        boundaries = self.get_similarity_chunk_boundaries(similarities)
        content_chunks = []
        for i in range(len(boundaries) - 1):
            content_chunks.append(" ".join(sentences[boundaries[i] : boundaries[i+1]]))
        
        question_batches = [[] for _ in range(len(content_chunks))]
        
        # Finding the similarity between sentences and their chunks
        question_embeddings = model.encode(questions)
        chunk_embeddings = model.encode(content_chunks)

        for i in range(len(question_embeddings)):
            chunk_similarity = cosine_similarity(question_embeddings[i].reshape(1, -1), chunk_embeddings)[0]

            most_similar_chunk = np.argmax(chunk_similarity)
            question_batches[most_similar_chunk].append(questions[i])

        
        return content_chunks, question_batches