import math
import re
import logging

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from ..input_handler.text_inputs import BaseTextInput

class TextChunkAndBatch():
    """
    Provides functions to chunk a large block of text and batch questions to it.
    """
    def chunk_sliding_window_by_length(
        text_input : BaseTextInput,
        chunk_char_size : int = 10000,
        window_char_size : int = 0
    ) -> list[str]:
        """
        Chunks an inputted text string into multiple smaller strings using the sliding window approach. 

        Args:
            text_input (BaseTextInput): The content to be chunked, held in a TextInput class (either BaseTextInput, FileInput or WebsiteInput)
            chunk_char_size (int): The maximum character length of returned chunks.
            window_char_size (int): The character length of the chunk windows. This is the overlap between consecutive chunks.
                                This is 0 by default.
        
        Output:
            list[str]: A list of strings, where each string is a chunk of the inputted content. Each string is of length 'chunk_char_size'
              except for the final string, which may be shorter.
        
        Raises:
            ValueError: This occurs if 'chunk_char_size' is smaller or equal to 'window_char_size' 
        """

        if (chunk_char_size <= window_char_size):
            logging.error("Window size is greater or equal to the chunk size.")
            raise ValueError("Window size is greater or equal to the chunk size.")

        chunked_content = []
        chunk_count = math.ceil(len(text_input.content) / (chunk_char_size - window_char_size))

        for i in range(chunk_count):
            start_pos = i * (chunk_char_size - window_char_size)
            end_pos = min(start_pos + chunk_char_size, len(text_input.content))
            chunked_content.append(text_input.content[start_pos : end_pos])

        return chunked_content

    def chunk_semantically(
        text_input : BaseTextInput,
        min_sentences_per_chunk : int = 5,
        max_sentences_per_chunk : int = 20,
        threshold_factor : float = 0.6,
        transformer_model : str = 'all-MiniLM-L6-v2'
    ) -> list[str]:
        """
        Chunks the input text into segments semantically based on the similarity between consecutive sentences.

        Args:
            text_input: The content to be chunked, held in a TextInput class (either BaseTextInput, FileInput or WebsiteInput)
            min_sentences_per_chunk: The minimum number of sentences within each chunk.
            max_sentences_per_chunk: The maximum number of sentences within each chunk.
            threshold_factor: The factor used to decide whether two consecutive sentences are similar enough,
              must be within mean-(std_dev*threshold_factor)
            transformer_model: The SentenceTransformer model used to create sentence embeddings.

        Output:
            list[str]: A list of strings, where each string is a chunk of the inputted content.

        Raises:
            Exception: If an error occurs during the loading of the SentenceTransformer model, the exception is reraised.
        """ 

        content_chunks = []

        try:
            model = SentenceTransformer(transformer_model)
        except Exception as e:
            logging.error(f"Failed to load transformer model \'{transformer_model}\' with exception {e}")
            raise Exception(f"Failed to load transformer model \'{transformer_model}\' with exception {e}")

        # Splitting sentences and stripping excess detail
        sentences = re.split(r'(?<=[.!?])\s+', text_input.content)
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
        
        mean = np.mean(similarities)
        std_dev = np.std(similarities)
        similarity_threshold = mean - (std_dev * threshold_factor)

        boundaries = [0]
        current_chunk_start_pos = 0
        for i in range(len(similarities)):
            # Checking if there is a natural boundary.
            if similarities[i] < similarity_threshold and (i + 1) - current_chunk_start_pos >= min_sentences_per_chunk:
                boundaries.append(i+1)
                current_chunk_start_pos = i + 1
            elif (i+1) - current_chunk_start_pos >= max_sentences_per_chunk:
                boundaries.append(i+1)
                current_chunk_start_pos = i + 1
        
        # Adding the end point if it has not already been added
        if boundaries[-1] != len(similarities) + 1:
            boundaries.append(len(similarities) + 1)
        
        content_chunks = []
        for i in range(len(boundaries) - 1):
            content_chunks.append(" ".join(sentences[boundaries[i] : boundaries[i+1]]))
        
        return content_chunks

    def batch_with_chunks_semantically(
        chunked_content : list[str],
        questions : list[str],
        transformer_model : str = 'all-MiniLM-L6-v2' 
    ) -> list[list[str]]:
        """
        Groups the inputted questions together based on their most semantically similar content chunk.

        Args:
            chunked_content (list[str]): The prechunked content, where each element in the list is a chunk of the content.
            questions (list[str]): The list of questions to be batched.
            transformer_model (str): The SentenceTransformer model used to create sentence embeddings.

        Output:
            list[list[str]]: A list of list of strings, where each string is one of the inputted questions and each sublist is a batch of questions.

        Raises:
            Exception: If an error occurs during the loading of the SentenceTransformer model, this is reraised.
        """ 
        try:
            model = SentenceTransformer(transformer_model)
        except Exception as e:
            logging.error(f"Failed to load transformer model \'{transformer_model}\' with exception {e}")
            raise Exception(f"Failed to load transformer model \'{transformer_model}\' with exception {e}")
        pass

        question_batches = [[] for _ in range(len(chunked_content))]

        # Finding the similarity between sentences and their chunks
        question_embeddings = model.encode(questions)
        chunk_embeddings = model.encode(chunked_content)

        for i in range(len(question_embeddings)):
            chunk_similarity = cosine_similarity(question_embeddings[i].reshape(1, -1), chunk_embeddings)[0]

            most_similar_chunk = np.argmax(chunk_similarity)
            question_batches[most_similar_chunk].append(questions[i])
        
        return question_batches