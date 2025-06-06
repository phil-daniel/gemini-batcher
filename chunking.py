import math
import json
import os

from google import genai
from google.genai import types

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

CONTENT = """
Python: A Powerful, Versatile Language for Modern Programming

Python is one of the most widely used programming languages in the world today, and its popularity continues to grow across industries and disciplines. Created in the late 1980s by Guido van Rossum and officially released in 1991, Python was designed to be easy to read, easy to write, and easy to maintain. It emphasizes code readability with its clean syntax, which makes it an excellent language for beginners while also being powerful enough to support complex systems and applications.

Clean Syntax and Readability
One of Python’s most celebrated features is its clean and readable syntax. Unlike languages that use semicolons and curly braces to delimit blocks of code, Python uses indentation. This approach forces developers to write neatly structured code, which is both a strength and a design philosophy. For example, a simple "if" statement or loop in Python is straightforward and readable, even for someone with limited programming experience. This focus on clarity not only reduces the likelihood of bugs but also improves collaboration among developers.

Dynamic Typing and Interpreted Nature
Python is dynamically typed, which means that you don’t need to declare variable types explicitly. The interpreter determines the type of variable at runtime. While this speeds up development, it can also introduce type-related bugs if not managed carefully. Still, for rapid prototyping and scripting, dynamic typing is a major advantage.

Python is also an interpreted language, meaning that code is executed line-by-line rather than being compiled into machine code ahead of time. This allows for faster development cycles, easier debugging, and better portability across systems. You can run the same Python code on different operating systems with little or no modification.

Multi-Paradigm Support
Python is a multi-paradigm language that supports procedural, object-oriented, and functional programming. This flexibility makes it suitable for a wide array of use cases. Beginners might start with procedural scripts to automate repetitive tasks, while advanced developers may design large, object-oriented systems or apply functional techniques for mathematical computations and data processing.

Extensive Standard Library
One of Python’s most powerful features is its standard library, often referred to as "batteries included." It includes modules for file I/O, regular expressions, system calls, internet protocols, data serialization, and much more. For instance, you can build a simple HTTP server, parse XML, or perform date and time operations—all without installing third-party packages. This built-in functionality allows developers to accomplish a lot with minimal setup.

Third-Party Ecosystem and Package Management
Beyond the standard library, Python has a vast ecosystem of third-party libraries and frameworks that extend its capabilities into virtually every domain of computing. For data science and numerical computing, libraries like NumPy, Pandas, and SciPy are widely used. For web development, frameworks such as Django and Flask provide powerful tools to build scalable web applications. In machine learning and artificial intelligence, Python leads the way with TensorFlow, PyTorch, Scikit-learn, and Keras. For game development, Pygame provides an easy-to-use interface to build 2D games.

Python’s package management system, primarily via pip, makes it simple to install, upgrade, and manage these external libraries. Python’s central package repository, PyPI (Python Package Index), hosts hundreds of thousands of projects, allowing developers to find and use tools tailored to their specific needs.

Cross-Platform Compatibility
Python runs on all major operating systems, including Windows, macOS, and various distributions of Linux. Its cross-platform nature means that code written on one OS will generally run on another without modification, making it a favorite for developers working in heterogeneous environments. Tools like virtual environments (venv or virtualenv) make it easy to manage dependencies and isolate project-specific packages, reducing compatibility issues.

Applications Across Industries
Python is used in a wide range of industries and domains. In web development, Django and Flask help developers build secure, scalable websites and APIs. In data science, tools like Jupyter Notebook make it easy to visualize and explore data interactively. In the financial sector, Python is used for quantitative analysis, algorithmic trading, and risk management. In bioinformatics, Python scripts automate the analysis of genetic data and lab results. Python is even used in fields as diverse as journalism, where it helps automate the processing of data for investigative reporting, and education, where it's the language of choice for many introductory computer science courses.

Machine Learning and AI
Python has become the de facto language for machine learning and artificial intelligence (AI). This dominance is due to its simple syntax, strong community support, and a powerful set of libraries and frameworks. Tools like TensorFlow and PyTorch allow developers and researchers to build and train complex neural networks. Scikit-learn provides a robust set of tools for traditional machine learning algorithms like decision trees, k-nearest neighbors, and support vector machines. Meanwhile, Keras offers a high-level API that simplifies the process of building deep learning models. Python’s simplicity allows data scientists to focus more on solving problems and less on the intricacies of the language.

Automation and Scripting
Another common use case for Python is automation and scripting. From writing small scripts to automate file system operations, to building bots that scrape websites or interact with APIs, Python excels in automating mundane and repetitive tasks. It’s especially popular among system administrators and DevOps engineers for tasks such as monitoring system health, deploying software, or managing cloud infrastructure.

Community and Resources
Python has a massive global community of developers, contributors, and educators. This vibrant ecosystem means that there are thousands of tutorials, forums, books, and video courses available for learners at all levels. Websites like Stack Overflow, Real Python, and Python.org are treasure troves of information. The Python Software Foundation (PSF) oversees the language’s development and fosters growth through conferences such as PyCon, which attract thousands of developers from around the world.

Versioning and Evolution
Python continues to evolve. The transition from Python 2 to Python 3 marked a major shift in the language’s design philosophy and feature set, bringing cleaner syntax and more consistent behavior. As of now, Python 3.x is the standard, and new features like structural pattern matching (introduced in Python 3.10), improved type hinting, and performance enhancements keep the language modern and relevant.

Conclusion
Python’s success lies in its simplicity, versatility, and the strength of its community. It’s a language that grows with you: approachable for beginners, yet powerful enough for experts working on cutting-edge problems in data science, AI, web development, and beyond. Whether you’re automating tasks, analyzing data, building web apps, or creating complex AI models, Python offers the tools and clarity to bring your ideas to life. Its philosophy of readability, rapid development, and community-driven progress makes Python not just a programming language, but a cornerstone of modern computing."""

