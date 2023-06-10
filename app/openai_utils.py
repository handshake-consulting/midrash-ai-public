""" Openai utilities """
import re
import time
from typing import List
import traceback
import openai
from openai.error import RateLimitError, InvalidRequestError
import tiktoken

from config import OpenAIConfig

# openai init
openai.api_key = OpenAIConfig.OPENAI_API_KEY


def get_openai_embeddings(content: str,
                          engine:str=OpenAIConfig.EMBEDDING_ENGINE) -> List:
    """ Retrive an embedding of content from openai """
    content = content.encode(encoding="ASCII", errors="ignore").decode()  # fix unicode errors
    response = openai.Embedding.create(input=content, engine=engine)
    vector = response['data'][0]['embedding']
    return vector


def openai_completion(messages, model=OpenAIConfig.MODEL_ENGINE, max_retry=5):
    """ Complete a request to openai and catch the possible errors
        When an error occurs wait 10 seconds to try and decrease the possibility of a rate limit 
    """
    retry = 0
    while True:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages
            )
            text = response["choices"][0]["message"]['content'].strip()
            text = re.sub(r'[\r\n]+', "\n", text)
            text = re.sub(r'[\t]+', " ", text)
            return text
        except RateLimitError as response_error:
            print("Rate Limit Exceeded, or openai bombarded with requests.")
            if retry >= max_retry:
                return f"GPT4 error: {response_error}"
            time.sleep(10)
        except InvalidRequestError as response_error:
            print(traceback.format_exc())
            print("Config might be wrong, check the vector length being used.")
            print(f'Openai error :{response_error}')
        except Exception as response_error:
            print(traceback.format_exc())
            retry += 1
            if retry >= max_retry:
                return f"GPT4 error: {response_error}"
            print("Error in communication with openai.")
            time.sleep(10)


def openai_completion_stream(messages, model=OpenAIConfig.MODEL_ENGINE, max_retry=5):
    """ Openai reponse stream """
    retry_number = 0
    retry = True
    while retry:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                stream=True
            )
            retry = False
            for chunk in response:
                try:
                    text = chunk["choices"][0]['delta']['content']
                    yield text
                except KeyError: # catch assistant # catch stop
                    continue
        except RateLimitError as response_error:
            print("Rate Limit Exceeded, or openai bombarded with requests.")
            if retry >= max_retry:
                return f"GPT4 error: {response_error}"
            time.sleep(10)
        except InvalidRequestError as response_error:
            print(traceback.format_exc())
            print("Config must be wrong.")
            print(f'Openai error :{response_error}')
        except Exception as response_error:
            print(traceback.format_exc())
            retry_number += 1
            if retry_number >= max_retry:
                retry = False
                return f"GPT4 error: {response_error}"
            print("Error in communication with openai.")
            time.sleep(10)


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens
