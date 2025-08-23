class DynamicBatch:
    """
    The DynamicBatch object is used to efficiently batch questions across chunks.
    It allows for the questions that have not been answered by a chunk to be kept track of, so that they can be answered by future chunks.

    Attributes:
        curr_chunk_question_queue (list[str]): The queue of questions to ask the current chunk.
        next_chunk_question_queue (list[str]): The queue of questions to ask the next chunk (already answered questions are removed).
    """

    curr_chunk_question_queue : list[str]
    next_chunk_question_queue : list[str]
    batch_size : int

    def __init__(
        self,
        questions : list[str],
        batch_size : int
    ) -> None:
        """
        Initialises the DynamicBatch object with the initial set of questions.

        Args:
            questions (list[str]): The complete list of questions to be asked.
        """
        self.curr_chunk_question_queue = questions.copy()
        self.next_chunk_question_queue = questions.copy()
        self.batch_size = batch_size

    def get_question_batch(
        self,
    ) -> list[str]:
        """
        Retrieves the next batch of questions to ask.
        If there are no more questions to ask the current chunk, an empty list is returned.

        Args:
            batch_size (int): The maximum number of questions to return.
        
        Returns:
            list[str]: A list of (up to `batch_size`) questions from the current question queue.
        """
        if len(self.curr_chunk_question_queue) == 0:
            self.curr_chunk_question_queue = self.next_chunk_question_queue
            return []
        else:
            batch_end_pos = min(self.batch_size, len(self.curr_chunk_question_queue))
            question_batch = self.curr_chunk_question_queue[:batch_end_pos]
            self.curr_chunk_question_queue = self.curr_chunk_question_queue[batch_end_pos:]
            return question_batch

    def mark_answered(
        self,
        question : str
    ) -> None:
        """
        Marks a question as answered by removing it from future queues.

        Args:
            question (str): The question to remove from the next chunk's queue.
        """
        self.next_chunk_question_queue.remove(question)

    def add_questions(
        self,
        questions : list[str]
    ) -> None:
        """
        Adds questions to the current question queue. This is useful when you would like a question reanswered.
        These new questions are added to the front of the queue.

        Args:
            questions (list[str]): The questions to be added to the queue.
        """
        self.curr_chunk_question_queue = questions + self.curr_chunk_question_queue
        
