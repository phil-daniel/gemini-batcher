import logging
import requests

# TODO: Using inheritance to simplify structure

class TextInput():

    def __init__(
        self,
        content : str
    ):
        self.content = content

class FileInput():

    def __init__(
        self,
        filepath : str,
        filetype : str = 'txt'
    ):
        self.content = ""
        if filetype == 'txt':
            # TODO: Error handling if website does not exist
            with open(filepath, 'r', encoding='utf-8') as file:
                self.content = file.read()
        else:
            logging.error('File reading has currently only been implemented for txt files.')
            raise NotImplementedError("Only text file reading has been implemented")

class WebsiteInput():

    def __init__(
        self,
        link : str
    ):
        # TODO: Error handling, website doesnt exist, retry error etc
        response = requests.get(link)
        self.content = response.text