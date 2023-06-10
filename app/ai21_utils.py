""" Ai21 utilites """
import ai21

from config import AI21Config

ai21.api_key = AI21Config.AI21_API_KEY


def ai21_chat_completion(prompt, model=AI21Config.MODEL_ENGINE):
    """ given a prompt get a reponse from ai21 """
    return ai21.Completion.execute(
        model=model,
        prompt=prompt,
        maxTokens=8192
    )
