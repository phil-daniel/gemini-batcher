import os
from dotenv import load_dotenv

from gemini_efficient_api_calls import GeminiApi

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

CONTENT_FILE_PATH = "./example-content/content.txt"
QUESTION_FILE_PATH = "./example-content/questions.txt"

# TODO: Can use pre-existing datasets from hugging face - TED-LIUM (TED talk transcripts) or LibriSpeech ASR Corpus (audiobooks)

if __name__ == "__main__":
    # TODO: Change the file path reading to use os library, with absolute file paths.
    content = ""
    with open(CONTENT_FILE_PATH, 'r', encoding='utf-8') as file:
        content = file.read()
    
    questions = []
    with open(QUESTION_FILE_PATH, 'r', encoding='utf-8') as file:
        for question in file:
            questions.append(question.strip())
    
    # TODO: Added number to the questions to make it clearer 
    for i in range(len(questions)):
        questions[i] = f'{i+1}: {questions[i]}'
    
    client = GeminiApi(GEMINI_API_KEY, "gemini-2.0-flash")
    answers = client.generate_content_fixed(content, questions, 30000)
    
    for q in answers.keys():
        print (f'{q} : {answers[q]}')

    