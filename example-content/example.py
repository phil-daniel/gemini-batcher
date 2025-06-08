import os
from dotenv import load_dotenv

from gemini_efficient_api_calls import Chunker

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

CONTENT_FILE_PATH = "./example-content/content.txt"
QUESTION_FILE_PATH = "./example-content/questions.txt"

if __name__ == "__main__":
    # TODO: Change the file path reading to use os library, with absolute file paths.
    content = ""
    with open(CONTENT_FILE_PATH, 'r', encoding='utf-8') as file:
        content = file.read()
    
    questions = []
    with open(QUESTION_FILE_PATH, 'r', encoding='utf-8') as file:
        for question in file:
            questions.append(question.strip())
    
    chunker = Chunker()
    chunker.generate_content_fixed(GEMINI_API_KEY, "gemini-2.0-flash", content, questions, 4000)

    