SYSTEM_PROMPT = """
Answer the following questions, in a brief and precise manner, using only the information provided by the attached content. If the information is not provided by the video, answer with '-1'.
Respond in valid JSON of the form:
```
{
    "1" : "Answer to question 1",
    "2" : "Answer to question 2",
}
```
"""

QUESTIONS = ["Explain what Python is used for.", "When was Python created?"]

def fixed_length_chunking(chunk_char_size = 400):
    chunked_content = []
    chunk_count = math.ceil(len(CONTENT) / chunk_char_size)

    for i in range(chunk_count):
        chunk_start_pos = i * chunk_char_size
        chunk_end_pos = min(chunk_start_pos + chunk_char_size, len(CONTENT))
        chunked_content.append(CONTENT[chunk_start_pos : chunk_end_pos])

    return chunked_content

def sliding_window_chunking(chunk_char_size = 400, window_char_size = 100):
    # TODO: Error handling, add check to ensure window < chunk

    chunked_content = []
    chunk_count = math.ceil(len(CONTENT) / (chunk_char_size - window_char_size))

    for i in range(chunk_count):
        chunk_start_pos = i * (chunk_char_size - window_char_size)
        chunk_end_pos = min(chunk_start_pos + chunk_char_size, len(CONTENT))
        chunked_content.append(CONTENT[chunk_start_pos : chunk_end_pos])

    return chunked_content

def fixed_question_batching(questions_per_batch = 10): 
    batches = []
    batch_count = math.ceil(len(QUESTIONS) / questions_per_batch)

    for i in range(batch_count):
        batches.append(QUESTIONS[i : min(i + questions_per_batch, len(QUESTIONS))])
    return batches

if __name__ == "__main__":
    chunks = fixed_length_chunking(4000)

    client = genai.Client(api_key=GEMINI_API_KEY)

    for chunk in chunks:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
            contents=[SYSTEM_PROMPT, chunk, QUESTIONS]
        )
        print(response.text)