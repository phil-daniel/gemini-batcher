import logging
import httpx
from pathlib import Path
from abc import ABC

class BaseInput(ABC):
    """
    Abstract base class for all input types.
    This provides a common interfact which allows input types to be used interchangably.
    """
    pass

class BaseTextInput(BaseInput):
    """
    A simple object holding the text input used throughout the chunking process.

    Attributes:
        content (str): The text content.
    """

    content : str

    def __init__(
        self,
        content : str
    ) -> None:
        """
        Initialises a BaseTextInput instance with the provided content.

        Args:
            content (str): The text contents to be stored in the instance.
        """
        self.content = content

class FileInput(BaseTextInput):
    """
    Represents a text input retrieved from a file (such as a '.txt' file).
    """

    def __init__(
        self,
        filepath : str,
    ) -> None:
        """
        Initialises a FileInput instance by retrieving the text contents of a file and storing it in the `content` attribute.

        Args:
            filepath (str): The path to the file to be read.

        Raises:
            FileNotFoundError: Occurs if the inputted file does not exist.
            Exception: For unexpected errors occuring during file reading (these exceptions are reraised).
        """
        
        path = Path(filepath)
        
        if not path.exists():
            logging.error(f"File {filepath} not found.")
            raise FileNotFoundError(f"File {filepath} not found.")

        self.content = ""
        try:
            with open(path, 'r', encoding='utf-8') as file:
                self.content = file.read()
        except Exception as e:
            logging.error(f"Error occured while retrieving file contents. More information: {e}")
            raise

class WebsiteInput(BaseTextInput):
    """
    Represents a text input retrieved from a website source (such as a raw text file).
    """

    def __init__(
        self,
        url : str
    ) -> None:
        """
        Initialises a WebsiteInput instance by retrieving the website's text content and storing it in the `content` attribute.
        It contains a retry mechanism if a connection error or timeout occured during the request.

        Args:
            url (str): The URL of the webpage to fetch content from.

        Raises:
            httpx.RequestError: If a network-related error occurs.
            httpx.HTTPStatusError: If the response contains an error HTTP status code.
        """
        max_retries = 3
        for i in range(max_retries):
            try:
                response = httpx.get(url, timeout=10.0)
                response.raise_for_status()
                self.content = response.text
                break
            except (httpx.ConnectError, httpx.ReadTimeout) as e:
                # Retryable errors: connection issues or timeouts
                if i < max_retries - 1:
                    logging.warning(f"Request failed (attempt {i + 1}/{max_retries}), retrying. More info: {e}")
                else:
                    logging.error(f"Request failed at final attempt. More info: {e}")
                    raise
            except httpx.HTTPStatusError as e:
                # Non-200 responses (like 404, 500)
                logging.error(f"HTTP error occurred while requesting {url}. More info: {e}")
                raise
            except httpx.RequestError as e:
                # Catch-all for httpx request-related issues
                logging.error(f"Unexpected error occurred while requesting {url}. More info: {e}")
                raise